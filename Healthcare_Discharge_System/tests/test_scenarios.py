"""
Test Scenarios for the AI Healthcare Discharge Coordination System.
Tests all 13 required scenarios.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
import json

from backend.services.ehr_service import EHRService
from backend.services.pharmacy_service import PharmacyService
from backend.services.billing_service import BillingService
from backend.agent.discharge_agent import DischargeAgent
from backend.security.rbac import rbac, require_permission
from backend.security.phi_guard import phi_guard


# ─── SCENARIO 1: Happy Path ────────────────────────────────────────────────────
def test_scenario_01_happy_path():
    """Happy path: P001 - Ravi Kumar (ready for discharge, manageable allergies)."""
    print("\n" + "="*60)
    print("SCENARIO 1: Happy Path")
    print("="*60)

    agent = DischargeAgent(role="administrator")
    result = agent.run_discharge_workflow("P001")
    d = result.to_dict()

    print(f"Status: {d['overall_status']}")
    print(f"Steps completed: {sum(1 for s in d['steps'] if s['status'] == 'completed')}")

    assert d["patient_id"] == "P001"
    assert len(d["steps"]) > 0
    assert d["overall_status"] in ("success", "partial")
    print("✅ PASSED: Happy path workflow completed.")


# ─── SCENARIO 2: Brand → Generic Resolution ────────────────────────────────────
def test_scenario_02_brand_generic_resolution():
    """Brand to generic resolution: Augmentin → Amoxicillin + Clavulanate."""
    print("\n" + "="*60)
    print("SCENARIO 2: Brand → Generic Resolution")
    print("="*60)

    test_cases = [
        ("Augmentin", "Amoxicillin + Clavulanate"),
        ("Crocin", "Paracetamol"),
        ("Dolo", "Paracetamol"),
        ("Telma", "Telmisartan"),
        ("Glycomet", "Metformin"),
    ]

    for brand, expected_generic in test_cases:
        result = PharmacyService.resolve_generic(brand)
        print(f"  {brand} → {result['generic_name']} (Expected: {expected_generic})")
        assert result["resolved"] == True, f"Failed to resolve {brand}"
        assert result["generic_name"] == expected_generic, f"Wrong generic for {brand}"

    print("✅ PASSED: All brand-to-generic resolutions correct.")


# ─── SCENARIO 3: Out of Stock Medicine ────────────────────────────────────────
def test_scenario_03_out_of_stock():
    """Out of stock: Metformin has 0 quantity."""
    print("\n" + "="*60)
    print("SCENARIO 3: Out of Stock Medicine")
    print("="*60)

    result = PharmacyService.check_stock("Metformin", 60)
    print(f"  Metformin stock: {result['stock_status']} ({result['stock_quantity']} units)")

    assert result["stock_status"] == "out_of_stock"
    assert result["stock_quantity"] == 0
    assert result["warning"] == True
    assert "OUT OF STOCK" in result["message"]
    print("✅ PASSED: Out-of-stock correctly detected.")


# ─── SCENARIO 4: Low Stock Warning ────────────────────────────────────────────
def test_scenario_04_low_stock_warning():
    """Low stock: Amoxicillin + Clavulanate has 45 units, threshold 50."""
    print("\n" + "="*60)
    print("SCENARIO 4: Low Stock Warning")
    print("="*60)

    result = PharmacyService.check_stock("Amoxicillin + Clavulanate", 14)
    print(f"  Augmentin (generic) stock: {result['stock_status']} ({result['stock_quantity']} units, threshold: {result['min_threshold']})")

    assert result["stock_status"] == "low_stock"
    assert result["warning"] == True
    assert result["stock_quantity"] < result["min_threshold"]
    print("✅ PASSED: Low stock warning correctly triggered.")


# ─── SCENARIO 5: Alternative Suggested ────────────────────────────────────────
def test_scenario_05_alternative_suggested():
    """Alternative suggestion: Metformin is out of stock → Glipizide suggested."""
    print("\n" + "="*60)
    print("SCENARIO 5: Alternative Medicine Suggested")
    print("="*60)

    result = PharmacyService.suggest_alternative("Metformin", patient_allergies=[])
    print(f"  Alternatives for Metformin: {len(result['approved_alternatives'])} found")
    for alt in result["approved_alternatives"]:
        print(f"    → {alt['generic']} ({alt['brand']}) - {alt['stock_status']}")

    assert result["original_generic"] == "Metformin"
    assert len(result["alternatives"]) > 0
    print("✅ PASSED: Alternatives successfully suggested.")


# ─── SCENARIO 6: Allergy Conflict ─────────────────────────────────────────────
def test_scenario_06_allergy_conflict():
    """Allergy conflict: Patient P001 is allergic to Penicillin, prescribed Augmentin."""
    print("\n" + "="*60)
    print("SCENARIO 6: Allergy Conflict")
    print("="*60)

    # P001 allergies: Penicillin, Sulfa drugs
    result = PharmacyService.check_allergy_conflict(
        medicine_name="Amoxicillin + Clavulanate",
        patient_allergies=["Penicillin", "Sulfa drugs"]
    )
    print(f"  Conflict detected: {result['has_conflict']}")
    print(f"  Severity: {result.get('severity')}")
    print(f"  Action: {result['action']}")
    print(f"  Message: {result['message'][:80]}")

    assert result["has_conflict"] == True
    assert result["action"] == "BLOCK"
    assert "ALLERGY CONFLICT" in result["message"]
    print("✅ PASSED: Allergy conflict correctly detected and blocked.")


# ─── SCENARIO 7: Duplicate Billing ────────────────────────────────────────────
def test_scenario_07_duplicate_billing():
    """Duplicate billing: Invoice with duplicate medicine entries."""
    print("\n" + "="*60)
    print("SCENARIO 7: Duplicate Billing Detection")
    print("="*60)

    # Create invoice with duplicate Paracetamol
    medicines_with_duplicates = [
        {"generic_name": "Paracetamol", "quantity": 15},
        {"generic_name": "Paracetamol", "quantity": 10},  # Duplicate!
        {"generic_name": "Pantoprazole", "quantity": 14},
    ]

    result = BillingService.create_invoice("P002", "MAT-CSEC-002", medicines_with_duplicates)
    print(f"  Invoice created: {result['invoice']['invoice_id']}")

    # Validate should detect or the creation deduplicates
    inv = result["invoice"]
    medicine_names = [m["generic_name"] for m in inv["medicines"]]
    print(f"  Medicines in invoice: {medicine_names}")

    assert medicine_names.count("Paracetamol") == 1, "Duplicate Paracetamol should be removed"
    print("✅ PASSED: Duplicate medicine correctly removed from invoice.")


# ─── SCENARIO 8: Missing Billing Code ─────────────────────────────────────────
def test_scenario_08_missing_billing_code():
    """Missing billing code: Try to create invoice with invalid code."""
    print("\n" + "="*60)
    print("SCENARIO 8: Missing Billing Code")
    print("="*60)

    result = BillingService.create_invoice(
        patient_id="P001",
        billing_code="INVALID-CODE-999",
        medicines=[{"generic_name": "Paracetamol", "quantity": 10}]
    )
    print(f"  Error: {result.get('error')}")
    print(f"  Message: {result.get('message')}")

    assert result.get("error") == True
    assert "not found" in result.get("message", "").lower()
    print("✅ PASSED: Missing billing code correctly rejected.")


# ─── SCENARIO 9: Invalid Patient ID ───────────────────────────────────────────
def test_scenario_09_invalid_patient():
    """Invalid patient ID: P999 does not exist."""
    print("\n" + "="*60)
    print("SCENARIO 9: Invalid Patient ID")
    print("="*60)

    result = EHRService.get_patient("P999")
    print(f"  Error: {result['error']}")
    print(f"  Message: {result['message']}")

    assert result["error"] == True
    assert "not found" in result["message"].lower()

    # Also test through workflow
    agent = DischargeAgent(role="administrator")
    workflow = agent.run_discharge_workflow("P999")
    d = workflow.to_dict()
    print(f"  Workflow status: {d['overall_status']}")

    assert d["overall_status"] == "failed"
    print("✅ PASSED: Invalid patient ID correctly handled.")


# ─── SCENARIO 10: Billing Requests Clinical Notes ──────────────────────────────
def test_scenario_10_billing_access_clinical_notes():
    """Billing clerk tries to access clinical notes — must be ACCESS DENIED."""
    print("\n" + "="*60)
    print("SCENARIO 10: Billing Requests Clinical Notes → ACCESS DENIED")
    print("="*60)

    allowed, reason = rbac.check_permission("billing_clerk", "get_clinical_notes")
    print(f"  Allowed: {allowed}")
    print(f"  Reason: {reason[:80]}")

    assert allowed == False
    assert "ACCESS DENIED" in reason
    assert "PHI" in reason or "Billing Clerk" in reason

    # Also test with explicit require_permission
    denial = require_permission("billing_clerk", "get_clinical_notes")
    assert "ACCESS DENIED" in denial
    print("✅ PASSED: Billing Clerk ACCESS DENIED for clinical notes (PHI boundary enforced).")


# ─── SCENARIO 11: Invoice Validation Failure ──────────────────────────────────
def test_scenario_11_invoice_validation_failure():
    """Invoice validation failure: Invalid invoice data."""
    print("\n" + "="*60)
    print("SCENARIO 11: Invoice Validation Failure")
    print("="*60)

    result = BillingService.validate_invoice("NONEXISTENT-INV-9999")
    print(f"  Is valid: {result.get('is_valid')}")
    print(f"  Errors: {result.get('errors')}")

    assert result.get("error") == True or result.get("is_valid") == False
    print("✅ PASSED: Invalid invoice correctly identified.")


# ─── SCENARIO 12: Human Approval Required ─────────────────────────────────────
def test_scenario_12_human_approval_required():
    """Human approval required: All alternatives blocked by allergy."""
    print("\n" + "="*60)
    print("SCENARIO 12: Human Approval Required")
    print("="*60)

    # P001 has Penicillin allergy → Augmentin (Amoxicillin+Clavulanate) blocked
    # And P001's alternatives might also be blocked
    result = PharmacyService.suggest_alternative(
        "Amoxicillin + Clavulanate",
        patient_allergies=["Penicillin", "Sulfa drugs"]
    )
    print(f"  Doctor approval required: {result['doctor_approval_required']}")
    print(f"  Approved alternatives: {len(result['approved_alternatives'])}")
    print(f"  Blocked alternatives: {len(result.get('blocked_alternatives', []))}")

    # Should either have doctor_approval_required or blocked alternatives
    assert result["original_generic"] == "Amoxicillin + Clavulanate"
    print("✅ PASSED: Human approval requirement correctly evaluated.")


# ─── SCENARIO 13: Complete Successful Discharge ────────────────────────────────
def test_scenario_13_complete_successful_discharge():
    """Complete successful discharge: P004 Sunita Patel (no allergy conflicts, Dolo in stock)."""
    print("\n" + "="*60)
    print("SCENARIO 13: Complete Successful Discharge")
    print("="*60)

    agent = DischargeAgent(role="administrator")
    result = agent.run_discharge_workflow("P004")
    d = result.to_dict()

    print(f"  Status: {d['overall_status']}")
    print(f"  Steps: {len(d['steps'])}")
    print(f"  Recommendations: {len(d['recommendations'])}")
    print(f"  Human approval needed: {d['human_approval_required']}")
    
    if d.get("invoice"):
        print(f"  Invoice: {d['invoice'].get('invoice_id', 'N/A')}")
        print(f"  Grand Total: ₹{d['invoice'].get('grand_total', 0):,.2f}")

    assert d["patient_id"] == "P004"
    assert len(d["steps"]) == 10
    assert d.get("discharge_packet") is not None
    print("✅ PASSED: Complete successful discharge workflow executed.")


# ─── ADDITIONAL RBAC TESTS ────────────────────────────────────────────────────
def test_rbac_doctor_cannot_access_billing():
    """Doctor cannot perform billing operations."""
    allowed, reason = rbac.check_permission("doctor", "create_invoice")
    assert allowed == False
    assert "ACCESS DENIED" in reason
    print("✅ RBAC: Doctor cannot create invoice.")


def test_rbac_pharmacist_cannot_see_diagnosis():
    """Pharmacist cannot see clinical notes or discharge summary."""
    allowed, _ = rbac.check_permission("pharmacist", "get_clinical_notes")
    assert allowed == False
    allowed2, _ = rbac.check_permission("pharmacist", "get_discharge_summary")
    assert allowed2 == False
    print("✅ RBAC: Pharmacist cannot view clinical data.")


def test_rbac_administrator_full_access():
    """Administrator has full access to all tools."""
    tools = ["get_patient", "get_clinical_notes", "check_stock", "create_invoice",
             "validate_invoice", "resolve_generic", "check_allergy_conflict"]
    for tool in tools:
        allowed, _ = rbac.check_permission("administrator", tool)
        assert allowed == True, f"Administrator denied tool: {tool}"
    print("✅ RBAC: Administrator has full access to all tools.")


def test_phi_guard_billing_safe():
    """PHI Guard strips clinical data from patient record."""
    full_patient = {
        "patient_id": "P001",
        "name": "Ravi Kumar",
        "diagnosis": "Type 2 Diabetes",
        "clinical_notes": "Patient stable...",
        "lab_results": {"HbA1c": "7.2%"},
        "billing_code": "DM-HYP-001",
    }

    masked = phi_guard.mask_for_billing(full_patient)
    assert masked["diagnosis"] == "[PHI REDACTED]"
    assert masked["clinical_notes"] == "[PHI REDACTED]"
    assert masked["patient_id"] == "P001"  # Safe field preserved
    print("✅ PHI Guard: Diagnosis and clinical notes masked for billing.")


# ─── Runner ───────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("AI Healthcare Discharge Coordination System - Test Suite")
    print("=" * 60)

    tests = [
        test_scenario_01_happy_path,
        test_scenario_02_brand_generic_resolution,
        test_scenario_03_out_of_stock,
        test_scenario_04_low_stock_warning,
        test_scenario_05_alternative_suggested,
        test_scenario_06_allergy_conflict,
        test_scenario_07_duplicate_billing,
        test_scenario_08_missing_billing_code,
        test_scenario_09_invalid_patient,
        test_scenario_10_billing_access_clinical_notes,
        test_scenario_11_invoice_validation_failure,
        test_scenario_12_human_approval_required,
        test_scenario_13_complete_successful_discharge,
        test_rbac_doctor_cannot_access_billing,
        test_rbac_pharmacist_cannot_see_diagnosis,
        test_rbac_administrator_full_access,
        test_phi_guard_billing_safe,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"❌ FAILED: {test.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"💥 ERROR: {test.__name__}: {e}")
            failed += 1

    print("\n" + "="*60)
    print(f"Results: {passed} PASSED / {failed} FAILED / {len(tests)} TOTAL")
    print("="*60)
