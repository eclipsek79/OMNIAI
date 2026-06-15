const runBtn = document.getElementById('runBtn');
const goalInput = document.getElementById('goal');
const output = document.getElementById('output');
const tokenInput = document.getElementById('token');

function pretty(obj) {
  try {
    return JSON.stringify(obj, null, 2);
  } catch (e) {
    return String(obj);
  }
}

runBtn.addEventListener('click', async () => {
  const goal = goalInput.value.trim();
  const token = tokenInput.value.trim() || '1234';
  if (!goal) {
    output.textContent = 'Please enter a goal.';
    return;
  }
  output.textContent = 'Running...';
  try {
    const resp = await fetch('/run', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': token
      },
      body: JSON.stringify({ goal })
    });
    if (!resp.ok) {
      const txt = await resp.text();
      output.textContent = `Error ${resp.status}: ${txt}`;
      return;
    }
    const data = await resp.json();
    output.textContent = pretty(data);
  } catch (err) {
    output.textContent = `Request failed: ${err}`;
  }
});
