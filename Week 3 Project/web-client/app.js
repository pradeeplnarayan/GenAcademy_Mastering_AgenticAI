const form = document.querySelector('#jarvisForm');
const question = document.querySelector('#question');
const webhookUrl = document.querySelector('#webhookUrl');
const submitButton = document.querySelector('#submitButton');
const resultSection = document.querySelector('#resultSection');
const resultContent = document.querySelector('#resultContent');
const resultMeta = document.querySelector('#resultMeta');
const settingsButton = document.querySelector('#settingsButton');
const connectionPanel = document.querySelector('#connectionPanel');
const characterCount = document.querySelector('#characterCount');
const copyButton = document.querySelector('#copyResult');
let lastPlainText = '';

const savedUrl = localStorage.getItem('askJarvisWebhookUrl');
if (savedUrl) webhookUrl.value = savedUrl;

settingsButton.addEventListener('click', () => {
  const isOpen = !connectionPanel.hidden;
  connectionPanel.hidden = isOpen;
  settingsButton.setAttribute('aria-expanded', String(!isOpen));
});

document.querySelector('#saveUrl').addEventListener('click', () => {
  const value = webhookUrl.value.trim();
  if (!isValidUrl(value)) return showError('Enter a complete webhook URL beginning with http:// or https://.');
  localStorage.setItem('askJarvisWebhookUrl', value);
  connectionPanel.hidden = true;
  settingsButton.setAttribute('aria-expanded', 'false');
});

question.addEventListener('input', () => {
  if (question.value.length > 2000) question.value = question.value.slice(0, 2000);
  characterCount.textContent = `${question.value.length.toLocaleString()} / 2,000`;
});

document.querySelectorAll('[data-prompt]').forEach(button => {
  button.addEventListener('click', () => {
    question.value = button.dataset.prompt;
    question.dispatchEvent(new Event('input'));
    question.focus();
  });
});

form.addEventListener('submit', async event => {
  event.preventDefault();
  const message = question.value.trim();
  const url = webhookUrl.value.trim();
  if (!message) return question.focus();
  if (!isValidUrl(url)) {
    connectionPanel.hidden = false;
    settingsButton.setAttribute('aria-expanded', 'true');
    return showError('Add a valid n8n webhook URL before submitting your question.');
  }

  localStorage.setItem('askJarvisWebhookUrl', url);
  setLoading(true);
  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message })
    });
    const raw = await response.text();
    let payload;
    try { payload = raw ? JSON.parse(raw) : {}; }
    catch { payload = { results: [{ agent: 'jarvis', status: 'completed', analysis: raw }] }; }
    if (!response.ok) throw new Error(payload.message || payload.error || `${response.status} ${response.statusText}`);
    renderResponse(payload);
  } catch (error) {
    const hint = error instanceof TypeError
      ? 'The browser could not reach n8n. Confirm the webhook is listening and that the Webhook node allows this page’s origin (CORS).'
      : error.message;
    showError(hint);
  } finally {
    setLoading(false, false);
  }
});

copyButton.addEventListener('click', async () => {
  if (!lastPlainText) return;
  await navigator.clipboard.writeText(lastPlainText);
  const original = copyButton.textContent;
  copyButton.textContent = 'Copied';
  setTimeout(() => copyButton.textContent = original, 1400);
});

function setLoading(loading, replace = true) {
  submitButton.disabled = loading;
  submitButton.querySelector('.button-label').textContent = loading ? 'Analyzing…' : 'Go Jarvis';
  if (loading && replace) {
    resultSection.hidden = false;
    resultMeta.replaceChildren();
    resultContent.replaceChildren(document.querySelector('#loadingTemplate').content.cloneNode(true));
    resultSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }
}

