// Mock Data (still used for patient list population)
const patients = [
    {
        id: "P001",
        name: "Ravi Kumar",
        age: 45,
        ward: "General",
        diagnosis: "Type 2 Diabetes Mellitus with Hypertension",
        treatment: "Patient is stable. Blood sugar levels controlled at 140 mg/dL. BP 130/80. Cleared for discharge with medication.",
        recommendation: "Patient admitted for uncontrolled diabetes. Stabilized with medication adjustment. Follow-up in 2 weeks."
    },
    {
        id: "P002",
        name: "Anita Desai",
        age: 32,
        ward: "Maternity",
        diagnosis: "Post-Cesarean Recovery",
        treatment: "Post-op day 3. Wound healing well. Vitals stable. Breastfeeding initiated.",
        recommendation: "Elective C-section performed. Mother and baby stable. Discharge with antibiotics and analgesics."
    },
    {
        id: "P003",
        name: "Mohammed Salim",
        age: 58,
        ward: "Cardiology",
        diagnosis: "Acute Myocardial Infarction (STEMI)",
        treatment: "Post-PCI day 5. EF 45%. Patient stable. No chest pain. Cardiac rehab initiated.",
        recommendation: "STEMI managed with primary PCI. 2 stents placed. Dual antiplatelet therapy started."
    },
    {
        id: "P004",
        name: "Sunita Patel",
        age: 28,
        ward: "Orthopedics",
        diagnosis: "Fracture Right Femur",
        treatment: "Post-op ORIF right femur. Wound clean. Physiotherapy started. Weight bearing as tolerated.",
        recommendation: "Femur fracture fixed with ORIF. Patient mobilizing with walker. Follow-up in 4 weeks with X-ray."
    },
    {
        id: "P005",
        name: "Arjun Nair",
        age: 67,
        ward: "Neurology",
        diagnosis: "Ischemic Stroke (CVA)",
        treatment: "Ischemic stroke left MCA territory. Partial recovery of speech. Physiotherapy ongoing.",
        recommendation: "CVA with aphasia. Discharged to rehab facility. Follow-up neurology in 1 month."
    },
    {
        id: "P006",
        name: "Priya Reddy",
        age: 41,
        ward: "Pulmonology",
        diagnosis: "Community Acquired Pneumonia",
        treatment: "CAP with consolidation right lower lobe. SpO2 98% on room air. Fever resolved.",
        recommendation: "Pneumonia treated with IV antibiotics switched to oral. Complete recovery expected."
    },
    {
        id: "P007",
        name: "Vikram Singh",
        age: 52,
        ward: "Gastroenterology",
        diagnosis: "Acute Pancreatitis",
        treatment: "Acute pancreatitis secondary to gallstones. Pain controlled. Tolerating oral diet.",
        recommendation: "Pancreatitis managed conservatively. Cholecystectomy planned as elective procedure."
    },
    {
        id: "P008",
        name: "Kavya Sharma",
        age: 19,
        ward: "General",
        diagnosis: "Dengue Fever with Thrombocytopenia",
        treatment: "Dengue NS1 positive. Platelet count recovering. No bleeding manifestations.",
        recommendation: "Dengue fever with mild thrombocytopenia. Platelet 95000/μL at discharge. Follow-up in 3 days."
    },
    {
        id: "P009",
        name: "Rajesh Menon",
        age: 63,
        ward: "Nephrology",
        diagnosis: "Chronic Kidney Disease Stage 3",
        treatment: "CKD Stage 3. eGFR 42 mL/min. Proteinuria 2+. Dietary restrictions counseled.",
        recommendation: "CKD Stage 3 managed medically. Nephrology follow-up monthly. Diet restriction advised."
    },
    {
        id: "P010",
        name: "Lakshmi Iyer",
        age: 35,
        ward: "Endocrinology",
        diagnosis: "Hyperthyroidism (Graves Disease)",
        treatment: "Graves disease confirmed by TSH receptor antibodies. Carbimazole started. Heart rate controlled.",
        recommendation: "Hyperthyroidism managed with antithyroid drugs. TFT monitoring in 6 weeks."
    }
];

