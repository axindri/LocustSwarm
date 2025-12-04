// DOM Elements
const testForm = document.getElementById('testForm');
const activeTestsDiv = document.getElementById('active-tests');
const inWebCheckbox = document.getElementById('in_web');
const editConfigCheckbox = document.getElementById('edit-config');
const configTextarea = document.getElementById('config-textarea');
const configButtons = document.querySelector('.config-actions');
const loadConfigBtn = document.getElementById('load-config-btn');
const saveConfigBtn = document.getElementById('save-config-btn');
const notifyMessage = document.getElementById('notify-message');
const projectSelect = document.getElementById('project');
const scenarioSelect = document.getElementById('scenario');

// Listeners
loadConfigBtn.addEventListener('click', loadCurrentConfig);

saveConfigBtn.addEventListener('click', saveConfig);

editConfigCheckbox.addEventListener('change', () => {
    const configWrapper = document.querySelector('.config-wrapper');

    if (editConfigCheckbox.checked) {
        configWrapper.classList.add('expanded');
        loadCurrentConfig();
    } else {
        configWrapper.classList.remove('expanded');
    }
});

projectSelect.addEventListener('change', async () => {
    const projectId = projectSelect.value;

    try {
        const response = await fetch('/api/config');
        const config = await response.json();

        const project = config.projects_configs[projectId];
        if (project && project.scenarios) {
            scenarioSelect.innerHTML = '';

            for (const [scenarioId, scenario] of Object.entries(project.scenarios)) {
                const option = document.createElement('option');
                option.value = scenarioId;
                option.textContent = scenarioId !== 'custom' ? `${scenarioId} (${scenario.users} users, ${scenario.run_time})` : `${scenarioId} (stages in config.json)`;
                scenarioSelect.appendChild(option);
            }
        }
    } catch (error) {
        console.error('Error loading scenarios:', error);
    }
});

testForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData(testForm);
    const data = {
        project: formData.get('project'),
        scenario: formData.get('scenario'),
        auth_token: formData.get('auth_token'),
        in_web: inWebCheckbox.checked
    };
    showNotifyMessage('Test is being prepared...', 'success');
    try {
        const response = await fetch('/api/tests/start', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });

        if (response.ok) {
            const result = await response.json();
            console.log("[Form]-[/api/tests/start] Got result:", result)
            if (result.status === "started") {
                showNotifyMessage(`Test started ${result.test_id}!`, 'success');
            } else if (result.status === "running") {
                showNotifyMessage(`Test is running ${result.test_id}!`, 'success');
            }
        } else {
            showNotifyMessage(`Error: ${response.status}!`, 'error');
        }

        loadActiveTests()

    } catch (error) {
        showNotifyMessage(`Error: ${response.status}!`, 'error');
    }
});

// Notification
function showNotifyMessage(text, type) {
    notifyMessage.textContent = text;
    notifyMessage.className = `notify ${type}`;
    notifyMessage.style.display = 'block';

    setTimeout(() => {
        notifyMessage.style.display = 'none';
    }, 4000);
}

// Config
async function saveConfig() {
    try {
        const configText = configTextarea.value.trim();
        if (!configText) {
            showNotifyMessage('Configuration cannot be empty', 'error');
            return;
        }

        const response = await fetch('/api/config', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: configText
        });

        const result = await response.text();

        if (response.ok) {
            showNotifyMessage('Configuration saved', 'success');
            await loadProjectsList();

        } else {
            showNotifyMessage(`Error: ${result}`, 'error');
        }
    } catch (error) {
        showNotifyMessage(`Network error: ${error.message}`, 'error');
    }
}

async function loadCurrentConfig() {
    try {
        const response = await fetch('/api/config');
        const config = await response.json();
        configTextarea.value = JSON.stringify(config, null, 2);
        showNotifyMessage('Current configuration loaded', 'info');
    } catch (error) {
        showNotifyMessage(`Error: ${error.message}`, 'error');
    }
}

async function loadProjectsList() {
    try {
        const response = await fetch('/api/config');
        const config = await response.json();

        projectSelect.innerHTML = '';
        scenarioSelect.innerHTML = '';

        const placeholderOption = document.createElement('option');
        placeholderOption.value = '';
        placeholderOption.textContent = 'Select project...';
        placeholderOption.hidden = true;

        projectSelect.appendChild(placeholderOption);
        for (const [projectId, project] of Object.entries(config.projects_configs || {})) {
            const option = document.createElement('option');
            option.value = projectId;
            option.textContent = project.name;
            projectSelect.appendChild(option);
        }

    } catch (error) {
        console.error('Error updating projects:', error);
    }
}