function renderResponse(payload) {
  resultSection.hidden = false;
  resultContent.replaceChildren();
  resultMeta.replaceChildren();
  const results = normalizeResults(payload);
  const executionMode = payload.execution_mode || (results.length > 1 ? 'multi_agent_fan_out' : 'single_specialist');
  addPill(executionMode === 'multi_agent_fan_out' ? 'Combined analysis' : 'Specialist analysis');
  addPill(`${results.length} agent${results.length === 1 ? '' : 's'} completed`);
  if (payload.human_approval_required) addPill('Human approval required');

  const plainParts = [];
  results.forEach(result => {
    const card = document.createElement('article');
    card.className = 'agent-card';
    const isSales = /sales|forecast/i.test(result.agent || '');
    const title = isSales ? 'Sales Forecast & Trend Analysis' : /customer|campaign|churn/i.test(result.agent || '') ? 'Customer Intelligence & Campaign' : 'Jarvis Analysis';
    const summary = result.analysis || result.summary || result.answer || result.output || 'No narrative was returned.';
    plainParts.push(`${title}\n${summary}`);

    card.append(createAgentHeader(isSales ? 'SF' : 'CI', title, result.status || 'completed'));
    const rich = document.createElement('div');
    rich.className = 'rich-text';
    rich.innerHTML = simpleMarkdown(summary);
    card.append(rich);

    if (result.audience_description) {
      const audience = document.createElement('div');
      audience.className = 'rich-text';
      audience.innerHTML = `<h4>Campaign audience</h4>${simpleMarkdown(result.audience_description)}`;
      card.append(audience);
      plainParts.push(`Campaign audience\n${result.audience_description}`);
    }

    const emails = Array.isArray(result.email_drafts) ? result.email_drafts : result.email_draft ? [result.email_draft] : [];
    emails.forEach(email => {
      const emailCard = document.createElement('div');
      emailCard.className = 'email-card';
      emailCard.innerHTML = `<div class="email-label">${escapeHtml(humanize(email.action || 'Email draft'))}</div><h4>${escapeHtml(email.subject || 'Draft email')}</h4><p>${escapeHtml(email.body || '')}</p>`;
      card.append(emailCard);
      plainParts.push(`Email draft\nSubject: ${email.subject || ''}\n${email.body || ''}`);
    });

    if (emails.length || result.human_approval_required) {
      const note = document.createElement('p');
      note.className = 'approval-note';
      note.textContent = 'Review and approve this draft before sending it to customers.';
      card.append(note);
    }

    if (Array.isArray(result.data) && result.data.length) card.append(createDataDetails(result.data));
    resultContent.append(card);
  });

  if (!results.length) {
    const fallback = document.createElement('article');
    fallback.className = 'agent-card';
    fallback.append(createAgentHeader('AI', 'Jarvis Response', 'completed'));
    const pre = document.createElement('div');
    pre.className = 'rich-text';
    pre.innerHTML = simpleMarkdown(typeof payload === 'string' ? payload : JSON.stringify(payload, null, 2));
    fallback.append(pre);
    resultContent.append(fallback);
  }
  lastPlainText = plainParts.join('\n\n');
  resultSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function normalizeResults(payload) {
  if (Array.isArray(payload?.results)) return payload.results.filter(item => item?.status !== 'skipped');
  if (Array.isArray(payload)) return payload;
  if (payload?.agent || payload?.analysis || payload?.summary || payload?.answer) return [payload];
  return [];
}

function createAgentHeader(icon, title, status) {
  const header = document.createElement('div');
  header.className = 'agent-card-header';
  header.innerHTML = `<div class="agent-icon">${icon}</div><div><h3>${escapeHtml(title)}</h3><p>${escapeHtml(humanize(status))}</p></div>`;
  return header;
}

function createDataDetails(rows) {
  const details = document.createElement('details');
  const summary = document.createElement('summary');
  summary.textContent = `View supporting data (${rows.length} row${rows.length === 1 ? '' : 's'})`;
  details.append(summary);
  const wrap = document.createElement('div');
  wrap.className = 'table-wrap';
  const table = document.createElement('table');
  const keys = [...new Set(rows.flatMap(row => Object.keys(row || {})))].slice(0, 12);
  table.innerHTML = `<thead><tr>${keys.map(key => `<th>${escapeHtml(humanize(key))}</th>`).join('')}</tr></thead><tbody>${rows.slice(0, 100).map(row => `<tr>${keys.map(key => `<td>${escapeHtml(formatCell(row[key]))}</td>`).join('')}</tr>`).join('')}</tbody>`;
  wrap.append(table);
  details.append(wrap);
  return details;
}

function simpleMarkdown(value) {
  const text = escapeHtml(String(value || '')).replace(/\r\n/g, '\n');
  const lines = text.split('\n');
  let html = '';
  let inList = false;
  for (const rawLine of lines) {
    const line = rawLine.trim();
    if (/^[-*]\s+/.test(line)) {
      if (!inList) { html += '<ul>'; inList = true; }
      html += `<li>${formatInline(line.replace(/^[-*]\s+/, ''))}</li>`;
      continue;
    }
    if (inList) { html += '</ul>'; inList = false; }
    if (!line) continue;
    if (/^###\s+/.test(line)) html += `<h4>${formatInline(line.replace(/^###\s+/, ''))}</h4>`;
    else if (/^##?\s+/.test(line)) html += `<h3>${formatInline(line.replace(/^##?\s+/, ''))}</h3>`;
    else html += `<p>${formatInline(line)}</p>`;
  }
  if (inList) html += '</ul>';
  return html;
}

function formatInline(text) {
  return text.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>').replace(/`(.+?)`/g, '<code>$1</code>');
}

function showError(message) {
  resultSection.hidden = false;
  resultMeta.replaceChildren();
  resultContent.innerHTML = `<div class="error-card"><h3>Jarvis could not complete the request</h3><p>${escapeHtml(message)}</p><p>Check that n8n is listening on the selected webhook URL, then try again.</p></div>`;
  resultSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function addPill(text) {
  const pill = document.createElement('span');
  pill.className = 'meta-pill';
  pill.textContent = text;
  resultMeta.append(pill);
}

function isValidUrl(value) {
  try { const url = new URL(value); return ['http:', 'https:'].includes(url.protocol); }
  catch { return false; }
}

function humanize(value) { return String(value || '').replaceAll('_', ' ').replace(/\b\w/g, char => char.toUpperCase()); }
function formatCell(value) {
  if (value === null || value === undefined) return '—';
  if (typeof value === 'number') return value.toLocaleString(undefined, { maximumFractionDigits: 2 });
  if (typeof value === 'object') return JSON.stringify(value);
  return String(value);
}
function escapeHtml(value) {
  return String(value ?? '').replace(/[&<>"]/g, char => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[char]));
}