// SVG Icons
const icons = {
    pending: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle></svg>`,
    active: `<svg class="spinner" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="2" x2="12" y2="6"></line><line x1="12" y1="18" x2="12" y2="22"></line><line x1="4.93" y1="4.93" x2="7.76" y2="7.76"></line><line x1="16.24" y1="16.24" x2="19.07" y2="19.07"></line><line x1="2" y1="12" x2="6" y2="12"></line><line x1="18" y1="12" x2="22" y2="12"></line><line x1="4.93" y1="19.07" x2="7.76" y2="16.24"></line><line x1="16.24" y1="7.76" x2="19.07" y2="4.93"></line></svg>`,
    completed: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>`,
    failed: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#EF4444" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="15" y1="9" x2="9" y2="15"></line><line x1="9" y1="9" x2="15" y2="15"></line></svg>`
};

// DOM Elements
const patientListEl = document.getElementById('patientList');
const searchInput = document.getElementById('searchInput');
const searchBtn = document.getElementById('searchBtn');
const notesContent = document.getElementById('notesContent');
const initiateDischargeBtn = document.getElementById('initiateDischargeBtn');

const doctorNotesCard = document.getElementById('doctorNotesCard');
const processingCard = document.getElementById('processingCard');
const stepsListEl = document.getElementById('stepsList');
const progressBarFill = document.getElementById('progressBarFill');
const progressText = document.getElementById('progressText');

const successWrapper = document.getElementById('successWrapper');
const successMessageCard = document.getElementById('successMessageCard');
const errorWrapper = document.getElementById('errorWrapper');
const errorMessage = document.getElementById('errorMessage');
const invoiceDetails = document.getElementById('invoiceDetails');

const alertsCard = document.getElementById('alertsCard');
const alertsList = document.getElementById('alertsList');

const invoiceModal = document.getElementById('invoiceModal');
const closeModalBtn = document.getElementById('closeModalBtn');
const downloadPdfBtn = document.getElementById('downloadPdfBtn');
const printInvoiceBtn = document.getElementById('printInvoiceBtn');
const invoicePreviewContent = document.getElementById('invoicePreviewContent');

let selectedPatient = null;
let isProcessing = false;
let currentInvoiceData = null;

// API Config
const API_URL = 'http://127.0.0.1:8000';

// Initialization
function init() {
    renderPatients(patients);
    setupEventListeners();
}

function renderPatients(patientData) {
    patientListEl.innerHTML = '';
    patientData.forEach(p => {
        const row = document.createElement('div');
        row.className = 'patient-row';
        row.dataset.id = p.id;
        row.innerHTML = `
            <div class="patient-id">${p.id}</div>
            <div class="patient-name">${p.name}</div>
            <div class="patient-details">
                <span>Age: ${p.age}</span> • <span>${p.ward}</span>
            </div>
        `;
        row.addEventListener('click', () => selectPatient(p, row));
        patientListEl.appendChild(row);
    });
}

function selectPatient(patient, rowElement) {
    if (isProcessing) return; // Prevent selection during processing

    document.querySelectorAll('.patient-row').forEach(r => r.classList.remove('selected'));
    rowElement.classList.add('selected');

    selectedPatient = patient;

    notesContent.classList.remove('empty-state');
    notesContent.innerHTML = `
        <div class="note-section" style="border-bottom: 1px solid #E2E8F0; padding-bottom: 12px; margin-bottom: 16px;">
            <h3 style="color: #0F172A; font-size: 1.1rem; text-transform: none; margin-bottom: 4px;">${patient.name}</h3>
            <div style="font-size: 0.85rem; color: #64748B;">ID: ${patient.id} • Age: ${patient.age} Years</div>
        </div>
        <div class="note-section">
            <h3>Diagnosis</h3>
            <p>${patient.diagnosis}</p>
        </div>
        <div class="note-section">
            <h3>Treatment Summary</h3>
            <p>${patient.treatment}</p>
        </div>
        <div class="note-section">
            <h3>Doctor Recommendation</h3>
            <p>${patient.recommendation}</p>
        </div>
    `;

    doctorNotesCard.classList.remove('hidden');

    resetWorkflowState();
    initiateDischargeBtn.disabled = false;
    initiateDischargeBtn.innerText = "Initiate Discharge";
}

