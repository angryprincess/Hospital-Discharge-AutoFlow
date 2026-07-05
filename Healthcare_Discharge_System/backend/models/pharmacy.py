"""
Pydantic models for Pharmacy data.
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum


class StockStatus(str, Enum):
    IN_STOCK = "in_stock"
    LOW_STOCK = "low_stock"
    OUT_OF_STOCK = "out_of_stock"


class AllergyAction(str, Enum):
    BLOCK = "BLOCK"
    WARN = "WARN"
    ALLOW = "ALLOW"


class InventoryItem(BaseModel):
    """Represents a pharmacy inventory item."""
    medicine_id: str
    generic_name: str
    brand_names: List[str]
    stock_quantity: int
    unit: str
    min_threshold: int
    stock_status: StockStatus
    price_per_unit: float
    expiry_date: str


class GenericResolution(BaseModel):
    """Result of brand-to-generic resolution."""
    brand_name: str
    generic_name: str
    drug_class: str
    category: str
    resolved: bool


class StockCheckResult(BaseModel):
    """Result of inventory stock check."""
    generic_name: str
    stock_status: StockStatus
    stock_quantity: int
    reserved: bool = False
    warning_message: Optional[str] = None


class AlternativeMedicine(BaseModel):
    """An alternative medicine suggestion."""
    generic: str
    brand: str
    drug_class: str
    category: str
    allergy_group: str
    stock_status: StockStatus


class AlternativeSuggestion(BaseModel):
    """Result of alternative medicine suggestion."""
    original_generic: str
    alternatives: List[AlternativeMedicine]
    approved_alternatives: List[AlternativeMedicine]
    doctor_approval_required: bool


class AllergyConflictResult(BaseModel):
    """Result of allergy conflict check."""
    medicine: str
    patient_allergies: List[str]
    conflicts: List[dict]
    has_conflict: bool
    severity: Optional[str] = None
    action: AllergyAction = AllergyAction.ALLOW
    message: str = ""
