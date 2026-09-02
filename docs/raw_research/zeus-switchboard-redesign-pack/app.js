(() => {
  'use strict';

  const state = {
    paused: false,
    theme: localStorage.getItem('zeus-theme') || 'obsidian',
    density: localStorage.getItem('zeus-density') || 'compact',
    reducedMotion: localStorage.getItem('zeus-reduced-motion') === 'true',
    activityIndex: 0,
  };

  const missions = [
    { id: 'CLIENT-REV-042', title: 'Marketing model client review', detail: 'Artifact builder · compiling', progress: 68, status: 'run', time: 'NOW', agents: ['AR','AN','RV','BL'], active: true },
    { id: 'RAPID-REL-01', title: 'Reliability patch validation', detail: 'Awaiting human approval', progress: 92, status: 'warn', time: '4m', agents: ['QA','RV'] },
    { id: 'PREFLIGHT-027', title: 'Credential classification fix', detail: 'Test agent · 31/42 checks', progress: 74, status: 'run', time: '9m', agents: ['IM','TS'] },
    { id: 'ROADMAP-013', title: 'Refresh execution roadmap', detail: 'Blocked by upstream evidence', progress: 37, status: 'blocked', time: '16m', agents: ['RS'] },
    { id: 'RESEARCH-118', title: 'Evaluate hierarchy patterns', detail: 'Research cell · synthesis', progress: 51, status: 'run', time: '23m', agents: ['R1','R2','RV'] },
    { id: 'MONITOR-006', title: 'Fleet health baseline', detail: 'Continuous monitoring', progress: 84, status: 'run', time: '1h', agents: ['OP','MO'] },
  ];

  const messages = [
    { avatar: 'AR', name: 'Architect', meta: '11:37 · agent', text: 'Success contract locked. The client artifact must reconcile both entities, expose the scope decision, and carry an evidence timestamp.' },
    { avatar: 'AN', name: 'Data analyst', meta: '11:41 · agent', text: 'Reconciliation complete. <code>NAVIRA gross−net = 5,015,478.00</code>; LECTRIC variance is zero. Evidence attached to the run.' },
    { avatar: 'PR', name: 'Paul', meta: '11:43 · operator', text: 'Keep the client view concise. Surface the measured defect and decision before implementation detail.', human: true },
    { avatar: 'BL', name: 'Artifact builder', meta: '11:47 · agent', text: 'Client review is compiling. One decision needs confirmation.', card: true },
  ];

  const activities = [
    ['11:46:31','builder','Loaded 7 authored sections from <strong>canonical state</strong>'],
    ['11:46:38','evidence','Verified 23 source references · <strong>0 unresolved</strong>'],
    ['11:46:44','builder','Rendered view model · 4 metric groups · 2 entities'],
    ['11:46:51','reviewer','Checked claim temporal status · <strong>CURRENT</strong>'],
    ['11:47:02','builder','Running layout and overflow validation'],
    ['11:47:13','system','Checkpoint persisted · context handoff available'],
  ];

  const commands = [
    { icon: '↗', title: 'Deploy a new mission', hint: 'Compose a formation, budget, gates and success contract', key: 'N', action: 'new' },
    { icon: '⌁', title: 'Broadcast to active formation', hint: 'Send a context-linked instruction to the mission squad', key: 'B', action: 'compose' },
    { icon: '✓', title: 'Open pending approvals', hint: '1 decision is waiting for operator review', key: 'G A', action: 'approval' },
    { icon: '◫', title: 'Open CLIENT-REV-042 artifacts', hint: '7 generated artifacts · latest changed 2m ago', key: 'G F', action: 'artifact' },
    { icon: '⌘', title: 'Enter focus command mode', hint: 'Collapse side panes and follow the active mission', key: 'F', action: 'focus' },
  ];

  const $ = (selector, root = document) => root.querySelector(selector);
  const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];

  function renderMissions() {
    $('#missionQueue').innerHTML = missions.map(m => `
      <article class="mission-card ${m.status} ${m.active ? 'active' : ''}" tabindex="0" data-mission="${m.id}">
        <div class="mission-card-top"><i></i><strong>${m.id}</strong><time>${m.time}</time></div>
        <h3>${m.title}</h3><p>${m.detail}</p>
        <div class="mission-progress"><b style="width:${m.progress}%"></b></div>
        <div class="mission-card-bottom"><span>${m.progress}% complete</span><span class="agent-stack">${m.agents.map(a => `<i>${a}</i>`).join('')}</span></div>
      </article>`).join('');
  }

  function renderMessages() {
    $('#commsFeed').innerHTML = `<div class="feed-marker">TODAY · LIVE MISSION CONTEXT</div>` + messages.map(m => `
      <article class="message">
        <div class="message-avatar ${m.human ? 'human' : ''}">${m.avatar}</div>
        <div class="message-copy"><div class="message-head"><strong>${m.name}</strong><span>${m.meta}</span></div><p>${m.text}</p>
        ${m.card ? `<div class="message-card"><strong>DECISION REQUIRED · GATE G7</strong><p>Use measured variance as the headline scope, with target scope shown separately?</p><div class="message-actions"><button class="primary" data-approve>Approve</button><button>Inspect evidence</button><button>Reply</button></div></div>` : ''}</div>
      </article>`).join('');
  }

  function renderActivity(extra) {
    const rows = extra ? [...activities, extra] : activities;
    $('#activityStream').innerHTML = rows.map(a => `<div class="activity-line"><time>${a[0]}</time><span class="source">${a[1]}</span><span class="message">${a[2]}</span></div>`).join('');
    $('#activityStream').scrollTop = $('#activityStream').scrollHeight;
  }

  function renderCommands(filter = '') {
    const normalized = filter.toLowerCase();
    const shown = commands.filter(c => `${c.title} ${c.hint}`.toLowerCase().includes(normalized));
    $('#paletteResults').innerHTML = shown.length ? shown.map((c, i) => `<button class="palette-result ${i === 0 ? 'active' : ''}" data-action="${c.action}"><span class="result-icon">${c.icon}</span><span><strong>${c.title}</strong><small>${c.hint}</small></span><kbd>${c.key}</kbd></button>`).join('') : `<div class="palette-result"><span class="result-icon">?</span><span><strong>No matching command</strong><small>Try missions, approvals, artifacts, formation or focus</small></span></div>`;
  }

  function openPalette() {
    renderCommands();
    $('#paletteBackdrop').hidden = false;
    requestAnimationFrame(() => $('#paletteInput').focus());
  }
  function closePalette() { $('#paletteBackdrop').hidden = true; }
  function openDeploy() { $('#missionBackdrop').hidden = false; requestAnimationFrame(() => $('.deploy-modal textarea').focus()); }
  function closeDeploy() { $('#missionBackdrop').hidden = true; }

  function openSettings() {
    $('#settingsDrawer').classList.add('open');
    $('#settingsDrawer').setAttribute('aria-hidden', 'false');
    $('#drawerScrim').hidden = false;
    requestAnimationFrame(() => $('#settingsClose').focus());
  }
  function closeSettings() {
    $('#settingsDrawer').classList.remove('open');
    $('#settingsDrawer').setAttribute('aria-hidden', 'true');
    $('#drawerScrim').hidden = true;
  }

  function toast(title, detail) {
    const el = document.createElement('div');
    el.className = 'toast';
    el.innerHTML = `<strong>${title}</strong><span>${detail}</span>`;
    $('#toastRegion').append(el);
    setTimeout(() => el.remove(), 3600);
  }

  function setTheme(theme) {
    state.theme = theme;
    document.documentElement.dataset.theme = theme;
    $$('[data-theme-value]').forEach(b => b.classList.toggle('active', b.dataset.themeValue === theme));
    localStorage.setItem('zeus-theme', theme);
  }

  function setDensity(density) {
    state.density = density;
    document.documentElement.dataset.density = density;
    $$('[data-density-value]').forEach(b => b.classList.toggle('active', b.dataset.densityValue === density));
    localStorage.setItem('zeus-density', density);
  }

  function setReducedMotion(enabled) {
    state.reducedMotion = enabled;
    document.documentElement.classList.toggle('reduce-motion', enabled);
    $('#reduceMotionToggle').checked = enabled;
    localStorage.setItem('zeus-reduced-motion', enabled);
  }

  function focusMode() {
    document.body.classList.toggle('focus-mode');
    const active = document.body.classList.contains('focus-mode');
    $('.queue-pane').style.display = active ? 'none' : '';
    $('.comms-pane').style.display = active ? 'none' : '';
    $('.pane-grid').style.gridTemplateColumns = active ? '1fr' : '';
    toast(active ? 'Focus mode enabled' : 'Focus mode closed', active ? 'Side channels hidden. Press F to restore.' : 'All command panes restored.');
  }

  function commandAction(action) {
    closePalette();
    if (action === 'new') openDeploy();
    else if (action === 'compose') { $('#messageInput').focus(); toast('Broadcast channel ready', 'Current run context is attached.'); }
    else if (action === 'focus') focusMode();
    else if (action === 'approval') { $('.comms-pane').scrollIntoView({ behavior: state.reducedMotion ? 'auto' : 'smooth' }); toast('Approval selected', 'Gate G7 is ready for review.'); }
    else toast('Artifact workspace', 'Adapter hook ready for the real artifact route.');
  }

  function wireTabs(selector) {
    $$(selector).forEach(button => button.addEventListener('click', () => {
      $$(selector).forEach(b => { b.classList.remove('active'); b.setAttribute('aria-selected', 'false'); });
      button.classList.add('active'); button.setAttribute('aria-selected', 'true');
      if (button.dataset.tab && button.dataset.tab !== 'live') toast(`${button.textContent.trim()} view`, 'View shell ready for real mission data.');
    }));
  }

  function currentTime() { return new Date().toLocaleTimeString([], { hour12:false, hour:'2-digit', minute:'2-digit', second:'2-digit' }); }

  renderMissions(); renderMessages(); renderActivity(); renderCommands();
  setTheme(state.theme); setDensity(state.density); setReducedMotion(state.reducedMotion);

  $('#searchButton').addEventListener('click', openPalette);
  $('#newMissionButton').addEventListener('click', openDeploy);
  $('#queueAddButton').addEventListener('click', openDeploy);
  $('#settingsButton').addEventListener('click', openSettings);
  $('#settingsClose').addEventListener('click', closeSettings);
  $('#drawerScrim').addEventListener('click', closeSettings);
  $$('.modal-close').forEach(b => b.addEventListener('click', closeDeploy));
  $('#paletteBackdrop').addEventListener('click', e => { if (e.target === e.currentTarget) closePalette(); });
  $('#missionBackdrop').addEventListener('click', e => { if (e.target === e.currentTarget) closeDeploy(); });
  $('#paletteInput').addEventListener('input', e => renderCommands(e.target.value));
  $('#paletteResults').addEventListener('click', e => { const target = e.target.closest('[data-action]'); if (target) commandAction(target.dataset.action); });
  $('#focusButton').addEventListener('click', focusMode);
  $('#recenterButton').addEventListener('click', () => { $('#formationStage').animate([{ transform:'scale(.985)' },{ transform:'scale(1)' }], { duration:240, easing:'ease-out' }); toast('Formation recentered', 'Camera is following Artifact builder.'); });
  $('#popoutComms').addEventListener('click', () => toast('Expanded communications', 'Pop-out route hook is ready for integration.'));
  $('#notificationButton').addEventListener('click', () => toast('3 operational alerts', '1 approval · 1 blocked mission · 1 budget watch'));
  $('#helpButton').addEventListener('click', () => { openPalette(); $('#paletteInput').value = ''; toast('Keyboard controls', '⌘K search · N deploy · F focus · B broadcast · Esc close'); });
  $('#missionSelector').addEventListener('click', () => toast('Campaign switcher', '3 recent campaigns · 1 pinned theatre'));

  $('#pauseRunButton').addEventListener('click', e => {
    state.paused = !state.paused;
    e.currentTarget.innerHTML = state.paused ? '<svg viewBox="0 0 20 20"><path d="m6 4 10 6-10 6V4Z"/></svg>Resume' : '<svg viewBox="0 0 20 20"><path d="M5 4h3v12H5V4Zm7 0h3v12h-3V4Z"/></svg>Pause';
    document.documentElement.classList.toggle('reduce-motion', state.paused || state.reducedMotion);
    renderActivity([currentTime(),'system',state.paused ? '<strong>Execution paused</strong> by operator' : '<strong>Execution resumed</strong> by operator']);
    toast(state.paused ? 'Mission paused' : 'Mission resumed', 'CLIENT-REV-042 · state checkpointed');
  });
  $('#abortRunButton').addEventListener('click', () => toast('Abort requires confirmation', 'Safety hook ready for a typed confirmation workflow.'));

  $('#composerForm').addEventListener('submit', e => {
    e.preventDefault();
    const input = $('#messageInput');
    if (!input.value.trim()) return;
    const item = document.createElement('article');
    item.className = 'message';
    item.innerHTML = `<div class="message-avatar human">PR</div><div class="message-copy"><div class="message-head"><strong>Paul</strong><span>now · operator</span></div><p>${input.value.replace(/[<>]/g, '')}</p></div>`;
    $('#commsFeed').append(item); input.value = ''; $('#commsFeed').scrollTop = $('#commsFeed').scrollHeight;
    toast('Command transmitted', 'Mission squad received the context-linked message.');
  });
  $('#messageInput').addEventListener('keydown', e => { if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') $('#composerForm').requestSubmit(); });
  $('#commsFeed').addEventListener('click', e => { if (e.target.matches('[data-approve]')) { e.target.closest('.message-card').innerHTML = '<strong style="color:var(--success)">APPROVED · GATE G7</strong><p>Decision recorded with operator identity and mission context.</p>'; toast('Gate G7 approved', 'Artifact builder can proceed to publish validation.'); } });

  $$('.node').forEach(node => node.addEventListener('click', () => toast(`${$('h3', node).textContent} inspector`, 'Overview · I/O · runtime · metrics · logs · source')));
  $('#missionQueue').addEventListener('click', e => { const card = e.target.closest('.mission-card'); if (!card) return; $$('.mission-card').forEach(c => c.classList.remove('active')); card.classList.add('active'); toast(card.dataset.mission, 'Mission selection previewed. Real routing belongs in the adapter.'); });
  wireTabs('.view-tabs [role="tab"]'); wireTabs('.queue-tabs [role="tab"]'); wireTabs('.comms-tabs [role="tab"]'); wireTabs('.dock-tabs button');

  $$('[data-theme-value]').forEach(b => b.addEventListener('click', () => setTheme(b.dataset.themeValue)));
  $$('[data-density-value]').forEach(b => b.addEventListener('click', () => setDensity(b.dataset.densityValue)));
  $('#reduceMotionToggle').addEventListener('change', e => setReducedMotion(e.target.checked));
  $('#motionToggle').addEventListener('change', e => document.documentElement.classList.toggle('reduce-motion', !e.target.checked || state.reducedMotion));
  $('#followToggle').addEventListener('change', e => { $('#settingsFollowToggle').checked = e.target.checked; toast(e.target.checked ? 'Following execution' : 'Manual camera enabled', e.target.checked ? 'The active formation stays centered.' : 'Explore without camera recentering.'); });
  $('#settingsFollowToggle').addEventListener('change', e => { $('#followToggle').checked = e.target.checked; });
  $('#resetSettings').addEventListener('click', () => { setTheme('obsidian'); setDensity('compact'); setReducedMotion(false); toast('Defaults restored', 'Obsidian · compact · fluid motion'); });
  $('#saveSettings').addEventListener('click', () => { closeSettings(); toast('Preset saved', `${state.theme} · ${state.density}`); });
  $('#exportSettings').addEventListener('click', () => {
    const config = JSON.stringify({ schemaVersion:1, appearance:{ theme:state.theme, density:state.density }, motion:{ reduced:state.reducedMotion }, diagram:{ followExecution:$('#followToggle').checked } }, null, 2);
    const blob = new Blob([config], { type:'application/json' }); const a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = 'zeus-switchboard-config.json'; a.click(); URL.revokeObjectURL(a.href);
  });
  $('#launchDemoButton').addEventListener('click', () => { closeDeploy(); toast('Mission draft created', 'Formation review is ready. No external action was taken.'); });

  document.addEventListener('keydown', e => {
    const typing = /INPUT|TEXTAREA|SELECT/.test(document.activeElement.tagName);
    if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') { e.preventDefault(); openPalette(); }
    else if (e.key === 'Escape') { closePalette(); closeDeploy(); closeSettings(); }
    else if (!typing && e.key.toLowerCase() === 'n') { e.preventDefault(); openDeploy(); }
    else if (!typing && e.key.toLowerCase() === 'f') { e.preventDefault(); focusMode(); }
    else if (!typing && e.key.toLowerCase() === 'b') { e.preventDefault(); $('#messageInput').focus(); }
  });

  document.addEventListener('visibilitychange', () => document.documentElement.classList.toggle('reduce-motion', document.hidden || state.reducedMotion));
})();