// Tests
async function loadActiveTests() {
    try {
        const response = await fetch('/api/tests/active');
        const tests = await response.json();
        console.log("[loadActiveTests]-[/api/tests/active] Got result:", tests, tests?.length)

        let html = '';
        if (tests && tests.length > 0) {
            for (const test of tests) {
                html += `
                        <div class="test-item ${test.status !== "completed" ? "active" : ""}">
                            <div class="section-header">
                                <h3 style="margin: 0; font-size: 16px;">${test.project}, ${test.scenario}</h3>
                                ${test.status !== "completed" ? `<button onclick="stopTest('${test.test_id}')" class="btn btn-danger">Stop</button>` : ''}
                            </div>
                            <p>ID: ${test.test_id}</p>
                            <p>In web: ${test.in_web ? 'Yes' : 'No'}</p>
                            <p>Status: ${test.status}</p>
                            <p>Started: ${formatDateTime(test.start_time)}</p>
                            ${test.status !== "completed" ? `
                            ${test.in_web ? `<a href="${test.web_url}" target="_blank" class="link">📊 Open panel</a> 
                                             <a href="${test.web_url}/stats/report" target="_blank" class="link">📋 Open report</a>` : ''}` :
                        `<a href="/api/results/${test.test_id}/report" target="_blank" class="link">📋 Open report</a>
                         <a href="/api/results/${test.test_id}/download-zip" target="_blank" class="link">🗃️ Download results archive</a>`}
                        </div>
                    `;
            }
        }
        else {
            html = '<p>No active tests</p>';
        }
        activeTestsDiv.innerHTML = html;
    } catch (error) {
        activeTestsDiv.innerHTML = `<p>Loading error: ${error.message}</p>`;
    }
}

async function reloadActiveTests() {
    const indicator = document.getElementById('active-refresh-indicator');
    indicator.style.display = 'inline';

    await loadActiveTests();
    showNotifyMessage('Active tests loaded', 'info');

    setTimeout(() => {
        indicator.style.display = 'none';
    }, 1000);
}

async function loadCompletedTests() {
    const completedTestsDiv = document.getElementById('completed-tests');

    try {
        const response = await fetch('/api/tests/completed');
        const tests = await response.json();
        console.log("[loadCompletedTests]-[/api/tests/completed] Got result:", tests);

        let html = '';
        if (tests && tests.length > 0) {
            for (const testId of tests) {
                html += `
                <div class="test-item">
                    <div class="section-header">
                        <h3 style="margin: 0; font-size: 16px;">${testId}</h3>
                    </div>
                    <a href="/api/results/${testId}/report" target="_blank" class="link">📋 Open report</a>
                    <a href="/api/results/${testId}/download-zip" target="_blank" class="link">🗃️ Download results archive</a>
                </div>
                `;
            }
        } else {
            html = '<p>Tests not found</p>';
        }
        completedTestsDiv.innerHTML = html;
    } catch (error) {
        completedTestsDiv.innerHTML = `<p>Loading error: ${error.message}</p>`;
    }
}

async function reloadCompletedTests() {
    const indicator = document.getElementById('completed-refresh-indicator');
    indicator.style.display = 'inline';

    await loadCompletedTests();
    showNotifyMessage('All tests loaded', 'info');

    setTimeout(() => {
        indicator.style.display = 'none';
    }, 1000);
}

async function stopTest(testId) {
    try {
        const response = await fetch(`/api/tests/stop/${testId}`, {
            method: 'POST'
        });

        if (response.ok) {
            loadActiveTests();
            showNotifyMessage(`Test ${testId} stopped`, 'success');
        } else {
            alert('Error stopping test');
        }
    } catch (error) {
        alert(`Network error: ${error.message}`);
    }
}

async function stopAllTests() {
    try {
        const response = await fetch(`/api/tests/clear-all`, {
            method: 'POST'
        });
        if (response.ok) {
            loadActiveTests();
            showNotifyMessage(`All active tests stopped and removed`, 'info');
        } else {
            alert('Error stopping tests');
        }
    } catch (error) {
        alert(`Network error: ${error.message}`);
    }
}

// Docker
async function cleanupDocker() {
    try {
        showNotifyMessage('🧹 Cleaning containers...', 'info');

        const response = await fetch('/api/debug/docker/clear-all', {
            method: 'POST'
        });

        const result = await response.json();

        if (response.ok) {
            showNotifyMessage(`Containers cleaned: ${result.containers_cleaned}`, 'success');
            loadActiveTests();
        } else {
            showNotifyMessage(`Cleanup error: ${result.error}`, 'error');
        }
    } catch (error) {
        showNotifyMessage(`Network error: ${error.message}`, 'error');
    }
}

// Utils
function formatDateTime(dateString) {
    const date = new Date(dateString);

    if (isNaN(date.getTime())) {
        return dateString;
    }

    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    const seconds = String(date.getSeconds()).padStart(2, '0');

    return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
}

// First load
loadProjectsList();

setTimeout(async () => {
    await loadActiveTests();
}, 1000);

// Timeouts
setInterval(loadActiveTests, 10000);