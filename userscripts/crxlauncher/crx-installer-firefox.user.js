// ==UserScript==
// @name         CRX Installer (Firefox)
// @namespace    https://github.com/alehaaaa/pipe/userscripts/crx-installer
// @version      1.0.0
// @description  "Add to Firefox" on the Chrome Web Store: converts the CRX into an XPI that Firefox runs natively. Userscript port of the CRX Installer add-on.
// @match        https://chromewebstore.google.com/*
// @grant        GM_xmlhttpRequest
// @grant        GM_registerMenuCommand
// @connect      clients2.google.com
// @connect      clients2.googleusercontent.com
// @connect      services.addons.mozilla.org
// @connect      addons.mozilla.org
// @require      https://cdnjs.cloudflare.com/ajax/libs/jszip/3.10.1/jszip.min.js
// ==/UserScript==

/* global JSZip, GM_xmlhttpRequest, GM_registerMenuCommand */
// Firefox already implements the chrome.* API, so nothing is emulated. The CRX only needs
// a few manifest fixes. Unsigned XPIs install on Nightly / Developer Edition / ESR /
// LibreWolf / Floorp / Zen when about:config has xpinstall.signatures.required = false.
// On release Firefox, use the downloaded file in about:debugging → "Load Temporary Add-on".

(function () {
  'use strict';

  const get = (url, type = 'arraybuffer') => new Promise((ok, fail) => GM_xmlhttpRequest({
    method: 'GET', url, responseType: type,
    onload: (r) => (r.status === 200 ? ok(r.response) : fail(new Error(`HTTP ${r.status}: ${url}`))),
    onerror: () => fail(new Error('Network error: ' + url)),
  }));

  const storeId = () => (/\/detail\/(?:[^/]+\/)?([a-p]{32})/.exec(location.pathname) || [])[1];

  // Patch a Chrome package so Firefox accepts it (same steps as the CRX Installer add-on).
  async function crxToXpi(crx, id) {
    const zip = await JSZip.loadAsync(crx); // JSZip skips the CRX header by itself
    // Chrome tolerates // comment lines in manifest.json; Firefox and JSON.parse don't.
    const m = JSON.parse((await zip.file('manifest.json').async('string')).replace(/^﻿/, '').replace(/^\s*\/\/.*$/gm, ''));
    const geckoId = `${id}@CWS_CRXInstaller`;

    // Firefox has no MV3 service workers: turn the worker into background scripts,
    // putting static importScripts() files first in the list.
    if (m.background && m.background.service_worker) {
      const sw = m.background.service_worker.replace(/^\/+/, '');
      const dir = sw.slice(0, sw.lastIndexOf('/') + 1);
      const imports = [];
      const code = (await zip.file(sw).async('string')).replace(/importScripts\s*\(([^)]*)\)/g, (_, args) => {
        for (const [, s] of args.matchAll(/['"`]([^'"`]+)['"`]/g)) imports.push(s.startsWith('/') ? s.slice(1) : dir + s);
        return '';
      });
      zip.file(sw, code);
      m.background = { ...m.background, scripts: [...new Set(imports), sw] };
      delete m.background.service_worker;
    }
    delete m.update_url;
    m.browser_specific_settings = { gecko: { id: geckoId } };
    for (const r of m.web_accessible_resources || []) {
      if (r.extension_ids) r.extension_ids = [geckoId];
      if (r.matches) r.matches = r.matches.filter((x) => !x.startsWith('chrome-extension://'));
    }
    zip.file('manifest.json', JSON.stringify(m, null, 2));
    zip.remove('_metadata'); // Chrome Web Store signature data, meaningless to Firefox
    return zip.generateAsync({ type: 'blob', mimeType: 'application/x-xpinstall' });
  }

  // If the developer publishes an official Firefox version, prefer that (signed, auto-updating).
  async function firefoxAlternative(id) {
    try {
      const maps = JSON.parse(await get('https://services.addons.mozilla.org/api/v5/addons/browser-mappings/?browser=chrome', 'text'));
      const hit = maps.results.find((x) => x.extension_id === id);
      return hit ? `https://addons.mozilla.org/firefox/addon/${encodeURIComponent(hit.addon_guid)}/` : null;
    } catch (e) { return null; }
  }

  async function install(download) {
    const id = storeId();
    if (!id) return alert('Open an extension page on the Chrome Web Store first.');
    const alt = await firefoxAlternative(id);
    if (alt && confirm('There is an official Firefox version of this extension. Open it instead?')) return void (location.href = alt);
    btn.textContent = 'Converting…';
    try {
      const crx = await get(`https://clients2.google.com/service/update2/crx?response=redirect&prodversion=140&acceptformat=crx3&x=id%3D${id}%26installsource%3Dondemand%26uc`);
      const url = URL.createObjectURL(await crxToXpi(crx, id));
      if (download) Object.assign(document.createElement('a'), { href: url, download: `${id}.xpi` }).click();
      else location.href = url; // Firefox shows its add-on install prompt
    } catch (e) {
      alert('CRX Installer: ' + e.message);
    } finally {
      btn.textContent = 'Add to Firefox';
    }
  }

  const btn = Object.assign(document.createElement('button'), { textContent: 'Add to Firefox', title: 'Shift-click to download the .xpi instead' });
  btn.style.cssText = 'position:fixed;right:16px;bottom:16px;z-index:2147483647;padding:10px 18px;border:0;border-radius:20px;background:#0b57d0;color:#fff;font:600 14px system-ui;cursor:pointer;box-shadow:0 2px 8px #0004';
  btn.addEventListener('click', (e) => install(e.shiftKey));
  setInterval(() => { // the store is a single-page app: show the button only on detail pages
    if (storeId() && !btn.isConnected) document.body.append(btn);
    if (!storeId() && btn.isConnected) btn.remove();
  }, 500);
  GM_registerMenuCommand('Download as .xpi', () => install(true));

  if (typeof window.__crxInstallerTest === 'function') window.__crxInstallerTest({ crxToXpi });
})();
