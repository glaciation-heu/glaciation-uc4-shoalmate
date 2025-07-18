let state = {
    cluster_id: undefined,
    experiment_duration_sec: undefined,
    experiment_tag: undefined,
    is_active: undefined,
    minutes_per_hour: undefined,
    virtual_time_sec: undefined,
};


async function update() {
    await fetchState();
    render();
}

async function fetchState(){
    const response = await fetch('/api/timesim');
    const data = await response.json();
    const old_inputs = [state.minutes_per_hour, state.experiment_tag];
    state = data;
    if (!state.is_active) {  // Use remote value if experiment started
        [state.minutes_per_hour, state.experiment_tag] = old_inputs;
    }
}

function render() {
    document.getElementById('cluster-id').textContent = state.cluster_id;
    document.getElementById('virtual-time').textContent = formatDuration(state.virtual_time_sec);
    document.getElementById('experiment-duration').textContent = formatDuration(state.experiment_duration_sec);
    const button = document.querySelector('button');
    const inputs = document.querySelectorAll('input');
    if (state.is_active) {
        button.textContent = 'Stop';
        button.setAttribute('onclick', 'onclickButtonStop()');
        inputs.forEach(input => input.disabled = true);
        document.getElementById("minuts-per-hour").value = state.minutes_per_hour;
        document.getElementById("experiment-tag").value = state.experiment_tag;
        button.classList.add('danger');
    } else {
        button.textContent = 'Start';
        button.setAttribute('onclick', 'onclickButtonStart()');
        inputs.forEach(input => input.disabled = false);
        button.classList.remove('danger');
    }
}

async function onclickButtonStop() {
    state.is_active = false;
    render();
    await fetch('/api/timesim/experiment', {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json'
        }
    });
}

async function onclickButtonStart() {
    const minutes_per_hour = document.getElementById("minuts-per-hour").value;
    const experiment_tag = document.getElementById("experiment-tag").value;
    state.is_active = true;
    state.minutes_per_hour = minutes_per_hour;
    state.experiment_tag = experiment_tag;
    render();
    await fetch('/api/timesim/experiment', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            minutes_per_hour: minutes_per_hour,
            experiment_tag: experiment_tag,
        })
    });
}

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

async function main() {
    await update();
    setInterval(async () => update(), 1000);
}

main();
