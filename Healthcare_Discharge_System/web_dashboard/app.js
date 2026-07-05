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
    
    resetWorkflowState();
    initiateDischargeBtn.disabled = false;
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
    
    if(downloadPdfBtn) downloadPdfBtn.addEventListener('click', openInvoicePreview);
    if(closeModalBtn) closeModalBtn.addEventListener('click', closeInvoicePreview);
    if(printInvoiceBtn) printInvoiceBtn.addEventListener('click', () => { window.print(); });
    
    window.addEventListener('click', (e) => {
        if (e.target === invoiceModal) closeInvoicePreview();
    });
}

function resetWorkflowState() {
    processingCard.classList.add('hidden');
    successWrapper.classList.add('hidden');
    if(errorWrapper) errorWrapper.classList.add('hidden');
    if(alertsCard) alertsCard.classList.add('hidden');
    initiateDischargeBtn.classList.remove('hidden');
    stepsListEl.innerHTML = '';
    if(alertsList) alertsList.innerHTML = '';
    progressBarFill.style.width = '0%';
    progressText.innerText = '0%';
    document.querySelectorAll('.module-item').forEach(el => el.classList.remove('completed'));
}

async function startDischargeWorkflow() {
    if (!selectedPatient) return;
    
    isProcessing = true;
    initiateDischargeBtn.classList.add('hidden');
    processingCard.classList.remove('hidden');
    
    try {
        const response = await fetch(`${API_URL}/discharge`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                patient_id: selectedPatient.id,
                role: "administrator"
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            await simulateStepRendering(data.workflow);
        } else {
            throw new Error(data.detail || 'Failed to trigger discharge');
        }
    } catch (err) {
        console.error(err);
        showErrorState("Could not connect to the backend server. Is it running?");
    } finally {
        isProcessing = false;
    }
}

