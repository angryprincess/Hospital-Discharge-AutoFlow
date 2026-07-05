"""
Pydantic models for Patient and EHR data.
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum


class DischargeStatus(str, Enum):
    READY_FOR_DISCHARGE = "ready_for_discharge"
    PENDING_PHARMACY = "pending_pharmacy"
    PENDING_BILLING = "pending_billing"
    COMPLETED = "completed"
    IN_PROGRESS = "in_progress"


class Medication(BaseModel):
    """Represents a single medication prescribed to a patient."""
    brand: str = Field(..., description="Brand name of the medicine")
    dosage: str = Field(..., description="Dosage specification")
    frequency: str = Field(..., description="How often the medicine should be taken")
    duration: str = Field(..., description="Duration of the medication course")


class Patient(BaseModel):
    """Complete patient record from the EHR system."""
    patient_id: str = Field(..., description="Unique patient identifier")
    name: str
    age: int
    gender: str
    blood_group: str
    contact: str
    address: str
    admission_date: str
    discharge_status: DischargeStatus
    ward: str
    attending_doctor: str
    diagnosis: str
    allergies: List[str]
    medications: List[Medication]
    clinical_notes: str
    discharge_summary: str
    lab_results: Dict[str, str]
    billing_code: str
    phi_category: str = "restricted"


class PatientSummary(BaseModel):
    """Non-PHI patient summary safe for non-clinical use."""
    patient_id: str
    name: str
    age: int
    gender: str
    ward: str
    discharge_status: DischargeStatus
    billing_code: str


class DischargeSummary(BaseModel):
    """Discharge summary information."""
    patient_id: str
    patient_name: str
    discharge_status: DischargeStatus
    attending_doctor: str
    discharge_summary: str
    medications: List[Medication]


class MedicationList(BaseModel):
    """Medication list for a patient."""
    patient_id: str
    medications: List[Medication]


class AllergyList(BaseModel):
    """Allergy list for a patient."""
    patient_id: str
    allergies: List[str]


class ClinicalNotes(BaseModel):
    """Clinical notes (PHI-restricted)."""
    patient_id: str
    clinical_notes: str
    lab_results: Dict[str, str]