function searchPatients() {
    const query = searchInput.value.toLowerCase();
    const filtered = patients.filter(p =>
        p.id.toLowerCase().includes(query) ||
        p.name.toLowerCase().includes(query)
    );
    renderPatients(filtered);
}

function setupEventListeners() {
    searchBtn.addEventListener('click', searchPatients);
    searchInput.addEventListener('keyup', (e) => {
        if (e.key === 'Enter') searchPatients();
    });

    initiateDischargeBtn.addEventListener('click', startDischargeWorkflow);

    if (downloadPdfBtn) downloadPdfBtn.addEventListener('click', openInvoicePreview);
    if (closeModalBtn) closeModalBtn.addEventListener('click', closeInvoicePreview);
    if (printInvoiceBtn) printInvoiceBtn.addEventListener('click', () => { window.print(); });

    window.addEventListener('click', (e) => {
        if (e.target === invoiceModal) closeInvoicePreview();
    });
}

function resetWorkflowState() {

    stepsListEl.innerHTML = "";

    progressBarFill.style.width = "0%";
    progressText.innerText = "0%";

    processingCard.classList.add("hidden");

    successWrapper.classList.add("hidden");
    if (successMessageCard) successMessageCard.classList.add("hidden");

    errorWrapper.classList.add("hidden");

    const evalsFooter = document.getElementById('evalsFooter');
    if (evalsFooter) evalsFooter.classList.add('hidden');

    alertsCard.classList.add("hidden");

    alertsList.innerHTML = "";

    document.querySelectorAll(".module-item").forEach(item => {
        item.classList.remove("completed");
    });

    document.querySelectorAll('.server-card').forEach(c => c.classList.remove('server-active'));
}

async function startDischargeWorkflow() {
    if (!selectedPatient) return;

    isProcessing = true;

    initiateDischargeBtn.disabled = true;
    initiateDischargeBtn.innerText = "Processing...";

    resetWorkflowState();

    processingCard.classList.remove("hidden");

    try {
        const response = await fetch(`${API_URL}/discharge`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                patient_id: selectedPatient.id,
                role: "administrator"
            })
        });

        const data = await response.json();

        console.log("API Response:", data);

        if (!response.ok) {
            throw new Error(data.detail || "Backend Error");
        }

        // Support both response formats
        const workflow = data.workflow ? data.workflow : data;
        console.log("Workflow Object:", workflow);
        console.log("Workflow Keys:", Object.keys(workflow));

        console.log("Steps:", workflow.steps);
        console.log("Total Steps:", workflow.steps ? workflow.steps.length : 0);

        if (workflow.steps) {
            workflow.steps.forEach((step, index) => {
                console.log(`Step ${index + 1}:`, step);
            });
        }

        await simulateStepRendering(workflow);

    } catch (err) {
        console.error(err);

        processingCard.classList.add("hidden");

        showErrorState(err.message || "Unable to connect to backend.");
    }
    finally {
        isProcessing = false;
        initiateDischargeBtn.disabled = false;
        initiateDischargeBtn.innerText = "Initiate Discharge";
    }
}

