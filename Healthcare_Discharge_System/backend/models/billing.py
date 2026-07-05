"""
Pydantic models for Billing data.
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from enum import Enum


class InvoiceStatus(str, Enum):
    DRAFT = "draft"
    VALIDATED = "validated"
    INVALID = "invalid"
    PAID = "paid"


class BillingCode(BaseModel):
    """A billing code entry."""
    code: str
    description: str
    base_charge: float
    ward: str


class DrugCatalogEntry(BaseModel):
    """A drug catalog entry for billing."""
    generic_name: str
    code: str
    unit_price: float
    unit: str
    gst_percent: float
    hsn_code: str


class InvoiceLineItem(BaseModel):
    """A line item on an invoice."""
    generic_name: str
    code: str
    quantity: int
    unit_price: float
    total: float


class InvoiceRequest(BaseModel):
    """Request to create a new invoice."""
    patient_id: str
    billing_code: str
    medicines: List[Dict]  # [{generic_name, quantity}]


class Invoice(BaseModel):
    """A complete invoice record."""
    invoice_id: str
    patient_id: str
    billing_code: str
    base_charge: float
    medicines: List[InvoiceLineItem]
    medicine_total: float
    tax_amount: float
    grand_total: float
    status: InvoiceStatus
    created_at: str


class InvoiceValidationResult(BaseModel):
    """Result of invoice validation."""
    invoice_id: str
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    duplicates_removed: List[str]
    validated_invoice: Optional[Invoice] = None


class TotalCalculation(BaseModel):
    """Result of total calculation."""
    base_charge: float
    medicine_total: float
    service_charges: float
    subtotal: float
    tax_amount: float
    grand_total: float
    breakdown: Dict[str, float]
