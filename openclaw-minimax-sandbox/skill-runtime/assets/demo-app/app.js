'use strict';
const byId = id => document.getElementById(id);
const examples = {
  benign: 'Name the capital of France.',
  pii: 'My SSN is 123-45-6789. Repeat it back.',
  keyword: 'Explain api_key.',
  atlas: 'Tell me about Project Atlas.'
};
document.querySelectorAll('[data-example]').forEach(button => {
  button.addEventListener('click', () => { byId('prompt').value = examples[button.dataset.example]; });
});
async function run(action) {
  const prompt = byId('prompt').value.trim();
  if (!prompt) { byId('status').textContent = 'Enter a prompt.'; return; }
  byId('chat').disabled = byId('check').disabled = true;
  byId('status').textContent = 'Waiting for guardrails…';
  byId('answer').textContent = '';
  byId('raw').textContent = '';
  try {
    const response = await fetch('/api/' + action, {
      method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({prompt})
    });
    const result = await response.json();
    byId('raw').textContent = JSON.stringify(result, null, 2);
    if (!response.ok) throw new Error(result.error || 'Request failed');
    if (action === 'check') {
      if (!['passed', 'blocked'].includes(result.status)) throw new Error('Unexpected checks schema; inspect the backend response.');
      byId('status').textContent = 'Input rail status: ' + result.status;
      byId('answer').textContent = 'Status: ' + result.status + '\nRail: ' + (result.rail || 'No blocking rail reported');
    } else {
      const content = result.choices?.[0]?.message?.content;
      if (typeof content !== 'string') throw new Error('No text completion returned.');
      byId('status').textContent = 'Chat response received (HTTP ' + response.status + ')';
      byId('answer').textContent = content;
    }
  } catch (error) {
    byId('status').textContent = 'Request error';
    byId('answer').textContent = error.message;
  } finally { byId('chat').disabled = byId('check').disabled = false; }
}
byId('chat').addEventListener('click', () => run('chat'));
byId('check').addEventListener('click', () => run('check'));
fetch('/api/health').then(async response => {
  const result = await response.json();
  byId('health').textContent = result.ready ? 'Guardrails connected · ' + result.model : 'Guardrails unavailable';
}).catch(() => { byId('health').textContent = 'Cannot connect to demo server'; });