async function simulateStepRendering(workflow) {
    const steps = workflow.steps;
    
    for (let i = 0; i < steps.length; i++) {
        const step = steps[i];
        
        // Render step as active
        const item = document.createElement('div');
        item.className = 'step-item active';
        item.id = `step-${i}`;
        
        // Determine step module based on step name
        let moduleName = 'ehr';
        const stepName = (step.name || "").toLowerCase();
        if (stepName.includes('invoice') || stepName.includes('billing')) moduleName = 'billing';
        else if (stepName.includes('stock') || stepName.includes('resolve') || stepName.includes('alternative') || stepName.includes('allergy') || stepName.includes('medication')) moduleName = 'pharmacy';
        else if (stepName.includes('summary') || stepName.includes('packet')) moduleName = 'final';
        
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
            document.getElementById(`status-${moduleName}`).classList.add('completed');
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
    
    setTimeout(() => {
        processingCard.classList.add('hidden');
        
        // Show alerts if any
        if (workflow.alerts && workflow.alerts.length > 0 && alertsCard && alertsList) {
            alertsList.innerHTML = '';
            workflow.alerts.forEach(alert => {
                let color = '#3B82F6'; // blue
                let bgColor = '#EFF6FF';
                let borderColor = '#BFDBFE';
                let icon = `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>`;
                
                if (alert.severity === 'warning') {
                    color = '#D97706'; bgColor = '#FEF3C7'; borderColor = '#FDE68A';
                    icon = `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>`;
                } else if (alert.severity === 'critical' || alert.severity === 'error') {
                    color = '#DC2626'; bgColor = '#FEE2E2'; borderColor = '#FECACA';
                    icon = `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="15" y1="9" x2="9" y2="15"></line><line x1="9" y1="9" x2="15" y2="15"></line></svg>`;
                }

                const alertEl = document.createElement('div');
                alertEl.style = `padding: 12px; background-color: ${bgColor}; border: 1px solid ${borderColor}; border-radius: 6px; color: ${color}; font-size: 0.9rem; display: flex; align-items: flex-start; gap: 8px;`;
                alertEl.innerHTML = `
                    <div style="flex-shrink: 0; margin-top: 2px;">${icon}</div>
                    <div>${alert.message}</div>
                `;
                alertsList.appendChild(alertEl);
            });
            alertsCard.classList.remove('hidden');
        }

        if (workflow.overall_status === 'success') {
            showSuccessState(workflow.invoice);
        } else {
            let errorMsg = workflow.summary || "Discharge process blocked due to safety validations.";
            // If there's an allergy alert, extract it to show specifically
            if (workflow.alerts && workflow.alerts.length > 0) {
                const critical = workflow.alerts.find(a => a.severity === 'critical');
                if (critical) errorMsg = critical.message;
            }
            showErrorState(errorMsg);
        }
    }, 1000);
}

function showSuccessState(invoiceData) {
    successWrapper.classList.remove('hidden');
    currentInvoiceData = invoiceData;
    
    if (invoiceData) {
        invoiceDetails.innerHTML = `
            <div class="invoice-row">
                <span>Invoice Number:</span>
                <strong>${invoiceData.invoice_id}</strong>
            </div>
            <div class="invoice-row">
                <span>Generated:</span>
                <span>${new Date(invoiceData.generated_at).toLocaleString()}</span>
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
    if(!errorWrapper) return; // Fallback if HTML not updated yet
    errorWrapper.classList.remove('hidden');
    errorMessage.innerText = message;
}

function openInvoicePreview() {
    if (!currentInvoiceData) return;
    invoiceModal.classList.remove('hidden');
    
    let itemsHtml = '';
    currentInvoiceData.medicines.forEach(m => {
        itemsHtml += `
            <tr>
                <td>${m.generic_name} (Qty: ${m.quantity})</td>
                <td class="amount">$${(m.total || (m.unit_price * m.quantity) || 0).toFixed(2)}</td>
            </tr>
        `;
    });
    
    // Add base charge and taxes to explain the grand total
    itemsHtml += `
        <tr>
            <td>Room / Base Charge</td>
            <td class="amount">$${(currentInvoiceData.base_charge || 0).toFixed(2)}</td>
        </tr>
        <tr>
            <td>Taxes</td>
            <td class="amount">$${(currentInvoiceData.tax_amount || 0).toFixed(2)}</td>
        </tr>
    `;
    
    invoicePreviewContent.innerHTML = `
        <div class="invoice-preview-header">
            <div>
                <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#2563EB" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-bottom:8px;"><path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>
                <h2 style="margin:0; font-size: 1.25rem;">City General Hospital</h2>
            </div>
            <div class="invoice-meta">
                <div style="font-size: 1.25rem; font-weight: 600; color: #0F172A; margin-bottom: 4px;">INVOICE</div>
                <div>${currentInvoiceData.invoice_id}</div>
                <div>Date: ${new Date(currentInvoiceData.generated_at).toLocaleDateString()}</div>
            </div>
        </div>
        <div style="margin-bottom: 24px;">
            <div style="font-weight: 600; margin-bottom: 8px;">Bill To: Patient ID ${currentInvoiceData.patient_id}</div>
            <div style="color: #64748B;">Diagnosis: ${currentInvoiceData.billing_description || 'N/A'}</div>
        </div>
        <table class="invoice-table">
            <thead>
                <tr>
                    <th>Description</th>
                    <th class="amount">Amount</th>
                </tr>
            </thead>
            <tbody>
                ${itemsHtml}
            </tbody>
            <tfoot>
                <tr>
                    <td style="text-align: right; font-weight: 600; padding: 12px;">Grand Total</td>
                    <td style="text-align: right; font-weight: 600; font-size: 1.1rem; padding: 12px;">$${(currentInvoiceData.grand_total || 0).toFixed(2)}</td>
                </tr>
            </tfoot>
        </table>
    `;
}

function closeInvoicePreview() {
    invoiceModal.classList.add('hidden');
}

// Start
init();