async function simulateStepRendering(workflow) {
    processingCard.classList.remove("hidden");

    stepsListEl.innerHTML = "";

    const steps = workflow.steps;

    for (let i = 0; i < steps.length; i++) {
        const step = steps[i];

        // Render step as active
        const item = document.createElement('div');
        item.className = 'step-item active';
        item.id = `step-${i}`;

        // Determine step module based on step name
        let moduleName = 'verification';
        const stepName = (step.name || "").toLowerCase();
        if (stepName.includes('invoice') || stepName.includes('billing')) moduleName = 'billing';
        else if (stepName.includes('stock') || stepName.includes('resolve') || stepName.includes('alternative') || stepName.includes('allergy') || stepName.includes('medication') || stepName.includes('pharmacy')) moduleName = 'pharmacy';
        else if (stepName.includes('summary') || stepName.includes('packet') || stepName.includes('final')) moduleName = 'final';
        else if (stepName.includes('ehr') || stepName.includes('record') || stepName.includes('read')) moduleName = 'records';

        // Update MCP server blinking
        document.querySelectorAll('.server-card').forEach(c => c.classList.remove('server-active'));
        if (moduleName === 'verification' || moduleName === 'records') {
            document.getElementById('mcp-ehr')?.classList.add('server-active');
        } else if (moduleName === 'pharmacy') {
            document.getElementById('mcp-pharmacy')?.classList.add('server-active');
        } else if (moduleName === 'billing' || moduleName === 'final') {
            document.getElementById('mcp-billing')?.classList.add('server-active');
        }

        item.innerHTML = `
            <div class="step-icon active" id="step-icon-${i}">
                ${icons.active}
            </div>
            <div class="step-name">${step.name}</div>
            <div class="step-time" id="step-time-${i}">Processing...</div>
            <div style="font-size: 0.8rem; color: #64748B; margin-top: 4px;">${step.message || ""}</div>
        `;
        stepsListEl.appendChild(item);
        item.scrollIntoView({ behavior: 'smooth', block: 'nearest' });

        // Artificial delay for UI effect
        await new Promise(r => setTimeout(r, 600));

        // Update step status based on backend response
        const iconEl = document.getElementById(`step-icon-${i}`);
        const timeEl = document.getElementById(`step-time-${i}`);
        item.classList.remove('active');

        if (step.status === 'completed' || step.status === 'success') {
            item.classList.add('completed');
            iconEl.className = 'step-icon completed';
            iconEl.innerHTML = icons.completed;
            document.getElementById(`status-${moduleName}`)?.classList.add('completed');
        } else {
            iconEl.className = 'step-icon failed';
            iconEl.innerHTML = icons.failed;
        }
        timeEl.innerText = new Date(step.timestamp || Date.now()).toLocaleTimeString();

        // Update Progress
        const progress = Math.round(((i + 1) / steps.length) * 100);
        progressBarFill.style.width = `${progress}%`;
        progressText.innerText = `${progress}%`;

        // Stop if a step fails
        if (step.status === 'failed' || step.status === 'blocked') {
            break;
        }
    }

    // Clear active server blinking after processing finishes
    document.querySelectorAll('.server-card').forEach(c => c.classList.remove('server-active'));

    setTimeout(() => {

        if (workflow.alerts && workflow.alerts.length) {

            alertsList.innerHTML = "";

            workflow.alerts.forEach(alert => {

                const div = document.createElement("div");

                div.className = "alert-item";

                div.innerHTML = alert.message;

                alertsList.appendChild(div);

            });

            alertsCard.classList.remove("hidden");
        }

        if (workflow.overall_status === "success") {

            showSuccessState(workflow.invoice);

        } else {

            showErrorState(workflow.summary || "Workflow Failed");

        }

        const evalsFooter = document.getElementById('evalsFooter');
        if (evalsFooter) {
            evalsFooter.classList.remove('hidden');
        }
    }, 800);
}

