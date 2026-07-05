<div align="center">
  
# 🏥 AI-Powered Cross-Department Discharge Coordination System

[![Python Version](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-00a393.svg)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Status](https://img.shields.io/badge/Status-Production_Ready-success.svg)]()

*A production-quality healthcare AI system that coordinates patient discharge across EHR, Pharmacy, and Billing departments using advanced AI reasoning and safety constraints.*

---
</div>

## 🌟 Overview

The **Healthcare AI Discharge Management System** automates the historically manual and error-prone hospital discharge process. By employing intelligent autonomous agents, the system orchestrates cross-department workflows, handles brand-to-generic medication conversions, enforces strict allergy safety blocks, and automatically generates accurate, deduped billing invoices.

✨ **New:** We've introduced a stunning, custom-built, responsive Web Dashboard for non-technical hospital staff, complete with dynamic animations and real-time AI reasoning transparency.

---

## 🚀 Quick Start

**Not a developer?** No problem! We have a dedicated, easy-to-read guide for you.  
👉 **[Click here to view the Non-Technical Setup Guide (Start.md)](Start.md)** 👈

For developers, follow these quick steps:

### 1. Install Dependencies
```bash
cd Healthcare_Discharge_System
pip install -r requirements.txt
```

### 2. Run the AI Backend Servers
Start the FastMCP servers (EHR, Pharmacy, Billing) and the FastAPI REST API (port 8000):
```bash
python run_servers.py
```
*(On Windows, run: `$env:PYTHONIOENCODING="utf-8"; python run_servers.py`)*

### 3. Launch the Web Dashboard
In a new terminal window, serve the static web dashboard (port 8080):
```bash
cd web_dashboard
python -m http.server 8080
```
Navigate to `http://localhost:8080` in your browser!

---

## 🎯 Key AI "Golden Scenarios" Handled

Our AI doesn't just pass data around; it *thinks* critically to protect patients.

- 🧬 **Brand-to-Generic Resolution:** Automatically resolves prescribed brands (e.g., *Augmentin*) to their generic equivalents (*Amoxicillin + Clavulanate*) for accurate pharmacy matching.
- 💊 **Out-of-Stock Intelligence:** If a drug is out of stock, the AI intelligently suggests safe clinical alternatives.
- 🚫 **Allergy-Safe Blocking:** Employs cross-tool reasoning to instantly **BLOCK** a discharge if a prescribed medication conflicts with a known patient allergy (e.g., *Penicillin* allergy vs. *Augmentin*).
- 🧾 **Duplicate Billing Prevention:** Validates invoices line-by-line to automatically remove duplicate medication entries before they reach the patient's bill.
- 🔒 **RBAC & PHI Enforcement:** Strict protocol-level access control ensures Billing agents never see sensitive clinical diagnoses.

---

## 🏗️ System Architecture

### FastMCP Server Network
| Server Name | Port | Available AI Tools |
|-------------|------|--------------------|
| 🩺 **EHR MCP** | 8001 | `get_patient`, `get_discharge_summary`, `get_allergies`, `get_clinical_notes` |
| 💊 **Pharmacy MCP** | 8002 | `resolve_generic`, `check_stock`, `suggest_alternative`, `check_allergy_conflict` |
| 💳 **Billing MCP** | 8003 | `get_billing_code`, `create_invoice`, `validate_invoice` |

### REST API Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/patients` | List all 10 synthetic patient records |
| `POST` | `/discharge` | **Triggers the 10-step AI discharge workflow** |
| `GET` | `/audit` | Retrieve JSON audit logs for security compliance |

---

## 🤖 The 10-Step Autonomous Workflow

When a discharge is initiated, the agent autonomously executes the following:
1. **Patient Search & Validation**
2. **EHR Data Extraction**
3. **Medication History Retrieval**
4. **Brand → Generic Semantic Resolution**
5. **Pharmacy Inventory Check**
6. **Alternative Medicine Suggestion** *(if out of stock)*
7. **Allergy Conflict Validation** *(hard block on failure)*
8. **Invoice Generation**
9. **Invoice Safety Validation & Deduplication**
10. **Discharge Packet Generation + Audit Logging**

---

## 🛡️ Security & Privacy

- **Role-Based Access Control (RBAC):** 4 roles (Administrator, Doctor, Pharmacist, Billing Clerk) restrict access to specific tools.
- **PHI Guard:** Automated PHI masking explicitly strips restricted fields before any billing operations are executed.
- **Complete Audit Trail:** Every single tool call, decision, and API request is permanently logged in JSON format for HIPAA-style compliance.

---
<div align="center">
<i>Built for AI-Powered Healthcare Discharge Coordination</i>
</div>
# Project5-v10
