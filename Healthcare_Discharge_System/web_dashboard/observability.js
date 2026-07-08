const API_URL = 'http://127.0.0.1:8000';

document.addEventListener('DOMContentLoaded', () => {
    // Parse patient_id from URL
    const urlParams = new URLSearchParams(window.location.search);
    const patientId = urlParams.get('patient_id');

    // Update back button href
    const backBtn = document.getElementById('back-btn');
    if (backBtn) {
        if (patientId) {
            backBtn.href = `evaluations.html?patient_id=${patientId}`;
        } else {
            backBtn.href = `evaluations.html`;
        }
    }

    // Load metrics immediately and set interval for polling
    fetchTelemetry();
    const intervalId = setInterval(fetchTelemetry, 2000);

    // Set refresh button listener
    const refreshBtn = document.getElementById('refreshBtn');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', () => {
            fetchTelemetry();
        });
    }
});

async function fetchTelemetry() {
    const lastUpdatedEl = document.getElementById('lastUpdated');
    try {
        const response = await fetch(`${API_URL}/api/telemetry`);
        const data = await response.json();

        if (response.ok) {
            updateTelemetryTable(data);
            lastUpdatedEl.textContent = `Last updated: ${new Date().toLocaleTimeString()}`;
        } else {
            lastUpdatedEl.textContent = 'Error fetching telemetry';
            console.error('Failed to fetch telemetry data:', data);
        }
    } catch (err) {
        lastUpdatedEl.textContent = 'Server connection failed';
        console.error('Connection error while fetching telemetry:', err);
    }
}

function updateTelemetryTable(telemetry) {
    const servers = ['EHR', 'Pharmacy', 'Billing'];
    let totalConcurrency = 0;
    let latencySum = 0;
    let latencyCount = 0;
    let totalRequests = 0;

    servers.forEach(server => {
        const serverLower = server.toLowerCase();
        const metrics = telemetry[server];

        if (!metrics) return;

        // Accumulate summaries
        totalConcurrency += metrics.active_concurrency;
        if (metrics.total_requests > 0) {
            latencySum += metrics.latency_avg_ms;
            latencyCount++;
        }
        totalRequests += metrics.total_requests;

        // Latency avg
        const avgLatEl = document.getElementById(`${serverLower}-latency-avg`);
        if (avgLatEl) {
            avgLatEl.textContent = metrics.total_requests > 0 ? `${metrics.latency_avg_ms.toFixed(2)} ms` : 'No data';
        }

        // Latency range
        const rangeLatEl = document.getElementById(`${serverLower}-latency-range`);
        if (rangeLatEl) {
            rangeLatEl.textContent = metrics.total_requests > 0 
                ? `Min: ${metrics.latency_min_ms.toFixed(1)} ms / Max: ${metrics.latency_max_ms.toFixed(1)} ms`
                : 'Range: N/A';
        }

        // Errors & Error Rate
        const errorsEl = document.getElementById(`${serverLower}-errors`);
        if (errorsEl) {
            errorsEl.textContent = `${metrics.failed_requests} failed / ${metrics.total_requests} total`;
        }

        const rateEl = document.getElementById(`${serverLower}-error-rate`);
        if (rateEl) {
            const errorRate = metrics.total_requests > 0 ? (metrics.failed_requests / metrics.total_requests) * 100 : 0.0;
            rateEl.textContent = `Error rate: ${errorRate.toFixed(1)}%`;
            if (errorRate > 0) {
                rateEl.style.color = 'var(--warning)';
                rateEl.style.fontWeight = '600';
            } else {
                rateEl.style.color = 'var(--text-muted)';
                rateEl.style.fontWeight = '500';
            }
        }

        // Concurrency
        const concurrencyEl = document.getElementById(`${serverLower}-concurrency`);
        if (concurrencyEl) {
            concurrencyEl.textContent = `${metrics.active_concurrency} active`;
        }

        const peakEl = document.getElementById(`${serverLower}-concurrency-peak`);
        if (peakEl) {
            peakEl.textContent = `Peak concurrency: ${metrics.max_concurrency}`;
        }

        // Resource usage (Memory & CPU)
        const memoryEl = document.getElementById(`${serverLower}-memory`);
        if (memoryEl) {
            memoryEl.textContent = `${metrics.memory_mb.toFixed(1)} MB`;
        }

        const cpuEl = document.getElementById(`${serverLower}-cpu`);
        if (cpuEl) {
            cpuEl.textContent = `CPU utilization: ${metrics.cpu_percent.toFixed(2)}%`;
        }

        // Memory bar indicator (base max is set to 100MB for visual scale)
        const memBarFill = document.getElementById(`${serverLower}-mem-bar`);
        if (memBarFill) {
            const percentage = Math.min(100, (metrics.memory_mb / 100) * 100);
            memBarFill.style.width = `${percentage}%`;
            // Color indicator based on memory size
            if (metrics.memory_mb > 80.0) {
                memBarFill.style.backgroundColor = '#EF4444'; // Red for potential leak / high memory
            } else if (metrics.memory_mb > 55.0) {
                memBarFill.style.backgroundColor = 'var(--warning)'; // Yellow for moderate memory
            } else {
                memBarFill.style.backgroundColor = 'var(--primary)'; // Blue for healthy
            }
        }
    });

    // Update global strip cards
    document.getElementById('stat-total-concurrency').textContent = totalConcurrency;
    
    const avgLatencyEl = document.getElementById('stat-avg-latency');
    if (latencyCount > 0) {
        avgLatencyEl.textContent = `${(latencySum / latencyCount).toFixed(1)} ms`;
    } else {
        avgLatencyEl.textContent = '0 ms';
    }

    document.getElementById('stat-total-requests').textContent = totalRequests;
}
