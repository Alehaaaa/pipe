// ==UserScript==
// @name         CRX Runner
// @namespace    https://github.com/alehaaaa/pipe/userscripts/crx-runner
// @version      1.0.0
// @description  Run Chrome extensions (.crx / .zip / Web Store ID) inside a userscript: content scripts, storage, messaging, i18n, popup & options pages, background emulation. A telemetry-free re-implementation of the CRXLauncher idea.
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
// @grant        GM_unregisterMenuCommand
// @grant        GM_openInTab
// @grant        GM_notification
// @grant        GM_download
// @grant        unsafeWindow
// @connect      clients2.google.com
// @connect      clients2.googleusercontent.com
// @connect      *
// @require      https://cdnjs.cloudflare.com/ajax/libs/jszip/3.10.1/jszip.min.js
// ==/UserScript==

/* global JSZip, GM_getValue, GM_setValue, GM_deleteValue, GM_listValues, GM_addValueChangeListener,
   GM_xmlhttpRequest, GM_registerMenuCommand, GM_unregisterMenuCommand, GM_openInTab,
   GM_notification, GM_download, GM_info */

(function () {
  'use strict';

  // ───────────────────────────── basics ─────────────────────────────
  const TAG = '[crx-runner]';
  const IS_TOP = window.top === window;
  const TAB_ID = 1 + Math.floor(Math.random() * 1e6); // stable for this page load
  const warned = new Set();
  const log = (...a) => console.log(TAG, ...a);
  const warn = (...a) => console.warn(TAG, ...a);
  const warnOnce = (k, ...a) => { if (!warned.has(k)) { warned.add(k); warn(...a); } };
  const clone = (v) => (v === undefined ? undefined : JSON.parse(JSON.stringify(v)));
  const later = (fn) => setTimeout(fn, 0);
  const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

  const K = {
    list: 'exts',
    meta: (id) => `ext:${id}`,
    file: (id, p) => `file:${id}:${p}`,
    store: (id, area) => `store:${id}:${area}`,
    ls: (id) => `ls:${id}`,
  };

  const MIME = {
    js: 'text/javascript', mjs: 'text/javascript', css: 'text/css', html: 'text/html', htm: 'text/html',
    json: 'application/json', txt: 'text/plain', svg: 'image/svg+xml', xml: 'application/xml',
    png: 'image/png', jpg: 'image/jpeg', jpeg: 'image/jpeg', gif: 'image/gif', webp: 'image/webp',
    ico: 'image/x-icon', bmp: 'image/bmp', woff: 'font/woff', woff2: 'font/woff2', ttf: 'font/ttf',
    otf: 'font/otf', eot: 'application/vnd.ms-fontobject', wasm: 'application/wasm', mp3: 'audio/mpeg',
    wav: 'audio/wav', ogg: 'audio/ogg', mp4: 'video/mp4', webm: 'video/webm',
  };
  const TEXT_EXT = new Set(['js', 'mjs', 'css', 'html', 'htm', 'json', 'txt', 'svg', 'xml']);
  const extOf = (p) => (/\.([a-z0-9]+)$/i.exec(p) || [])[1]?.toLowerCase() || '';

  // Permissions this emulator cannot provide (shown in the manager).
  const UNSUPPORTED_PERMS = new Set([
    'webRequest', 'webRequestBlocking', 'declarativeNetRequest', 'declarativeNetRequestWithHostAccess',
    'declarativeNetRequestFeedback', 'proxy', 'debugger', 'nativeMessaging', 'cookies', 'history',
    'bookmarks', 'management', 'privacy', 'tabCapture', 'desktopCapture', 'offscreen', 'sidePanel',
    'webNavigation', 'browsingData', 'topSites', 'tabGroups', 'sessions', 'pageCapture', 'devtools',
    'enterprise.platformKeys', 'fontSettings', 'gcm', 'identity', 'idle', 'power', 'system.cpu',
    'system.memory', 'system.storage', 'tts', 'ttsEngine', 'userScripts', 'vpnProvider', 'wallpaper',
  ]);

  // ───────────────────────────── binary helpers ─────────────────────────────
  function b64encode(u8) {
    let s = '';
    for (let i = 0; i < u8.length; i += 0x8000) s += String.fromCharCode.apply(null, u8.subarray(i, i + 0x8000));
    return btoa(s);
  }
  function b64decode(b64) {
    const s = atob(b64);
    const u8 = new Uint8Array(s.length);
    for (let i = 0; i < s.length; i++) u8[i] = s.charCodeAt(i);
    return u8;
  }
  const idFromBytes = (b) => Array.from(b.slice(0, 16), (x) => String.fromCharCode(97 + (x >> 4)) + String.fromCharCode(97 + (x & 15))).join('');
  async function sha256(u8) { return new Uint8Array(await crypto.subtle.digest('SHA-256', u8)); }

  // Minimal protobuf walker, enough to read the CRX3 header's crx_id.
  function pbFields(u8) {
    const out = [];
    let i = 0;
    const varint = () => { let r = 0, s = 0, b; do { b = u8[i++]; r += (b & 0x7f) * 2 ** s; s += 7; } while (b & 0x80); return r; };
    while (i < u8.length) {
      const key = varint(), field = Math.floor(key / 8), wt = key & 7;
      if (wt === 0) out.push({ field, value: varint() });
      else if (wt === 2) { const len = varint(); out.push({ field, bytes: u8.subarray(i, i + len) }); i += len; }
      else if (wt === 5) i += 4;
      else if (wt === 1) i += 8;
      else break;
    }
    return out;
  }

  function unpackCrx(buf) {
    const u8 = new Uint8Array(buf);
    const dv = new DataView(buf);
    if (u8[0] === 0x43 && u8[1] === 0x72 && u8[2] === 0x32 && u8[3] === 0x34) { // "Cr24"
      const ver = dv.getUint32(4, true);
      if (ver === 2) {
        const pk = dv.getUint32(8, true), sig = dv.getUint32(12, true);
        return { zip: buf.slice(16 + pk + sig), pubKey: u8.slice(16, 16 + pk) };
      }
      if (ver === 3) {
        const hl = dv.getUint32(8, true);
        let crxId = null;
        try {
          const signed = pbFields(u8.subarray(12, 12 + hl)).find((f) => f.field === 10000);
          const idf = signed && pbFields(signed.bytes).find((f) => f.field === 1);
          if (idf && idf.bytes.length === 16) crxId = idFromBytes(idf.bytes);
        } catch (e) { /* ignore */ }
        return { zip: buf.slice(12 + hl), crxId };
      }
      throw new Error('Unsupported CRX version ' + ver);
    }
    return { zip: buf };
  }

  function parseJsonLoose(text) {
    text = text.replace(/^﻿/, '');
    try { return JSON.parse(text); } catch (e) { /* Chrome tolerates comments in manifest.json */ }
    let out = '', inStr = false;
    for (let i = 0; i < text.length; i++) {
      const c = text[i], n = text[i + 1];
      if (inStr) { out += c; if (c === '\\') { out += n; i++; } else if (c === '"') inStr = false; continue; }
      if (c === '"') { inStr = true; out += c; continue; }
      if (c === '/' && n === '/') { while (i < text.length && text[i] !== '\n') i++; out += '\n'; continue; }
      if (c === '/' && n === '*') { i += 2; while (i < text.length && !(text[i] === '*' && text[i + 1] === '/')) i++; i++; continue; }
      out += c;
    }
    return JSON.parse(out.replace(/,(\s*[}\]])/g, '$1'));
  }

  // ───────────────────────────── installation ─────────────────────────────
  const listIds = () => GM_getValue(K.list, []);

  async function installFromBuffer(buf, source) {
    if (typeof JSZip === 'undefined') throw new Error('JSZip failed to load (@require)');
    const { zip, pubKey, crxId } = unpackCrx(buf);
    const z = await JSZip.loadAsync(zip);
    const all = {};
    z.forEach((p, entry) => { if (!entry.dir) all[p.replace(/^\.?\//, '')] = entry; });
    let root = '';
    if (!all['manifest.json']) {
      const m = Object.keys(all).filter((p) => /(^|\/)manifest\.json$/.test(p)).sort((a, b) => a.length - b.length)[0];
      if (!m) throw new Error('No manifest.json found in archive');
      root = m.slice(0, -'manifest.json'.length);
    }
    const files = {};
    for (const p in all) if (p.startsWith(root)) files[p.slice(root.length)] = all[p];
    const manifest = parseJsonLoose(await files['manifest.json'].async('string'));

    let id = source && source.id;
    if (!id && crxId) id = crxId;
    if (!id && pubKey) id = idFromBytes(await sha256(pubKey));
    if (!id && manifest.key) { try { id = idFromBytes(await sha256(b64decode(manifest.key))); } catch (e) { /* ignore */ } }
    if (!id) id = idFromBytes(await sha256(new TextEncoder().encode('crx-runner:' + manifest.name)));

    const prev = GM_getValue(K.meta(id), null);
    removeFiles(id);

    const locales = {};
    let bytes = 0;
    for (const [p, entry] of Object.entries(files)) {
      if (p.startsWith('_metadata/') || p.endsWith('.map')) continue;
      const ext = extOf(p);
      const m = MIME[ext] || 'application/octet-stream';
      let rec;
      if (TEXT_EXT.has(ext)) { const t = await entry.async('string'); rec = { m, t }; bytes += t.length; }
      else { const u = await entry.async('uint8array'); rec = { m, b: b64encode(u) }; bytes += u.length; }
      const lm = /^_locales\/([^/]+)\/messages\.json$/i.exec(p);
      if (lm) {
        try {
          const raw = parseJsonLoose(rec.t);
          const msgs = {};
          for (const k in raw) {
            const ph = {};
            for (const pk in raw[k].placeholders || {}) ph[pk.toLowerCase()] = raw[k].placeholders[pk];
            msgs[k.toLowerCase()] = { message: raw[k].message, placeholders: ph };
          }
          locales[lm[1]] = msgs;
        } catch (e) { warn('bad locale file', p, e); }
        continue;
      }
      GM_setValue(K.file(id, p), rec);
    }

    const meta = {
      id,
      manifest,
      locales,
      enabled: prev ? prev.enabled : true,
      runBackground: prev ? prev.runBackground : true,
      installedAt: prev ? prev.installedAt : Date.now(),
      updatedAt: Date.now(),
      previousVersion: prev ? prev.manifest.version : null,
      installEventPending: prev ? (prev.manifest.version !== manifest.version ? 'update' : null) : 'install',
      source: source || { type: 'file' },
      bytes,
    };
    GM_setValue(K.meta(id), meta);
    const ids = listIds();
    if (!ids.includes(id)) { ids.push(id); GM_setValue(K.list, ids); }
    return meta;
  }

  function removeFiles(id) {
    const prefix = `file:${id}:`;
    for (const k of GM_listValues()) if (k.startsWith(prefix)) GM_deleteValue(k);
  }

  function uninstall(id) {
    for (const k of GM_listValues()) {
      if (k.startsWith(`file:${id}:`) || k.startsWith(`store:${id}:`) || k === K.ls(id)) GM_deleteValue(k);
    }
    GM_deleteValue(K.meta(id));
    GM_setValue(K.list, listIds().filter((x) => x !== id));
  }

  function gmGetBuffer(url) {
    return new Promise((resolve, reject) => {
      GM_xmlhttpRequest({
        method: 'GET', url, responseType: 'arraybuffer',
        onload: (r) => (r.status >= 200 && r.status < 300 && r.response ? resolve(r.response) : reject(new Error(`HTTP ${r.status} for ${url}`))),
        onerror: () => reject(new Error('Network error for ' + url)),
        ontimeout: () => reject(new Error('Timeout for ' + url)),
      });
    });
  }

  function webStoreDownloadUrl(id) {
    const v = (/Chrome\/([\d.]+)/.exec(navigator.userAgent) || [])[1] || '130.0.0.0';
    return `https://clients2.google.com/service/update2/crx?response=redirect&prodversion=${v}&acceptformat=crx2,crx3&x=id%3D${id}%26uc`;
  }

  async function installFromInput(input) {
    input = input.trim();
    const cws = /(?:^|[/=])([a-p]{32})(?:$|[/?#&])/.exec(input);
    if (cws && !/\.(crx|zip)(\?|$)/i.test(input)) {
      const id = cws[1];
      return installFromBuffer(await gmGetBuffer(webStoreDownloadUrl(id)), { type: 'webstore', id, url: input });
    }
    if (/^https?:\/\//i.test(input)) return installFromBuffer(await gmGetBuffer(input), { type: 'url', url: input });
    throw new Error('Enter a Chrome Web Store URL / 32-letter extension ID, or a direct .crx/.zip URL');
  }

  // ───────────────────────────── loaded extension model ─────────────────────────────
  const uiLocale = (navigator.language || 'en').replace('-', '_');
  const blobToPath = new Map(); // blob url -> {id, path}

  function loadExt(id) {
    const meta = GM_getValue(K.meta(id), null);
    if (!meta) return null;
    const def = meta.manifest.default_locale;
    const order = [uiLocale, uiLocale.split('_')[0], def].filter(Boolean);
    const messages = Object.assign({}, ...[...order].reverse().map((l) => meta.locales[l] || {}));
    const ext = { ...meta, messages, fileCache: new Map(), urlCache: new Map() };
    ext.name = localize(ext, meta.manifest.name || id);
    return ext;
  }

  function getMessage(ext, name, subs) {
    name = String(name).toLowerCase();
    if (name === '@@extension_id') return ext.id;
    if (name === '@@ui_locale') return uiLocale;
    if (name === '@@bidi_dir') return 'ltr';
    if (name === '@@bidi_reversed_dir') return 'rtl';
    if (name === '@@bidi_start_edge') return 'left';
    if (name === '@@bidi_end_edge') return 'right';
    const msg = ext.messages[name];
    if (!msg) return '';
    subs = subs == null ? [] : Array.isArray(subs) ? subs.map(String) : [String(subs)];
    const sub = (s) => s.replace(/\$(\d)/g, (m, n) => subs[n - 1] ?? '');
    let text = msg.message.replace(/\$([a-z0-9_@]+)\$/gi, (m, p) => {
      const ph = msg.placeholders[p.toLowerCase()];
      return ph ? sub(ph.content) : m;
    });
    return sub(text).replace(/\$\$/g, '$');
  }
  const localize = (ext, s) => (typeof s === 'string' ? s.replace(/__MSG_(\w+)__/g, (m, n) => getMessage(ext, n)) : s);

  function readFile(ext, path) {
    path = normPath(path);
    if (!ext.fileCache.has(path)) ext.fileCache.set(path, GM_getValue(K.file(ext.id, path), null));
    return ext.fileCache.get(path);
  }
  const fileText = (f) => (f ? (f.t !== undefined ? f.t : new TextDecoder().decode(b64decode(f.b))) : null);
  const fileBlob = (f) => new Blob([f.t !== undefined ? f.t : b64decode(f.b)], { type: f.m });
  function normPath(p) {
    const parts = [];
    for (const s of String(p).split(/[?#]/)[0].split('/')) {
      if (s === '' || s === '.') continue;
      if (s === '..') parts.pop(); else parts.push(decodeURIComponent(s));
    }
    return parts.join('/');
  }
  function fileUrl(ext, path) {
    path = normPath(path);
    if (ext.urlCache.has(path)) return ext.urlCache.get(path);
    const f = readFile(ext, path);
    let url = null;
    if (f) {
      if (f.m === 'text/css') {
        url = URL.createObjectURL(new Blob([processCss(ext, f.t, path)], { type: f.m }));
      } else {
        url = URL.createObjectURL(fileBlob(f));
      }
      blobToPath.set(url, { id: ext.id, path });
    }
    ext.urlCache.set(path, url);
    return url;
  }
  function fileDataUrl(ext, path) {
    const f = readFile(ext, path);
    if (!f) return null;
    return `data:${f.m};base64,` + (f.b !== undefined ? f.b : b64encode(new TextEncoder().encode(f.t)));
  }
  // Map any URL an extension may use for its own files to a package path (or null).
  function extPath(ext, url, base = '') {
    url = String(url);
    const pre = 'chrome-extension://';
    if (url.startsWith(pre)) { const rest = url.slice(pre.length); return normPath(rest.slice(rest.indexOf('/') + 1)); }
    if (blobToPath.has(url)) return blobToPath.get(url).path;
    if (/^[a-z][a-z0-9+.-]*:/i.test(url) || url.startsWith('//') || url.startsWith('#')) return null;
    if (url.startsWith('/')) return normPath(url);
    const dir = base.includes('/') ? base.slice(0, base.lastIndexOf('/') + 1) : '';
    return normPath(dir + url);
  }
  function getURL(ext, path) {
    const p = extPath(ext, path) ?? normPath(path);
    return fileUrl(ext, p) || `chrome-extension://${ext.id}/${p}`;
  }
  function processCss(ext, css, basePath = '') {
    css = localize(ext, css);
    return css.replace(/url\(\s*(['"]?)([^'")]+)\1\s*\)/g, (m, q, u) => {
      const p = extPath(ext, u.trim(), basePath);
      if (p == null) return m;
      const b = fileUrl(ext, p);
      return b ? `url("${b}")` : m;
    });
  }

  // ───────────────────────────── match patterns ─────────────────────────────
  const reEsc = (s) => s.replace(/[.*+?^${}()|[\]\\/]/g, '\\$&');
  const reCache = new Map();
  function patternRe(p) {
    if (reCache.has(p)) return reCache.get(p);
    let re;
    if (p === '<all_urls>') re = /^(https?|wss?|file|ftp):\/\//;
    else {
      const m = /^(\*|https?|wss?|file|ftp|urn):\/\/([^/]*)(\/.*)?$/.exec(p);
      if (!m) re = /^\b$/;
      else {
        const [, scheme, host, path = '/*'] = m;
        let s = '^' + (scheme === '*' ? 'https?' : reEsc(scheme)) + ':\\/\\/';
        if (host === '*') s += '[^/]*';
        else if (host.startsWith('*.')) s += '(?:[^/]*\\.)?' + reEsc(host.slice(2));
        else s += reEsc(host);
        if (!host.includes(':')) s += '(?::\\d+)?';
        s += reEsc(path).replace(/\\\*/g, '.*') + '$';
        re = new RegExp(s, 'i');
      }
    }
    reCache.set(p, re);
    return re;
  }
  const globRe = (g) => new RegExp('^' + reEsc(g).replace(/\\\*/g, '.*').replace(/\\\?/g, '.') + '$');
  function csMatches(cs, url) {
    const u = url.split('#')[0];
    if (!(cs.matches || []).some((p) => patternRe(p).test(u))) return false;
    if ((cs.exclude_matches || []).some((p) => patternRe(p).test(u))) return false;
    if (cs.include_globs && cs.include_globs.length && !cs.include_globs.some((g) => globRe(g).test(u))) return false;
    if ((cs.exclude_globs || []).some((g) => globRe(g).test(u))) return false;
    return true;
  }

  // ───────────────────────────── chrome.* emulation ─────────────────────────────
  class Ev {
    constructor() { this.l = []; }
    addListener(f) { if (typeof f === 'function' && !this.l.includes(f)) this.l.push(f); }
    removeListener(f) { this.l = this.l.filter((x) => x !== f); }
    hasListener(f) { return this.l.includes(f); }
    hasListeners() { return this.l.length > 0; }
    fire(...a) { for (const f of [...this.l]) { try { f(...a); } catch (e) { console.error(TAG, e); } } }
  }

  const buses = new Map();       // ext id -> Set of contexts
  const sessionStores = new Map();
  const bus = (ext) => { if (!buses.has(ext.id)) buses.set(ext.id, new Set()); return buses.get(ext.id); };

  const TAB = {
    id: TAB_ID, index: 0, windowId: 1, active: true, highlighted: true, selected: true, pinned: false,
    incognito: false, status: 'complete', discarded: false, autoDiscardable: true, groupId: -1,
    get url() { return location.href; }, get title() { return document.title; },
    get favIconUrl() { const l = document.querySelector('link[rel~="icon"]'); return l ? l.href : ''; },
  };
  const tabSnapshot = () => ({ ...TAB, url: location.href, title: document.title, favIconUrl: TAB.favIconUrl });

  // Turn an async implementation into a chrome-style API that supports both callbacks and promises.
  function apiFn(ctx, fn) {
    return function (...args) {
      const cb = typeof args[args.length - 1] === 'function' ? args.pop() : null;
      const p = Promise.resolve().then(() => fn.apply(this, args));
      if (!cb) return p;
      p.then((r) => cb(r), (e) => {
        ctx.lastError = { message: String((e && e.message) || e) };
        try { cb(); } finally { ctx.lastError = undefined; }
      });
      return undefined;
    };
  }

  function stubNS(path) {
    const store = {};
    return new Proxy(function () {}, {
      get(t, k) {
        if (typeof k === 'symbol' || k === 'then') return undefined;
        if (!(k in store)) store[k] = /^on[A-Z]/.test(k) ? new Ev() : stubNS(path + '.' + k);
        return store[k];
      },
      set(t, k, v) { store[k] = v; return true; },
      apply(t, self, args) {
        warnOnce(path, `chrome.${path}() is not emulated`);
        const cb = args.find((a) => typeof a === 'function');
        if (cb) later(cb);
        return Promise.resolve(undefined);
      },
    });
  }

  // storage.onChanged plumbing
  function fireStorage(ext, changes, area) {
    if (!Object.keys(changes).length) return;
    for (const ctx of bus(ext)) {
      ctx.api.storage.onChanged.fire(clone(changes), area);
      ctx.api.storage[area].onChanged.fire(clone(changes));
    }
  }
  function diff(oldObj = {}, newObj = {}) {
    const ch = {};
    for (const k of new Set([...Object.keys(oldObj), ...Object.keys(newObj)])) {
      const a = JSON.stringify(oldObj[k]), b = JSON.stringify(newObj[k]);
      if (a !== b) { ch[k] = {}; if (k in oldObj) ch[k].oldValue = oldObj[k]; if (k in newObj) ch[k].newValue = newObj[k]; }
    }
    return ch;
  }
  const watchedStores = new Set();
  function watchStorage(ext) {
    if (watchedStores.has(ext.id) || typeof GM_addValueChangeListener !== 'function') return;
    watchedStores.add(ext.id);
    for (const area of ['local', 'sync']) {
      GM_addValueChangeListener(K.store(ext.id, area), (k, o, n, remote) => { if (remote) fireStorage(ext, diff(o, n), area); });
    }
  }

  function makeStorageArea(ext, ctx, area) {
    const key = K.store(ext.id, area);
    const read = () => (area === 'session' ? (sessionStores.get(ext.id) || {}) : GM_getValue(key, {}));
    const write = (obj, before) => {
      if (area === 'session') sessionStores.set(ext.id, obj); else GM_setValue(key, obj);
      const ch = diff(before, obj);
      later(() => fireStorage(ext, ch, area));
    };
    const f = (fn) => apiFn(ctx, fn);
    return {
      QUOTA_BYTES: area === 'sync' ? 102400 : 10485760,
      onChanged: new Ev(),
      get: f((keys) => {
        const data = read();
        if (keys == null) return clone(data);
        if (typeof keys === 'string') keys = [keys];
        const r = {};
        if (Array.isArray(keys)) { for (const k of keys) if (k in data) r[k] = clone(data[k]); return r; }
        for (const k in keys) r[k] = k in data ? clone(data[k]) : keys[k];
        return r;
      }),
      getKeys: f(() => Object.keys(read())),
      set: f((items) => {
        const before = read(), data = { ...before };
        for (const k in items) { if (items[k] === undefined) continue; data[k] = clone(items[k]); }
        write(data, before);
      }),
      remove: f((keys) => {
        const before = read(), data = { ...before };
        for (const k of [].concat(keys)) delete data[k];
        write(data, before);
      }),
      clear: f(() => write({}, read())),
      getBytesInUse: f(() => JSON.stringify(read()).length),
      setAccessLevel: f(() => {}),
    };
  }

  function senderOf(ext, ctx) {
    if (ctx.kind === 'cs') return { id: ext.id, url: location.href, origin: location.origin, tab: tabSnapshot(), frameId: IS_TOP ? 0 : 1, documentId: String(TAB_ID) };
    return { id: ext.id, url: `chrome-extension://${ext.id}/${ctx.path || ''}`, origin: `chrome-extension://${ext.id}` };
  }

  // Deliver a one-off message to listeners in `targets`; resolves with the first response.
  function deliver(targets, msg, sender) {
    return new Promise((resolve, reject) => {
      later(() => {
        let done = false, waiting = 0, any = false;
        const respond = (v) => { if (!done) { done = true; resolve(clone(v)); } };
        for (const t of targets) {
          for (const fn of [...t.api.runtime.onMessage.l]) {
            any = true;
            let r;
            try { r = fn(clone(msg), sender, respond); } catch (e) { console.error(TAG, e); continue; }
            if (r === true) waiting++;
            else if (r && typeof r.then === 'function') { waiting++; r.then(respond, (e) => { if (!done) { done = true; reject(e); } }); }
          }
        }
        if (!any) { done = true; reject(new Error('Could not establish connection. Receiving end does not exist.')); }
        else if (!waiting) respond(undefined);
      });
    });
  }

  function makePortPair(name, senderA, senderB) {
    const mk = (sender) => ({
      name, sender, onMessage: new Ev(), onDisconnect: new Ev(), _open: true, _peer: null,
      postMessage(m) {
        if (!this._open) throw new Error('Attempting to use a disconnected port object');
        const peer = this._peer, v = clone(m);
        later(() => peer._open && peer.onMessage.fire(v, peer));
      },
      disconnect() {
        if (!this._open) return;
        this._open = false; const peer = this._peer; peer._open = false;
        later(() => peer.onDisconnect.fire(peer));
      },
    });
    const a = mk(senderA), b = mk(senderB);
    a._peer = b; b._peer = a;
    for (const p of [a, b]) for (const k of ['postMessage', 'disconnect']) p[k] = p[k].bind(p);
    return [a, b];
  }

  // Background is started lazily (like an MV3 service worker waking up).
  const extTargets = (ext, from) => {
    if (ext._bgStarter && !ext._bgStarted && from.kind !== 'bg') ext._bgStarter();
    return [...bus(ext)].filter((c) => c !== from && c.kind !== 'cs');
  };
  const csTargets = (ext) => [...bus(ext)].filter((c) => c.kind === 'cs');

  function makeChrome(ext, ctx) {
    const f = (fn) => apiFn(ctx, fn);
    const manifest = ext.manifest;
    const mv = manifest.manifest_version || 2;
    const isPrivileged = ctx.kind !== 'cs';
    const ev = () => new Ev();

    const connect = (targets, info = {}) => {
      const name = (info && info.name) || '';
      const recv = targets.find((t) => t.api.runtime.onConnect.hasListeners());
      const [mine, theirs] = makePortPair(name, recv ? senderOf(ext, recv) : undefined, senderOf(ext, ctx));
      if (!recv) { later(() => { ctx.lastError = { message: 'Could not establish connection. Receiving end does not exist.' }; mine._open = false; mine.onDisconnect.fire(mine); ctx.lastError = undefined; }); }
      else later(() => recv.api.runtime.onConnect.fire(theirs));
      return mine;
    };

    const runtime = {
      id: ext.id,
      get lastError() { return ctx.lastError; },
      getManifest: () => clone(manifest),
      getURL: (p) => getURL(ext, p),
      getPlatformInfo: f(() => ({ os: /Win/.test(navigator.platform) ? 'win' : /Mac/.test(navigator.platform) ? 'mac' : /Android/.test(navigator.userAgent) ? 'android' : /CrOS/.test(navigator.userAgent) ? 'cros' : 'linux', arch: 'x86-64', nacl_arch: 'x86-64' })),
      sendMessage: f((...args) => {
        if (typeof args[0] === 'string' && args.length > 1 && args[0] !== ext.id) throw new Error('Cross-extension messaging is not supported');
        if (typeof args[0] === 'string' && args.length > 1) args.shift();
        return deliver(extTargets(ext, ctx), args[0], senderOf(ext, ctx));
      }),
      connect: (...args) => {
        if (typeof args[0] === 'string') args.shift();
        return connect(extTargets(ext, ctx), args[0]);
      },
      onMessage: ev(), onConnect: ev(), onInstalled: ev(), onStartup: ev(), onSuspend: ev(),
      onSuspendCanceled: ev(), onUpdateAvailable: ev(), onMessageExternal: ev(), onConnectExternal: ev(),
      onUserScriptMessage: ev(), onRestartRequired: ev(),
      openOptionsPage: f(() => { const p = optionsPath(ext); if (p) openPage(ext, p, 'options'); }),
      setUninstallURL: f(() => {}),
      reload: () => location.reload(),
      requestUpdateCheck: f(() => ({ status: 'no_update' })),
      getContexts: f(() => [...bus(ext)].map((c) => ({ contextType: c.kind === 'bg' ? 'BACKGROUND' : c.kind === 'cs' ? 'CONTENT_SCRIPT' : c.pageKind === 'popup' ? 'POPUP' : 'TAB' }))),
      getBackgroundPage: f(() => (ext._bgWindow || null)),
      OnInstalledReason: { INSTALL: 'install', UPDATE: 'update', CHROME_UPDATE: 'chrome_update', SHARED_MODULE_UPDATE: 'shared_module_update' },
      PlatformOs: { MAC: 'mac', WIN: 'win', ANDROID: 'android', CROS: 'cros', LINUX: 'linux', OPENBSD: 'openbsd' },
    };

    const storage = {
      local: makeStorageArea(ext, ctx, 'local'),
      sync: makeStorageArea(ext, ctx, 'sync'),
      session: makeStorageArea(ext, ctx, 'session'),
      managed: { get: f(() => ({})), getBytesInUse: f(() => 0), onChanged: ev() },
      onChanged: ev(),
    };

    const i18n = {
      getMessage: (n, s) => getMessage(ext, n, s),
      getUILanguage: () => uiLocale.replace('_', '-'),
      getAcceptLanguages: f(() => [...(navigator.languages || [navigator.language])]),
      detectLanguage: f(() => ({ isReliable: false, languages: [] })),
    };

    // Run code/functions "in the tab" (this frame), as chrome.scripting / tabs.executeScript would.
    const execInTab = async (details) => {
      const cs = contentContext(ext);
      if (details.func || details.function) {
        const fn = details.func || details.function;
        if (details.world === 'MAIN') return [{ frameId: 0, documentId: String(TAB_ID), result: await runInMain(`(${fn})(...${JSON.stringify(details.args || [])})`) }];
        // Like Chrome, the function is serialized and re-created in the content-script world,
        // so it sees the tab's document rather than the caller's closure.
        const res = await runCode(cs, `return (${fn}).apply(null, ${JSON.stringify(details.args || [])});`, 'executeScript');
        return [{ frameId: 0, documentId: String(TAB_ID), result: clone(res) }];
      }
      const results = [];
      for (const file of details.files || []) {
        const code = fileText(readFile(ext, file));
        if (code == null) throw new Error('Could not load file: ' + file);
        results.push(details.world === 'MAIN' ? await runInMain(code) : runCode(cs, code, file));
      }
      return [{ frameId: 0, documentId: String(TAB_ID), result: clone(results[results.length - 1]) }];
    };
    const insertCss = async (details) => {
      let css = details.css || '';
      for (const file of details.files || []) css += processCss(ext, fileText(readFile(ext, file)) || '', file);
      addStyle(css, ext.id + ':' + css.length + ':' + (details.files || []).join(','));
    };

    const tabs = {
      TAB_ID_NONE: -1,
      query: f(() => [tabSnapshot()]),
      get: f(() => tabSnapshot()),
      getCurrent: f(() => (ctx.kind === 'page' && ctx.pageKind !== 'popup' ? tabSnapshot() : undefined)),
      create: f((props = {}) => openUrl(ext, props.url, props.active !== false)),
      update: f((...args) => {
        const props = typeof args[0] === 'object' ? args[0] : args[1] || {};
        if (props.url) { const p = extPath(ext, props.url); if (p && /\.html?$/.test(p)) openPage(ext, p, 'tab'); else location.href = props.url; }
        return tabSnapshot();
      }),
      reload: f(() => location.reload()),
      remove: f(() => { warnOnce('tabs.remove', 'chrome.tabs.remove(): closing pages is not emulated'); }),
      sendMessage: f((tabId, msg) => deliver(csTargets(ext), msg, senderOf(ext, ctx))),
      connect: (tabId, info) => connect(csTargets(ext), info),
      executeScript: f((...args) => {
        const d = typeof args[0] === 'object' ? args[0] : args[1] || {};
        if (d.code != null) return [runCode(contentContext(ext), d.code, 'executeScript')];
        return execInTab({ files: d.file ? [d.file] : [] }).then((r) => [r[0].result]);
      }),
      insertCSS: f((...args) => insertCss(typeof args[0] === 'object' ? { css: args[0].code, files: args[0].file ? [args[0].file] : [] } : { css: args[1]?.code, files: args[1]?.file ? [args[1].file] : [] })),
      captureVisibleTab: f(() => { throw new Error('captureVisibleTab is not supported'); }),
      detectLanguage: f(() => document.documentElement.lang || 'und'),
      getZoom: f(() => 1), setZoom: f(() => {}),
      onUpdated: ev(), onActivated: ev(), onCreated: ev(), onRemoved: ev(), onReplaced: ev(), onHighlighted: ev(), onMoved: ev(), onAttached: ev(), onDetached: ev(), onZoomChange: ev(),
    };

    const scripting = {
      executeScript: f((d) => execInTab(d)),
      insertCSS: f((d) => insertCss(d)),
      removeCSS: f(() => {}),
      registerContentScripts: f(() => warnOnce('rcs', 'chrome.scripting.registerContentScripts() only affects the current page')),
      getRegisteredContentScripts: f(() => []),
      unregisterContentScripts: f(() => {}),
      updateContentScripts: f(() => {}),
      ExecutionWorld: { ISOLATED: 'ISOLATED', MAIN: 'MAIN' },
    };

    const actionState = ext._action || (ext._action = { badge: '', title: '', popup: null });
    const action = {
      setBadgeText: f((d) => { actionState.badge = d.text || ''; }), getBadgeText: f(() => actionState.badge),
      setBadgeBackgroundColor: f(() => {}), getBadgeBackgroundColor: f(() => [0, 0, 0, 0]),
      setBadgeTextColor: f(() => {}), getBadgeTextColor: f(() => [255, 255, 255, 255]),
      setTitle: f((d) => { actionState.title = d.title; }), getTitle: f(() => actionState.title || ext.name),
      setIcon: f(() => {}), setPopup: f((d) => { actionState.popup = d.popup; }),
      getPopup: f(() => (actionState.popup ?? popupPath(ext) ?? '')),
      enable: f(() => {}), disable: f(() => {}), isEnabled: f(() => true),
      openPopup: f(() => { const p = actionState.popup || popupPath(ext); if (p) openPage(ext, p, 'popup'); }),
      getUserSettings: f(() => ({ isOnToolbar: true })),
      onClicked: ext._actionClicked || (ext._actionClicked = new Ev()),
    };

    const alarmTimers = ext._alarms || (ext._alarms = new Map());
    const onAlarm = ext._onAlarm || (ext._onAlarm = new Ev());
    const alarms = {
      create: f((...args) => {
        const name = typeof args[0] === 'string' ? args.shift() : '';
        const info = args[0] || {};
        if (alarmTimers.has(name)) clearTimeout(alarmTimers.get(name).t);
        const period = info.periodInMinutes;
        const when = info.when || Date.now() + (info.delayInMinutes ?? period ?? 0) * 60000;
        const a = { name, scheduledTime: when, periodInMinutes: period };
        const arm = () => {
          a.t = setTimeout(() => {
            onAlarm.fire({ name, scheduledTime: a.scheduledTime, periodInMinutes: period });
            if (period) { a.scheduledTime = Date.now() + period * 60000; arm(); } else alarmTimers.delete(name);
          }, Math.max(0, a.scheduledTime - Date.now()));
        };
        arm();
        alarmTimers.set(name, a);
      }),
      get: f((name = '') => { const a = alarmTimers.get(name); return a ? { name, scheduledTime: a.scheduledTime, periodInMinutes: a.periodInMinutes } : undefined; }),
      getAll: f(() => [...alarmTimers.values()].map((a) => ({ name: a.name, scheduledTime: a.scheduledTime, periodInMinutes: a.periodInMinutes }))),
      clear: f((name = '') => { const a = alarmTimers.get(name); if (a) clearTimeout(a.t); return alarmTimers.delete(name); }),
      clearAll: f(() => { for (const a of alarmTimers.values()) clearTimeout(a.t); alarmTimers.clear(); return true; }),
      onAlarm,
    };

    const menus = ext._menus || (ext._menus = { items: new Map(), onClicked: new Ev() });
    const contextMenus = {
      ACTION_MENU_TOP_LEVEL_LIMIT: 6,
      create: (props, cb) => {
        const id = props.id ?? String(menus.items.size + 1);
        menus.items.set(id, { ...props, id });
        refreshMenus();
        if (cb) later(cb);
        return id;
      },
      update: f((id, props) => { const it = menus.items.get(id); if (it) Object.assign(it, props); refreshMenus(); }),
      remove: f((id) => { menus.items.delete(id); refreshMenus(); }),
      removeAll: f(() => { menus.items.clear(); refreshMenus(); }),
      onClicked: menus.onClicked,
    };

    let notifSeq = 0;
    const notifications = {
      create: f((...args) => {
        const id = typeof args[0] === 'string' ? args.shift() : `n${++notifSeq}`;
        const o = args[0] || {};
        const p = o.iconUrl && extPath(ext, o.iconUrl);
        GM_notification({
          title: o.title || ext.name, text: o.message || ' ', image: p ? fileDataUrl(ext, p) : o.iconUrl,
          onclick: () => notifications.onClicked.fire(id),
          ondone: () => notifications.onClosed.fire(id, true),
        });
        return id;
      }),
      update: f(() => true), clear: f(() => true), getAll: f(() => ({})), getPermissionLevel: f(() => 'granted'),
      onClicked: ev(), onClosed: ev(), onButtonClicked: ev(), onShowSettings: ev(), onPermissionLevelChanged: ev(),
    };

    let dlSeq = 0;
    const downloads = {
      download: f((o) => {
        const id = ++dlSeq;
        const p = extPath(ext, o.url);
        GM_download({ url: p ? fileDataUrl(ext, p) : o.url, name: o.filename || (o.url.split('/').pop() || 'download'), saveAs: !!o.saveAs });
        return id;
      }),
      search: f(() => []), cancel: f(() => {}), open: f(() => {}), show: f(() => {}), erase: f(() => []),
      onCreated: ev(), onChanged: ev(), onErased: ev(), onDeterminingFilename: ev(),
    };

    const permissions = {
      contains: f(() => true), request: f(() => true), remove: f(() => true),
      getAll: f(() => ({ permissions: manifest.permissions || [], origins: manifest.host_permissions || [] })),
      onAdded: ev(), onRemoved: ev(),
    };

    const windows = {
      WINDOW_ID_CURRENT: -2, WINDOW_ID_NONE: -1,
      get: f(() => ({ id: 1, focused: true, type: 'normal', state: 'normal', incognito: false, tabs: [tabSnapshot()] })),
      getCurrent: f(() => ({ id: 1, focused: true, type: 'normal', state: 'normal', incognito: false, tabs: [tabSnapshot()] })),
      getLastFocused: f(() => ({ id: 1, focused: true, type: 'normal', state: 'normal', incognito: false })),
      getAll: f(() => [{ id: 1, focused: true, type: 'normal', state: 'normal', incognito: false, tabs: [tabSnapshot()] }]),
      create: f((o = {}) => { openUrl(ext, [].concat(o.url || [])[0], true); return { id: 2, tabs: [] }; }),
      update: f(() => ({ id: 1 })), remove: f(() => {}),
      onCreated: ev(), onRemoved: ev(), onFocusChanged: ev(), onBoundsChanged: ev(),
    };

    const extension = {
      getURL: (p) => getURL(ext, p),
      inIncognitoContext: false,
      isAllowedIncognitoAccess: f(() => false),
      isAllowedFileSchemeAccess: f(() => false),
      getBackgroundPage: () => ext._bgWindow || null,
      getViews: () => [],
      sendMessage: runtime.sendMessage,
      onMessage: runtime.onMessage,
    };

    const base = { runtime, storage, i18n, extension };
    if (isPrivileged) {
      Object.assign(base, {
        tabs, scripting, alarms, notifications, downloads, permissions, windows,
        contextMenus, menus: contextMenus,
        action, browserAction: action, pageAction: action,
      });
    } else {
      // Content scripts only get a handful of APIs in real Chrome.
      Object.assign(base, { permissions: { contains: permissions.contains, request: permissions.request, getAll: permissions.getAll } });
    }

    return new Proxy(base, {
      get(t, k) {
        if (k in t || typeof k === 'symbol') return t[k];
        if (k === 'then' || k === 'toJSON') return undefined;
        return (t[k] = stubNS(k));
      },
    });
  }

  function registerContext(ext, ctx) {
    ctx.api = makeChrome(ext, ctx);
    bus(ext).add(ctx);
    watchStorage(ext);
    return ctx;
  }

  function contentContext(ext) {
    if (!ext._cs) ext._cs = registerContext(ext, { kind: 'cs' });
    return ext._cs;
  }

  // ───────────────────────────── code execution ─────────────────────────────
  // Code runs in the userscript sandbox (an isolated world), never in the page's own JS world.
  function runCode(ctx, code, name) {
    try {
      return new Function('chrome', 'browser', `${code}\n//# sourceURL=crx-runner/${encodeURI(name)}`).call(window, ctx.api, ctx.api);
    } catch (e) {
      console.error(TAG, `error in ${name}:`, e);
      return undefined;
    }
  }

  function runInMain(code) {
    return new Promise((resolve) => {
      const s = document.createElement('script');
      const url = URL.createObjectURL(new Blob([code], { type: 'text/javascript' }));
      s.src = url;
      s.onload = s.onerror = () => { URL.revokeObjectURL(url); s.remove(); resolve(undefined); };
      (document.head || document.documentElement).appendChild(s);
    });
  }

  const styleKeys = new Set();
  function addStyle(css, key) {
    if (key && styleKeys.has(key)) return;
    if (key) styleKeys.add(key);
    try {
      const sheet = new CSSStyleSheet();
      sheet.replaceSync(css);
      document.adoptedStyleSheets = [...document.adoptedStyleSheets, sheet];
    } catch (e) {
      const st = document.createElement('style');
      st.textContent = css;
      (document.head || document.documentElement).appendChild(st);
    }
  }

  // ───────────────────────────── content scripts ─────────────────────────────
  function onPhase(phase, fn) {
    const rs = document.readyState;
    if (phase === 'document_start') {
      // Chrome guarantees <html> exists at document_start; userscript managers may run earlier.
      return whenRoot(fn);
    }
    if (phase === 'document_end') {
      if (rs !== 'loading') return fn();
      return document.addEventListener('DOMContentLoaded', fn, { once: true });
    }
    // document_idle: after DOMContentLoaded, as soon as load fires or 200 ms later, whichever first.
    let ran = false;
    const go = () => { if (!ran) { ran = true; fn(); } };
    if (rs === 'complete') return later(go);
    window.addEventListener('load', go, { once: true });
    const afterDcl = () => setTimeout(go, 200);
    if (rs === 'interactive') afterDcl(); else document.addEventListener('DOMContentLoaded', afterDcl, { once: true });
  }

  function runContentScripts(ext) {
    const entries = (ext.manifest.content_scripts || []).filter((cs) => (IS_TOP || cs.all_frames) && csMatches(cs, location.href));
    if (!entries.length) return false;
    const phases = { document_start: [], document_end: [], document_idle: [] };
    const mainPhases = { document_start: [], document_end: [], document_idle: [] };
    for (const cs of entries) {
      const runAt = phases[cs.run_at] ? cs.run_at : 'document_idle';
      if (cs.css && cs.css.length) {
        const css = cs.css.map((p) => processCss(ext, fileText(readFile(ext, p)) || '', p)).join('\n');
        addStyle(css, ext.id + ':cs:' + cs.css.join(','));
      }
      for (const p of cs.js || []) {
        const code = fileText(readFile(ext, p));
        if (code == null) { warn(`${ext.name}: missing content script ${p}`); continue; }
        (cs.world === 'MAIN' ? mainPhases : phases)[runAt].push(`/* ── ${p} ── */\n${code}\n;`);
      }
    }
    // All isolated-world content scripts of one extension share a single scope (like Chrome's
    // per-extension isolated world). A generator lets that one scope run in stages:
    // document_start → yield → document_end → yield → document_idle.
    const ctx = contentContext(ext);
    let gen = null;
    try {
      const body = 'void 0;\n' + phases.document_start.join('\n') + '\nyield 1;\n' + phases.document_end.join('\n') + '\nyield 2;\n' + phases.document_idle.join('\n');
      gen = new Function('chrome', 'browser', `return function* () {\n${body}\n}\n//# sourceURL=crx-runner/${encodeURI(ext.name)}/content.js`)(ctx.api, ctx.api).call(window);
    } catch (e) { console.error(TAG, `${ext.name}: content script failed to compile`, e); }
    const step = () => { if (!gen) return; try { if (gen.next().done) gen = null; } catch (e) { gen = null; console.error(TAG, `${ext.name}: content script error`, e); } };
    for (const phase of ['document_start', 'document_end', 'document_idle']) {
      onPhase(phase, () => {
        step();
        if (mainPhases[phase].length) runInMain(mainPhases[phase].join('\n'));
      });
    }
    return true;
  }

  // ───────────────────────────── shadow UI host ─────────────────────────────
  let uiRoot = null;
  const UI_CSS = `
    :host{all:initial}
    *{box-sizing:border-box;font-family:system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
    .ov{position:fixed;z-index:2147483647;background:var(--bg);color:var(--fg);border:1px solid var(--bd);border-radius:10px;box-shadow:0 12px 40px rgba(0,0,0,.35);display:flex;flex-direction:column;overflow:hidden;
        --bg:#fff;--fg:#1d1d1f;--mut:#6b6b70;--bd:#d9d9de;--acc:#2f6fdf;--chip:#f1f1f4;--bad:#c4372f}
    @media (prefers-color-scheme:dark){.ov{--bg:#1f1f23;--fg:#ececf0;--mut:#9a9aa3;--bd:#3a3a42;--acc:#6aa0ff;--chip:#2b2b31;--bad:#ff7a70}}
    .bar{display:flex;align-items:center;gap:8px;padding:6px 8px 6px 12px;border-bottom:1px solid var(--bd);font-size:13px;font-weight:600;min-height:34px}
    .bar img{width:16px;height:16px}
    .bar .t{flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
    button{font:inherit;font-size:12px;border:1px solid var(--bd);background:var(--chip);color:var(--fg);border-radius:6px;padding:4px 10px;cursor:pointer}
    button:hover{border-color:var(--acc)}
    button.x{border:none;background:none;font-size:18px;line-height:1;padding:2px 6px;color:var(--mut)}
    button.danger{color:var(--bad)}
    iframe{border:0;display:block;background:#fff}
    .popup{top:8px;right:8px;max-width:calc(100vw - 16px);max-height:calc(100vh - 16px)}
    .page{inset:4vh 4vw}
    .page iframe{flex:1;width:100%}
    .mgr{top:8px;right:8px;width:min(460px,calc(100vw - 16px));max-height:calc(100vh - 16px)}
    .body{padding:12px;overflow:auto;font-size:13px;display:flex;flex-direction:column;gap:12px}
    .row{display:flex;gap:6px;align-items:center;flex-wrap:wrap}
    input[type=text]{flex:1;min-width:0;font:inherit;font-size:12px;padding:5px 8px;border:1px solid var(--bd);border-radius:6px;background:var(--bg);color:var(--fg)}
    .status{font-size:12px;color:var(--mut);min-height:1em;white-space:pre-wrap}
    .status.err{color:var(--bad)}
    .ext{border:1px solid var(--bd);border-radius:8px;padding:10px;display:flex;flex-direction:column;gap:6px}
    .ext .h{display:flex;gap:8px;align-items:center}
    .ext .h img{width:24px;height:24px}
    .ext .n{font-weight:600}
    .mut{color:var(--mut);font-size:11px;word-break:break-all}
    .warn{color:var(--bad);font-size:11px}
    label.chk{display:flex;gap:4px;align-items:center;font-size:12px}
    .empty{color:var(--mut);font-size:12px}
  `;
  function getUi() {
    if (uiRoot) return uiRoot;
    const host = document.createElement('crx-runner-ui');
    host.style.cssText = 'all:initial;position:fixed;top:0;left:0;width:0;height:0;z-index:2147483647';
    const root = host.attachShadow({ mode: 'closed' });
    try {
      const sheet = new CSSStyleSheet(); sheet.replaceSync(UI_CSS); root.adoptedStyleSheets = [sheet];
    } catch (e) { const st = document.createElement('style'); st.textContent = UI_CSS; root.appendChild(st); }
    whenRoot(() => document.documentElement.appendChild(host));
    uiRoot = root;
    return root;
  }
  function el(tag, attrs = {}, ...kids) {
    const n = document.createElement(tag);
    for (const [k, v] of Object.entries(attrs)) {
      if (k.startsWith('on')) n.addEventListener(k.slice(2), v);
      else if (k === 'text') n.textContent = v;
      else if (v !== false && v != null) n.setAttribute(k, v === true ? '' : v);
    }
    for (const c of kids.flat()) if (c != null) n.append(c);
    return n;
  }

  function iconUrl(ext, size = 32) {
    const icons = ext.manifest.icons || (ext.manifest.action || ext.manifest.browser_action || {}).default_icon;
    if (!icons) return null;
    if (typeof icons === 'string') return fileUrl(ext, icons);
    const sizes = Object.keys(icons).map(Number).sort((a, b) => a - b);
    const pick = sizes.find((s) => s >= size) || sizes[sizes.length - 1];
    return pick ? fileUrl(ext, icons[pick]) : null;
  }

  // ───────────────────────────── extension pages (popup / options / tabs) ─────────────────────────────
  const popupPath = (ext) => {
    const a = ext.manifest.action || ext.manifest.browser_action || ext.manifest.page_action || {};
    return a.default_popup ? normPath(a.default_popup) : null;
  };
  const optionsPath = (ext) => {
    const p = (ext.manifest.options_ui && ext.manifest.options_ui.page) || ext.manifest.options_page;
    return p ? normPath(p) : null;
  };

  function openUrl(ext, url, active) {
    if (!url) return tabSnapshot();
    const p = extPath(ext, url);
    if (p != null && /\.html?$/i.test(p)) { openPage(ext, p, 'tab'); return tabSnapshot(); }
    if (p != null) url = fileUrl(ext, p) || url;
    GM_openInTab(url, { active });
    return { ...tabSnapshot(), id: TAB_ID + 1, url };
  }

  // GM-backed localStorage replacement for extension pages / background.
  function fakeLocalStorage(ext) {
    const read = () => GM_getValue(K.ls(ext.id), {});
    const write = (o) => GM_setValue(K.ls(ext.id), o);
    const api = {
      getItem: (k) => { const o = read(); return Object.prototype.hasOwnProperty.call(o, k) ? o[k] : null; },
      setItem: (k, v) => { const o = read(); o[k] = String(v); write(o); },
      removeItem: (k) => { const o = read(); delete o[k]; write(o); },
      clear: () => write({}),
      key: (i) => Object.keys(read())[i] ?? null,
      get length() { return Object.keys(read()).length; },
    };
    return new Proxy(api, {
      get: (t, k) => (k in t ? t[k] : typeof k === 'string' ? t.getItem(k) ?? undefined : undefined),
      set: (t, k, v) => { t.setItem(k, v); return true; },
      deleteProperty: (t, k) => { t.removeItem(k); return true; },
      ownKeys: () => Object.keys(read()),
      getOwnPropertyDescriptor: (t, k) => ({ value: t.getItem(k), enumerable: true, configurable: true }),
    });
  }

  // fetch() for privileged contexts: package files are served locally, everything else goes
  // through GM_xmlhttpRequest so host_permissions-style cross-origin requests work.
  function makeFetch(ext, basePath = '') {
    return function gmFetch(input, init = {}) {
      let url = typeof input === 'string' ? input : input instanceof URL ? input.href : input.url;
      if (input && typeof input === 'object' && !(input instanceof URL)) init = { method: input.method, headers: input.headers, ...init };
      const p = extPath(ext, url, basePath);
      if (p != null) {
        const f = readFile(ext, p);
        return Promise.resolve(f ? new Response(fileBlob(f), { status: 200, headers: { 'content-type': f.m } }) : new Response('', { status: 404 }));
      }
      if (/^(blob|data):/i.test(url)) return fetch(url, init);
      return new Promise((resolve, reject) => {
        const headers = {};
        new Headers(init.headers || {}).forEach((v, k) => { headers[k] = v; });
        let data = init.body;
        if (data instanceof URLSearchParams) { data = data.toString(); headers['content-type'] = headers['content-type'] || 'application/x-www-form-urlencoded;charset=UTF-8'; }
        const req = GM_xmlhttpRequest({
          method: (init.method || 'GET').toUpperCase(), url, headers, data, responseType: 'arraybuffer',
          anonymous: init.credentials === 'omit',
          onload: (r) => {
            if (!r.status) return reject(new TypeError('Failed to fetch'));
            const h = new Headers();
            for (const line of (r.responseHeaders || '').trim().split(/\r?\n/)) {
              const i = line.indexOf(':');
              if (i > 0) try { h.append(line.slice(0, i).trim(), line.slice(i + 1).trim()); } catch (e) { /* skip */ }
            }
            const noBody = [101, 204, 205, 304].includes(r.status);
            const resp = new Response(noBody ? null : r.response, { status: r.status, statusText: r.statusText || '', headers: h });
            Object.defineProperty(resp, 'url', { value: r.finalUrl || url });
            resolve(resp);
          },
          onerror: () => reject(new TypeError('Failed to fetch')),
          ontimeout: () => reject(new TypeError('Failed to fetch (timeout)')),
          onabort: () => reject(new DOMException('The user aborted a request.', 'AbortError')),
        });
        if (init.signal) init.signal.addEventListener('abort', () => req && req.abort && req.abort());
      });
    };
  }

  // Prepare an about:blank iframe as a JS "global" for extension code. Code runs in this
  // userscript's world with `with (iframeWindow)`, so it is immune to the page's CSP.
  function prepareWindow(ext, iw, ctx, { serviceWorker = false, basePath = '' } = {}) {
    const def = (k, v) => { try { Object.defineProperty(iw, k, { value: v, configurable: true, writable: true }); } catch (e) { try { iw[k] = v; } catch (e2) { /* ignore */ } } };
    def('chrome', ctx.api);
    def('browser', ctx.api);
    def('fetch', makeFetch(ext, basePath));
    def('localStorage', fakeLocalStorage(ext));
    if (serviceWorker) {
      def('importScripts', (...files) => { for (const p of files) evalIn(ext, iw, ctx, fileText(readFile(ext, extPath(ext, p, basePath))) || '', p, serviceWorker); });
      def('clients', { matchAll: async () => [], claim: async () => {}, openWindow: async (u) => openUrl(ext, u, true) });
      def('registration', { scope: `chrome-extension://${ext.id}/`, showNotification: (t, o = {}) => ctx.api.notifications.create({ title: t, message: o.body || '', iconUrl: o.icon }) });
      def('skipWaiting', async () => {});
    }
  }

  function scopeFor(iw, serviceWorker) {
    if (!serviceWorker) return iw;
    // Hide DOM globals from service-worker code, and keep `this` sane for native functions.
    return new Proxy(iw, {
      has: (t, k) => k !== 'eval' && (k in t || k === 'window' || k === 'document'),
      get: (t, k) => {
        if (k === Symbol.unscopables) return undefined;
        if (k === 'window' || k === 'document') return undefined;
        const v = t[k];
        return typeof v === 'function' && !v.prototype && !/^[A-Z]/.test(String(k)) ? v.bind(t) : v;
      },
      set: (t, k, v) => { t[k] = v; return true; },
    });
  }

  function evalIn(ext, iw, ctx, code, name, serviceWorker = false) {
    const fn = new Function('__scope', `with (__scope) {\n${code}\n}\n//# sourceURL=crx-runner/${encodeURI(ext.name)}/${encodeURI(name)}`);
    return fn.call(serviceWorker ? scopeFor(iw, true) : iw, scopeFor(iw, serviceWorker));
  }

  function hiddenFrame() {
    const ui = getUi();
    const fr = el('iframe', { style: 'display:none', 'aria-hidden': 'true' });
    ui.appendChild(fr);
    return fr;
  }

  function inlineImportScripts(ext, code, basePath) {
    // Statically inline `importScripts('a.js', 'b.js')` so imported globals share one scope.
    return code.replace(/\bimportScripts\s*\(\s*((?:(['"`])[^'"`]+\2\s*,?\s*)+)\)\s*;?/g, (m, args) => {
      const files = [...args.matchAll(/(['"`])([^'"`]+)\1/g)].map((x) => x[2]);
      const parts = files.map((p) => fileText(readFile(ext, extPath(ext, p, basePath))));
      if (parts.some((x) => x == null)) return m;
      return parts.map((c, i) => `/* ── ${files[i]} ── */\n${inlineImportScripts(ext, c, basePath)}\n;`).join('\n');
    });
  }

  function whenRoot(fn) {
    if (document.documentElement) return fn();
    const mo = new MutationObserver(() => { if (document.documentElement) { mo.disconnect(); fn(); } });
    mo.observe(document, { childList: true });
  }

  function startBackground(ext) {
    if (ext._bgStarted) return;
    ext._bgStarted = true;
    whenRoot(() => runBackground(ext));
  }

  function runBackground(ext) {
    const bg = ext.manifest.background || {};
    let files = [];
    let sw = false;
    if (bg.service_worker) { files = [normPath(bg.service_worker)]; sw = true; }
    else if (bg.scripts) files = bg.scripts.map(normPath);
    else if (bg.page) {
      const html = fileText(readFile(ext, bg.page)) || '';
      const doc = new DOMParser().parseFromString(html, 'text/html');
      files = [...doc.querySelectorAll('script[src]')].map((s) => extPath(ext, s.getAttribute('src'), bg.page)).filter(Boolean);
    }
    if (!files.length) return;
    if (bg.type === 'module') warn(`${ext.name}: ES-module background workers are not supported; trying as a classic script.`);
    const ctx = registerContext(ext, { kind: 'bg', path: files[0] });
    const fr = hiddenFrame();
    const iw = fr.contentWindow;
    ext._bgWindow = iw;
    prepareWindow(ext, iw, ctx, { serviceWorker: sw, basePath: files[0] });
    const code = files.map((p) => { const c = fileText(readFile(ext, p)); if (c == null) warn(`${ext.name}: missing background file ${p}`); return `/* ── ${p} ── */\n${inlineImportScripts(ext, c || '', p)}\n;`; }).join('\n');
    try { evalIn(ext, iw, ctx, 'void 0;\n' + code, sw ? 'service_worker.js' : 'background.js', sw); }
    catch (e) { console.error(TAG, `${ext.name}: background error`, e); }

    const pending = ext.installEventPending;
    if (pending) {
      const meta = GM_getValue(K.meta(ext.id), null);
      if (meta && meta.installEventPending) { meta.installEventPending = null; GM_setValue(K.meta(ext.id), meta); }
      later(() => ctx.api.runtime.onInstalled.fire(pending === 'update' ? { reason: 'update', previousVersion: ext.previousVersion } : { reason: 'install' }));
    }
  }

  function closeOverlay(ext, node) {
    if (!node || !node.isConnected) return;
    node.remove();
    if (node._ctx) {
      bus(ext).delete(node._ctx);
      try { node._iw && node._iw.dispatchEvent(new node._iw.Event('unload')); } catch (e) { /* ignore */ }
    }
  }

  const openPages = new Map(); // `${id}:${kind}` -> overlay
  function openPage(ext, path, kind) {
    const html = fileText(readFile(ext, path));
    if (html == null) { warn(`${ext.name}: page not found: ${path}`); return; }
    const key = `${ext.id}:${kind === 'popup' ? 'popup' : 'page'}`;
    if (openPages.has(key)) closeOverlay(ext, openPages.get(key));
    if (ext._bgStarter) ext._bgStarter();

    const ui = getUi();
    const icon = iconUrl(ext, 16);
    const frame = el('iframe', {});
    const node = el('div', { class: 'ov ' + (kind === 'popup' ? 'popup' : 'page') },
      el('div', { class: 'bar' }, icon ? el('img', { src: icon, alt: '' }) : null, el('span', { class: 't', text: ext.name + (kind === 'popup' ? '' : ' — ' + path) }),
        el('button', { class: 'x', title: 'Close', onclick: () => closeOverlay(ext, node) }, '×')),
      frame);
    ui.appendChild(node);
    openPages.set(key, node);

    const iw = frame.contentWindow;
    const idoc = iw.document;
    const src = new DOMParser().parseFromString(html, 'text/html');

    // Collect scripts in document order, then strip them from the markup.
    const scripts = [];
    for (const s of src.querySelectorAll('script')) {
      const type = (s.getAttribute('type') || '').toLowerCase();
      if (type && !/javascript|module|^$/.test(type)) continue;
      if (type === 'module') warnOnce('module:' + ext.id, `${ext.name}: <script type="module"> pages are run as classic scripts; import/export will fail.`);
      const sp = s.getAttribute('src');
      if (sp) { const p = extPath(ext, sp, path); scripts.push({ name: p, code: p && fileText(readFile(ext, p)) }); }
      else scripts.push({ name: path + '#inline', code: s.textContent });
      s.remove();
    }
    // Stylesheets → constructable sheets (not subject to the page's style-src CSP).
    const sheets = [];
    for (const n of src.querySelectorAll('link[rel~="stylesheet"][href], style')) {
      if (n.tagName === 'STYLE') sheets.push(processCss(ext, n.textContent, path));
      else { const p = extPath(ext, n.getAttribute('href'), path); const t = p && fileText(readFile(ext, p)); if (t != null) sheets.push(processCss(ext, t, p)); }
      n.remove();
    }
    for (const n of src.querySelectorAll('[src],[href],[srcset],[poster]')) {
      for (const a of ['src', 'href', 'poster']) {
        const v = n.getAttribute(a);
        if (!v) continue;
        const p = extPath(ext, v, path);
        if (p == null) continue;
        if (n.tagName === 'A' && /\.html?$/i.test(p)) {
          n.setAttribute('href', '#');
          n.addEventListener('click', (e) => { e.preventDefault(); openPage(ext, p, 'tab'); });
          continue;
        }
        const u = fileUrl(ext, p);
        if (u) n.setAttribute(a, u);
      }
    }

    idoc.open();
    idoc.write('<!DOCTYPE html><html><head><meta charset="utf-8"></head><body></body></html>');
    idoc.close();
    for (const a of src.documentElement.attributes) idoc.documentElement.setAttribute(a.name, a.value);
    for (const a of src.body.attributes) idoc.body.setAttribute(a.name, a.value);
    idoc.head.append(...[...src.head.childNodes].map((n) => idoc.importNode(n, true)));
    idoc.body.append(...[...src.body.childNodes].map((n) => idoc.importNode(n, true)));
    try {
      idoc.adoptedStyleSheets = sheets.map((css) => { const s = new iw.CSSStyleSheet(); s.replaceSync(css); return s; });
    } catch (e) { for (const css of sheets) idoc.head.append(Object.assign(idoc.createElement('style'), { textContent: css })); }

    const ctx = registerContext(ext, { kind: 'page', pageKind: kind, path });
    node._ctx = ctx; node._iw = iw;
    prepareWindow(ext, iw, ctx, { basePath: path });
    try { Object.defineProperty(iw, 'close', { value: () => closeOverlay(ext, node), configurable: true }); } catch (e) { /* ignore */ }

    if (kind === 'popup') {
      const fit = () => {
        const d = idoc.documentElement;
        frame.style.width = Math.min(800, Math.max(40, Math.ceil(d.getBoundingClientRect().width))) + 'px';
        frame.style.height = Math.min(600, Math.max(30, d.scrollHeight, idoc.body ? idoc.body.scrollHeight : 0)) + 'px';
      };
      frame.style.width = '400px'; frame.style.height = '30px';
      idoc.documentElement.style.width = 'max-content';
      setTimeout(fit, 0);
      try { new iw.ResizeObserver(fit).observe(idoc.body); } catch (e) { setInterval(fit, 500); }
    }

    const code = scripts.map((s) => (s.code == null ? `console.warn(${JSON.stringify(TAG + ' missing script ' + s.name)});` : `/* ── ${s.name} ── */\n${s.code}\n;`)).join('\n');
    try { evalIn(ext, iw, ctx, 'void 0;\n' + code, path); } catch (e) { console.error(TAG, `${ext.name}: error in ${path}`, e); }
    try {
      idoc.dispatchEvent(new iw.Event('DOMContentLoaded', { bubbles: true }));
      iw.dispatchEvent(new iw.Event('load'));
    } catch (e) { console.error(TAG, e); }
    return node;
  }

  // ───────────────────────────── menu commands ─────────────────────────────
  const menuIds = [];
  const loaded = [];
  function refreshMenus() {
    if (!IS_TOP || typeof GM_registerMenuCommand !== 'function') return;
    if (typeof GM_unregisterMenuCommand === 'function') while (menuIds.length) GM_unregisterMenuCommand(menuIds.pop());
    const add = (title, fn) => menuIds.push(GM_registerMenuCommand(title, fn));
    add('⚙ CRX Runner: manage extensions', openManager);
    for (const ext of loaded) {
      const pp = popupPath(ext);
      const ap = (ext._action && ext._action.popup) || pp;
      add(`▶ ${ext.name}`, () => {
        if (ap) openPage(ext, ap, 'popup');
        else { if (ext._bgStarter) ext._bgStarter(); later(() => ext._actionClicked && ext._actionClicked.fire(tabSnapshot())); }
      });
      if (optionsPath(ext)) add(`⚙ ${ext.name}: options`, () => openPage(ext, optionsPath(ext), 'options'));
      if (ext._menus) {
        for (const it of ext._menus.items.values()) {
          if (it.visible === false || it.type === 'separator' || !it.title) continue;
          add(`☰ ${ext.name}: ${it.title.replace(/%s/g, '…')}`, () => {
            const sel = String(getSelection() || '');
            const info = { menuItemId: it.id, parentMenuItemId: it.parentId, pageUrl: location.href, frameUrl: location.href, frameId: 0, editable: false, selectionText: sel || undefined };
            if (typeof it.onclick === 'function') it.onclick(info, tabSnapshot());
            ext._menus.onClicked.fire(info, tabSnapshot());
          });
        }
      }
    }
  }

  // ───────────────────────────── manager UI ─────────────────────────────
  let mgrNode = null;
  function openManager() {
    const ui = getUi();
    if (mgrNode && mgrNode.isConnected) { mgrNode.remove(); mgrNode = null; return; }
    const status = el('div', { class: 'status' });
    const setStatus = (msg, err) => { status.textContent = msg; status.className = 'status' + (err ? ' err' : ''); };
    const list = el('div', { style: 'display:flex;flex-direction:column;gap:8px' });
    const file = el('input', { type: 'file', accept: '.crx,.zip', style: 'display:none' });
    const urlIn = el('input', { type: 'text', placeholder: 'Web Store URL / extension ID / .crx or .zip URL' });

    const done = (p) => p.then((m) => { setStatus(`Installed ${m.manifest.name} ${m.manifest.version}. Reload pages to apply.`); render(); }, (e) => setStatus(String(e.message || e), true));
    file.addEventListener('change', () => {
      const fl = file.files[0];
      if (!fl) return;
      setStatus('Installing ' + fl.name + '…');
      done(fl.arrayBuffer().then((b) => installFromBuffer(b, { type: 'file', name: fl.name })));
      file.value = '';
    });
    const goUrl = () => { if (!urlIn.value.trim()) return; setStatus('Downloading…'); done(installFromInput(urlIn.value)); };
    urlIn.addEventListener('keydown', (e) => { if (e.key === 'Enter') goUrl(); });

    function render() {
      list.textContent = '';
      const ids = listIds();
      if (!ids.length) list.append(el('div', { class: 'empty', text: 'No extensions installed yet.' }));
      for (const id of ids) {
        const ext = loadExt(id);
        if (!ext) continue;
        const m = ext.manifest;
        const perms = [...(m.permissions || []), ...(m.optional_permissions || [])].filter((p) => typeof p === 'string' && !p.includes('://'));
        const bad = perms.filter((p) => UNSUPPORTED_PERMS.has(p));
        const save = (patch) => { const meta = GM_getValue(K.meta(id)); Object.assign(meta, patch); GM_setValue(K.meta(id), meta); setStatus('Saved. Reload pages to apply.'); };
        const icon = iconUrl(ext, 24);
        const loadedExt = loaded.find((x) => x.id === id) || ext;
        list.append(el('div', { class: 'ext' },
          el('div', { class: 'h' }, icon ? el('img', { src: icon, alt: '' }) : null,
            el('div', { style: 'flex:1;min-width:0' }, el('div', { class: 'n', text: `${ext.name} ${m.version || ''}` }), el('div', { class: 'mut', text: `${id} · MV${m.manifest_version || 2} · ${Math.round((ext.bytes || 0) / 1024)} KB` }))),
          bad.length ? el('div', { class: 'warn', text: 'Not emulated: ' + bad.join(', ') }) : null,
          el('div', { class: 'row' },
            el('label', { class: 'chk' }, el('input', { type: 'checkbox', checked: ext.enabled, onchange: (e) => save({ enabled: e.target.checked }) }), 'Enabled'),
            el('label', { class: 'chk', title: 'Run the background script/service worker inside each tab' }, el('input', { type: 'checkbox', checked: ext.runBackground, onchange: (e) => save({ runBackground: e.target.checked }) }), 'Background'),
          ),
          el('div', { class: 'row' },
            popupPath(ext) ? el('button', { onclick: () => openPage(loadedExt, popupPath(ext), 'popup') }, 'Popup') : null,
            optionsPath(ext) ? el('button', { onclick: () => openPage(loadedExt, optionsPath(ext), 'options') }, 'Options') : null,
            ext.source && ext.source.type !== 'file' ? el('button', { onclick: () => { setStatus('Updating…'); done(installFromInput(ext.source.id || ext.source.url)); } }, 'Update') : null,
            el('button', { onclick: () => { if (confirm(`Clear all stored data of ${ext.name}?`)) { for (const a of ['local', 'sync']) GM_deleteValue(K.store(id, a)); GM_deleteValue(K.ls(id)); setStatus('Storage cleared.'); } } }, 'Clear data'),
            el('button', { class: 'danger', onclick: () => { if (confirm(`Remove ${ext.name}?`)) { uninstall(id); setStatus('Removed. Reload pages to apply.'); render(); } } }, 'Remove'),
          )));
      }
    }

    mgrNode = el('div', { class: 'ov mgr' },
      el('div', { class: 'bar' }, el('span', { class: 't', text: 'CRX Runner' }), el('button', { class: 'x', title: 'Close', onclick: () => { mgrNode.remove(); mgrNode = null; } }, '×')),
      el('div', { class: 'body' },
        el('div', { class: 'row' }, el('button', { onclick: () => file.click() }, 'Install .crx / .zip…'), file),
        el('div', { class: 'row' }, urlIn, el('button', { onclick: goUrl }, 'Install')),
        status,
        list));
    ui.appendChild(mgrNode);
    render();
  }

  // ───────────────────────────── boot ─────────────────────────────
  function boot() {
    for (const id of listIds()) {
      const ext = loadExt(id);
      if (!ext || !ext.enabled) continue;
      loaded.push(ext);
      if (IS_TOP && ext.runBackground && ext.manifest.background) {
        ext._bgStarter = () => startBackground(ext);
      }
      const hasCs = runContentScripts(ext);
      // Start eagerly when a content script runs here or when menus/alarms must exist up front;
      // otherwise wake it on first message, popup or action click.
      const perms = ext.manifest.permissions || [];
      if (ext._bgStarter && (hasCs || perms.includes('contextMenus') || perms.includes('menus') || ext.installEventPending)) ext._bgStarter();
    }
    refreshMenus();
  }

  const api = { installFromBuffer, installFromInput, uninstall, listIds, loadExt, openPage, openManager, loaded, webStoreDownloadUrl, csMatches, patternRe };
  try { if (typeof GM_info !== 'undefined' && GM_info && typeof GM_info.__crxRunnerTest === 'function') GM_info.__crxRunnerTest(api); } catch (e) { /* ignore */ }

  try { boot(); } catch (e) { console.error(TAG, 'boot failed', e); }
})();
