"""
EHR Service - Business logic for Electronic Health Records operations.
"""
import logging
from typing import Optional, Dict, Any, List

from backend.utils.data_loader import DataLoader
from backend.models.patient import Patient, DischargeSummary, MedicationList, AllergyList, ClinicalNotes

logger = logging.getLogger(__name__)


class EHRService:
    """
    Service class providing EHR business logic.
    Reads from the synthetic_records.json dataset.
    """

    @staticmethod
    def get_patient(patient_id: str) -> Dict[str, Any]:
        """
        Retrieve full patient record by ID.

        Args:
            patient_id: Patient identifier (e.g., 'P001')

        Returns:
            Patient record dict or error dict
        """
        patient = DataLoader.get_patient_by_id(patient_id)
        if not patient:
            logger.warning(f"Patient not found: {patient_id}")
            return {
                "error": True,
                "message": f"Patient '{patient_id}' not found in the EHR system.",
                "patient_id": patient_id,
            }
        logger.info(f"Retrieved patient: {patient_id}")
        return {"error": False, "data": patient}

    @staticmethod
    def get_discharge_summary(patient_id: str) -> Dict[str, Any]:
        """Get discharge summary for a patient."""
        patient = DataLoader.get_patient_by_id(patient_id)
        if not patient:
            return {"error": True, "message": f"Patient '{patient_id}' not found."}

        return {
            "error": False,
            "data": {
                "patient_id": patient["patient_id"],
                "patient_name": patient["name"],
                "discharge_status": patient["discharge_status"],
                "attending_doctor": patient["attending_doctor"],
                "discharge_summary": patient["discharge_summary"],
                "medications": patient["medications"],
                "admission_date": patient["admission_date"],
            }
        }

    @staticmethod
    def get_medications(patient_id: str) -> Dict[str, Any]:
        """Get medication list for a patient."""
        patient = DataLoader.get_patient_by_id(patient_id)
        if not patient:
            return {"error": True, "message": f"Patient '{patient_id}' not found."}

        return {
            "error": False,
            "data": {
                "patient_id": patient_id,
                "medications": patient["medications"],
            }
        }

    @staticmethod
    def get_allergies(patient_id: str) -> Dict[str, Any]:
        """Get allergy list for a patient."""
        patient = DataLoader.get_patient_by_id(patient_id)
        if not patient:
            return {"error": True, "message": f"Patient '{patient_id}' not found."}

        return {
            "error": False,
            "data": {
                "patient_id": patient_id,
                "allergies": patient["allergies"],
                "allergy_count": len(patient["allergies"]),
            }
        }

    @staticmethod
    def get_clinical_notes(patient_id: str) -> Dict[str, Any]:
        """Get clinical notes for a patient (PHI-restricted)."""
        patient = DataLoader.get_patient_by_id(patient_id)
        if not patient:
            return {"error": True, "message": f"Patient '{patient_id}' not found."}

        return {
            "error": False,
            "data": {
                "patient_id": patient_id,
                "clinical_notes": patient["clinical_notes"],
                "lab_results": patient["lab_results"],
                "attending_doctor": patient["attending_doctor"],
            }
        }

    @staticmethod
    def search_patients(query: str = "", status: str = None) -> List[Dict]:
        """
        Search patients by name/ID or filter by status.

        Args:
            query: Search string
            status: Discharge status filter

        Returns:
            List of matching patient summaries
        """
        patients = DataLoader.get_all_patients()
        results = []
        query = query.strip().lower()

        for p in patients:
            # Apply status filter
            if status and p.get("discharge_status") != status:
                continue

            # Apply text search
            if query:
                if not (
                    query in p.get("name", "").lower()
                    or query in p.get("patient_id", "").lower()
                    or query in p.get("ward", "").lower()
                ):
                    continue

            results.append({
                "patient_id": p["patient_id"],
                "name": p["name"],
                "age": p["age"],
                "gender": p["gender"],
                "ward": p["ward"],
                "discharge_status": p["discharge_status"],
                "attending_doctor": p["attending_doctor"],
                "diagnosis": p["diagnosis"],
                "admission_date": p["admission_date"],
            })

        return results

    @staticmethod
    def get_dashboard_stats() -> Dict[str, Any]:
        """Get statistics for dashboard display."""
        patients = DataLoader.get_all_patients()

        stats = {
            "total_patients": len(patients),
            "ready_for_discharge": 0,
            "pending_pharmacy": 0,
            "pending_billing": 0,
            "completed": 0,
            "by_ward": {},
        }

        for p in patients:
            status = p.get("discharge_status", "")
            if status == "ready_for_discharge":
                stats["ready_for_discharge"] += 1
            elif status == "pending_pharmacy":
                stats["pending_pharmacy"] += 1
            elif status == "pending_billing":
                stats["pending_billing"] += 1
            elif status == "completed":
                stats["completed"] += 1

            ward = p.get("ward", "Unknown")
            stats["by_ward"][ward] = stats["by_ward"].get(ward, 0) + 1

        return stats
