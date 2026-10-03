// Shared helpers + small page handlers (profile, resume, setup, history)
async function api(url, options = {}) {
  const opts = { headers: {}, ...options };
  if (opts.body && !(opts.body instanceof FormData)) {
    opts.headers['Content-Type'] = 'application/json';
    opts.body = JSON.stringify(opts.body);
  }
  const res = await fetch(url, opts);
  let data = {};
  try { data = await res.json(); } catch (e) { /* non-JSON response */ }
  if (res.status === 401) { window.location = '/login'; throw new Error('Please log in.'); }
  if (!res.ok) throw new Error(data.error || `Request failed (${res.status})`);
  return data;
}

const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const list = arr => '<ul>' + (arr || []).map(x => `<li>${esc(x)}</li>`).join('') + '</ul>';

function notify(msg, type = 'info') {
  const box = document.getElementById('toast');
  box.textContent = msg;
  box.className = 'toast show ' + type;
  clearTimeout(window._toastTimer);
  window._toastTimer = setTimeout(() => (box.className = 'toast'), 4000);
}

// Profile
const profileForm = document.getElementById('profile-form');
if (profileForm) profileForm.addEventListener('submit', async e => {
  e.preventDefault();
  try {
    await api('/api/profile', { method: 'PUT', body: Object.fromEntries(new FormData(profileForm)) });
    notify('Profile saved', 'success');
  } catch (err) { notify(err.message, 'error'); }
});

// Resume upload
const resumeForm = document.getElementById('resume-form');
if (resumeForm) resumeForm.addEventListener('submit', async e => {
  e.preventDefault();
  const file = resumeForm.resume.files[0];
  if (!file) return notify('Choose a file first.', 'error');
  const fd = new FormData();
  fd.append('resume', file);
  const btn = resumeForm.querySelector('button');
  btn.disabled = true;
  try {
    const d = await api('/api/resume', { method: 'POST', body: fd });
    const p = d.parsed;
    document.getElementById('resume-result').innerHTML = `<div class="card"><h3>Resume analysed: ${esc(d.filename)}</h3>
      <p><b>Detected skills:</b> ${p.skills.length ? p.skills.map(esc).join(', ') : 'none found'}</p>
      <p><b>Email:</b> ${esc(p.email || 'not found')} &middot; <b>Words:</b> ${p.word_count}</p>
      ${p.education.length ? '<p><b>Education lines:</b></p>' + list(p.education) : ''}
      <p class="muted">These skills are now used to personalise your interview questions.</p>
      <a class="btn" href="/interview/setup">Start an interview</a></div>`;
    notify('Resume uploaded', 'success');
  } catch (err) { notify(err.message, 'error'); }
  btn.disabled = false;
});

// Interview setup
const setupForm = document.getElementById('setup-form');
if (setupForm) setupForm.addEventListener('submit', async e => {
  e.preventDefault();
  const btn = setupForm.querySelector('button');
  btn.disabled = true; btn.textContent = 'Generating questions...';
  try {
    const d = await api('/api/interviews', { method: 'POST', body: {
      type: setupForm.elements['type'].value, num_questions: Number(setupForm.elements['num_questions'].value) } });
    window.location = '/interview/' + d.interview_id;
  } catch (err) {
    notify(err.message, 'error');
    btn.disabled = false; btn.textContent = 'Generate questions and begin';
  }
});

// History table
const historyBody = document.getElementById('history-body');
if (historyBody) api('/api/interviews').then(d => {
  if (!d.interviews.length) {
    historyBody.innerHTML = '<tr><td colspan="6">No completed interviews yet. <a href="/interview/setup">Start one</a>.</td></tr>';
    return;
  }
  const f = v => (v == null ? '-' : v);
  historyBody.innerHTML = d.interviews.map(i => `<tr><td>${esc((i.created_at || '').slice(0, 16))}</td>
    <td>${esc(i.interview_type)}</td><td><b>${f(i.avg_score)}</b>/10</td><td>${f(i.technical_score)}</td>
    <td>${f(i.hr_score)}</td><td><a href="/interview/${i.interview_id}/result">View</a></td></tr>`).join('');
}).catch(err => notify(err.message, 'error'));