function showSuccessState(invoiceData) {
    successWrapper.classList.remove('hidden');
    if (successMessageCard) successMessageCard.classList.remove('hidden');
    currentInvoiceData = invoiceData;

    if (invoiceData) {
        invoiceDetails.innerHTML = `
            <div class="invoice-row">
                <span>Invoice Number:</span>
                <strong>${invoiceData.invoice_id}</strong>
            </div>
            <div class="invoice-row">
                <span>Generated:</span>
                <span>${invoiceData.generated_at
                ? new Date(invoiceData.generated_at).toLocaleString()
                : new Date().toLocaleString()
            }</span>
            </div>
            <div class="invoice-row total">
                <span>Total Amount:</span>
                <span>$${invoiceData.grand_total.toFixed(2)}</span>
            </div>
        `;
    } else {
        invoiceDetails.innerHTML = "<p>No invoice data available.</p>";
    }
}

function showErrorState(message) {
    if (!errorWrapper) return; // Fallback if HTML not updated yet
    errorWrapper.classList.remove('hidden');
    errorMessage.innerText = message;
}

function numberToWords(amount) {
    // Very simple approximation for demo purposes
    if (amount > 9000) return "Nine Thousand One Hundred Eighty Seven and Fifty Paise";
    return amount.toString();
}

function formatDateFull(dateString) {
    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    return new Date(dateString).toLocaleDateString('en-US', options);
}

function formatTime(dateString) {
    const options = { hour: '2-digit', minute: '2-digit', hour12: true };
    return new Date(dateString).toLocaleTimeString('en-US', options);
}

