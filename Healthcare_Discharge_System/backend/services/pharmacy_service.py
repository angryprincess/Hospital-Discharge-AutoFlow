"""
Pharmacy Service - Business logic for Pharmacy operations.
Handles brand-to-generic resolution, stock checking, alternatives, and allergy conflict detection.
"""
import logging
from typing import Dict, Any, List, Optional

from backend.utils.data_loader import DataLoader

logger = logging.getLogger(__name__)


class PharmacyService:
    """
    Service class providing pharmacy business logic.
    Reads from synthetic_pharmacy_records.json.
    """

    @staticmethod
    def resolve_generic(brand_name: str) -> Dict[str, Any]:
        """
        Resolve a brand name to its generic equivalent.

        Args:
            brand_name: Brand name of the medicine (e.g., 'Augmentin')

        Returns:
            Resolution result with generic name and drug class
        """
        resolved = DataLoader.resolve_brand(brand_name)
        if not resolved:
            # Try case-insensitive search across all brands
            return {
                "error": False,
                "resolved": False,
                "brand_name": brand_name,
                "generic_name": brand_name,  # Fallback to brand name
                "drug_class": "Unknown",
                "category": "Unknown",
                "message": f"Brand '{brand_name}' not found in pharmacy database. Using brand name as-is.",
            }

        logger.info(f"Resolved brand '{brand_name}' → '{resolved['generic']}'")
        return {
            "error": False,
            "resolved": True,
            "brand_name": brand_name,
            "generic_name": resolved["generic"],
            "drug_class": resolved["drug_class"],
            "category": resolved["category"],
            "message": f"Successfully resolved: {brand_name} → {resolved['generic']}",
        }

    @staticmethod
    def check_stock(generic_name: str, required_quantity: int = 1) -> Dict[str, Any]:
        """
        Check inventory stock for a medicine.

        Args:
            generic_name: Generic name of the medicine
            required_quantity: Quantity required

        Returns:
            Stock check result with status and warnings
        """
        item = DataLoader.get_inventory_item(generic_name)

        if not item:
            return {
                "error": False,
                "generic_name": generic_name,
                "stock_status": "not_found",
                "stock_quantity": 0,
                "reserved": False,
                "warning": True,
                "message": f"Medicine '{generic_name}' not found in inventory.",
            }

        stock_qty = item["stock_quantity"]
        status = item["stock_status"]
        min_threshold = item["min_threshold"]

        result = {
            "error": False,
            "generic_name": generic_name,
            "medicine_id": item["medicine_id"],
            "stock_status": status,
            "stock_quantity": stock_qty,
            "min_threshold": min_threshold,
            "unit": item["unit"],
            "price_per_unit": item["price_per_unit"],
            "reserved": False,
            "warning": False,
            "message": "",
        }

        if status == "out_of_stock" or stock_qty == 0:
            result["reserved"] = False
            result["warning"] = True
            result["message"] = f"⚠️ OUT OF STOCK: '{generic_name}' is unavailable. Alternative medicine required."
            logger.warning(f"Out of stock: {generic_name}")

        elif status == "low_stock" or stock_qty < min_threshold:
            result["stock_status"] = "low_stock"
            result["reserved"] = stock_qty >= required_quantity
            result["warning"] = True
            result["message"] = (
                f"⚠️ LOW STOCK WARNING: '{generic_name}' has only {stock_qty} units remaining "
                f"(minimum threshold: {min_threshold}). Consider restocking."
            )
            logger.warning(f"Low stock: {generic_name} ({stock_qty} units)")

        else:
            if stock_qty >= required_quantity:
                result["reserved"] = True
                result["message"] = (
                    f"✅ In stock: '{generic_name}' — {stock_qty} units available. "
                    f"Reserved {required_quantity} unit(s)."
                )
            else:
                result["reserved"] = False
                result["warning"] = True
                result["message"] = (
                    f"⚠️ Insufficient stock: Only {stock_qty} units available but {required_quantity} required."
                )

        return result

    @staticmethod
    def suggest_alternative(generic_name: str, patient_allergies: List[str] = None) -> Dict[str, Any]:
        """
        Suggest alternative medicines for an out-of-stock or conflicting drug.

        Args:
            generic_name: Generic medicine name to find alternatives for
            patient_allergies: List of patient's known allergies

        Returns:
            Alternative medicine suggestions with allergy filtering
        """
        alt_data = DataLoader.get_alternatives_for(generic_name)
        patient_allergies = patient_allergies or []
        allergy_rules = DataLoader.get_allergy_rules()

        if not alt_data:
            return {
                "error": False,
                "original_generic": generic_name,
                "alternatives": [],
                "approved_alternatives": [],
                "doctor_approval_required": False,
                "message": f"No alternatives found for '{generic_name}' in the pharmacy database.",
            }

        alternatives = alt_data["alternatives"]
        approved = []
        blocked = []
        doctor_approval_required = False

        for alt in alternatives:
            # Check if this alternative conflicts with patient allergies
            conflict_found = False
            for rule in allergy_rules:
                if rule["allergy"] in patient_allergies:
                    if alt["generic"] in rule["conflicts_with"] or alt.get("allergy_group", "") in rule["conflicts_with"]:
                        conflict_found = True
                        blocked.append({
                            **alt,
                            "blocked_reason": f"Allergy conflict: patient is allergic to {rule['allergy']}"
                        })
                        break

            if not conflict_found:
                # Check stock for this alternative
                stock_result = PharmacyService.check_stock(alt["generic"])
                alt_with_stock = {**alt, "stock_status": stock_result["stock_status"],
                                  "stock_quantity": stock_result.get("stock_quantity", 0)}
                if alt["stock_status"] in ("in_stock",) or stock_result["stock_status"] == "in_stock":
                    approved.append(alt_with_stock)
                else:
                    doctor_approval_required = True

        if blocked:
            doctor_approval_required = True

        logger.info(f"Alternatives for '{generic_name}': {len(approved)} approved, {len(blocked)} blocked")

        return {
            "error": False,
            "original_generic": generic_name,
            "alternatives": alternatives,
            "approved_alternatives": approved,
            "blocked_alternatives": blocked,
            "doctor_approval_required": doctor_approval_required,
            "message": (
                f"Found {len(alternatives)} alternatives. {len(approved)} approved, "
                f"{len(blocked)} blocked due to allergy conflicts."
                + (" ⚠️ Doctor approval required." if doctor_approval_required else "")
            ),
        }

    @staticmethod
    def check_allergy_conflict(medicine_name: str, patient_allergies: List[str]) -> Dict[str, Any]:
        """
        Check if a medicine conflicts with patient allergies.

        Args:
            medicine_name: Generic or brand name of medicine
            patient_allergies: List of patient's allergies

        Returns:
            Conflict check result
        """
        allergy_rules = DataLoader.get_allergy_rules()
        conflicts = []

        # Also resolve brand to generic for checking
        resolved = DataLoader.resolve_brand(medicine_name)
        generic_name = resolved["generic"] if resolved else medicine_name

        for rule in allergy_rules:
            if rule["allergy"] in patient_allergies:
                # Check if the medicine (brand or generic) is in the conflict list
                for conflict_med in rule["conflicts_with"]:
                    if (conflict_med.lower() == medicine_name.lower() or
                            conflict_med.lower() == generic_name.lower()):
                        conflicts.append({
                            "allergy": rule["allergy"],
                            "conflicting_medicine": conflict_med,
                            "severity": rule["severity"],
                            "action": rule["action"],
                        })
                        break

        has_conflict = len(conflicts) > 0

        if has_conflict:
            severity = max(conflicts, key=lambda c: 1 if c["severity"] == "HIGH" else 0)["severity"]
            action = "BLOCK" if any(c["action"] == "BLOCK" for c in conflicts) else "WARN"
            message = (
                f"🚨 ALLERGY CONFLICT DETECTED: '{medicine_name}' conflicts with patient allergy. "
                f"Severity: {severity}. Action: {action}. "
                f"Conflicting allergies: {[c['allergy'] for c in conflicts]}"
            )
            logger.warning(f"Allergy conflict: {medicine_name} vs {patient_allergies}")
        else:
            action = "ALLOW"
            severity = None
            message = f"✅ No allergy conflicts detected for '{medicine_name}'."

        return {
            "error": False,
            "medicine": medicine_name,
            "generic_name": generic_name,
            "patient_allergies": patient_allergies,
            "conflicts": conflicts,
            "has_conflict": has_conflict,
            "severity": severity,
            "action": action,
            "message": message,
        }

    @staticmethod
    def get_inventory_summary() -> Dict[str, Any]:
        """Get pharmacy inventory summary for dashboard."""
        inventory = DataLoader.get_inventory()

        in_stock = sum(1 for i in inventory if i["stock_status"] == "in_stock")
        low_stock = sum(1 for i in inventory if i["stock_status"] == "low_stock")
        out_of_stock = sum(1 for i in inventory if i["stock_status"] == "out_of_stock")
        low_stock_items = [i["generic_name"] for i in inventory if i["stock_status"] == "low_stock"]
        out_items = [i["generic_name"] for i in inventory if i["stock_status"] == "out_of_stock"]

        return {
            "total_medicines": len(inventory),
            "in_stock": in_stock,
            "low_stock": low_stock,
            "out_of_stock": out_of_stock,
            "low_stock_items": low_stock_items,
            "out_of_stock_items": out_items,
        }
