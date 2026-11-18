importScripts('lib.js');
const bgInfo = { lib: LIB_VALUE, hasWindow: typeof window, hasDocument: typeof document, hasSelf: typeof self };
chrome.runtime.onInstalled.addListener((d) => { chrome.storage.local.set({ installReason: d.reason }); });
chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (msg.type === 'ping') {
    setTimeout(() => sendResponse({ pong: msg.n + 1, bgInfo, senderTab: !!sender.tab, senderUrl: sender.url }), 10);
    return true;
  }
  if (msg.type === 'fromPopup') { sendResponse({ ok: 'bg-got-popup' }); }
});
chrome.runtime.onConnect.addListener((port) => { port.onMessage.addListener((m) => port.postMessage({ echo: m, name: port.name })); });
chrome.contextMenus.create({ id: 'm1', title: 'Test menu %s', contexts: ['selection'] });
chrome.contextMenus.onClicked.addListener((info) => { chrome.storage.local.set({ menuClicked: info.menuItemId }); });
fetch('data.json').then((r) => r.json()).then((j) => chrome.storage.session.set({ bgFetch: j.v }));
