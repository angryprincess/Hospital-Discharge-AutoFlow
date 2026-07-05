"""
Pharmacy FastMCP Server.
Exposes Pharmacy tools over MCP protocol.
Tools: resolve_generic, check_stock, suggest_alternative, check_allergy_conflict
"""
import sys
import os
import logging

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from mcp.server.fastmcp import FastMCP
from backend.services.pharmacy_service import PharmacyService
from backend.security.rbac import require_permission
from backend.utils.audit_logger import audit_logger
from backend.models.audit import AuditStatus

logging.basicConfig(level=logging.INFO, format="%(asctime)s [PHARMACY-MCP] %(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

mcp = FastMCP(
    name="Pharmacy-MCP-Server",
    instructions="""
    Pharmacy MCP Server.
    Provides medication resolution, stock checking, alternative suggestions, and allergy conflict detection.
    All calls are RBAC-controlled and audit-logged.
    """
)


@mcp.tool()
def resolve_generic(brand_name: str, role: str = "administrator") -> dict:
    """
    Resolve a brand name to its generic drug equivalent.

    Args:
        brand_name: Brand name (e.g., 'Augmentin', 'Crocin', 'Dolo')
        role: Caller role for RBAC check

    Returns:
        Generic name, drug class, and category
    """
    tool_name = "resolve_generic"
    denial = require_permission(role, tool_name)
    if denial:
        audit_logger.log_denied("Pharmacy", tool_name, role, denial,
                                input_data={"brand_name": brand_name})
        return {"status": "DENIED", "message": denial}

    result = PharmacyService.resolve_generic(brand_name)

    if result.get("error"):
        audit_logger.log_failure("Pharmacy", tool_name, role, result.get("message", "Unknown error"),
                                 input_data={"brand_name": brand_name})
        return {"status": "ERROR", "message": result["message"]}

    audit_logger.log_success("Pharmacy", tool_name, role,
                             input_data={"brand_name": brand_name},
                             output_summary=result.get("message", ""))
    return {"status": "SUCCESS", "data": result}


@mcp.tool()
def check_stock(generic_name: str, required_quantity: int = 1, role: str = "administrator") -> dict:
    """
    Check pharmacy inventory stock for a medicine.

    Args:
        generic_name: Generic medicine name (e.g., 'Paracetamol')
        required_quantity: Quantity needed
        role: Caller role for RBAC check

    Returns:
        Stock status, quantity, and warning flags
    """
    tool_name = "check_stock"
    denial = require_permission(role, tool_name)
    if denial:
        audit_logger.log_denied("Pharmacy", tool_name, role, denial,
                                input_data={"generic_name": generic_name})
        return {"status": "DENIED", "message": denial}

    result = PharmacyService.check_stock(generic_name, required_quantity)

    status_label = "SUCCESS"
    audit_status_fn = audit_logger.log_success

    if result.get("warning"):
        status_label = "WARNING"

    if result.get("error"):
        audit_logger.log_failure("Pharmacy", tool_name, role, "Lookup error",
                                 input_data={"generic_name": generic_name})
        return {"status": "ERROR", "message": "Error checking stock"}

    audit_status = AuditStatus.WARNING if result.get("warning") else AuditStatus.SUCCESS
    audit_logger.log(
        server="Pharmacy", tool=tool_name, role=role,
        status=audit_status,
        input_data={"generic_name": generic_name, "required_quantity": required_quantity},
        output_summary=result.get("message", ""),
    )
    return {"status": status_label, "data": result}


@mcp.tool()
def suggest_alternative(generic_name: str, patient_allergies: list = None, role: str = "administrator") -> dict:
    """
    Suggest alternative medicines for an out-of-stock or conflicting drug.

    Args:
        generic_name: Generic medicine name to find alternatives for
        patient_allergies: List of patient's known allergies
        role: Caller role for RBAC check

    Returns:
        List of approved alternatives and any blocked ones due to allergy conflicts
    """
    tool_name = "suggest_alternative"
    denial = require_permission(role, tool_name)
    if denial:
        audit_logger.log_denied("Pharmacy", tool_name, role, denial,
                                input_data={"generic_name": generic_name})
        return {"status": "DENIED", "message": denial}

    patient_allergies = patient_allergies or []
    result = PharmacyService.suggest_alternative(generic_name, patient_allergies)

    from backend.models.audit import AuditStatus
    audit_status = AuditStatus.WARNING if result.get("doctor_approval_required") else AuditStatus.SUCCESS
    audit_logger.log(
        server="Pharmacy", tool=tool_name, role=role,
        status=audit_status,
        input_data={"generic_name": generic_name, "patient_allergies": patient_allergies},
        output_summary=result.get("message", ""),
    )

    return {"status": "SUCCESS", "data": result}


@mcp.tool()
def check_allergy_conflict(medicine_name: str, patient_allergies: list, role: str = "administrator") -> dict:
    """
    Check if a medicine conflicts with the patient's known allergies.

    Args:
        medicine_name: Generic or brand name of the medicine
        patient_allergies: List of patient's allergies
        role: Caller role for RBAC check

    Returns:
        Conflict status, severity, and recommended action (BLOCK/WARN/ALLOW)
    """
    tool_name = "check_allergy_conflict"
    denial = require_permission(role, tool_name)
    if denial:
        audit_logger.log_denied("Pharmacy", tool_name, role, denial,
                                input_data={"medicine_name": medicine_name})
        return {"status": "DENIED", "message": denial}

    result = PharmacyService.check_allergy_conflict(medicine_name, patient_allergies)

    from backend.models.audit import AuditStatus
    if result["has_conflict"]:
        audit_status = AuditStatus.WARNING if result["action"] == "WARN" else AuditStatus.FAILURE
        audit_logger.log(
            server="Pharmacy", tool=tool_name, role=role,
            status=audit_status,
            input_data={"medicine_name": medicine_name, "allergies": patient_allergies},
            output_summary=result.get("message", ""),
            reason=f"Allergy conflict: {[c['allergy'] for c in result['conflicts']]}",
        )
    else:
        audit_logger.log_success("Pharmacy", tool_name, role,
                                 input_data={"medicine_name": medicine_name},
                                 output_summary=result.get("message", ""))

    return {
        "status": "CONFLICT" if result["has_conflict"] and result["action"] == "BLOCK" else "SUCCESS",
        "data": result,
    }


if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Pharmacy FastMCP Server on port 8002...")
    app = mcp.streamable_http_app()
    uvicorn.run(app, host="127.0.0.1", port=8002)
