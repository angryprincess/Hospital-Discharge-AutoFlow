"""
AI Discharge Coordination Agent.
Orchestrates the complete discharge process by coordinating EHR, Pharmacy, and Billing services.
Implements a 10-step workflow with intelligent decision-making, conflict resolution, and audit logging.
"""
import sys
import os
import uuid
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from backend.services.ehr_service import EHRService
from backend.services.pharmacy_service import PharmacyService
from backend.services.billing_service import BillingService
from backend.security.rbac import require_permission
from backend.security.phi_guard import phi_guard
from backend.utils.audit_logger import audit_logger
from backend.utils.data_loader import DataLoader
from backend.models.audit import AuditStatus

logging.basicConfig(level=logging.INFO, format="%(asctime)s [AI-AGENT] %(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


class WorkflowStep:
    """Represents a single step in the discharge workflow."""
    def __init__(self, step_number: int, name: str, status: str = "pending",
                 message: str = "", data: Dict = None, warnings: List[str] = None):
        self.step_number = step_number
        self.name = name
        self.status = status  # pending, in_progress, completed, failed, warning, skipped
        self.message = message
        self.data = data or {}
        self.warnings = warnings or []
        self.timestamp = datetime.now().isoformat()

    def to_dict(self) -> Dict:
        return {
            "step_number": self.step_number,
            "name": self.name,
            "status": self.status,
            "message": self.message,
            "data": self.data,
            "warnings": self.warnings,
            "timestamp": self.timestamp,
        }


class DischargeWorkflowResult:
    """Complete result of the discharge workflow."""
    def __init__(self, workflow_id: str, patient_id: str, role: str):
        self.workflow_id = workflow_id
        self.patient_id = patient_id
        self.role = role
        self.started_at = datetime.now().isoformat()
        self.completed_at: Optional[str] = None
        self.steps: List[WorkflowStep] = []
        self.overall_status: str = "in_progress"  # success, partial, failed
        self.discharge_packet: Optional[Dict] = None
        self.recommendations: List[Dict] = []
        self.alerts: List[Dict] = []
        self.human_approval_required: bool = False
        self.approval_reasons: List[str] = []
        self.invoice: Optional[Dict] = None
        self.medication_map: List[Dict] = []

    def add_step(self, step: WorkflowStep):
        self.steps.append(step)

    def add_recommendation(self, category: str, message: str, severity: str = "info"):
        self.recommendations.append({"category": category, "message": message, "severity": severity})

    def add_alert(self, alert_type: str, message: str, severity: str = "warning"):
        self.alerts.append({"type": alert_type, "message": message, "severity": severity})

    def require_human_approval(self, reason: str):
        self.human_approval_required = True
        self.approval_reasons.append(reason)

    def to_dict(self) -> Dict:
        return {
            "workflow_id": self.workflow_id,
            "patient_id": self.patient_id,
            "role": self.role,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "overall_status": self.overall_status,
            "steps": [s.to_dict() for s in self.steps],
            "discharge_packet": self.discharge_packet,
            "recommendations": self.recommendations,
            "alerts": self.alerts,
            "human_approval_required": self.human_approval_required,
            "approval_reasons": self.approval_reasons,
            "invoice": self.invoice,
            "medication_map": self.medication_map,
        }


class DischargeAgent:
    """
    AI Discharge Coordination Agent.

    Orchestrates the full discharge workflow:
    1. Search Patient
    2. Read EHR
    3. Retrieve Medications
    4. Resolve Brand → Generic
    5. Check Inventory
    6. Suggest Alternatives (if needed)
    7. Check Allergy Conflicts
    8. Generate Invoice
    9. Validate Invoice
    10. Generate Final Discharge Packet + Audit Log
    """

    def __init__(self, role: str = "administrator"):
        self.role = role
        logger.info(f"DischargeAgent initialized with role: {role}")

    def run_discharge_workflow(self, patient_id: str,
                               override_approvals: bool = False) -> DischargeWorkflowResult:
        """
        Execute the complete discharge coordination workflow.

        Args:
            patient_id: Patient ID to discharge
            override_approvals: If True, bypass human approval for testing

        Returns:
            DischargeWorkflowResult with all step results
        """
        workflow_id = f"WF-{datetime.now().strftime('%Y%m%d%H%M%S')}-{str(uuid.uuid4())[:4].upper()}"
        result = DischargeWorkflowResult(workflow_id, patient_id, self.role)

        logger.info(f"Starting discharge workflow {workflow_id} for patient {patient_id}")
        audit_logger.log(
            server="Agent", tool="run_discharge_workflow", role=self.role,
            status=AuditStatus.SUCCESS,
            input_data={"patient_id": patient_id, "workflow_id": workflow_id},
            output_summary=f"Workflow started",
            patient_id=patient_id,
        )

        try:
            # ── Step 1: Search & Validate Patient ──────────────────────────────
            patient_data = self._step1_search_patient(patient_id, result)
            if not patient_data:
                result.overall_status = "failed"
                result.completed_at = datetime.now().isoformat()
                return result

            # ── Step 2: Read Full EHR ──────────────────────────────────────────
            self._step2_read_ehr(patient_id, patient_data, result)

            # ── Step 3: Retrieve Medications ───────────────────────────────────
            medications = patient_data.get("medications", [])
            self._step3_retrieve_medications(patient_id, medications, result)

            # ── Step 4: Resolve Brand → Generic ───────────────────────────────
            medication_map = self._step4_resolve_generics(medications, result)
            result.medication_map = medication_map

            # ── Step 5: Check Inventory ────────────────────────────────────────
            stock_results = self._step5_check_inventory(medication_map, result)

            # ── Step 6: Suggest Alternatives for Out-of-Stock ─────────────────
            allergies = patient_data.get("allergies", [])
            final_medications = self._step6_suggest_alternatives(
                medication_map, stock_results, allergies, result
            )

            # ── Step 7: Check Allergy Conflicts ───────────────────────────────
            self._step7_check_allergies(final_medications, allergies, result)

            # ── Step 8: Generate Invoice ───────────────────────────────────────
            billing_code = patient_data.get("billing_code", "")
            invoice_data = self._step8_generate_invoice(
                patient_id, billing_code, final_medications, result
            )

            # ── Step 9: Validate Invoice ───────────────────────────────────────
            if invoice_data:
                self._step9_validate_invoice(invoice_data, result)

            # ── Step 10: Generate Discharge Packet ────────────────────────────
            self._step10_discharge_packet(patient_data, final_medications, invoice_data, result)

        except Exception as e:
            logger.error(f"Workflow error: {e}", exc_info=True)
            result.add_alert("system_error", f"Unexpected error in workflow: {str(e)}", "critical")
            result.overall_status = "failed"
            audit_logger.log_failure("Agent", "run_discharge_workflow", self.role,
                                     str(e), patient_id)

        result.completed_at = datetime.now().isoformat()

        # Determine final status
        if result.overall_status == "in_progress":
            failed_steps = [s for s in result.steps if s.status == "failed"]
            if len(failed_steps) > 2:
                result.overall_status = "failed"
            elif result.human_approval_required:
                result.overall_status = "partial"
            else:
                result.overall_status = "success"

        audit_logger.log(
            server="Agent", tool="run_discharge_workflow", role=self.role,
            status=AuditStatus.SUCCESS if result.overall_status == "success" else AuditStatus.WARNING,
            input_data={"workflow_id": workflow_id},
            output_summary=f"Workflow {result.overall_status}. Steps: {len(result.steps)}",
            patient_id=patient_id,
        )

        logger.info(f"Workflow {workflow_id} completed: {result.overall_status}")
        return result

    # ─────────────────────────────────────────────────────────────────────────
    # STEP IMPLEMENTATIONS
    # ─────────────────────────────────────────────────────────────────────────

    def _step1_search_patient(self, patient_id: str, result: DischargeWorkflowResult) -> Optional[Dict]:
        """Step 1: Search and validate patient existence."""
        step = WorkflowStep(1, "Patient Search & Validation")
        step.status = "in_progress"

        ehr_result = EHRService.get_patient(patient_id)

        if ehr_result.get("error"):
            step.status = "failed"
            step.message = f"❌ Patient '{patient_id}' not found in EHR system."
            result.add_alert("patient_not_found", step.message, "critical")
            result.add_recommendation("patient", f"Verify patient ID '{patient_id}' and try again.", "error")
            result.add_step(step)
            return None

        patient = ehr_result["data"]
        step.status = "completed"
        step.message = f"✅ Patient found: {patient['name']} (ID: {patient_id}, Ward: {patient['ward']})"
        step.data = {
            "patient_id": patient_id,
            "name": patient["name"],
            "ward": patient["ward"],
            "discharge_status": patient["discharge_status"],
        }
        result.add_step(step)
        result.add_recommendation("patient", f"Patient {patient['name']} located successfully.", "success")
        return patient

    def _step2_read_ehr(self, patient_id: str, patient_data: Dict, result: DischargeWorkflowResult):
        """Step 2: Read and analyze full EHR data."""
        step = WorkflowStep(2, "EHR Data Read")
        step.status = "in_progress"

        allergies = patient_data.get("allergies", [])
        diagnosis = patient_data.get("diagnosis", "Unknown")
        discharge_status = patient_data.get("discharge_status", "unknown")

        step.status = "completed"
        step.message = (
            f"✅ EHR read complete. Diagnosis: {diagnosis}. "
            f"Discharge status: {discharge_status}. "
            f"Allergies: {len(allergies)} recorded."
        )
        step.data = {
            "diagnosis": diagnosis,
            "discharge_status": discharge_status,
            "allergy_count": len(allergies),
            "allergies": allergies,
            "admission_date": patient_data.get("admission_date"),
        }

        if allergies:
            result.add_alert(
                "allergies_present",
                f"Patient has {len(allergies)} known allergy/allergies: {', '.join(allergies)}",
                "warning"
            )

        result.add_step(step)

    def _step3_retrieve_medications(self, patient_id: str, medications: List[Dict],
                                     result: DischargeWorkflowResult):
        """Step 3: Retrieve and list all medications."""
        step = WorkflowStep(3, "Medication Retrieval")
        step.status = "in_progress"

        if not medications:
            step.status = "warning"
            step.message = "⚠️ No medications prescribed for this patient."
            result.add_recommendation("pharmacy", "No medications to process.", "warning")
        else:
            brand_list = [m["brand"] for m in medications]
            step.status = "completed"
            step.message = (
                f"✅ Retrieved {len(medications)} medication(s): {', '.join(brand_list)}"
            )
            step.data = {"medications": medications, "count": len(medications)}

        result.add_step(step)

    def _step4_resolve_generics(self, medications: List[Dict],
                                 result: DischargeWorkflowResult) -> List[Dict]:
        """Step 4: Resolve brand names to generic equivalents."""
        step = WorkflowStep(4, "Brand → Generic Resolution")
        step.status = "in_progress"

        medication_map = []
        resolved_count = 0
        unresolved = []

        for med in medications:
            brand = med["brand"]
            resolution = PharmacyService.resolve_generic(brand)

            med_entry = {
                "brand": brand,
                "generic": resolution.get("generic_name", brand),
                "drug_class": resolution.get("drug_class", "Unknown"),
                "category": resolution.get("category", "Unknown"),
                "resolved": resolution.get("resolved", False),
                "dosage": med.get("dosage", ""),
                "frequency": med.get("frequency", ""),
                "duration": med.get("duration", ""),
            }

            if resolution.get("resolved"):
                resolved_count += 1
                result.add_recommendation(
                    "pharmacy",
                    f"Brand resolved: {brand} → {resolution['generic_name']} ({resolution['drug_class']})",
                    "success"
                )
            else:
                unresolved.append(brand)

            medication_map.append(med_entry)

        step.status = "completed" if resolved_count > 0 else "warning"
        step.message = (
            f"✅ Resolved {resolved_count}/{len(medications)} medications. "
            + (f"Unresolved: {unresolved}" if unresolved else "All resolved.")
        )
        step.data = {"medication_map": medication_map, "resolved_count": resolved_count}
        result.add_step(step)
        return medication_map

    def _step5_check_inventory(self, medication_map: List[Dict],
                                result: DischargeWorkflowResult) -> Dict[str, Dict]:
        """Step 5: Check pharmacy inventory for each medicine."""
        step = WorkflowStep(5, "Pharmacy Inventory Check")
        step.status = "in_progress"

        stock_results = {}
        low_stock_items = []
        out_of_stock_items = []

        for med in medication_map:
            generic = med["generic"]
            # Estimate quantity based on duration (simplified)
            quantity = self._estimate_quantity(med)
            stock = PharmacyService.check_stock(generic, quantity)
            stock_results[generic] = stock

            if stock["stock_status"] == "out_of_stock":
                out_of_stock_items.append(generic)
                result.add_alert(
                    "out_of_stock",
                    f"❌ {generic} is OUT OF STOCK. Alternative required.",
                    "critical"
                )
            elif stock["stock_status"] == "low_stock":
                low_stock_items.append(generic)
                result.add_alert(
                    "low_stock",
                    f"⚠️ {generic} has LOW STOCK ({stock['stock_quantity']} units remaining).",
                    "warning"
                )

        if out_of_stock_items:
            step.status = "warning"
            step.message = (
                f"⚠️ Inventory check complete. "
                f"{len(out_of_stock_items)} out-of-stock, {len(low_stock_items)} low-stock."
            )
        elif low_stock_items:
            step.status = "warning"
            step.message = f"⚠️ Inventory check complete. Low stock: {', '.join(low_stock_items)}"
        else:
            step.status = "completed"
            step.message = f"✅ All {len(medication_map)} medicines in stock."

        step.data = {
            "stock_results": {k: {"status": v["stock_status"], "quantity": v["stock_quantity"]}
                              for k, v in stock_results.items()},
            "out_of_stock": out_of_stock_items,
            "low_stock": low_stock_items,
        }
        result.add_step(step)
        return stock_results

    def _step6_suggest_alternatives(self, medication_map: List[Dict],
                                     stock_results: Dict[str, Dict],
                                     allergies: List[str],
                                     result: DischargeWorkflowResult) -> List[Dict]:
        """Step 6: Suggest alternatives for out-of-stock or conflicting medicines."""
        step = WorkflowStep(6, "Alternative Medicine Suggestion")
        step.status = "in_progress"

        final_medications = []
        alternatives_suggested = 0
        doctor_approval_needed = []

        for med in medication_map:
            generic = med["generic"]
            stock = stock_results.get(generic, {})

            if stock.get("stock_status") in ("out_of_stock", "not_found") or stock.get("stock_quantity", 0) == 0:
                # Suggest alternative
                alt_result = PharmacyService.suggest_alternative(generic, allergies)

                if alt_result["approved_alternatives"]:
                    best_alt = alt_result["approved_alternatives"][0]
                    alternatives_suggested += 1
                    result.add_recommendation(
                        "pharmacy",
                        f"Alternative suggested: {generic} → {best_alt['generic']} ({best_alt['brand']}). "
                        f"Stock: {best_alt['stock_status']}",
                        "warning"
                    )
                    final_medications.append({
                        **med,
                        "generic": best_alt["generic"],
                        "brand": best_alt["brand"],
                        "is_alternative": True,
                        "original_generic": generic,
                    })
                elif alt_result["blocked_alternatives"]:
                    doctor_approval_needed.append(generic)
                    result.require_human_approval(
                        f"All alternatives for '{generic}' conflict with patient allergies. "
                        "Doctor must select and approve an alternative."
                    )
                    result.add_alert(
                        "allergy_block",
                        f"🚨 All alternatives for '{generic}' are blocked due to allergy conflicts. "
                        "Doctor approval required.",
                        "critical"
                    )
                    # Keep original with approval flag
                    final_medications.append({**med, "approval_required": True})
                else:
                    result.add_alert(
                        "no_alternative",
                        f"No alternatives found for '{generic}'. Manual procurement required.",
                        "critical"
                    )
                    final_medications.append({**med, "out_of_stock": True})
            else:
                final_medications.append({**med, "is_alternative": False})

        if alternatives_suggested == 0 and not doctor_approval_needed:
            step.status = "completed"
            step.message = "✅ No alternative medicines needed. All medications available."
        elif alternatives_suggested > 0:
            step.status = "warning"
            step.message = f"⚠️ {alternatives_suggested} alternative(s) suggested due to stock issues."
        else:
            step.status = "warning"
            step.message = f"⚠️ Doctor approval required for {len(doctor_approval_needed)} medicine(s)."

        step.data = {
            "alternatives_suggested": alternatives_suggested,
            "doctor_approval_needed": doctor_approval_needed,
            "final_medication_count": len(final_medications),
        }
        result.add_step(step)
        return final_medications

    def _step7_check_allergies(self, final_medications: List[Dict],
                                allergies: List[str],
                                result: DischargeWorkflowResult):
        """Step 7: Check all final medications against patient allergies."""
        step = WorkflowStep(7, "Allergy Conflict Check")
        step.status = "in_progress"

        conflicts_found = []
        blocked_medicines = []

        if not allergies:
            step.status = "completed"
            step.message = "✅ No known allergies. All medications approved."
            result.add_step(step)
            return

        for med in final_medications:
            generic = med["generic"]
            conflict = PharmacyService.check_allergy_conflict(generic, allergies)

            if conflict["has_conflict"]:
                conflicts_found.append({
                    "medicine": generic,
                    "conflict": conflict,
                })
                if conflict["action"] == "BLOCK":
                    blocked_medicines.append(generic)
                    result.add_alert(
                        "allergy_conflict",
                        f"🚨 BLOCKED: {generic} conflicts with allergy '{conflict['conflicts'][0]['allergy']}'. "
                        f"Severity: {conflict['severity']}",
                        "critical"
                    )
                    result.require_human_approval(
                        f"Medicine '{generic}' is blocked due to patient allergy conflict. "
                        "Doctor must prescribe a safe alternative."
                    )
                else:
                    result.add_alert(
                        "allergy_warning",
                        f"⚠️ Warning: {generic} may interact with '{conflict['conflicts'][0]['allergy']}'. "
                        "Monitor carefully.",
                        "warning"
                    )

        if blocked_medicines:
            step.status = "failed"
            step.message = (
                f"🚨 ALLERGY CONFLICTS DETECTED! {len(blocked_medicines)} medicine(s) blocked: "
                f"{', '.join(blocked_medicines)}. Doctor approval required."
            )
        elif conflicts_found:
            step.status = "warning"
            step.message = f"⚠️ {len(conflicts_found)} allergy warning(s). No critical blocks."
        else:
            step.status = "completed"
            step.message = "✅ No allergy conflicts detected. All medications safe."

        step.data = {
            "conflicts_found": len(conflicts_found),
            "blocked_medicines": blocked_medicines,
            "checked_medicines": [m["generic"] for m in final_medications],
        }
        result.add_step(step)

    def _step8_generate_invoice(self, patient_id: str, billing_code: str,
                                 final_medications: List[Dict],
                                 result: DischargeWorkflowResult) -> Optional[Dict]:
        """Step 8: Generate the patient invoice (PHI-safe)."""
        step = WorkflowStep(8, "Invoice Generation")
        step.status = "in_progress"

        # PHI Guard: only safe fields to billing
        medicines_for_billing = []
        for med in final_medications:
            if not med.get("out_of_stock") and not med.get("approval_required"):
                quantity = self._estimate_quantity(med)
                medicines_for_billing.append({
                    "generic_name": med["generic"],
                    "quantity": quantity,
                })

        invoice_result = BillingService.create_invoice(patient_id, billing_code, medicines_for_billing)

        if invoice_result.get("error"):
            step.status = "failed"
            step.message = f"❌ Invoice creation failed: {invoice_result['message']}"
            result.add_alert("invoice_error", step.message, "critical")
            result.add_step(step)
            return None

        invoice = invoice_result["invoice"]
        result.invoice = invoice

        step.status = "completed"
        step.message = (
            f"✅ Invoice created: {invoice['invoice_id']}. "
            f"Grand Total: ₹{invoice['grand_total']:,.2f}"
        )
        step.data = {
            "invoice_id": invoice["invoice_id"],
            "grand_total": invoice["grand_total"],
            "medicine_count": len(invoice["medicines"]),
        }

        if invoice.get("warnings"):
            for w in invoice["warnings"]:
                result.add_alert("invoice_warning", w, "warning")

        result.add_step(step)
        return invoice

    def _step9_validate_invoice(self, invoice: Dict, result: DischargeWorkflowResult):
        """Step 9: Validate the generated invoice."""
        step = WorkflowStep(9, "Invoice Validation")
        step.status = "in_progress"

        invoice_id = invoice["invoice_id"]
        validation = BillingService.validate_invoice(invoice_id)

        if validation.get("error"):
            step.status = "failed"
            step.message = f"❌ Invoice validation error: {validation.get('errors', ['Unknown'])[0]}"
            result.add_alert("validation_error", step.message, "critical")
            result.add_step(step)
            return

        if validation["is_valid"]:
            step.status = "completed"
            step.message = f"✅ Invoice {invoice_id} validated successfully."
            result.add_recommendation(
                "billing",
                f"Invoice {invoice_id} is valid. Grand Total: ₹{invoice.get('grand_total', 0):,.2f}",
                "success"
            )
        else:
            step.status = "warning"
            step.message = (
                f"⚠️ Invoice validation found {len(validation['errors'])} error(s): "
                f"{'; '.join(validation['errors'])}"
            )
            result.add_alert("invoice_invalid", step.message, "warning")
            result.require_human_approval(
                f"Invoice {invoice_id} has validation errors that need manual review."
            )

        if validation.get("duplicates_removed"):
            step.warnings.extend(validation["duplicates_removed"])
            result.add_recommendation(
                "billing",
                f"Duplicates removed from invoice: {validation['duplicates_removed']}",
                "info"
            )

        step.data = {
            "is_valid": validation["is_valid"],
            "errors": validation.get("errors", []),
            "warnings": validation.get("warnings", []),
            "duplicates_removed": validation.get("duplicates_removed", []),
        }
        result.add_step(step)

    def _step10_discharge_packet(self, patient_data: Dict, final_medications: List[Dict],
                                  invoice: Optional[Dict],
                                  result: DischargeWorkflowResult):
        """Step 10: Generate the final discharge packet."""
        step = WorkflowStep(10, "Discharge Packet Generation")
        step.status = "in_progress"

        # Build discharge packet
        packet = {
            "packet_id": f"DISCH-{patient_data['patient_id']}-{datetime.now().strftime('%Y%m%d')}",
            "generated_at": datetime.now().isoformat(),
            "patient": {
                "patient_id": patient_data["patient_id"],
                "name": patient_data["name"],
                "age": patient_data["age"],
                "gender": patient_data["gender"],
                "ward": patient_data["ward"],
                "attending_doctor": patient_data["attending_doctor"],
                "admission_date": patient_data["admission_date"],
            },
            "discharge_summary": patient_data.get("discharge_summary", ""),
            "medications": final_medications,
            "medication_map": result.medication_map,
            "invoice_summary": {
                "invoice_id": invoice["invoice_id"] if invoice else None,
                "grand_total": invoice.get("grand_total", 0) if invoice else 0,
                "status": invoice.get("status", "not_generated") if invoice else "not_generated",
            },
            "workflow_id": result.workflow_id,
            "human_approval_required": result.human_approval_required,
            "approval_reasons": result.approval_reasons,
            "recommendations": result.recommendations,
            "alerts": result.alerts,
            "instructions": self._generate_patient_instructions(patient_data, final_medications),
        }

        result.discharge_packet = packet
        result.add_recommendation(
            "discharge",
            "Discharge packet generated successfully. Review before final discharge.",
            "success"
        )

        if result.human_approval_required:
            step.status = "warning"
            step.message = (
                f"⚠️ Discharge packet ready but requires human approval: "
                f"{'; '.join(result.approval_reasons)}"
            )
        else:
            step.status = "completed"
            step.message = f"✅ Discharge packet generated: {packet['packet_id']}"

        step.data = {
            "packet_id": packet["packet_id"],
            "medicine_count": len(final_medications),
            "has_invoice": invoice is not None,
        }
        result.add_step(step)

        # Final audit log
        audit_logger.log(
            server="Agent", tool="generate_discharge_packet", role=self.role,
            status=AuditStatus.SUCCESS if not result.human_approval_required else AuditStatus.WARNING,
            input_data={"patient_id": patient_data["patient_id"], "workflow_id": result.workflow_id},
            output_summary=f"Packet {packet['packet_id']} generated. Approval needed: {result.human_approval_required}",
            patient_id=patient_data["patient_id"],
        )

    def _estimate_quantity(self, med: Dict) -> int:
        """Estimate quantity of medicine needed based on dosage and duration."""
        duration = med.get("duration", "7 days").lower()
        frequency = med.get("frequency", "once daily").lower()

        # Extract days
        days = 7  # default
        for word in duration.split():
            try:
                days = int(word)
                break
            except ValueError:
                pass

        # Extract times per day
        freq_map = {
            "once daily": 1, "twice daily": 2, "thrice daily": 3,
            "four times daily": 4, "every 8 hours": 3, "every 6 hours": 4,
            "every 12 hours": 2, "three times daily": 3, "twice a day": 2,
            "thrice a day": 3, "with meals": 3,
        }

        times = 1
        for key, val in freq_map.items():
            if key in frequency:
                times = val
                break

        # Handle "lifetime" duration - supply 30 days
        if "lifetime" in duration or "month" in duration:
            days = 30

        return max(1, days * times)

    @staticmethod
    def _generate_patient_instructions(patient_data: Dict, medications: List[Dict]) -> List[str]:
        """Generate patient discharge instructions."""
        instructions = [
            "Take all medications as prescribed by your doctor.",
            "Complete the full course of antibiotics (if any) even if you feel better.",
            "Attend all follow-up appointments as scheduled.",
            "Contact emergency services or return to hospital if symptoms worsen.",
        ]

        allergies = patient_data.get("allergies", [])
        if allergies:
            instructions.append(f"IMPORTANT: You are allergic to: {', '.join(allergies)}. "
                                 "Inform all healthcare providers of these allergies.")

        return instructions

    def quick_check(self, patient_id: str) -> Dict[str, Any]:
        """Quick status check for a patient without full workflow."""
        patient_result = EHRService.get_patient(patient_id)
        if patient_result.get("error"):
            return {"error": True, "message": patient_result["message"]}

        patient = patient_result["data"]
        inventory_summary = PharmacyService.get_inventory_summary()

        return {
            "patient_id": patient_id,
            "name": patient["name"],
            "discharge_status": patient["discharge_status"],
            "medication_count": len(patient.get("medications", [])),
            "allergy_count": len(patient.get("allergies", [])),
            "inventory_summary": inventory_summary,
            "ready": patient["discharge_status"] == "ready_for_discharge",
        }
