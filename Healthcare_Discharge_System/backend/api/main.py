"""
FastAPI REST API for the AI Healthcare Discharge Coordination System.
Provides REST endpoints for patient management, discharge workflow, and dashboard.
"""
import sys
import os
import logging
from datetime import datetime
from typing import Optional, List

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from backend.services.ehr_service import EHRService
from backend.services.pharmacy_service import PharmacyService
from backend.services.billing_service import BillingService
from backend.agent.discharge_agent import DischargeAgent
from backend.security.rbac import rbac, UserRole
from backend.utils.audit_logger import audit_logger
from backend.utils.data_loader import DataLoader

logging.basicConfig(level=logging.INFO, format="%(asctime)s [API] %(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# ─── FastAPI App ──────────────────────────────────────────────────────────────
app = FastAPI(
    title="AI Healthcare Discharge Coordination System",
    description="""
    ## AI-Powered Cross-Department Discharge Coordination System

    Coordinates patient discharge across EHR, Pharmacy, and Billing departments.

    ### Features
    - **AI Discharge Agent**: Automated 10-step discharge workflow
    - **RBAC**: Role-based access control (Administrator, Doctor, Pharmacist, Billing Clerk)
    - **PHI Protection**: Strict PHI boundary enforcement
    - **Audit Logging**: Complete audit trail for all operations
    - **Real-time Inventory**: Live pharmacy stock monitoring
    - **Invoice Generation**: Automated billing with validation
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Request/Response Models ──────────────────────────────────────────────────

class DischargeRequest(BaseModel):
    patient_id: str
    role: str = "administrator"
    override_approvals: bool = False


class StockCheckRequest(BaseModel):
    generic_name: str
    required_quantity: int = 1
    role: str = "pharmacist"


class InvoiceCreateRequest(BaseModel):
    patient_id: str
    billing_code: str
    medicines: List[dict]
    role: str = "billing_clerk"


class InvoiceValidateRequest(BaseModel):
    invoice_id: str
    role: str = "billing_clerk"


class AllergyCheckRequest(BaseModel):
    medicine_name: str
    patient_allergies: List[str]
    role: str = "pharmacist"


# ─── Health Check ─────────────────────────────────────────────────────────────

@app.get("/", tags=["Health"])
def root():
    """System health check."""
    return {
        "system": "AI Healthcare Discharge Coordination System",
        "version": "1.0.0",
        "status": "operational",
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "docs": "/docs",
            "dashboard": "/dashboard",
            "patients": "/patient/{id}",
            "audit": "/audit",
        }
    }


@app.get("/health", tags=["Health"])
def health_check():
    """Detailed health check."""
    try:
        # Check data files
        DataLoader.get_ehr_data()
        DataLoader.get_pharmacy_data()
        DataLoader.get_billing_data()
        data_status = "healthy"
    except Exception as e:
        data_status = f"error: {str(e)}"

    return {
        "status": "healthy",
        "data_files": data_status,
        "timestamp": datetime.now().isoformat(),
    }


# ─── Patient Endpoints ────────────────────────────────────────────────────────

@app.get("/patient/{patient_id}", tags=["Patient"])
def get_patient(
    patient_id: str,
    role: str = Query("administrator", description="User role for RBAC"),
):
    """
    Retrieve a patient record from the EHR system.

    - **patient_id**: Patient identifier (e.g., P001)
    - **role**: Caller role for access control
    """
    denial = rbac.check_permission(role, "get_patient")
    if not denial[0]:
        raise HTTPException(status_code=403, detail=denial[1])

    result = EHRService.get_patient(patient_id)
    if result.get("error"):
        raise HTTPException(status_code=404, detail=result["message"])

    return {"status": "success", "data": result["data"]}


@app.get("/patients", tags=["Patient"])
def list_patients(
    role: str = Query("administrator"),
    status: Optional[str] = Query(None, description="Filter by discharge status"),
    query: str = Query("", description="Search by name or ID"),
):
    """List all patients with optional filtering."""
    patients = EHRService.search_patients(query, status)
    return {"status": "success", "count": len(patients), "patients": patients}


# ─── Discharge Endpoint ───────────────────────────────────────────────────────

@app.post("/discharge", tags=["Discharge"])
def run_discharge(request: DischargeRequest):
    """
    Execute the AI discharge coordination workflow for a patient.

    Runs the complete 10-step discharge process:
    1. Patient Search → 2. EHR Read → 3. Medication Retrieval →
    4. Brand/Generic Resolution → 5. Stock Check → 6. Alternatives →
    7. Allergy Check → 8. Invoice Generation → 9. Validation → 10. Discharge Packet
    """
    agent = DischargeAgent(role=request.role)
    result = agent.run_discharge_workflow(
        patient_id=request.patient_id,
        override_approvals=request.override_approvals,
    )

    return {
        "status": "success",
        "workflow": result.to_dict(),
    }


# ─── Pharmacy Endpoints ───────────────────────────────────────────────────────

@app.post("/check-stock", tags=["Pharmacy"])
def check_stock(request: StockCheckRequest):
    """Check pharmacy inventory for a medicine."""
    denial = rbac.check_permission(request.role, "check_stock")
    if not denial[0]:
        raise HTTPException(status_code=403, detail=denial[1])

    result = PharmacyService.check_stock(request.generic_name, request.required_quantity)
    return {"status": "success", "data": result}


@app.post("/check-allergy", tags=["Pharmacy"])
def check_allergy(request: AllergyCheckRequest):
    """Check allergy conflicts for a medicine."""
    denial = rbac.check_permission(request.role, "check_allergy_conflict")
    if not denial[0]:
        raise HTTPException(status_code=403, detail=denial[1])

    result = PharmacyService.check_allergy_conflict(
        request.medicine_name, request.patient_allergies
    )
    return {"status": "success", "data": result}


@app.get("/inventory", tags=["Pharmacy"])
def get_inventory(role: str = Query("pharmacist")):
    """Get pharmacy inventory summary."""
    denial = rbac.check_permission(role, "check_stock")
    if not denial[0]:
        raise HTTPException(status_code=403, detail=denial[1])

    summary = PharmacyService.get_inventory_summary()
    return {"status": "success", "data": summary}


# ─── Billing Endpoints ────────────────────────────────────────────────────────

@app.post("/create-invoice", tags=["Billing"])
def create_invoice(request: InvoiceCreateRequest):
    """Create a new patient invoice."""
    denial = rbac.check_permission(request.role, "create_invoice")
    if not denial[0]:
        raise HTTPException(status_code=403, detail=denial[1])

    result = BillingService.create_invoice(
        patient_id=request.patient_id,
        billing_code=request.billing_code,
        medicines=request.medicines,
    )

    if result.get("error"):
        raise HTTPException(status_code=400, detail=result["message"])

    return {"status": "success", "data": result}


@app.post("/validate-invoice", tags=["Billing"])
def validate_invoice(request: InvoiceValidateRequest):
    """Validate an existing invoice."""
    denial = rbac.check_permission(request.role, "validate_invoice")
    if not denial[0]:
        raise HTTPException(status_code=403, detail=denial[1])

    result = BillingService.validate_invoice(request.invoice_id)
    return {"status": "success", "data": result}


@app.get("/billing-codes", tags=["Billing"])
def get_billing_codes(role: str = Query("billing_clerk")):
    """Get all available billing codes."""
    denial = rbac.check_permission(role, "get_billing_code")
    if not denial[0]:
        raise HTTPException(status_code=403, detail=denial[1])

    codes = DataLoader.get_billing_codes()
    return {"status": "success", "count": len(codes), "billing_codes": codes}


# ─── Audit Log Endpoint ───────────────────────────────────────────────────────

@app.get("/audit", tags=["Audit"])
def get_audit_logs(
    role: str = Query("administrator"),
    limit: int = Query(50, ge=1, le=500),
    patient_id: Optional[str] = Query(None),
    log_status: Optional[str] = Query(None),
    log_role: Optional[str] = Query(None),
):
    """
    Retrieve audit logs. Administrator access required.
    """
    denial = rbac.check_permission(role, "get_audit_logs")
    if not denial[0]:
        raise HTTPException(status_code=403, detail=denial[1])

    logs = audit_logger.get_logs(
        limit=limit,
        patient_id=patient_id,
        role=log_role,
        status=log_status,
    )
    stats = audit_logger.get_statistics()

    return {
        "status": "success",
        "count": len(logs),
        "statistics": stats,
        "logs": logs,
    }


# ─── Dashboard Endpoint ───────────────────────────────────────────────────────

@app.get("/dashboard", tags=["Dashboard"])
def get_dashboard(role: str = Query("administrator")):
    """
    Get comprehensive dashboard statistics.
    """
    ehr_stats = EHRService.get_dashboard_stats()
    inventory_stats = PharmacyService.get_inventory_summary()
    audit_stats = audit_logger.get_statistics()
    invoices = BillingService.get_all_invoices()

    invoice_summary = {
        "total": len(invoices),
        "validated": sum(1 for i in invoices if i.get("status") == "validated"),
        "draft": sum(1 for i in invoices if i.get("status") == "draft"),
        "invalid": sum(1 for i in invoices if i.get("status") == "invalid"),
    }

    return {
        "status": "success",
        "dashboard": {
            "ehr": ehr_stats,
            "pharmacy": inventory_stats,
            "billing": invoice_summary,
            "audit": audit_stats,
            "timestamp": datetime.now().isoformat(),
        }
    }


# ─── RBAC Info Endpoint ───────────────────────────────────────────────────────

@app.get("/rbac/roles", tags=["Security"])
def get_roles():
    """Get all available roles and their permissions."""
    roles_info = {}
    for role in rbac.list_roles():
        roles_info[role] = list(rbac.get_role_permissions(role))
    return {"status": "success", "roles": roles_info}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
