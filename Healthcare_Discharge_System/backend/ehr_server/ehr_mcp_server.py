"""
EHR FastMCP Server.
Exposes EHR tools over MCP protocol.
Tools: get_patient, get_discharge_summary, get_medications, get_allergies, get_clinical_notes
"""
import sys
import os
import logging

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from mcp.server.fastmcp import FastMCP
from backend.services.ehr_service import EHRService
from backend.security.rbac import require_permission
from backend.utils.audit_logger import audit_logger

logging.basicConfig(level=logging.INFO, format="%(asctime)s [EHR-MCP] %(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# Create FastMCP server
mcp = FastMCP(
    name="EHR-MCP-Server",
    instructions="""
    Electronic Health Records MCP Server.
    Provides access to patient records, medications, allergies, and clinical notes.
    All calls are RBAC-controlled and audit-logged.
    """
)


@mcp.tool()
def get_patient(patient_id: str, role: str = "administrator") -> dict:
    """
    Retrieve full patient record from the EHR system.

    Args:
        patient_id: Patient identifier (e.g., 'P001')
        role: Caller role for RBAC check

    Returns:
        Complete patient record or access denied message
    """
    tool_name = "get_patient"
    denial = require_permission(role, tool_name)
    if denial:
        audit_logger.log_denied("EHR", tool_name, role, denial, patient_id, {"patient_id": patient_id})
        return {"status": "DENIED", "message": denial}

    result = EHRService.get_patient(patient_id)

    if result.get("error"):
        audit_logger.log_failure("EHR", tool_name, role, result["message"], patient_id, {"patient_id": patient_id})
        return {"status": "ERROR", "message": result["message"]}

    audit_logger.log_success("EHR", tool_name, role, patient_id,
                             {"patient_id": patient_id},
                             f"Retrieved patient: {result['data']['name']}")
    return {"status": "SUCCESS", "data": result["data"]}


@mcp.tool()
def get_discharge_summary(patient_id: str, role: str = "administrator") -> dict:
    """
    Get discharge summary for a patient.

    Args:
        patient_id: Patient identifier
        role: Caller role for RBAC check

    Returns:
        Discharge summary including status, doctor, and summary text
    """
    tool_name = "get_discharge_summary"
    denial = require_permission(role, tool_name)
    if denial:
        audit_logger.log_denied("EHR", tool_name, role, denial, patient_id, {"patient_id": patient_id})
        return {"status": "DENIED", "message": denial}

    result = EHRService.get_discharge_summary(patient_id)

    if result.get("error"):
        audit_logger.log_failure("EHR", tool_name, role, result["message"], patient_id)
        return {"status": "ERROR", "message": result["message"]}

    audit_logger.log_success("EHR", tool_name, role, patient_id,
                             {"patient_id": patient_id},
                             f"Discharge status: {result['data']['discharge_status']}")
    return {"status": "SUCCESS", "data": result["data"]}


@mcp.tool()
def get_medications(patient_id: str, role: str = "administrator") -> dict:
    """
    Get the medication list for a patient.

    Args:
        patient_id: Patient identifier
        role: Caller role for RBAC check

    Returns:
        List of prescribed medications with dosage and frequency
    """
    tool_name = "get_medications"
    denial = require_permission(role, tool_name)
    if denial:
        audit_logger.log_denied("EHR", tool_name, role, denial, patient_id, {"patient_id": patient_id})
        return {"status": "DENIED", "message": denial}

    result = EHRService.get_medications(patient_id)

    if result.get("error"):
        audit_logger.log_failure("EHR", tool_name, role, result["message"], patient_id)
        return {"status": "ERROR", "message": result["message"]}

    med_count = len(result["data"]["medications"])
    audit_logger.log_success("EHR", tool_name, role, patient_id,
                             {"patient_id": patient_id},
                             f"Retrieved {med_count} medications")
    return {"status": "SUCCESS", "data": result["data"]}


@mcp.tool()
def get_allergies(patient_id: str, role: str = "administrator") -> dict:
    """
    Get the allergy list for a patient.

    Args:
        patient_id: Patient identifier
        role: Caller role for RBAC check

    Returns:
        List of known patient allergies
    """
    tool_name = "get_allergies"
    denial = require_permission(role, tool_name)
    if denial:
        audit_logger.log_denied("EHR", tool_name, role, denial, patient_id, {"patient_id": patient_id})
        return {"status": "DENIED", "message": denial}

    result = EHRService.get_allergies(patient_id)

    if result.get("error"):
        audit_logger.log_failure("EHR", tool_name, role, result["message"], patient_id)
        return {"status": "ERROR", "message": result["message"]}

    audit_logger.log_success("EHR", tool_name, role, patient_id,
                             {"patient_id": patient_id},
                             f"Retrieved {result['data']['allergy_count']} allergies")
    return {"status": "SUCCESS", "data": result["data"]}


@mcp.tool()
def get_clinical_notes(patient_id: str, role: str = "administrator") -> dict:
    """
    Get clinical notes for a patient. PHI-restricted to Doctor and Administrator only.

    Args:
        patient_id: Patient identifier
        role: Caller role for RBAC check (must be doctor or administrator)

    Returns:
        Clinical notes and lab results, or ACCESS DENIED
    """
    tool_name = "get_clinical_notes"
    denial = require_permission(role, tool_name)
    if denial:
        audit_logger.log_denied("EHR", tool_name, role, denial, patient_id,
                                {"patient_id": patient_id, "role": role})
        return {"status": "DENIED", "message": denial}

    result = EHRService.get_clinical_notes(patient_id)

    if result.get("error"):
        audit_logger.log_failure("EHR", tool_name, role, result["message"], patient_id)
        return {"status": "ERROR", "message": result["message"]}

    audit_logger.log_success("EHR", tool_name, role, patient_id,
                             {"patient_id": patient_id},
                             "Clinical notes retrieved (PHI access)")
    return {"status": "SUCCESS", "data": result["data"]}


if __name__ == "__main__":
    import uvicorn
    logger.info("Starting EHR FastMCP Server on port 8001...")
    app = mcp.streamable_http_app()
    uvicorn.run(app, host="127.0.0.1", port=8001)
