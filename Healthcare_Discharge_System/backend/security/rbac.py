"""
RBAC (Role-Based Access Control) module.
Controls access to MCP tools based on user roles.
"""
from typing import Dict, Set, Optional
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class UserRole(str, Enum):
    """Available user roles in the system."""
    ADMINISTRATOR = "administrator"
    DOCTOR = "doctor"
    PHARMACIST = "pharmacist"
    BILLING_CLERK = "billing_clerk"


# Permission map: role -> set of allowed tools
ROLE_PERMISSIONS: Dict[str, Set[str]] = {
    UserRole.ADMINISTRATOR: {
        # EHR tools
        "get_patient", "get_discharge_summary", "get_medications",
        "get_allergies", "get_clinical_notes",
        # Pharmacy tools
        "resolve_generic", "check_stock", "suggest_alternative", "check_allergy_conflict",
        # Billing tools
        "get_billing_code", "create_invoice", "validate_invoice", "calculate_total",
        # Agent tools
        "run_discharge_workflow", "get_dashboard_stats", "get_audit_logs",
    },
    UserRole.DOCTOR: {
        # EHR tools
        "get_patient", "get_discharge_summary", "get_medications",
        "get_allergies", "get_clinical_notes",
        # Pharmacy tools (read-only, no stock editing)
        "resolve_generic", "check_allergy_conflict", "suggest_alternative",
        # Agent tools
        "run_discharge_workflow",
    },
    UserRole.PHARMACIST: {
        # EHR tools (limited)
        "get_medications", "get_allergies",
        # Pharmacy tools (full)
        "resolve_generic", "check_stock", "suggest_alternative", "check_allergy_conflict",
    },
    UserRole.BILLING_CLERK: {
        # EHR tools (none - only patient_id allowed)
        # Billing tools (full)
        "get_billing_code", "create_invoice", "validate_invoice", "calculate_total",
    },
}

# PHI-sensitive tools that Billing cannot access
PHI_RESTRICTED_FROM_BILLING: Set[str] = {
    "get_clinical_notes", "get_patient", "get_discharge_summary",
}

# Tools that expose diagnosis/clinical info
CLINICAL_TOOLS: Set[str] = {
    "get_clinical_notes", "get_discharge_summary",
}


class RBACController:
    """
    Role-Based Access Controller.
    Validates user roles against tool permissions.
    """

    def __init__(self):
        self._permissions = ROLE_PERMISSIONS

    def check_permission(self, role: str, tool_name: str) -> tuple[bool, str]:
        """
        Check if a role has permission to call a tool.

        Args:
            role: The user's role string
            tool_name: The tool/function being called

        Returns:
            Tuple of (is_allowed: bool, reason: str)
        """
        try:
            user_role = UserRole(role.lower())
        except ValueError:
            logger.warning(f"Unknown role attempted access: {role}")
            return False, f"Unknown role: '{role}'. Valid roles: {[r.value for r in UserRole]}"

        allowed_tools = self._permissions.get(user_role, set())

        if tool_name in allowed_tools:
            logger.info(f"Access GRANTED: role={role}, tool={tool_name}")
            return True, "Access granted"
        else:
            reason = self._get_denial_reason(user_role, tool_name)
            logger.warning(f"ACCESS DENIED: role={role}, tool={tool_name}, reason={reason}")
            return False, reason

    def _get_denial_reason(self, role: UserRole, tool_name: str) -> str:
        """Generate a descriptive denial reason."""
        if role == UserRole.BILLING_CLERK and tool_name in CLINICAL_TOOLS:
            return (
                f"ACCESS DENIED: Billing Clerk cannot access clinical tool '{tool_name}'. "
                "PHI boundary enforced: Diagnosis, Clinical Notes, and Medical History "
                "are not accessible to Billing department."
            )
        elif role == UserRole.BILLING_CLERK and tool_name in {"get_patient", "get_discharge_summary"}:
            return (
                f"ACCESS DENIED: Billing Clerk cannot access '{tool_name}'. "
                "PHI boundary enforced: Patient clinical records are restricted."
            )
        elif role == UserRole.PHARMACIST and tool_name in CLINICAL_TOOLS:
            return (
                f"ACCESS DENIED: Pharmacist cannot access clinical tool '{tool_name}'. "
                "Pharmacist is not authorized to view diagnosis or clinical notes."
            )
        elif role == UserRole.DOCTOR and tool_name in {"create_invoice", "validate_invoice", "calculate_total"}:
            return (
                f"ACCESS DENIED: Doctor cannot perform billing operations ('{tool_name}'). "
                "Please contact the Billing department."
            )
        else:
            return (
                f"ACCESS DENIED: Role '{role.value}' does not have permission to use "
                f"tool '{tool_name}'."
            )

    def get_role_permissions(self, role: str) -> Set[str]:
        """Return the set of allowed tools for a role."""
        try:
            user_role = UserRole(role.lower())
            return self._permissions.get(user_role, set())
        except ValueError:
            return set()

    def list_roles(self) -> list:
        """List all available roles."""
        return [r.value for r in UserRole]


# Singleton RBAC controller
rbac = RBACController()


def require_permission(role: str, tool_name: str) -> str:
    """
    Decorator-style permission check.
    Returns 'ACCESS DENIED: ...' message if not permitted, else None.
    """
    allowed, reason = rbac.check_permission(role, tool_name)
    if not allowed:
        return reason
    return ""
