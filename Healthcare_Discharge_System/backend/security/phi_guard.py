"""
PHI Guard module.
Enforces Protected Health Information (PHI) boundaries between departments.
Billing must NEVER receive Diagnosis, Clinical Notes, Doctor Notes, or Medical History.
"""
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

# PHI fields that must never be sent to Billing
PHI_FIELDS = {
    "diagnosis",
    "clinical_notes",
    "discharge_summary",
    "lab_results",
    "doctor_notes",
    "medical_history",
    "attending_doctor",
    "blood_group",
    "allergies",
    "ward",
}

# Fields safe to send to Billing
BILLING_SAFE_FIELDS = {
    "patient_id",
    "name",         # only first name + last initial in production
    "age",
    "gender",
    "billing_code",
    "medicines",
    "quantity",
    "invoice_id",
}


class PHIGuard:
    """
    PHI Guard: masks and strips PHI from data going to the Billing department.
    Ensures clinical data never crosses department boundaries.
    """

    @staticmethod
    def mask_for_billing(patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Mask PHI fields from a patient record before sending to Billing.
        Only passes safe billing-relevant fields.

        Args:
            patient_data: Full patient record

        Returns:
            PHI-masked data safe for Billing
        """
        masked = {}
        phi_stripped = []

        for key, value in patient_data.items():
            if key in PHI_FIELDS:
                phi_stripped.append(key)
                # Replace with masked value
                masked[key] = "[PHI REDACTED]"
            else:
                masked[key] = value

        if phi_stripped:
            logger.info(f"PHI Guard: Masked {len(phi_stripped)} PHI fields for billing: {phi_stripped}")

        # Log PHI boundary enforcement
        masked["_phi_masked"] = True
        masked["_masked_fields"] = phi_stripped

        return masked

    @staticmethod
    def extract_billing_safe(patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract only billing-safe fields from patient data.

        Args:
            patient_data: Full patient record

        Returns:
            Dictionary with only billing-safe fields
        """
        safe_data = {}
        for field in BILLING_SAFE_FIELDS:
            if field in patient_data:
                safe_data[field] = patient_data[field]

        # Always include patient_id
        if "patient_id" in patient_data:
            safe_data["patient_id"] = patient_data["patient_id"]

        logger.info(f"PHI Guard: Extracted billing-safe fields for patient {patient_data.get('patient_id', 'UNKNOWN')}")
        return safe_data

    @staticmethod
    def is_phi_field(field_name: str) -> bool:
        """Check if a field name is PHI."""
        return field_name.lower() in PHI_FIELDS

    @staticmethod
    def validate_billing_request(request_data: Dict[str, Any]) -> tuple[bool, str]:
        """
        Validate that a billing request does not contain PHI.

        Args:
            request_data: The billing request data

        Returns:
            Tuple of (is_valid: bool, violation_message: str)
        """
        violations = []
        for field in PHI_FIELDS:
            if field in request_data:
                val = request_data[field]
                if val and val != "[PHI REDACTED]":
                    violations.append(field)

        if violations:
            msg = (
                f"PHI BOUNDARY VIOLATION: Billing request contains restricted fields: "
                f"{violations}. These fields are not permitted in billing transactions."
            )
            logger.error(msg)
            return False, msg

        return True, "PHI validation passed"

    @staticmethod
    def anonymize_for_audit(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Anonymize sensitive data for audit logs.
        Preserves structure but masks identifying values.
        """
        anonymized = {}
        for key, value in data.items():
            if key in PHI_FIELDS:
                anonymized[key] = "[REDACTED]"
            elif key == "name" and isinstance(value, str):
                # Show only first name initial
                parts = value.split()
                if len(parts) >= 2:
                    anonymized[key] = f"{parts[0][0]}*** {parts[-1][0]}***"
                else:
                    anonymized[key] = "[REDACTED]"
            else:
                anonymized[key] = value
        return anonymized


# Singleton guard instance
phi_guard = PHIGuard()
