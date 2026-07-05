"""
Audit Logger utility.
Logs every MCP tool call with timestamp, server, tool, role, status, input, output, and reason.
"""
import json
import uuid
import logging
import os
from datetime import datetime
from typing import Any, Dict, Optional
from pathlib import Path

from backend.models.audit import AuditLogEntry, AuditStatus

logger = logging.getLogger(__name__)

# Path to the audit log file
AUDIT_LOG_PATH = Path(__file__).parent.parent.parent / "data" / "audit_logs.json"


class AuditLogger:
    """
    Thread-safe audit logger that persists logs to a JSON file.
    Records every MCP tool call with full context.
    """

    def __init__(self, log_path: Path = AUDIT_LOG_PATH):
        self.log_path = log_path
        self._ensure_log_file()

    def _ensure_log_file(self):
        """Ensure the audit log file exists."""
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.log_path.exists():
            self.log_path.write_text("[]", encoding="utf-8")

    def _load_logs(self) -> list:
        """Load existing audit logs."""
        try:
            content = self.log_path.read_text(encoding="utf-8")
            return json.loads(content) if content.strip() else []
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def _save_logs(self, logs: list):
        """Save audit logs to file."""
        self.log_path.write_text(
            json.dumps(logs, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )

    def log(
        self,
        server: str,
        tool: str,
        role: str,
        status: AuditStatus,
        input_data: Dict[str, Any] = None,
        output_summary: str = "",
        reason: Optional[str] = None,
        patient_id: Optional[str] = None,
        user_id: Optional[str] = None,
        duration_ms: Optional[float] = None,
    ) -> AuditLogEntry:
        """
        Log an MCP tool call to the audit file.

        Args:
            server: MCP server name (EHR/Pharmacy/Billing)
            tool: Tool/function name
            role: User role
            status: Call status (SUCCESS/FAILURE/DENIED/WARNING)
            input_data: Input parameters
            output_summary: Summary of the output
            reason: Reason for failure/denial
            patient_id: Associated patient ID
            user_id: User identifier
            duration_ms: Execution duration in milliseconds

        Returns:
            The created AuditLogEntry
        """
        entry = AuditLogEntry(
            log_id=str(uuid.uuid4())[:8].upper(),
            timestamp=datetime.now().isoformat(),
            server=server,
            tool=tool,
            role=role,
            user_id=user_id,
            status=status,
            input_data=input_data or {},
            output_summary=output_summary,
            reason=reason,
            patient_id=patient_id,
            duration_ms=duration_ms,
        )

        logs = self._load_logs()
        logs.append(entry.model_dump())
        self._save_logs(logs)

        log_level = logging.WARNING if status in (AuditStatus.DENIED, AuditStatus.FAILURE) else logging.INFO
        logger.log(log_level, f"[AUDIT] {server}/{tool} | role={role} | status={status.value} | patient={patient_id}")

        return entry

    def log_success(self, server: str, tool: str, role: str, patient_id: str = None,
                    input_data: dict = None, output_summary: str = "") -> AuditLogEntry:
        """Shortcut for logging a successful call."""
        return self.log(
            server=server, tool=tool, role=role,
            status=AuditStatus.SUCCESS,
            input_data=input_data, output_summary=output_summary,
            patient_id=patient_id,
        )

    def log_denied(self, server: str, tool: str, role: str, reason: str,
                   patient_id: str = None, input_data: dict = None) -> AuditLogEntry:
        """Shortcut for logging an access denied event."""
        return self.log(
            server=server, tool=tool, role=role,
            status=AuditStatus.DENIED,
            input_data=input_data, reason=reason,
            patient_id=patient_id,
            output_summary="ACCESS DENIED",
        )

    def log_failure(self, server: str, tool: str, role: str, reason: str,
                    patient_id: str = None, input_data: dict = None) -> AuditLogEntry:
        """Shortcut for logging a failure."""
        return self.log(
            server=server, tool=tool, role=role,
            status=AuditStatus.FAILURE,
            input_data=input_data, reason=reason,
            patient_id=patient_id,
            output_summary=f"FAILED: {reason}",
        )

    def log_warning(self, server: str, tool: str, role: str, reason: str,
                    patient_id: str = None, input_data: dict = None,
                    output_summary: str = "") -> AuditLogEntry:
        """Shortcut for logging a warning."""
        return self.log(
            server=server, tool=tool, role=role,
            status=AuditStatus.WARNING,
            input_data=input_data, reason=reason,
            patient_id=patient_id,
            output_summary=output_summary,
        )

    def get_logs(self, limit: int = 100, patient_id: str = None,
                 role: str = None, status: str = None) -> list:
        """
        Retrieve audit logs with optional filtering.

        Args:
            limit: Maximum number of logs to return
            patient_id: Filter by patient
            role: Filter by role
            status: Filter by status

        Returns:
            List of audit log entries
        """
        logs = self._load_logs()

        if patient_id:
            logs = [l for l in logs if l.get("patient_id") == patient_id]
        if role:
            logs = [l for l in logs if l.get("role") == role]
        if status:
            logs = [l for l in logs if l.get("status") == status]

        # Return most recent first
        return list(reversed(logs[-limit:]))

    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics from audit logs."""
        logs = self._load_logs()
        stats = {
            "total_calls": len(logs),
            "success_count": sum(1 for l in logs if l.get("status") == "SUCCESS"),
            "failure_count": sum(1 for l in logs if l.get("status") == "FAILURE"),
            "denied_count": sum(1 for l in logs if l.get("status") == "DENIED"),
            "warning_count": sum(1 for l in logs if l.get("status") == "WARNING"),
            "by_server": {},
            "by_role": {},
            "by_tool": {},
        }

        for log in logs:
            server = log.get("server", "Unknown")
            role = log.get("role", "Unknown")
            tool = log.get("tool", "Unknown")
            stats["by_server"][server] = stats["by_server"].get(server, 0) + 1
            stats["by_role"][role] = stats["by_role"].get(role, 0) + 1
            stats["by_tool"][tool] = stats["by_tool"].get(tool, 0) + 1

        return stats


# Singleton logger instance
audit_logger = AuditLogger()
