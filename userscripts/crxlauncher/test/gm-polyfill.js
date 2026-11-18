(() => {
  const P = '__gm:';
  const listeners = {};
  let lid = 0;
  window.GM_getValue = (k, d) => { const v = localStorage.getItem(P + k); return v == null ? d : JSON.parse(v); };
  window.GM_setValue = (k, v) => { const o = GM_getValue(k); localStorage.setItem(P + k, JSON.stringify(v)); for (const l of Object.values(listeners)) if (l.k === k) l.f(k, o, v, false); };
  window.GM_deleteValue = (k) => localStorage.removeItem(P + k);
  window.GM_listValues = () => Object.keys(localStorage).filter((k) => k.startsWith(P)).map((k) => k.slice(P.length));
  window.GM_addValueChangeListener = (k, f) => { listeners[++lid] = { k, f }; return lid; };
  window.addEventListener('storage', (e) => { if (!e.key || !e.key.startsWith(P)) return; const k = e.key.slice(P.length); for (const l of Object.values(listeners)) if (l.k === k) l.f(k, e.oldValue && JSON.parse(e.oldValue), e.newValue && JSON.parse(e.newValue), true); });
  window.__menus = [];
  window.GM_registerMenuCommand = (t, f) => { window.__menus.push({ t, f }); return window.__menus.length; };
  window.GM_unregisterMenuCommand = (id) => { window.__menus[id - 1] = null; };
  window.GM_openInTab = (u) => { window.__opened = u; };
  window.GM_notification = (o) => { window.__notif = o; };
  window.GM_download = (o) => { window.__download = o; };
  window.GM_xmlhttpRequest = (o) => {
    fetch(o.url, { method: o.method, headers: o.headers, body: o.data }).then(async (r) => {
      const buf = await r.arrayBuffer();
      let h = ''; r.headers.forEach((v, k) => { h += k + ': ' + v + '\r\n'; });
      o.onload && o.onload({ status: r.status, statusText: r.statusText, response: buf, responseHeaders: h, finalUrl: r.url });
    }, () => o.onerror && o.onerror({}));
    return { abort() {} };
  };
  window.GM_info = { script: { name: 'CRX Runner' }, __crxRunnerTest: (api) => { window.__crx = api; } };
})();
