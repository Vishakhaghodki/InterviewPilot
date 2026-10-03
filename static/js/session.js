// Interview session page + result page
(function () {
  const sessionRoot = document.getElementById('session');
  if (sessionRoot) runSession(sessionRoot.dataset.id);
  const resultRoot = document.getElementById('result');
  if (resultRoot) runResult(resultRoot.dataset.id);

  function evalHtml(q) {
    return `<div class="score">${q.score}/10</div><p>${esc(q.feedback)}</p>
      <div class="good"><h4>Strengths</h4>${list(q.strengths)}</div>
      <div class="bad"><h4>Weaknesses</h4>${list(q.weaknesses)}</div>
      <div class="tip"><h4>How to improve</h4>${list(q.suggestions)}</div>`;
  }

  async function runSession(id) {
    const $ = x => document.getElementById(x);
    let data;
    try { data = await api(`/api/interviews/${id}`); } catch (e) { return notify(e.message, 'error'); }
    const qs = data.questions;
    let i = qs.findIndex(q => !q.answered);
    if (i < 0) i = qs.length - 1;

    async function finish() {
      try { await api(`/api/interviews/${id}/complete`, { method: 'POST' }); window.location = `/interview/${id}/result`; }
      catch (e) { notify(e.message, 'error'); }
    }

    function show() {
      const q = qs[i];
      const done = qs.filter(x => x.answered).length;
      $('progress-bar').style.width = `${(done / qs.length) * 100}%`;
      $('q-count').textContent = `Question ${i + 1} of ${qs.length}`;
      $('q-cat').textContent = q.category === 'hr' ? 'HR' : 'Technical';
      $('q-topic').textContent = q.topic;
      $('q-text').textContent = q.text;
      $('answer').value = q.answered ? q.answer_text : '';
      $('answer').disabled = q.answered;
      $('submit-btn').hidden = q.answered;
      $('next-btn').hidden = !q.answered;
      $('next-btn').textContent = i < qs.length - 1 ? 'Next question' : 'Finish interview';
      $('eval-box').hidden = !q.answered;
      if (q.answered) $('eval-box').innerHTML = evalHtml(q);
      $('finish-early').hidden = done === 0 || (i === qs.length - 1 && q.answered);
    }

    $('submit-btn').onclick = async () => {
      const text = $('answer').value.trim();
      if (text.length < 5) return notify('Please write a longer answer.', 'error');
      const btn = $('submit-btn');
      btn.disabled = true; btn.textContent = 'Evaluating...';
      try {
        const d = await api(`/api/interviews/${id}/answer`, { method: 'POST', body: { question_id: qs[i].id, answer: text } });
        Object.assign(qs[i], { answered: true, answer_text: text }, d.evaluation);
        show();
      } catch (e) { notify(e.message, 'error'); }
      btn.disabled = false; btn.textContent = 'Submit answer';
    };
    $('next-btn').onclick = () => { if (i < qs.length - 1) { i++; show(); } else finish(); };
    $('finish-early').onclick = finish;
    show();
  }

  async function runResult(id) {
    let d;
    try { d = await api(`/api/interviews/${id}`); } catch (e) { return notify(e.message, 'error'); }
    const answered = d.questions.filter(q => q.answered);
    const weak = [...new Set(answered.filter(q => q.score < 6.5).map(q => q.topic))];
    document.getElementById('result').innerHTML = `
      <h1>Interview results</h1>
      <div class="card"><div class="score" style="font-size:2.6rem;font-weight:800;color:var(--brand)">${d.avg_score}/10</div>
        <p>${esc(d.type)} interview &middot; ${answered.length} of ${d.questions.length} answered &middot; ${esc(d.ai_mode)} mode</p>
        <p><b>Topics to revisit:</b> ${weak.length ? weak.map(esc).join(', ') : 'none - strong performance!'}</p></div>
      ${d.questions.map((q, n) => `<div class="card eval"><p class="muted">Question ${n + 1} &middot; ${esc(q.category)} &middot; ${esc(q.topic)}</p>
        <h3>${esc(q.text)}</h3>
        ${q.answered ? `<p><b>Your answer:</b> ${esc(q.answer_text)}</p>${evalHtml(q)}` : '<p class="muted">Not answered.</p>'}</div>`).join('')}`;
  }
})();
