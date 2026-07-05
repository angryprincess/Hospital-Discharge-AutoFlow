"""
Billing FastMCP Server.
Exposes Billing tools over MCP protocol.
Tools: get_billing_code, create_invoice, validate_invoice, calculate_total
PHI boundary strictly enforced: NO clinical data, diagnosis, or notes allowed.
"""
import sys
import os
import logging

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from mcp.server.fastmcp import FastMCP
from backend.services.billing_service import BillingService
from backend.security.rbac import require_permission
from backend.security.phi_guard import phi_guard
from backend.utils.audit_logger import audit_logger
from backend.models.audit import AuditStatus

logging.basicConfig(level=logging.INFO, format="%(asctime)s [BILLING-MCP] %(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

mcp = FastMCP(
    name="Billing-MCP-Server",
    instructions="""
    Billing MCP Server.
    Handles invoice creation, validation, billing codes, and total calculations.
    STRICT PHI boundary: Diagnosis, Clinical Notes, Doctor Notes, and Medical History
    must NEVER be included in billing requests.
    All calls are RBAC-controlled and audit-logged.
    """
)


@mcp.tool()
def get_billing_code(code: str, role: str = "administrator") -> dict:
    """
    Retrieve billing code information from the catalog.

    Args:
        code: Billing code (e.g., 'DM-HYP-001')
        role: Caller role for RBAC check

    Returns:
        Billing code details with description and base charge
    """
    tool_name = "get_billing_code"
    denial = require_permission(role, tool_name)
    if denial:
        audit_logger.log_denied("Billing", tool_name, role, denial,
                                input_data={"code": code})
        return {"status": "DENIED", "message": denial}

    result = BillingService.get_billing_code(code)

    if result.get("error"):
        audit_logger.log_failure("Billing", tool_name, role, result["message"],
                                 input_data={"code": code})
        return {"status": "ERROR", "message": result["message"]}

    audit_logger.log_success("Billing", tool_name, role,
                             input_data={"code": code},
                             output_summary=f"Code: {code}, Charge: ₹{result['data']['base_charge']}")
    return {"status": "SUCCESS", "data": result["data"]}


@mcp.tool()
def create_invoice(patient_id: str, billing_code: str, medicines: list,
                   role: str = "administrator") -> dict:
    """
    Create a new invoice for a patient discharge.
    PHI BOUNDARY: Only patient_id, billing_code, and medicines allowed.
    Clinical notes, diagnosis, lab results must NOT be included.

    Args:
        patient_id: Patient identifier
        billing_code: Billing code for the condition
        medicines: List of medicines [{generic_name, quantity}]
        role: Caller role for RBAC check

    Returns:
        Created invoice with line items and grand total
    """
    tool_name = "create_invoice"
    denial = require_permission(role, tool_name)
    if denial:
        audit_logger.log_denied("Billing", tool_name, role, denial, patient_id,
                                input_data={"patient_id": patient_id, "billing_code": billing_code})
        return {"status": "DENIED", "message": denial}

    # PHI boundary check — validate no PHI in the request
    request_check = {"patient_id": patient_id, "billing_code": billing_code, "medicines": medicines}
    phi_valid, phi_msg = phi_guard.validate_billing_request(request_check)
    if not phi_valid:
        audit_logger.log_denied("Billing", tool_name, role, phi_msg, patient_id,
                                input_data={"patient_id": patient_id})
        return {"status": "PHI_VIOLATION", "message": phi_msg}

    result = BillingService.create_invoice(patient_id, billing_code, medicines)

    if result.get("error"):
        audit_logger.log_failure("Billing", tool_name, role, result["message"], patient_id,
                                 input_data={"patient_id": patient_id, "billing_code": billing_code})
        return {"status": "ERROR", "message": result["message"]}

    invoice = result["invoice"]
    audit_logger.log_success("Billing", tool_name, role, patient_id,
                             input_data={"patient_id": patient_id, "billing_code": billing_code,
                                         "medicine_count": len(medicines)},
                             output_summary=f"Invoice {invoice['invoice_id']} created. Total: ₹{invoice['grand_total']}")
    return {"status": "SUCCESS", "data": result}


@mcp.tool()
def validate_invoice(invoice_id: str, role: str = "administrator") -> dict:
    """
    Validate an invoice for errors, duplicates, and missing information.

    Checks performed:
    - Duplicate medicines (brand + generic)
    - Missing billing code
    - Missing/invalid prices
    - Invalid quantities
    - Total calculation accuracy

    Args:
        invoice_id: Invoice identifier to validate
        role: Caller role for RBAC check

    Returns:
        Validation result with errors, warnings, and duplicates removed
    """
    tool_name = "validate_invoice"
    denial = require_permission(role, tool_name)
    if denial:
        audit_logger.log_denied("Billing", tool_name, role, denial,
                                input_data={"invoice_id": invoice_id})
        return {"status": "DENIED", "message": denial}

    result = BillingService.validate_invoice(invoice_id)

    if result.get("error"):
        audit_logger.log_failure("Billing", tool_name, role, result["errors"][0] if result.get("errors") else "Error",
                                 input_data={"invoice_id": invoice_id})
        return {"status": "ERROR", **result}

    from backend.models.audit import AuditStatus
    audit_status = AuditStatus.SUCCESS if result["is_valid"] else AuditStatus.FAILURE
    audit_logger.log(
        server="Billing", tool=tool_name, role=role,
        status=audit_status,
        input_data={"invoice_id": invoice_id},
        output_summary=result.get("message", ""),
        reason="; ".join(result.get("errors", [])) if not result["is_valid"] else None,
    )

    return {
        "status": "VALID" if result["is_valid"] else "INVALID",
        "data": result,
    }


@mcp.tool()
def calculate_total(patient_id: str, billing_code: str, medicines: list,
                    service_items: list = None, role: str = "administrator") -> dict:
    """
    Calculate total bill without creating an invoice.

    Args:
        patient_id: Patient identifier
        billing_code: Billing code for the procedure
        medicines: List of medicines [{generic_name, quantity}]
        service_items: Optional additional service charges
        role: Caller role for RBAC check

    Returns:
        Itemized total breakdown with tax and grand total
    """
    tool_name = "calculate_total"
    denial = require_permission(role, tool_name)
    if denial:
        audit_logger.log_denied("Billing", tool_name, role, denial, patient_id,
                                input_data={"patient_id": patient_id})
        return {"status": "DENIED", "message": denial}

    result = BillingService.calculate_total(patient_id, billing_code, medicines, service_items)

    audit_logger.log_success("Billing", tool_name, role, patient_id,
                             input_data={"patient_id": patient_id, "billing_code": billing_code},
                             output_summary=f"Grand Total: ₹{result['grand_total']}")
    return {"status": "SUCCESS", "data": result}


if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Billing FastMCP Server on port 8003...")
    app = mcp.streamable_http_app()
    uvicorn.run(app, host="127.0.0.1", port=8003)
