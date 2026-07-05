"""
Pydantic models for Audit logging.
"""
from pydantic import BaseModel, Field
from typing import Optional, Any, Dict
from datetime import datetime
from enum import Enum


class AuditStatus(str, Enum):
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    DENIED = "DENIED"
    WARNING = "WARNING"


class AuditLogEntry(BaseModel):
    """A single audit log entry for an MCP tool call."""
    log_id: str = Field(..., description="Unique log identifier")
    timestamp: str = Field(..., description="ISO format timestamp")
    server: str = Field(..., description="MCP server name (EHR/Pharmacy/Billing)")
    tool: str = Field(..., description="Tool/function name called")
    role: str = Field(..., description="Role of the caller")
    user_id: Optional[str] = Field(None, description="User identifier if available")
    status: AuditStatus = Field(..., description="Call status")
    input_data: Dict[str, Any] = Field(default_factory=dict, description="Input parameters")
    output_summary: str = Field("", description="Summary of output")
    reason: Optional[str] = Field(None, description="Reason for failure/denial")
    patient_id: Optional[str] = Field(None, description="Associated patient ID")
    duration_ms: Optional[float] = Field(None, description="Execution time in milliseconds")
