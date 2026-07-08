const API_URL = 'http://127.0.0.1:8000';

document.addEventListener('DOMContentLoaded', () => {
    const urlParams = new URLSearchParams(window.location.search);
    const patientId = urlParams.get('patient_id');

    if (!patientId) {
        document.getElementById('stream-output').textContent = 'Error: No patient ID provided.';
        document.getElementById('stream-status-text').textContent = 'Stream Failed';
        const dot = document.getElementById('stream-status-dot');
        dot.className = 'pulse-dot error';
        return;
    }

    // Set up Back Button
    const backBtn = document.getElementById('back-btn');
    backBtn.href = `evaluations.html?patient_id=${patientId}`;
    
    // Set Patient ID
    document.getElementById('patient-id-val').textContent = patientId;

    // Start streaming
    startStreaming(patientId);
});

function startStreaming(patientId) {
    const outputEl = document.getElementById('stream-output');
    const statusTextEl = document.getElementById('stream-status-text');
    const statusDotEl = document.getElementById('stream-status-dot');

    outputEl.textContent = ''; // clear initial text

    const eventSource = new EventSource(`${API_URL}/api/stream-judge?patient_id=${patientId}`);

    eventSource.onopen = () => {
        statusTextEl.textContent = 'Streaming Judge Reasoning...';
    };

    eventSource.onmessage = (event) => {
        try {
            const data = JSON.parse(event.data);
            if (data.chunk) {
                // If it contains the stream completed signal
                if (data.chunk.includes('[Stream Completed successfully]')) {
                    statusTextEl.textContent = 'Evaluation Completed';
                    statusDotEl.className = 'pulse-dot completed';
                    eventSource.close();
                }
                
                // Append text
                outputEl.textContent += data.chunk;
                
                // Auto scroll to bottom
                const panel = document.querySelector('.stream-panel');
                panel.scrollTop = panel.scrollHeight;
            }
        } catch (err) {
            console.error('Error parsing SSE data:', err);
        }
    };

    eventSource.onerror = (err) => {
        console.error('SSE connection error:', err);
        // Only show error if the stream hasn't completed
        if (statusTextEl.textContent !== 'Evaluation Completed') {
            statusTextEl.textContent = 'Connection Error / Stream Completed';
            statusDotEl.className = 'pulse-dot error';
        }
        eventSource.close();
    };
}
