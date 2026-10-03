// Dashboard + analytics charts (Chart.js loaded from cdnjs)
(async function () {
  if (!document.getElementById('chart-avg')) return;
  let s;
  try { s = await api('/api/analytics'); } catch (e) { return notify(e.message, 'error'); }
  const set = (id, v) => { const el = document.getElementById(id); if (el) el.textContent = v; };
  const f = v => (v == null ? '-' : v);
  set('stat-avg', f(s.average_score)); set('stat-count', s.interviews_completed);
  set('stat-tech', f(s.technical_avg)); set('stat-hr', f(s.hr_avg)); set('stat-answers', s.answers_count);
  if (!s.answers_count) document.getElementById('no-data').hidden = false;

  const base = { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } };
  const y10 = { y: { min: 0, max: 10 } };
  const avg = s.average_score || 0;
  new Chart('chart-avg', { type: 'doughnut', data: { labels: ['Score', 'Remaining'],
    datasets: [{ data: [avg, 10 - avg], backgroundColor: ['#0f766e', '#cbd5d9'] }] }, options: { ...base, cutout: '70%' } });
  new Chart('chart-split', { type: 'bar', data: { labels: ['Technical', 'HR'],
    datasets: [{ data: [s.technical_avg || 0, s.hr_avg || 0], backgroundColor: ['#0f766e', '#d97706'] }] },
    options: { ...base, scales: y10 } });
  new Chart('chart-time', { type: 'line', data: { labels: s.timeline.map(t => t.date),
    datasets: [{ data: s.timeline.map(t => t.score), borderColor: '#0f766e', tension: 0.3, fill: false }] },
    options: { ...base, scales: y10 } });
  const low = s.topics.slice(0, 6);
  new Chart('chart-topics', { type: 'bar', data: { labels: low.map(t => t.topic),
    datasets: [{ data: low.map(t => t.avg), backgroundColor: low.map(t => (t.avg < 6.5 ? '#dc2626' : '#16a34a')) }] },
    options: { ...base, indexAxis: 'y', scales: { x: { min: 0, max: 10 } } } });

  const body = document.getElementById('topic-body');
  if (body) body.innerHTML = s.topics.map(t => `<tr><td>${esc(t.topic)}</td><td>${t.avg}/10</td><td>${t.count}</td></tr>`).join('')
    || '<tr><td colspan="3" class="muted">No data yet.</td></tr>';

  const box = document.getElementById('recs');
  if (box) {
    try {
      const r = await api('/api/recommendations');
      box.innerHTML = r.recommendations.length
        ? r.recommendations.map(x => `<div class="rec"><b>${esc(x.topic)}</b><p>${esc(x.tip)}</p></div>`).join('')
        : '<p class="muted">No weak areas yet. Complete a few interviews to get recommendations.</p>';
    } catch (e) { box.textContent = 'Could not load recommendations.'; }
  }
})();
