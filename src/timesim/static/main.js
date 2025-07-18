function formatDuration(seconds_total) {
    let formatted = "-";
    if (seconds_total) {
        const seconds = Math.floor(seconds_total % 60);
        const minutes = Math.floor(seconds_total / 60) % 60;
        const hours = Math.floor(seconds_total / 3600) % 24;
        const days = Math.floor(seconds_total / 86400);
        formatted = `${seconds}s`;
        if (minutes > 0) formatted = `${minutes}h ` + formatted;
        if (hours > 0) formatted = `${hours}h ` + formatted;
        if (days > 0) formatted = `${days}d ` + formatted;
    }
    return formatted;
}

async function updateRows() {
    const response = await fetch('/api/timesim');
    const data = await response.json();
    document.getElementById('cluster-id').textContent = data.cluster_id;
    document.getElementById('virtual-time').textContent = data.virtual_time_sec;
    document.getElementById('virtual-time').textContent = formatDuration(data.virtual_time_sec);
    document.getElementById('experiment-duration').textContent = formatDuration(data.experiment_duration_sec);

    if (data.is_active) {
        await disableButton();
    } else {
        await enableButton();
    }
}

async function startExperiment() {
    await fetch('/api/timesim/experiment', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            minutes_per_hour: document.getElementById('minuts-per-hour').value,
            experiment_tag: document.getElementById('experiment-tag').value
        })
    });
}

async function stopExperiment() {
    await fetch('/api/timesim/experiment', {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json'
        }
    });
}

async function disableButton() {
    const startButton = document.querySelector('button');
    startButton.textContent = 'Stop';
    startButton.setAttribute('onclick', 'enableButton()');
    await startExperiment();
}

async function enableButton() {
    const startButton = document.querySelector('button');
    startButton.textContent = 'Start';
    startButton.setAttribute('onclick', 'disableButton()');
    await stopExperiment();
}


async function main() {
    await updateRows();
    setInterval(updateRows, 900);
}

main();
