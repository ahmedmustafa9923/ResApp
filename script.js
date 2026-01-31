// Simulate a live counter increasing
let count = 850;
const counterElement = document.getElementById('counter');

function updateCounter() {
    count += Math.floor(Math.random() * 5);
    counterElement.innerText = count.toLocaleString();
}
setInterval(updateCounter, 3000);

// Add simulated logs
const logs = [
    "[INFO] Navigating to Target URL...",
    "[INFO] Intercepting XHR/Fetch request...",
    "[SUCCESS] JSON payload captured.",
    "[INFO] Parsing data with Python logic...",
    "[AWS] Pushing records to PostgreSQL...",
    "[INFO] Waiting for next scheduled interval..."
];

const logContainer = document.getElementById('log-container');

function addLog() {
    const time = new Date().toLocaleTimeString();
    const randomLog = logs[Math.floor(Math.random() * logs.length)];
    const newEntry = document.createElement('code');
    newEntry.innerHTML = `<span class="text-muted">[${time}]</span> ${randomLog}`;
    logContainer.prepend(newEntry);
}
setInterval(addLog, 4000);

// Live Clock
setInterval(() => {
    document.getElementById('live-clock').innerText = "System Time: " + new Date().toLocaleString();
}, 1000);