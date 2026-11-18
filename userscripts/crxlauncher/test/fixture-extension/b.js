(async () => {
  const r = {};
  r.shared = SHARED;
  r.startState = startState;
  r.idleState = document.readyState;
  r.greet = chrome.i18n.getMessage('greet', ['Bob']);
  r.id = chrome.runtime.id;
  r.pong = await chrome.runtime.sendMessage({ type: 'ping', n: 41 });
  r.cbStyle = await new Promise((res) => chrome.runtime.sendMessage({ type: 'ping', n: 1 }, (resp) => res(resp)));
  await chrome.storage.local.set({ fromCs: 7 });
  r.stored = await chrome.storage.local.get(['fromCs', 'installReason']);
  r.hasTabs = typeof chrome.tabs; // content scripts must not get tabs
  const img = new Image(); img.src = chrome.runtime.getURL('icon.png');
  await new Promise((res) => { img.onload = res; img.onerror = res; });
  r.imgWidth = img.naturalWidth;
  r.dataJson = await (await fetch(chrome.runtime.getURL('data.json'))).json();
  const port = chrome.runtime.connect({ name: 'p1' });
  r.portEcho = await new Promise((res) => { port.onMessage.addListener((m) => res(m)); port.postMessage({ hi: 1 }); });
  chrome.runtime.onMessage.addListener((m, s, send) => { if (m.type === 'toCs') send({ fromCs: m.v * 2, title: document.title }); });
  const el = document.createElement('div'); el.className = 'crx-test-el'; el.textContent = 'x'; document.body.append(el);
  r.color = getComputedStyle(el).color;
  r.bg = getComputedStyle(el).backgroundImage.slice(0, 10);
  document.body.dataset.result = JSON.stringify(r);
})().catch((e) => { document.body.dataset.result = JSON.stringify({ error: String(e && e.stack || e) }); });
