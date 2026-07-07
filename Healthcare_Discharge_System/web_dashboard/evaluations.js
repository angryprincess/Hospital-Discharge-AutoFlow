const API_URL = 'http://127.0.0.1:8000';

document.addEventListener('DOMContentLoaded', async () => {
    // Parse patient_id from URL
    const urlParams = new URLSearchParams(window.location.search);
    const patientId = urlParams.get('patient_id');

    // Load initial evaluations if patientId is present
    if (patientId) {
        loadEvaluations(patientId);
    } else {
        showErrorState("No patient selected for evaluation. Please select a patient on the dashboard first.");
    }
});

async function loadEvaluations(patientId) {
    // Show loading state
    setLoadingState(true);

    try {
        const response = await fetch(`${API_URL}/api/evaluations?patient_id=${patientId}`);
        const data = await response.json();

        if (response.ok) {
            updateDashboard(data);
        } else {
            console.error("Failed to load evaluations:", data.detail);
            showErrorState(data.detail || "Error loading evaluation metrics.");
        }
    } catch (err) {
        console.error("Network error while loading evaluations:", err);
        showErrorState("Server connection failed. Make sure backend servers are running.");
    } finally {
        setLoadingState(false);
    }
}

function updateDashboard(data) {
    // Update stats strip
    document.getElementById('stat-patient-id').textContent = data.patient_id;
    document.getElementById('stat-exec-time').textContent = `${data.execution_time_ms} ms`;
    document.getElementById('stat-tokens').textContent = data.token_count;
    document.getElementById('lastUpdated').textContent = `Last evaluated: ${new Date().toLocaleTimeString()}`;

    const evals = data.evaluations;

    // AI Agent cells
    updateCell('agent-basic', evals.ai_agent.basic);
    updateCell('agent-middling', evals.ai_agent.middling);
    updateCell('agent-advanced', evals.ai_agent.advanced);

    // MCP Server cells
    updateCell('mcp-basic', evals.mcp_server.basic);
    updateCell('mcp-middling', evals.mcp_server.middling);
    updateCell('mcp-advanced', evals.mcp_server.advanced);

    // Compliance cells
    updateCell('compliance-basic', evals.compliance.basic);
    updateCell('compliance-middling', evals.compliance.middling);
    updateCell('compliance-advanced', evals.compliance.advanced);
}

function updateCell(cellPrefix, metric) {
    const badge = document.getElementById(`${cellPrefix}-badge`);
    const result = document.getElementById(`${cellPrefix}-result`);

    // Set result text
    result.textContent = metric.result;

    // Set badge text
    badge.textContent = metric.status === 'pass' ? 'PASS' : (metric.status === 'warning' ? 'WARN' : 'FAILED');

    // Reset classes
    badge.className = 'eval-cell-badge';

    // Set correct badge design
    if (metric.status === 'pass') {
        badge.classList.add('badge-pass');
    } else if (metric.status === 'warning') {
        badge.classList.add('badge-warning');
    } else {
        badge.classList.add('badge-failed');
    }
}

function setLoadingState(isLoading) {
    const elements = [
        'stat-patient-id', 'stat-exec-time', 'stat-tokens',
        'agent-basic-result', 'agent-middling-result', 'agent-advanced-result',
        'mcp-basic-result', 'mcp-middling-result', 'mcp-advanced-result',
        'compliance-basic-result', 'compliance-middling-result', 'compliance-advanced-result'
    ];

    elements.forEach(id => {
        const el = document.getElementById(id);
        if (el) {
            if (isLoading) {
                el.classList.add('pulse');
                if (id.includes('result') || id.includes('stat')) el.textContent = '...';
            } else {
                el.classList.remove('pulse');
            }
        }
    });
}

function showErrorState(msg) {
    alert(msg);
}
