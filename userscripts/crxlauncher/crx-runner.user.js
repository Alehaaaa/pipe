// ==UserScript==
// @name         CRX Runner
// @namespace    https://github.com/alehaaaa/pipe/userscripts/crx-runner
// @version      2.0.0
// @description  Run a Chrome extension (.crx / .zip / Web Store ID) without installing it, by emulating the chrome.* API. Telemetry-free take on CRXLauncher.
// @match        http://*/*
// @match        https://*/*
// @run-at       document-start
// @grant        GM_getValue
// @grant        GM_setValue
// @grant        GM_deleteValue
// @grant        GM_listValues
// @grant        GM_addValueChangeListener
// @grant        GM_xmlhttpRequest
// @grant        GM_registerMenuCommand
// @grant        GM_openInTab
// @connect      *
// @require      https://cdnjs.cloudflare.com/ajax/libs/jszip/3.10.1/jszip.min.js
// ==/UserScript==

/* global JSZip, GM_getValue, GM_setValue, GM_deleteValue, GM_listValues, GM_addValueChangeListener,
   GM_xmlhttpRequest, GM_registerMenuCommand, GM_openInTab, GM_info */
// On Firefox, use crx-installer-firefox.user.js instead: Firefox runs Chrome extensions natively.

(function () {
  'use strict';
  const TAG = '[crx-runner]';
  const TOP = window.top === window;
  const TAB_ID = 1 + Math.floor(Math.random() * 1e6);
  const later = (f) => setTimeout(f, 0);
  const clone = (v) => (v === undefined ? undefined : JSON.parse(JSON.stringify(v)));
  const whenRoot = (f) => {
    if (document.documentElement) return f();
    const mo = new MutationObserver(() => document.documentElement && (mo.disconnect(), f()));
    mo.observe(document, { childList: true });
  };

  // ───────── install: files live in GM storage as "f:<id>:<path>" ─────────
  const TEXT = /\.(js|css|html?|json|txt|svg)$/i;
  const MIME = { js: 'text/javascript', css: 'text/css', html: 'text/html', htm: 'text/html', json: 'application/json', svg: 'image/svg+xml', png: 'image/png', jpg: 'image/jpeg', jpeg: 'image/jpeg', gif: 'image/gif', webp: 'image/webp', woff2: 'font/woff2', woff: 'font/woff', ttf: 'font/ttf' };
  const mimeOf = (p) => MIME[(/\.(\w+)$/.exec(p) || [])[1]?.toLowerCase()] || 'application/octet-stream';
  const ids = () => GM_getValue('exts', []);
  const parseJson = (t) => JSON.parse(t.replace(/^﻿/, '').replace(/^\s*\/\/.*$/gm, '')); // manifests may hold // comments

  async function install(buf, id) {
    const zip = await JSZip.loadAsync(buf); // reads .crx too: JSZip skips the CRX header
    const mf = Object.keys(zip.files).filter((p) => /(^|\/)manifest\.json$/.test(p)).sort((a, b) => a.length - b.length)[0];
    if (!mf) throw new Error('No manifest.json in package');
    const root = mf.slice(0, -'manifest.json'.length);
    const manifest = parseJson(await zip.file(mf).async('string'));
    id = id || 'x' + [...manifest.name].reduce((h, c) => (h * 31 + c.charCodeAt(0)) >>> 0, 7).toString(16);
    uninstall(id, true);
    const locales = {};
    for (const [full, f] of Object.entries(zip.files)) {
      const p = full.slice(root.length);
      if (f.dir || !full.startsWith(root) || p.startsWith('_metadata/') || p.endsWith('.map')) continue;
      const loc = /^_locales\/([^/]+)\/messages\.json$/.exec(p);
      if (loc) {
        const raw = parseJson(await f.async('string'));
        locales[loc[1]] = Object.fromEntries(Object.entries(raw).map(([k, v]) => [k.toLowerCase(), v]));
      } else if (TEXT.test(p)) GM_setValue(`f:${id}:${p}`, { m: mimeOf(p), t: await f.async('string') });
      else GM_setValue(`f:${id}:${p}`, { m: mimeOf(p), b: await f.async('base64') });
    }
    GM_setValue(`ext:${id}`, { id, manifest, locales, enabled: true, fresh: true });
    if (!ids().includes(id)) GM_setValue('exts', [...ids(), id]);
    return { id, manifest };
  }

  function uninstall(id, keepData) {
    for (const k of GM_listValues()) if (k.startsWith(`f:${id}:`) || (!keepData && k.startsWith(`s:${id}:`))) GM_deleteValue(k);
    if (!keepData) { GM_deleteValue(`ext:${id}`); GM_setValue('exts', ids().filter((x) => x !== id)); }
  }

  const download = (url) => new Promise((ok, fail) => GM_xmlhttpRequest({
    method: 'GET', url, responseType: 'arraybuffer',
    onload: (r) => (r.status === 200 ? ok(r.response) : fail(new Error(`HTTP ${r.status}`))), onerror: () => fail(new Error('Network error')),
  }));
  function installFrom(input) {
    const id = (/(?:^|\/)([a-p]{32})(?:$|[/?#])/.exec(input.trim()) || [])[1];
    if (id) return download(`https://clients2.google.com/service/update2/crx?response=redirect&prodversion=140&acceptformat=crx3&x=id%3D${id}%26uc`).then((b) => install(b, id));
    return download(input.trim()).then((b) => install(b));
  }

  // ───────── a loaded extension: files, URLs, i18n ─────────
  const blobPaths = new Map(); // blob: URL → package path
  const norm = (p) => p.split(/[?#]/)[0].split('/').reduce((a, s) => (s === '..' ? a.slice(0, -1) : s && s !== '.' ? [...a, s] : a), []).join('/');

  function loadExt(id) {
    const meta = GM_getValue(`ext:${id}`, null);
    if (!meta) return null;
    const lang = navigator.language.replace('-', '_');
    const msgs = Object.assign({}, meta.locales[meta.manifest.default_locale], meta.locales[lang.split('_')[0]], meta.locales[lang]);
    const ext = { ...meta, msgs, files: new Map(), urls: new Map(), ctxs: new Set(), menus: new Map() };
    ext.name = i18n(ext, meta.manifest.name);
    return ext;
  }
  function msg(ext, name, subs) {
    name = String(name).toLowerCase();
    if (name === '@@extension_id') return ext.id;
    if (name === '@@ui_locale') return navigator.language.replace('-', '_');
    const m = ext.msgs[name];
    if (!m) return '';
    subs = [].concat(subs ?? []).map(String);
    const ph = Object.fromEntries(Object.entries(m.placeholders || {}).map(([k, v]) => [k.toLowerCase(), v.content]));
    return m.message.replace(/\$(\w+)\$/g, (s, k) => ph[k.toLowerCase()] ?? s).replace(/\$(\d)/g, (s, n) => subs[n - 1] ?? '').replace(/\$\$/g, '$');
  }
  function i18n(ext, s) { return String(s).replace(/__MSG_(\w+)__/g, (_, n) => msg(ext, n)); }
  function file(ext, p) {
    p = norm(p);
    if (!ext.files.has(p)) ext.files.set(p, GM_getValue(`f:${ext.id}:${p}`, null));
    return ext.files.get(p);
  }
  const text = (ext, p) => { const f = file(ext, p); return f ? (f.t ?? atob(f.b)) : null; };
  const blob = (f) => new Blob([f.t ?? Uint8Array.from(atob(f.b), (c) => c.charCodeAt(0))], { type: f.m });
  // Any URL an extension may use for its own files → package path, or null for real web URLs.
  function pathOf(ext, url, base = '') {
    url = String(url);
    if (url.startsWith('chrome-extension://')) return norm(url.replace(/^chrome-extension:\/\/[^/]*/, ''));
    if (blobPaths.has(url)) return blobPaths.get(url);
    if (/^[a-z][\w+.-]*:|^\/\/|^#/i.test(url)) return null;
    return norm(url.startsWith('/') ? url : base.replace(/[^/]*$/, '') + url);
  }
  // runtime.getURL → a blob: URL the page can load (CSS gets its own url()s rewritten too).
  function getURL(ext, p) {
    p = pathOf(ext, p) ?? norm(p);
    if (!ext.urls.has(p)) {
      const f = file(ext, p);
      const u = f ? URL.createObjectURL(f.m === 'text/css' ? new Blob([css(ext, f.t, p)], { type: f.m }) : blob(f)) : `chrome-extension://${ext.id}/${p}`;
      blobPaths.set(u, p);
      ext.urls.set(p, u);
    }
    return ext.urls.get(p);
  }
  function css(ext, t, base) {
    return i18n(ext, t).replace(/url\(\s*(['"]?)([^'")]+)\1\s*\)/g, (m, q, u) => {
      const p = pathOf(ext, u.trim(), base);
      return p != null && file(ext, p) ? `url("${getURL(ext, p)}")` : m;
    });
  }

  // ───────── match patterns ─────────
  const rx = (s) => s.replace(/[.+?^${}()|[\]\\/]/g, '\\$&').replace(/\*/g, '.*');
  function patternRe(p) {
    if (p === '<all_urls>') return /^(https?|file|ftp):/;
    const [, sch, host, path] = /^([^:]+):\/\/([^/]*)(\/.*)?$/.exec(p) || [];
    if (!sch) return /^$/;
    const h = host === '*' ? '[^/]*' : host.startsWith('*.') ? '([^/]*\\.)?' + rx(host.slice(2)) : rx(host);
    return new RegExp(`^${sch === '*' ? 'https?' : rx(sch)}://${h}(:\\d+)?${rx(path || '/*')}$`, 'i');
  }
  function csMatches(cs, url) {
    url = url.split('#')[0];
    const any = (list, f) => (list || []).some((x) => f(x).test(url));
    const glob = (g) => new RegExp('^' + rx(g).replace(/\\\?/g, '.') + '$');
    return any(cs.matches, patternRe) && !any(cs.exclude_matches, patternRe) &&
      (!cs.include_globs?.length || any(cs.include_globs, glob)) && !any(cs.exclude_globs, glob);
  }

  // ───────── chrome.* ─────────
  class Ev {
    constructor() { this.l = []; }
    addListener(f) { this.l.includes(f) || this.l.push(f); }
    removeListener(f) { this.l = this.l.filter((x) => x !== f); }
    hasListener(f) { return this.l.includes(f); }
    hasListeners() { return this.l.length > 0; }
    fire(...a) { for (const f of [...this.l]) try { f(...a); } catch (e) { console.error(TAG, e); } }
  }
  // Everything not implemented below: calls resolve to undefined, events never fire.
  const stub = (name) => new Proxy(function () {}, {
    get: (t, k) => (typeof k === 'symbol' || k === 'then' ? undefined : (t[k] ??= /^on[A-Z]/.test(k) ? new Ev() : stub(`${name}.${k}`))),
    apply: (t, s, args) => { console.debug(TAG, `chrome.${name}() not emulated`); args.find((a) => typeof a === 'function')?.(); return Promise.resolve(); },
  });

  // Make an async function usable with both callbacks and promises; errors go to runtime.lastError.
  const api = (ctx, fn) => (...args) => {
    const cb = typeof args.at(-1) === 'function' ? args.pop() : null;
    const p = Promise.resolve().then(() => fn(...args));
    if (!cb) return p;
    p.then(cb, (e) => { ctx.lastError = { message: e.message }; cb(); ctx.lastError = undefined; });
  };

  function storageArea(ext, ctx, area) {
    const key = `s:${ext.id}:${area}`;
    const mem = (ext.session ??= {});
    const read = () => (area === 'session' ? mem : GM_getValue(key, {}));
    const write = (next) => {
      const before = { ...read() };
      if (area === 'session') { Object.keys(mem).forEach((k) => delete mem[k]); Object.assign(mem, next); } else GM_setValue(key, next);
      later(() => storageChanged(ext, before, next, area));
    };
    const f = (fn) => api(ctx, fn);
    return {
      onChanged: new Ev(),
      get: f((keys) => {
        const d = read();
        if (keys == null) return clone(d);
        if (typeof keys === 'object' && !Array.isArray(keys)) return Object.fromEntries(Object.entries(keys).map(([k, v]) => [k, k in d ? clone(d[k]) : v]));
        return Object.fromEntries([].concat(keys).filter((k) => k in d).map((k) => [k, clone(d[k])]));
      }),
      set: f((items) => write({ ...read(), ...clone(items) })),
      remove: f((keys) => { const d = { ...read() }; [].concat(keys).forEach((k) => delete d[k]); write(d); }),
      clear: f(() => write({})),
      getBytesInUse: f(() => JSON.stringify(read()).length),
    };
  }
  function storageChanged(ext, a = {}, b = {}, area) {
    const ch = {};
    for (const k of new Set([...Object.keys(a), ...Object.keys(b)])) {
      if (JSON.stringify(a[k]) !== JSON.stringify(b[k])) ch[k] = { oldValue: a[k], newValue: b[k] };
    }
    if (!Object.keys(ch).length) return;
    for (const c of ext.ctxs) { c.api.storage.onChanged.fire(clone(ch), area); c.api.storage[area].onChanged.fire(clone(ch)); }
  }

  // One-shot messages: the first sendResponse (or returned promise) wins.
  const deliver = (targets, m, sender) => new Promise((ok, fail) => later(() => {
    const fns = targets.flatMap((t) => t.api.runtime.onMessage.l);
    if (!fns.length) return fail(new Error('Could not establish connection. Receiving end does not exist.'));
    let done = false, wait = false;
    const reply = (v) => { if (!done) { done = true; ok(clone(v)); } };
    for (const f of fns) {
      const r = f(clone(m), sender, reply);
      if (r === true) wait = true;
      else if (r?.then) { wait = true; r.then(reply, fail); }
    }
    if (!wait) reply(undefined);
  }));
  function port(targets, name, sender) {
    const mk = () => ({ name, onMessage: new Ev(), onDisconnect: new Ev() });
    const a = mk(), b = mk();
    for (const [x, y] of [[a, b], [b, a]]) {
      x.postMessage = (m) => later(() => y.onMessage.fire(clone(m), y));
      x.disconnect = () => later(() => y.onDisconnect.fire(y));
    }
    b.sender = sender;
    const t = targets.find((c) => c.api.runtime.onConnect.hasListeners());
    later(() => (t ? t.api.runtime.onConnect.fire(b) : a.onDisconnect.fire(a)));
    return a;
  }

  const tab = () => ({ id: TAB_ID, index: 0, windowId: 1, active: true, url: location.href, title: document.title, status: 'complete' });

  function makeChrome(ext, kind, path = '') {
    const ctx = { kind };
    const f = (fn) => api(ctx, fn);
    const ev = () => new Ev();
    const sender = kind === 'cs' ? { id: ext.id, url: location.href, origin: location.origin, tab: tab(), frameId: TOP ? 0 : 1 } : { id: ext.id, url: `chrome-extension://${ext.id}/${path}` };
    // runtime.* talks to the background and extension pages; tabs.* talks to content scripts.
    const toExt = () => { startBackground(ext); return [...ext.ctxs].filter((c) => c !== ctx && c.kind !== 'cs'); };
    const toTab = () => [...ext.ctxs].filter((c) => c.kind === 'cs');
    const run = (code) => new Function('chrome', 'browser', code).call(window, contentApi(ext), contentApi(ext));

    const runtime = {
      id: ext.id,
      get lastError() { return ctx.lastError; },
      getManifest: () => clone(ext.manifest),
      getURL: (p) => getURL(ext, p),
      sendMessage: f((...a) => deliver(toExt(), a.length > 1 && typeof a[0] === 'string' ? a[1] : a[0], sender)),
      connect: (...a) => port(toExt(), (typeof a[0] === 'string' ? a[1] : a[0])?.name || '', sender),
      onMessage: ev(), onConnect: ev(), onInstalled: ev(), onStartup: ev(),
      openOptionsPage: f(() => openPage(ext, optionsOf(ext), 'page')),
      getPlatformInfo: f(() => ({ os: 'linux', arch: 'x86-64' })),
      reload: () => location.reload(),
    };
    const chrome = {
      runtime,
      extension: { getURL: runtime.getURL, inIncognitoContext: false },
      storage: { local: storageArea(ext, ctx, 'local'), sync: storageArea(ext, ctx, 'sync'), session: storageArea(ext, ctx, 'session'), onChanged: ev() },
      i18n: { getMessage: (n, s) => msg(ext, n, s), getUILanguage: () => navigator.language },
      permissions: { contains: f(() => true), request: f(() => true), getAll: f(() => ({ permissions: ext.manifest.permissions || [], origins: [] })) },
    };
    if (kind !== 'cs') {
      const page = (url) => { const p = pathOf(ext, url || ''); return p && /\.html?$/.test(p) ? p : null; };
      Object.assign(chrome, {
        tabs: {
          query: f(() => [tab()]), get: f(tab), getCurrent: f(() => undefined),
          sendMessage: f((id, m) => deliver(toTab(), m, sender)),
          connect: (id, info) => port(toTab(), info?.name || '', sender),
          create: f(({ url }) => (page(url) ? openPage(ext, page(url), 'page') : GM_openInTab(url, { active: true }), tab())),
          update: f((...a) => { const u = (a.find((x) => typeof x === 'object') || {}).url; if (u) page(u) ? openPage(ext, page(u), 'page') : (location.href = u); return tab(); }),
          executeScript: f((id, d = id) => [run(d.code ?? text(ext, d.file))]), // MV2
          onUpdated: ev(), onActivated: ev(), onRemoved: ev(),
        },
        scripting: {
          // The function is re-created from its source, like Chrome does, so it sees the tab's DOM.
          executeScript: f(async (d) => [{ frameId: 0, result: clone(await (d.func
            ? run(`return (${d.func}).apply(null, ${JSON.stringify(d.args || [])})`)
            : d.files.map((p) => run(text(ext, p))).at(-1))) }]),
          insertCSS: f((d) => addStyle((d.css || '') + (d.files || []).map((p) => css(ext, text(ext, p), p)).join('\n'))),
        },
        action: {
          onClicked: (ext.actionClicked ??= ev()),
          openPopup: f(() => openPage(ext, popupOf(ext), 'popup')),
          setBadgeText: f(() => {}), setTitle: f(() => {}), setIcon: f(() => {}), setPopup: f(() => {}),
        },
        alarms: {
          // Alarms live only as long as the tab: good enough for "check again later" logic.
          create: f((name, info = name) => {
            name = typeof name === 'string' ? name : '';
            clearTimeout((ext.alarms ??= {})[name]);
            const tick = (ms) => { ext.alarms[name] = setTimeout(() => { ext.onAlarm.fire({ name, scheduledTime: Date.now() }); if (info.periodInMinutes) tick(info.periodInMinutes * 6e4); }, ms); };
            tick(info.when ? info.when - Date.now() : (info.delayInMinutes ?? info.periodInMinutes ?? 0) * 6e4);
          }),
          clear: f((name = '') => { clearTimeout(ext.alarms?.[name]); return true; }),
          onAlarm: (ext.onAlarm ??= ev()),
        },
        contextMenus: {
          // Context-menu items become userscript menu commands.
          create: (p, cb) => { ext.menus.set(p.id, p); refreshMenus(); cb && later(cb); return p.id; },
          remove: f((id) => { ext.menus.delete(id); }),
          removeAll: f(() => { ext.menus.clear(); }),
          onClicked: (ext.menuClicked ??= ev()),
        },
      });
      chrome.browserAction = chrome.pageAction = chrome.action;
      chrome.menus = chrome.contextMenus;
    }
    ctx.api = new Proxy(chrome, { get: (t, k) => (k in t || typeof k === 'symbol' ? t[k] : (t[k] = stub(k))) });
    ext.ctxs.add(ctx);
    if (!ext.watching) { // storage changes made in other tabs
      ext.watching = true;
      for (const area of ['local', 'sync']) GM_addValueChangeListener(`s:${ext.id}:${area}`, (k, a, b, remote) => remote && storageChanged(ext, a, b, area));
    }
    return ctx;
  }
  const contentApi = (ext) => (ext.cs ??= makeChrome(ext, 'cs')).api;

  function addStyle(t) {
    const s = new CSSStyleSheet(); // constructable sheets aren't blocked by the site's CSP
    s.replaceSync(t);
    document.adoptedStyleSheets = [...document.adoptedStyleSheets, s];
  }

  // ───────── content scripts ─────────
  // All of an extension's content scripts share one scope (Chrome gives each extension one
  // isolated world). A generator keeps that scope alive across the three run_at phases.
  function runContentScripts(ext) {
    const list = (ext.manifest.content_scripts || []).filter((cs) => (TOP || cs.all_frames) && csMatches(cs, location.href));
    if (!list.length) return false;
    const phases = ['document_start', 'document_end', 'document_idle'];
    const code = [[], [], []];
    for (const cs of list) {
      if (cs.css) whenRoot(() => addStyle(cs.css.map((p) => css(ext, text(ext, p) || '', p)).join('\n')));
      const i = Math.max(0, phases.indexOf(cs.run_at || 'document_idle'));
      for (const p of cs.js || []) {
        // world: "MAIN" scripts go into the page itself, as a <script src="blob:…">.
        if (cs.world === 'MAIN') code[i].push(`document.documentElement.append(Object.assign(document.createElement('script'), { src: chrome.runtime.getURL(${JSON.stringify(p)}) }));`);
        else code[i].push(`/* ${p} */\n${text(ext, p) ?? ''}\n;`);
      }
    }
    const capi = contentApi(ext);
    let gen = new Function('chrome', 'browser', `return function* () { void 0;\n${code.map((c) => c.join('\n')).join('\nyield;\n')}\n}`)(capi, capi).call(window);
    const step = () => { try { gen?.next(); } catch (e) { gen = null; console.error(TAG, ext.name, e); } };
    whenRoot(step); // document_start
    const end = () => { step(); document.readyState === 'complete' ? later(step) : addEventListener('load', step, { once: true }); };
    document.readyState === 'loading' ? document.addEventListener('DOMContentLoaded', end, { once: true }) : end();
    return true;
  }

  // ───────── background & extension pages ─────────
  // Both run in an about:blank iframe used as their "window". The code is evaluated in the
  // userscript sandbox with `with (iframeWindow)`, so the site's CSP can't block it.
  let shadow;
  function ui() {
    if (shadow) return shadow;
    const host = document.createElement('crx-runner');
    shadow = host.attachShadow({ mode: 'closed' });
    document.documentElement.append(host);
    return shadow;
  }
  function evalIn(ext, iw, ctx, code, name) {
    Object.assign(iw, { chrome: ctx.api, browser: ctx.api });
    iw.fetch = (u, init) => { // privileged fetch: package files locally, everything else cross-origin
      const p = pathOf(ext, u.url || u);
      if (p != null) { const fl = file(ext, p); return Promise.resolve(fl ? new Response(blob(fl)) : new Response('', { status: 404 })); }
      return new Promise((ok, fail) => GM_xmlhttpRequest({
        method: init?.method || 'GET', url: String(u.url || u), headers: init?.headers, data: init?.body, responseType: 'blob',
        onload: (r) => ok(new Response(r.response, { status: r.status, statusText: r.statusText })), onerror: () => fail(new TypeError('Failed to fetch')),
      }));
    };
    try { new Function('__w', `with (__w) { void 0;\n${code}\n}`).call(iw, iw); } catch (e) { console.error(TAG, ext.name, name, e); }
  }

  function startBackground(ext) {
    if (ext.bgStarted || !TOP || !ext.manifest.background) return;
    ext.bgStarted = true;
    const bg = ext.manifest.background;
    let files = bg.service_worker ? [bg.service_worker] : bg.scripts || [];
    if (bg.page) files = [...new DOMParser().parseFromString(text(ext, bg.page) || '', 'text/html').querySelectorAll('script[src]')].map((s) => pathOf(ext, s.getAttribute('src'), bg.page));
    // importScripts('a.js') → inline a.js, so everything shares one scope.
    const inline = (code, base) => code.replace(/importScripts\s*\(([^)]*)\)/g, (m, args) => [...args.matchAll(/['"`]([^'"`]+)['"`]/g)].map(([, p]) => inline(text(ext, pathOf(ext, p, base)) || '', base)).join(';\n'));
    const code = files.map((p) => inline(text(ext, p) || '', p)).join('\n;\n');
    const ctx = makeChrome(ext, 'bg', files[0] || '');
    whenRoot(() => {
      const fr = document.createElement('iframe');
      fr.style.display = 'none';
      ui().append(fr);
      evalIn(ext, fr.contentWindow, ctx, code, files[0]);
      if (ext.fresh) { // first run after install
        GM_setValue(`ext:${ext.id}`, { ...GM_getValue(`ext:${ext.id}`), fresh: false });
        later(() => ctx.api.runtime.onInstalled.fire({ reason: 'install' }));
      }
    });
  }

  const popupOf = (ext) => (ext.manifest.action || ext.manifest.browser_action || ext.manifest.page_action || {}).default_popup;
  const optionsOf = (ext) => ext.manifest.options_ui?.page || ext.manifest.options_page;

  function openPage(ext, path, kind) {
    path = norm(path || '');
    const html = text(ext, path);
    if (html == null) return console.warn(TAG, 'page not found', path);
    startBackground(ext);
    ext.overlay?.close();
    const doc = new DOMParser().parseFromString(html, 'text/html');
    const scripts = [...doc.querySelectorAll('script')].map((s) => (s.remove(), s.hasAttribute('src') ? text(ext, pathOf(ext, s.getAttribute('src'), path)) : s.textContent));
    const styles = [...doc.querySelectorAll('link[rel=stylesheet], style')].map((n) => {
      n.remove();
      if (n.tagName === 'STYLE') return css(ext, n.textContent, path);
      const p = pathOf(ext, n.getAttribute('href'), path);
      return css(ext, text(ext, p) || '', p);
    });
    for (const n of doc.querySelectorAll('[src], link[href]')) {
      const a = n.hasAttribute('src') ? 'src' : 'href', p = pathOf(ext, n.getAttribute(a), path);
      if (p != null) n.setAttribute(a, getURL(ext, p));
    }

    const box = document.createElement('div');
    box.style.cssText = `position:fixed;z-index:2147483647;${kind === 'popup' ? 'top:8px;right:8px' : 'inset:5vh 5vw'};background:#fff;border-radius:8px;box-shadow:0 8px 32px #0006;overflow:hidden;display:flex;flex-direction:column`;
    const bar = Object.assign(document.createElement('div'), { textContent: `${ext.name}  ✕` });
    bar.style.cssText = 'font:600 12px system-ui;padding:6px 10px;cursor:pointer;background:#eee;color:#222;text-align:right';
    const fr = document.createElement('iframe');
    fr.style.cssText = 'border:0;flex:1;width:100%;min-width:200px';
    box.append(bar, fr);
    ui().append(box);
    const ctx = makeChrome(ext, 'page', path);
    ext.overlay = { close: () => { box.remove(); ext.ctxs.delete(ctx); ext.overlay = null; } };
    bar.onclick = ext.overlay.close;

    const iw = fr.contentWindow, d = iw.document;
    d.open(); d.write('<!DOCTYPE html><html><head></head><body></body></html>'); d.close();
    d.head.append(...[...doc.head.childNodes].map((n) => d.importNode(n, true)));
    d.body.append(...[...doc.body.childNodes].map((n) => d.importNode(n, true)));
    d.adoptedStyleSheets = styles.map((t) => { const s = new iw.CSSStyleSheet(); s.replaceSync(t); return s; });
    iw.close = ext.overlay.close;
    if (kind === 'popup') { // size to content, like Chrome's popup bubble
      d.documentElement.style.width = 'max-content';
      const fit = () => { fr.style.width = Math.min(800, d.documentElement.getBoundingClientRect().width) + 'px'; fr.style.height = Math.min(600, d.documentElement.scrollHeight) + 'px'; };
      new iw.ResizeObserver(fit).observe(d.body);
    }
    evalIn(ext, iw, ctx, scripts.filter(Boolean).join('\n;\n'), path);
    d.dispatchEvent(new iw.Event('DOMContentLoaded'));
    iw.dispatchEvent(new iw.Event('load'));
    return box;
  }

  // ───────── menu & manager ─────────
  const loaded = [];
  const menuIds = new Set();
  function refreshMenus() {
    if (!TOP) return;
    const add = (key, title, fn) => { if (!menuIds.has(key)) { menuIds.add(key); GM_registerMenuCommand(title, fn); } };
    add('mgr', '⚙ CRX Runner: manage', manager);
    for (const ext of loaded) {
      add(`a:${ext.id}`, `▶ ${ext.name}`, () => (popupOf(ext) ? openPage(ext, popupOf(ext), 'popup') : (startBackground(ext), later(() => ext.actionClicked?.fire(tab())))));
      if (optionsOf(ext)) add(`o:${ext.id}`, `⚙ ${ext.name}: options`, () => openPage(ext, optionsOf(ext), 'page'));
      for (const m of ext.menus.values()) {
        if (!m.title) continue;
        add(`m:${ext.id}:${m.id}`, `☰ ${m.title.replace('%s', '…')}`, () => {
          if (!ext.menus.has(m.id)) return;
          const info = { menuItemId: m.id, pageUrl: location.href, selectionText: String(getSelection()) || undefined };
          m.onclick?.(info, tab());
          ext.menuClicked?.fire(info, tab());
        });
      }
    }
  }

  // A file picker must be opened by a click on the page itself, so the manager is a tiny panel.
  function manager() {
    const el = (tag, props) => Object.assign(document.createElement(tag), props);
    const box = el('div');
    box.style.cssText = 'position:fixed;z-index:2147483647;top:8px;right:8px;width:340px;background:#fff;color:#222;font:13px system-ui;border-radius:8px;box-shadow:0 8px 32px #0006;padding:12px;display:grid;gap:8px';
    const status = el('div');
    const items = el('div');
    const list = () => items.replaceChildren(...ids().map((id) => {
      const row = el('div', { textContent: `${loadExt(id)?.name || id} ` });
      row.append(el('button', { textContent: 'Remove', onclick: () => { uninstall(id); list(); } }));
      return row;
    }));
    const run = (p) => { status.textContent = 'Working…'; p.then((r) => { status.textContent = `Installed ${r.manifest.name}. Reload the page.`; list(); }, (e) => { status.textContent = e.message; }); };
    const fileIn = el('input', { type: 'file', accept: '.crx,.zip', onchange: () => run(fileIn.files[0].arrayBuffer().then((b) => install(b))) });
    const urlIn = el('input', { placeholder: 'Web Store URL / ID or .crx URL, then Enter', onkeydown: (e) => e.key === 'Enter' && run(installFrom(urlIn.value)) });
    box.append(fileIn, urlIn, status, items, el('button', { textContent: 'Close', onclick: () => box.remove() }));
    ui().append(box);
    list();
  }

  // ───────── boot ─────────
  for (const id of ids()) {
    const ext = loadExt(id);
    if (!ext?.enabled) continue;
    loaded.push(ext);
    // Start the background right away where it's likely needed; otherwise on first use.
    if (runContentScripts(ext) || ext.fresh || ext.manifest.permissions?.includes('contextMenus')) startBackground(ext);
  }
  refreshMenus();
  if (typeof GM_info !== 'undefined' && typeof GM_info.__crxRunnerTest === 'function') GM_info.__crxRunnerTest({ install, installFrom, uninstall, loaded, openPage, manager });
})();