function openInvoicePreview() {
    if (!currentInvoiceData) return;
    invoiceModal.classList.remove('hidden');

    const generatedDate = currentInvoiceData.generated_at ? new Date(currentInvoiceData.generated_at) : new Date();
    const dateOnly = formatDateFull(generatedDate);
    const timeOnly = formatTime(generatedDate);

    // Calculate values
    const roomRent = currentInvoiceData.base_charge || 4200.00;
    const taxes = currentInvoiceData.tax_amount || 437.50;
    const subTotal = currentInvoiceData.grand_total - taxes;

    let medsHtml = '';
    currentInvoiceData.medicines.forEach((m, index) => {
        medsHtml += `
            <tr style="border-bottom: 1px solid #cbd5e1; background: white;">
                <td style="padding: 8px; border-right: 1px solid #cbd5e1; text-align: center;">${index + 1}</td>
                <td style="padding: 8px; border-right: 1px solid #cbd5e1; text-align: left;">${m.generic_name}</td>
                <td style="padding: 8px; border-right: 1px solid #cbd5e1; text-align: center;">${m.quantity}</td>
                <td style="padding: 8px; border-right: 1px solid #cbd5e1; text-align: right;">${(m.unit_price || (m.total / m.quantity)).toFixed(2)}</td>
                <td style="padding: 8px; text-align: right;">${(m.total || (m.unit_price * m.quantity)).toFixed(2)}</td>
            </tr>
        `;
    });

    const baseMedCount = currentInvoiceData.medicines.length;

    invoicePreviewContent.innerHTML = `
    <div style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #1e3a8a; background: white; line-height: 1.4;">
        <!-- Header -->
        <div style="display: flex; justify-content: space-between; border-bottom: 2px solid #1e3a8a; padding-bottom: 8px; margin-bottom: 10px;">
            <div>
                <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 8px;">
                    <div style="background: #1e3a8a; color: white; width: 40px; height: 40px; display: flex; align-items: center; justify-content: center; font-size: 28px; font-weight: bold; border-radius: 4px;">+</div>
                    <div>
                        <h1 style="margin: 0; font-size: 1.8rem; color: #1e3a8a; letter-spacing: 1px;">CITY GENERAL HOSPITAL</h1>
                        <p style="margin: 0; font-size: 0.95rem; color: #0ea5e9;">Compassionate Care, Advanced Technology</p>
                    </div>
                </div>
                <div style="font-size: 0.8rem; color: #334155; display: grid; grid-template-columns: 1fr 1fr; gap: 16px;">
                     <div>
                        <div style="display: flex; gap: 8px;"><span style="color:#1e3a8a;">📍</span> 123 Health Street, Medical District<br>Mumbai - 400001, Maharashtra, India</div>
                     </div>
                     <div>
                         <div style="display: flex; gap: 8px; margin-bottom: 2px;"><span style="color:#1e3a8a;">📞</span> +91 22 1234 5678</div>
                         <div style="display: flex; gap: 8px; margin-bottom: 2px;"><span style="color:#1e3a8a;">✉️</span> billing@citygeneralhospital.com</div>
                         <div style="display: flex; gap: 8px;"><span style="color:#1e3a8a;">🌐</span> www.citygeneralhospital.com</div>
                     </div>
                </div>
            </div>
            <div style="text-align: right; width: 220px;">
                <h1 style="margin: 0; font-size: 2rem; color: #1e3a8a; letter-spacing: 1px;">INVOICE</h1>
                <p style="margin: 0; font-size: 0.85rem; color: #334155; margin-bottom: 8px;">Original for Recipient</p>
                <div style="background: #1e3a8a; color: white; padding: 4px; font-weight: bold; font-size: 0.85rem; text-align: center;">Invoice No.</div>
                <div style="font-weight: bold; font-size: 1rem; padding: 4px; color: #0f172a; text-align: center; border-bottom: 1px solid #e2e8f0; margin-bottom: 8px;">${currentInvoiceData.invoice_id}</div>
                <div style="font-size: 0.8rem; color: #334155; display: flex; align-items: flex-start; gap: 6px; justify-content: flex-end;">
                    <span style="color:#1e3a8a;">📅</span> 
                    <div style="text-align: left;">
                        Generated On<br>
                        <span style="color: #0f172a; font-weight: 500;">${dateOnly} | ${timeOnly}</span>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Patient & Visit Details -->
        <div style="display: flex; gap: 16px; margin-bottom: 16px;">
            <!-- BILL TO -->
            <div style="flex: 1; border: 1px solid #cbd5e1; border-radius: 6px; padding: 12px; background: #f8fafc;">
                <h3 style="margin: 0 0 12px 0; font-size: 1.05rem; color: #1e3a8a; display: flex; align-items: center; gap: 8px;">
                    📄 BILL TO
                </h3>
                <table style="width: 100%; font-size: 0.9rem; color: #0f172a; line-height: 1.6;">
                    <tr><td style="font-weight: 600; width: 35%;">Patient ID</td><td>: ${selectedPatient.id}</td></tr>
                    <tr><td style="font-weight: 600;">Patient Name</td><td>: ${selectedPatient.name}</td></tr>
                    <tr><td style="font-weight: 600;">Age / Gender</td><td>: ${selectedPatient.age} Years</td></tr>
                    <tr><td style="font-weight: 600;">Contact No.</td><td>: +91 98765 43210</td></tr>
                    <tr><td style="font-weight: 600; vertical-align: top;">Address</td><td>: 12, Green Park Society,<br>&nbsp; Andheri (E), Mumbai - 400069</td></tr>
                </table>
            </div>
            <!-- VISIT & DIAGNOSIS DETAILS -->
            <div style="flex: 1; border: 1px solid #cbd5e1; border-radius: 6px; padding: 12px; background: #f8fafc;">
                <h3 style="margin: 0 0 12px 0; font-size: 1.05rem; color: #1e3a8a; display: flex; align-items: center; gap: 8px;">
                    👤 VISIT & DIAGNOSIS DETAILS
                </h3>
                <table style="width: 100%; font-size: 0.9rem; color: #0f172a; line-height: 1.6;">
                    <tr><td style="font-weight: 600; width: 40%;">Visit ID</td><td>: VIS-2026-${selectedPatient.id.replace('P', '')}</td></tr>
                    <tr><td style="font-weight: 600;">Admission Date</td><td>: May 12, 2026</td></tr>
                    <tr><td style="font-weight: 600;">Discharge Date</td><td>: ${dateOnly}</td></tr>
                    <tr><td style="font-weight: 600;">Department</td><td>: ${selectedPatient.ward}</td></tr>

                    <tr><td style="font-weight: 600;">Consultant</td><td>: Dr. A. Sharma (MD)</td></tr>
                </table>
            </div>
        </div>
        
        <!-- Table -->
        <div style="border: 1px solid #cbd5e1; overflow: hidden; margin-bottom: 16px;">
            <div style="background: #1e3a8a; color: white; padding: 10px 12px; font-weight: bold; font-size: 1.05rem;">INVOICE DETAILS</div>
            <table style="width: 100%; border-collapse: collapse; font-size: 0.9rem; color: #0f172a;">
                <tr style="border-bottom: 1px solid #cbd5e1; font-weight: bold; background: white;">
                    <td style="padding: 10px; border-right: 1px solid #cbd5e1; width: 8%; text-align: center;">Sr. No.</td>
                    <td style="padding: 10px; border-right: 1px solid #cbd5e1; text-align: left;">Description</td>
                    <td style="padding: 10px; border-right: 1px solid #cbd5e1; width: 12%; text-align: center;">Quantity</td>
                    <td style="padding: 10px; border-right: 1px solid #cbd5e1; width: 18%; text-align: center;">Unit Price (₹)</td>
                    <td style="padding: 10px; width: 18%; text-align: center;">Amount (₹)</td>
                </tr>
                
                <tr style="background: #e0f2fe; font-weight: bold; text-align: left;">
                    <td colspan="5" style="padding: 6px 12px; border-bottom: 1px solid #cbd5e1; color: #1e3a8a;">A. MEDICATIONS</td>
                </tr>
                ${medsHtml}

                <tr style="background: #e0f2fe; font-weight: bold; text-align: left;">
                    <td colspan="5" style="padding: 6px 12px; border-bottom: 1px solid #cbd5e1; color: #1e3a8a;">B. SERVICES & PROCEDURES</td>
                </tr>
                <tr style="border-bottom: 1px solid #cbd5e1; background: white;">
                    <td style="padding: 8px; border-right: 1px solid #cbd5e1; text-align: center;">${baseMedCount + 1}</td>
                    <td style="padding: 8px; border-right: 1px solid #cbd5e1; text-align: left;">Room Rent (${selectedPatient.ward} Ward)</td>
                    <td style="padding: 8px; border-right: 1px solid #cbd5e1; text-align: center;">1</td>
                    <td style="padding: 8px; border-right: 1px solid #cbd5e1; text-align: right;">${roomRent.toFixed(2)}</td>
                    <td style="padding: 8px; text-align: right;">${roomRent.toFixed(2)}</td>
                </tr>
                <tr style="border-bottom: 1px solid #cbd5e1; background: white;">
                    <td style="padding: 8px; border-right: 1px solid #cbd5e1; text-align: center;">${baseMedCount + 2}</td>
                    <td style="padding: 8px; border-right: 1px solid #cbd5e1; text-align: left;">Consultant Visit Charges</td>
                    <td style="padding: 8px; border-right: 1px solid #cbd5e1; text-align: center;">2</td>
                    <td style="padding: 8px; border-right: 1px solid #cbd5e1; text-align: right;">500.00</td>
                    <td style="padding: 8px; text-align: right;">1000.00</td>
                </tr>

                <!-- Totals Row -->
                <tr style="background: white;">
                    <td colspan="2" rowspan="5" style="padding: 16px; border-right: 1px solid #cbd5e1; text-align: left; vertical-align: bottom;">
                    </td>
                    <td colspan="2" style="padding: 8px; border-right: 1px solid #cbd5e1; border-bottom: 1px solid #cbd5e1; text-align: left;">Sub Total</td>
                    <td style="padding: 8px; border-bottom: 1px solid #cbd5e1; font-weight: bold; text-align: right;">₹ ${(subTotal + 1000).toFixed(2)}</td>
                </tr>
                <tr style="background: white;">
                    <td colspan="2" style="padding: 8px; border-right: 1px solid #cbd5e1; border-bottom: 1px solid #cbd5e1; text-align: left;">Discount</td>
                    <td style="padding: 8px; border-bottom: 1px solid #cbd5e1; font-weight: bold; text-align: right;">₹ 0.00</td>
                </tr>
                <tr style="background: white;">
                    <td colspan="2" style="padding: 8px; border-right: 1px solid #cbd5e1; border-bottom: 1px solid #cbd5e1; text-align: left;">Taxable Amount</td>
                    <td style="padding: 8px; border-bottom: 1px solid #cbd5e1; font-weight: bold; text-align: right;">₹ ${(subTotal + 1000).toFixed(2)}</td>
                </tr>
                <tr style="background: white;">
                    <td colspan="2" style="padding: 8px; border-right: 1px solid #cbd5e1; border-bottom: 1px solid #cbd5e1; text-align: left;">CGST & SGST</td>
                    <td style="padding: 8px; border-bottom: 1px solid #cbd5e1; font-weight: bold; text-align: right;">₹ ${taxes.toFixed(2)}</td>
                </tr>
                <tr style="background: #1e3a8a; color: white; font-weight: bold; font-size: 1.1rem;">
                    <td colspan="2" style="padding: 12px; border-right: 1px solid #cbd5e1; text-align: left;">GRAND TOTAL</td>
                    <td style="padding: 12px; text-align: right;">₹ ${(currentInvoiceData.grand_total + 1000).toFixed(2)}</td>
                </tr>
            </table>
        </div>

        <!-- Footer Info -->
        <div style="display: flex; justify-content: flex-start; align-items: center; border-top: 1px solid #cbd5e1; border-bottom: 1px solid #cbd5e1; padding: 12px 0; margin-bottom: 16px; font-size: 0.85rem; color: #0f172a; background: white;">
            <div style="display: flex; align-items: flex-start; gap: 12px; width: 40%;">
                <div style="font-size: 2rem; color: #1e3a8a;">💳</div>
                <div>
                    <div style="font-weight: 600; color: #1e3a8a; margin-bottom: 4px;">PAYMENT MODE</div>
                    <div style="color: #334155;">Cash / Card / UPI<br>Net Banking</div>
                </div>
            </div>
            <div style="display: flex; align-items: flex-start; gap: 12px; width: 60%; border-left: 1px solid #cbd5e1; padding-left: 16px;">
                <div style="font-size: 2rem; color: #1e3a8a;">ℹ️</div>
                <div>
                    <div style="font-weight: 600; color: #1e3a8a; margin-bottom: 4px;">NOTE</div>
                    <div style="color: #334155;">This is a computer generated invoice and does not require a physical signature.</div>
                </div>
            </div>
        </div>

        <div style="display: flex; justify-content: space-between; align-items: flex-end; font-size: 0.95rem; color: #1e3a8a; padding-bottom: 24px; background: white;">
            <div>
                <div>Thank you for choosing City General Hospital.</div>
                <div style="font-weight: 600;">We wish you good health!</div>
            </div>
            <div style="text-align: center;">
                <div style="font-family: 'Brush Script MT', cursive, serif; font-size: 2rem; margin-bottom: 4px; color: #1e3a8a;">Anurag Sharma</div>
                <div style="font-weight: 600; color: #0f172a;">Authorized Signatory</div>
                <div style="font-size: 0.85rem; color: #64748b;">Billing Department</div>
            </div>
        </div>
    </div>
    `;
}

function closeInvoicePreview() {
    invoiceModal.classList.add('hidden');
}

// Start
init();

// Redirection handler for Evaluations (Tech) page
const goToEvalsBtn = document.getElementById('goToEvalsBtn');
if (goToEvalsBtn) {
    goToEvalsBtn.addEventListener('click', () => {
        if (selectedPatient) {
            window.location.href = `evaluations.html?patient_id=${selectedPatient.id}`;
        } else {
            window.location.href = `evaluations.html`;
        }
    });
}
