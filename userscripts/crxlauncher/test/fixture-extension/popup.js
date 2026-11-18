document.addEventListener('DOMContentLoaded', async () => {
  const out = {};
  out.stored = await chrome.storage.local.get(null);
  out.bg = await chrome.runtime.sendMessage({ type: 'fromPopup' });
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  out.tabUrl = tab.url;
  out.cs = await chrome.tabs.sendMessage(tab.id, { type: 'toCs', v: 21 });
  out.exec = (await chrome.scripting.executeScript({ target: { tabId: tab.id }, func: (a) => document.title + a, args: ['!'] }))[0].result;
  out.h1color = getComputedStyle(document.getElementById('h')).color;
  out.ls = (localStorage.setItem('k', 'v'), localStorage.getItem('k'));
  document.getElementById('h').textContent = JSON.stringify(out);
});
