const API_BASE_URL = window.location.origin.includes('8000') 
    ? window.location.origin
    : "http://localhost:8000";

const IP_MAPPING = {
    "Local Author": "192.168.1.10",
    "Local Publisher": "192.168.1.11",
    "Dev Author": "192.168.1.12",
    "Dev Publisher": "192.168.1.13",
    "Stage Author": "192.168.1.14",
    "Stage Publisher": "192.168.1.15"
};

document.addEventListener('DOMContentLoaded', () => {
    const serverSelect = document.getElementById('server_id');
    const ipInput = document.getElementById('ip_address');
    
    // IP auto-fill listener
    serverSelect.addEventListener('change', (e) => {
        const selectedServer = e.target.value;
        if (IP_MAPPING[selectedServer]) {
            ipInput.value = IP_MAPPING[selectedServer];
        }
    });

    // Ensure initial state is populated if applicable
    if(IP_MAPPING[serverSelect.value] && !ipInput.value) {
        ipInput.value = IP_MAPPING[serverSelect.value];
    }
});

async function submitAnalysis() {
    const btn = document.getElementById('analyze-btn');
    const btnSpinner = document.getElementById('btn-spinner');
    const btnText = document.getElementById('btn-text');
    const loadingOverlay = document.getElementById('loading-overlay');
    const errorContainer = document.getElementById('error-container');
    const errorText = document.getElementById('error-text');
    
    const rawLogsPane = document.getElementById('raw-logs-pane');
    const analysisPane = document.getElementById('analysis-pane');

    // Gather inputs
    const serverId = document.getElementById('server_id').value;
    const ipAddress = document.getElementById('ip_address').value;
    const port = parseInt(document.getElementById('port').value, 10);
    const logType = document.getElementById('log_type').value;

    // Reset UI States
    errorContainer.style.display = 'none';
    btn.disabled = true;
    btnSpinner.style.display = 'block';
    btnText.textContent = 'Processing...';
    loadingOverlay.style.display = 'flex';
    
    rawLogsPane.textContent = '';
    analysisPane.innerHTML = '';

    try {
        const response = await fetch(`${API_BASE_URL}/analyze`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify({
                server_id: serverId,
                ip_address: ipAddress,
                port: port,
                log_type: logType
            })
        });

        if (!response.ok) {
            let errorMessage = `Server error: ${response.status}`;
            try {
                const errData = await response.json();
                errorMessage = errData.detail || errorMessage;
            } catch (e) {
                // Fallback if not JSON
            }
            throw new Error(errorMessage);
        }

        const data = await response.json();

        // Render Logs in Terminal View
        rawLogsPane.textContent = data.raw_logs;

        // Render Markdown for AI Analysis
        analysisPane.innerHTML = marked.parse(data.analysis);

    } catch (err) {
        errorText.textContent = err.message;
        errorContainer.style.display = 'block';
    } finally {
        btn.disabled = false;
        btnSpinner.style.display = 'none';
        btnText.textContent = 'Analyze Logs';
        loadingOverlay.style.display = 'none';
    }
}
