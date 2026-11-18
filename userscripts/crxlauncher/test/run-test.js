const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
const [,, userscript, port] = process.argv;
const base = `http://localhost:${port}`;
const init = [
  fs.readFileSync(require.resolve('jszip/dist/jszip.min.js'), 'utf8'),
  fs.readFileSync(path.join(__dirname, 'gm-polyfill.js'), 'utf8'),
  fs.readFileSync(userscript, 'utf8'),
].join('\n;\n');
const ok = (c, m) => { console.log((c ? 'PASS ' : 'FAIL ') + m); if (!c) process.exitCode = 1; };
(async () => {
  const browser = await chromium.launch();
  const context = await browser.newContext({ locale: 'en-US' }); const page = await context.newPage();
  const errors = [];
  page.on('console', (m) => { if (m.type() === 'error' || m.type() === 'warning') errors.push(m.text()); });
  page.on('pageerror', (e) => errors.push('pageerror: ' + e.message));
  await page.addInitScript(init);
  await page.goto(base + '/index.html');

  // 1. CRX3 parsing + extension-ID derivation using the real CRXLauncher package (optional).
  const crx = await page.evaluate(async () => {
    const res = await fetch('/crxlauncher.crx');
    if (!res.ok) return null;
    const buf = await res.arrayBuffer();
    const m = await window.__crx.install(buf, 'kiilhncajadbgbmdbdcopdpnmdhlbdle');
    const out = { id: m.id, mv: m.manifest.manifest_version, files: Object.keys(localStorage).filter((k) => k.includes('f:' + m.id)).length };
    window.__crx.uninstall(m.id);
    out.leftover = Object.keys(localStorage).filter((k) => k.includes(m.id)).length;
    return out;
  });
  if (!crx) console.log('SKIP CRX3 test (www/crxlauncher.crx not present)');
  else {
  ok(crx.mv === 3 && crx.files > 10, 'raw .crx read by JSZip (' + crx.files + ' files)');
  ok(crx.leftover === 0, 'uninstall removes all keys');
  }

  // 2. Install the test extension from a ZIP and reload.
  const meta = await page.evaluate(async () => {
    const buf = await (await fetch('/ext.zip')).arrayBuffer();
    const m = await window.__crx.install(buf);
    return { id: m.id, cs: m.manifest.content_scripts.length };
  });
  ok(!!meta.id, 'zip installed with id ' + meta.id);
  await page.reload();
  try { await page.waitForFunction(() => document.body && document.body.dataset.result, null, { timeout: 5000 }); } catch (e) { console.log('ERRORS', errors); throw e; }
  const r = JSON.parse(await page.evaluate(() => document.body.dataset.result));
  console.log('content result:', JSON.stringify(r));
  ok(!r.error, 'content script ran without error');
  ok(r.shared === 'from-a', 'content scripts share one scope across files/phases');
  ok(r.startState !== 'complete', 'document_start ran before load: ' + r.startState);
  ok(r.idleState !== 'loading', 'document_idle ran after DOM parsed');
  ok(r.greet === 'Hello Bob! (Bob)', 'i18n placeholders: ' + r.greet);
  ok(r.id === meta.id, 'runtime.id');
  ok(r.pong && r.pong.pong === 42, 'runtime.sendMessage → background async sendResponse');
  ok(r.pong && r.pong.bgInfo.lib === 'lib-ok', 'importScripts inlined');
  ok(r.pong && r.pong.senderTab === true, 'sender.tab set for content scripts');
  ok(r.cbStyle && r.cbStyle.pong === 2, 'callback-style sendMessage');
  ok(r.stored.fromCs === 7, 'storage.local set/get');
  ok(r.stored.installReason === 'install', 'runtime.onInstalled fired with reason install');
  ok(r.hasTabs === 'object' || r.hasTabs === 'function', 'unknown APIs are stubbed (chrome.tabs in CS => stub)');
  ok(r.imgWidth === 4, 'runtime.getURL serves packaged image');
  ok(r.dataJson && r.dataJson.v === 99, 'fetch(getURL(json)) works');
  ok(r.portEcho && r.portEcho.echo.hi === 1 && r.portEcho.name === 'p1', 'runtime.connect ports');
  ok(r.color === 'rgb(1, 2, 3)', 'content CSS injected with __MSG_ substitution');
  ok(r.bg && r.bg.startsWith('url("blob:'), 'CSS url() rewritten to package blob');

  // 3. Menus, popup, options.
  const menus = await page.evaluate(() => window.__menus.filter(Boolean).map((m) => m.t));
  console.log('menus:', menus);
  ok(menus.some((t) => t.includes('Test menu')), 'contextMenus.create → menu command');
  await page.evaluate(() => window.__menus.filter(Boolean).find((m) => m.t.includes('Test menu')).f());
  await page.waitForTimeout(100);
  const menuClicked = await page.evaluate((id) => JSON.parse(localStorage.getItem('__gm:s:' + id + ':local')).menuClicked, meta.id);
  ok(menuClicked === 'm1', 'contextMenus.onClicked fired');

  const popup = await page.evaluate(async (id) => {
    const ext = window.__crx.loaded.find((e) => e.id === id);
    const node = window.__crx.openPage(ext, 'popup.html', 'popup');
    const doc = node.querySelector('iframe').contentDocument;
    for (let i = 0; i < 50 && doc.getElementById('h').textContent === 'loading'; i++) await new Promise((r) => setTimeout(r, 50));
    const imgOk = doc.getElementById('i').naturalWidth;
    return { text: doc.getElementById('h').textContent, imgOk, w: node.querySelector('iframe').style.width };
  }, meta.id);
  console.log('popup:', popup.text);
  const p = JSON.parse(popup.text);
  ok(p.bg && p.bg.ok === 'bg-got-popup', 'popup → background messaging');
  ok(p.cs && p.cs.fromCs === 42 && p.cs.title === 'Test Page', 'popup tabs.sendMessage → content script');
  ok(p.exec === 'Test Page!', 'scripting.executeScript(func,args)');
  ok(p.h1color === 'rgb(9, 8, 7)', 'popup stylesheet applied');
  ok(p.tabUrl === base + '/index.html', 'tabs.query returns current tab');
  ok(p.stored.fromCs === 7, 'popup sees same storage');
  ok(popup.imgOk === 4, 'popup <img src> rewritten');
  ok(parseInt(popup.w) >= 220 && parseInt(popup.w) < 400, 'popup auto-sized: ' + popup.w);
  const sess = await page.evaluate(() => new Promise((r) => setTimeout(r, 50)));

  const opts = await page.evaluate((id) => {
    const ext = window.__crx.loaded.find((e) => e.id === id);
    const node = window.__crx.openPage(ext, 'options.html', 'options');
    return node.querySelector('iframe').contentDocument.getElementById('o').textContent;
  }, meta.id);
  ok(opts === 'options:Test Ext', 'options page with inline script + i18n: ' + opts);

  // 4. exclude_matches + storage.onChanged across tabs
  const page2 = await page.context().newPage();
  await page2.addInitScript(init);
  await page2.goto(base + '/excluded.html');
  await page2.waitForTimeout(600);
  ok(!(await page2.evaluate(() => document.body.dataset.result)) && (await page2.evaluate(() => document.documentElement.dataset.a)) === 'loading', 'exclude_matches honoured, other entry still runs');

  await page.evaluate(() => { window.__changes = []; });
  await page.evaluate((id) => {
    const ext = window.__crx.loaded.find((e) => e.id === id);
    ext.cs.api.storage.onChanged.addListener((c, area) => window.__changes.push({ c, area }));
  }, meta.id);
  await page2.evaluate((id) => {
    const ext = window.__crx.loaded.find((e) => e.id === id);
    return ext.cs.api.storage.local.set({ crossTab: 'yes' });
  }, meta.id);
  await page.waitForTimeout(200);
  const ch = await page.evaluate(() => window.__changes);
  ok(ch.some((x) => x.area === 'local' && x.c.crossTab && x.c.crossTab.newValue === 'yes'), 'storage.onChanged fires across tabs');

  const bgFetch = await page.evaluate((id) => window.__crx.loaded.find((e) => e.id === id).cs.api.storage.session.get('bgFetch'), meta.id);
  ok(bgFetch.bgFetch === 99, 'background fetch(relative package path)');


  // 5. Firefox converter: CRX/ZIP → XPI manifest patching.
  const fxPage = await context.newPage();
  await fxPage.goto(base + '/index.html');
  await fxPage.addScriptTag({ content: fs.readFileSync(require.resolve('jszip/dist/jszip.min.js'), 'utf8') });
  await fxPage.evaluate(() => { window.GM_xmlhttpRequest = () => {}; window.GM_registerMenuCommand = () => {}; window.__crxInstallerTest = (t) => { window.__fx = t; }; });
  await fxPage.addScriptTag({ content: fs.readFileSync(path.join(path.dirname(userscript), 'crx-installer-firefox.user.js'), 'utf8') });
  const fx = await fxPage.evaluate(async () => {
    const xpi = await window.__fx.crxToXpi(await (await fetch('/ext.zip')).arrayBuffer(), 'abc');
    const z = await JSZip.loadAsync(xpi);
    const m = JSON.parse(await z.file('manifest.json').async('string'));
    return { type: xpi.type, bg: m.background, gecko: m.browser_specific_settings.gecko.id, sw: await z.file('sw.js').async('string'), hasMeta: !!z.file(/^_metadata\//).length };
  });
  ok(fx.type === 'application/x-xpinstall', 'XPI blob type');
  ok(JSON.stringify(fx.bg.scripts) === '["lib.js","sw.js"]' && !fx.bg.service_worker, 'service_worker → background.scripts with importScripts first');
  ok(!/importScripts/.test(fx.sw), 'importScripts calls removed');
  ok(fx.gecko === 'abc@CWS_CRXInstaller', 'gecko id set');
  const relevant = errors.filter((e) => !/declarativeNetRequest|not emulated/.test(e));
  console.log('console warnings/errors:', errors);
  ok(relevant.length === 0, 'no unexpected console errors');
  await browser.close();
})().catch((e) => { console.error(e); process.exit(1); });
