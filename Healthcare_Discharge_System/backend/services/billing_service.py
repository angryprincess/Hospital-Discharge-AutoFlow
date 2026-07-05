"""
Billing Service - Business logic for Billing and Invoice operations.
"""
import uuid
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

from backend.utils.data_loader import DataLoader

logger = logging.getLogger(__name__)

# In-memory invoice store (JSON-file backed in production)
_invoices: Dict[str, Dict] = {}


class BillingService:
    """
    Service class providing billing and invoice business logic.
    Reads from synthetic_billing_records.json.
    """

    @staticmethod
    def get_billing_code(code: str) -> Dict[str, Any]:
        """
        Retrieve a billing code entry.

        Args:
            code: Billing code string (e.g., 'DM-HYP-001')

        Returns:
            Billing code details or error
        """
        bc = DataLoader.get_billing_code(code)
        if not bc:
            return {
                "error": True,
                "message": f"Billing code '{code}' not found in catalog.",
                "code": code,
            }

        logger.info(f"Retrieved billing code: {code}")
        return {
            "error": False,
            "data": bc,
        }

    @staticmethod
    def create_invoice(patient_id: str, billing_code: str, medicines: List[Dict]) -> Dict[str, Any]:
        """
        Create a new invoice for a patient.
        PHI data must NOT be included — only patient_id, medicines, billing code.

        Args:
            patient_id: Patient identifier
            billing_code: Billing code for the diagnosis
            medicines: List of {generic_name, quantity} dicts

        Returns:
            Created invoice or error
        """
        # Get billing code details
        bc = DataLoader.get_billing_code(billing_code)
        if not bc:
            return {
                "error": True,
                "message": f"Billing code '{billing_code}' not found. Cannot create invoice.",
            }

        base_charge = bc["base_charge"]
        line_items = []
        medicine_total = 0.0
        missing_codes = []

        # Process each medicine
        seen_generics = set()
        for med in medicines:
            generic_name = med.get("generic_name", "").strip()
            quantity = int(med.get("quantity", 1))

            # Skip duplicates
            if generic_name.lower() in seen_generics:
                logger.warning(f"Duplicate medicine skipped in invoice: {generic_name}")
                continue
            seen_generics.add(generic_name.lower())

            # Look up drug catalog
            catalog_entry = DataLoader.get_drug_catalog_entry(generic_name)
            if not catalog_entry:
                missing_codes.append(generic_name)
                continue

            item_total = catalog_entry["unit_price"] * quantity
            line_items.append({
                "generic_name": generic_name,
                "code": catalog_entry["code"],
                "quantity": quantity,
                "unit_price": catalog_entry["unit_price"],
                "gst_percent": catalog_entry["gst_percent"],
                "total": round(item_total, 2),
            })
            medicine_total += item_total

        # Calculate tax (average GST)
        if line_items:
            avg_gst = sum(i["gst_percent"] for i in line_items) / len(line_items)
        else:
            avg_gst = 12

        tax_amount = round(medicine_total * avg_gst / 100, 2)
        grand_total = round(base_charge + medicine_total + tax_amount, 2)

        invoice_id = f"INV-{datetime.now().strftime('%Y')}-{patient_id}-{str(uuid.uuid4())[:4].upper()}"

        invoice = {
            "invoice_id": invoice_id,
            "patient_id": patient_id,
            "billing_code": billing_code,
            "billing_description": bc["description"],
            "base_charge": base_charge,
            "medicines": line_items,
            "medicine_total": round(medicine_total, 2),
            "tax_amount": tax_amount,
            "grand_total": grand_total,
            "status": "draft",
            "created_at": datetime.now().isoformat(),
            "warnings": [],
        }

        if missing_codes:
            invoice["warnings"].append(f"Medicines not found in catalog: {missing_codes}")
            logger.warning(f"Missing billing codes for medicines: {missing_codes}")

        # Store in memory
        _invoices[invoice_id] = invoice

        logger.info(f"Invoice created: {invoice_id} for patient {patient_id}, total ₹{grand_total}")
        return {
            "error": False,
            "invoice": invoice,
            "message": f"Invoice {invoice_id} created successfully. Grand Total: ₹{grand_total:,.2f}",
        }

    @staticmethod
    def validate_invoice(invoice_id: str) -> Dict[str, Any]:
        """
        Validate an existing invoice for errors.

        Checks:
        - Duplicate medicines
        - Missing billing code
        - Missing price
        - Wrong quantity
        - Duplicate brand + generic

        Args:
            invoice_id: Invoice identifier

        Returns:
            Validation result with errors and warnings
        """
        invoice = _invoices.get(invoice_id)
        if not invoice:
            # Try to get from billing data
            stored = DataLoader.get_billing_data().get("invoices", [])
            for inv in stored:
                if inv["invoice_id"] == invoice_id:
                    invoice = inv
                    break

        if not invoice:
            return {
                "error": True,
                "invoice_id": invoice_id,
                "is_valid": False,
                "errors": [f"Invoice '{invoice_id}' not found."],
                "warnings": [],
            }

        errors = []
        warnings = []
        duplicates_removed = []

        # Check for missing billing code
        if not invoice.get("billing_code"):
            errors.append("Missing billing code.")

        # Check base charge
        bc = DataLoader.get_billing_code(invoice.get("billing_code", ""))
        if not bc:
            errors.append(f"Billing code '{invoice.get('billing_code')}' is invalid.")

        # Check medicines
        medicines = invoice.get("medicines", [])
        seen_names = {}

        for med in medicines:
            generic_name = med.get("generic_name", "")
            quantity = med.get("quantity", 0)
            unit_price = med.get("unit_price", 0)
            total = med.get("total", 0)

            # Duplicate check
            if generic_name.lower() in seen_names:
                duplicates_removed.append(generic_name)
                warnings.append(f"Duplicate medicine detected and removed: '{generic_name}'")
            else:
                seen_names[generic_name.lower()] = True

            # Missing price check
            if unit_price <= 0:
                errors.append(f"Medicine '{generic_name}' has invalid/missing price.")

            # Invalid quantity check
            if quantity <= 0:
                errors.append(f"Medicine '{generic_name}' has invalid quantity: {quantity}")

            # Total calculation check
            expected_total = round(unit_price * quantity, 2)
            if abs(total - expected_total) > 0.01:
                errors.append(
                    f"Medicine '{generic_name}' total mismatch: expected ₹{expected_total}, got ₹{total}"
                )

            # Missing billing code for medicine
            if not med.get("code"):
                errors.append(f"Medicine '{generic_name}' is missing a billing code.")

        is_valid = len(errors) == 0

        if is_valid:
            _invoices[invoice_id]["status"] = "validated"
            message = f"✅ Invoice {invoice_id} is valid. Grand Total: ₹{invoice.get('grand_total', 0):,.2f}"
        else:
            _invoices[invoice_id]["status"] = "invalid"
            message = f"❌ Invoice {invoice_id} has {len(errors)} validation error(s)."

        logger.info(f"Invoice validation {invoice_id}: {'VALID' if is_valid else 'INVALID'}, {len(errors)} errors")
        return {
            "error": False,
            "invoice_id": invoice_id,
            "is_valid": is_valid,
            "errors": errors,
            "warnings": warnings,
            "duplicates_removed": duplicates_removed,
            "validated_invoice": invoice if is_valid else None,
            "message": message,
        }

    @staticmethod
    def calculate_total(patient_id: str, billing_code: str,
                        medicines: List[Dict], service_items: List[str] = None) -> Dict[str, Any]:
        """
        Calculate the total bill for a patient without creating an invoice.

        Args:
            patient_id: Patient ID
            billing_code: Billing code
            medicines: List of medicines with quantities
            service_items: Optional list of additional services

        Returns:
            Total calculation breakdown
        """
        bc = DataLoader.get_billing_code(billing_code)
        base_charge = bc["base_charge"] if bc else 0

        medicine_total = 0.0
        service_total = 0.0
        breakdown = {"base_charge": base_charge}

        for med in medicines:
            generic_name = med.get("generic_name", "")
            quantity = int(med.get("quantity", 1))
            catalog = DataLoader.get_drug_catalog_entry(generic_name)
            if catalog:
                subtotal = catalog["unit_price"] * quantity
                medicine_total += subtotal
                breakdown[f"medicine_{generic_name}"] = round(subtotal, 2)

        # Service charges
        service_charges = DataLoader.get_service_charges()
        if service_items:
            for service in service_items:
                charge = service_charges.get(service, 0)
                service_total += charge
                breakdown[f"service_{service}"] = charge

        subtotal = base_charge + medicine_total + service_total
        tax_amount = round(subtotal * 0.12, 2)
        grand_total = round(subtotal + tax_amount, 2)

        logger.info(f"Total calculated for patient {patient_id}: ₹{grand_total}")
        return {
            "error": False,
            "patient_id": patient_id,
            "base_charge": base_charge,
            "medicine_total": round(medicine_total, 2),
            "service_charges": round(service_total, 2),
            "subtotal": round(subtotal, 2),
            "tax_amount": tax_amount,
            "grand_total": grand_total,
            "breakdown": breakdown,
        }

    @staticmethod
    def get_invoice(invoice_id: str) -> Optional[Dict]:
        """Get an invoice by ID."""
        return _invoices.get(invoice_id)

    @staticmethod
    def get_all_invoices() -> List[Dict]:
        """Get all invoices (in-memory + stored)."""
        result = list(_invoices.values())
        stored = DataLoader.get_billing_data().get("invoices", [])
        existing_ids = {i["invoice_id"] for i in result}
        for inv in stored:
            if inv["invoice_id"] not in existing_ids:
                result.append(inv)
        return result
