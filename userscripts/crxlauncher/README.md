# CRX Runner: a userscript that does what CRXLauncher does

`crx-runner.user.js` is a single userscript for Tampermonkey or Violentmonkey. It runs Chrome
extensions (`.crx`, `.zip`, or a Chrome Web Store URL or ID) without installing them in the browser.
It re-implements the idea behind the
[CRXLauncher](https://chromewebstore.google.com/detail/kiilhncajadbgbmdbdcopdpnmdhlbdle) extension,
without the parts listed below.

## What CRXLauncher actually is (reverse-engineering notes)

These notes are based on version 1.1.0 (`kiilhncajadbgbmdbdcopdpnmdhlbdle`), downloaded from the Web Store
update endpoint and unpacked from its CRX3 container.

**Architecture.** CRXLauncher is a "meta-extension". It hosts one guest extension inside itself by
emulating the `chrome.*` API:

| Piece | File | Role |
|---|---|---|
| Engine | `assets/js/bg.js` | Unzips the guest (JSZip), "compiles" manifest, locales, content scripts, popup and options, and stores them in `chrome.storage.local`. |
| Background host | `offscr.html` → `sb.html` (`sb.js`) | Runs the guest's service worker inside a sandboxed iframe in an offscreen document, and proxies API calls back to `bg.js`. |
| Content bridge | `brg.js` (ISOLATED world) + `content.js` (**MAIN world**) + `vendor.js` (MAIN) | Registered with `chrome.scripting.registerContentScripts` on **every `http(s)://*/*` page, all frames**. `content.js` asks for the guest's content-script code and injects it as a `blob:` `<script>` into the page's own JS world, wrapped in a `chrome` shim plus webextension-polyfill. |
| Popup / side panel / options | `popup.js`, `panel.js`, `opt.js` (React) | Render the guest's UI pages, plus the installer and permission wizard. |

**Installation flow.** The crxlauncher.com website talks to the extension through
`externally_connectable` (`runtime.onMessageExternal` → `{action:"install", downloadUrl, updateUrl, appId}`).
It can also make the extension **uninstall itself** (`{action:"uninstall"}` → `management.uninstallSelf()`).
A `declarativeNetRequest` rule adds an `Extension: crxlauncher` header to every request to crxlauncher.com,
so the site can detect the extension.

**Telemetry and bloat found:**

- **GA4 Measurement Protocol** with hard-coded credentials (`measurement_id=G-Z14126F651`, plus an `api_secret`).
  A persistent random `client_id` is kept in `storage.sync`, so it follows your Google account across devices.
- Events sent: `installed`, `updated`, `extension` (guest **appId, name and version**, every 2 h),
  `extension_installed/updated/error`, `page_view` (each popup, panel or options open) and `installer_error`.
- **Browsing leak:** `brg.js` adds a `window.onerror` listener to **every page you visit**. Any JS error on any
  site sends `{type:"bridge_error", message, hostname}` to the background, which forwards it to Google Analytics.
  The result is a stream of the hostnames you visit, attached to your stable client id.
- Opens `crxlauncher.com/welcome` on install. Two alarms run: an auto-update every 30 min
  (fetching `updateUrl`) and a "no extension installed" nag every 60 min.
- Guest content scripts run in the **page's MAIN world**, together with the `chrome` shim. Any website can
  therefore see, hook or call into the guest extension and its storage. This is weaker isolation than a real
  extension's isolated world.
- `optional_host_permissions: http(s)://*/*`, `scripting` and `unlimitedStorage`: it asks for access to all sites.

## What the userscript does instead

- **No network traffic** except the downloads you start yourself (from the Web Store update endpoint or a URL you
  paste). No analytics, no auto-update pings, no website hooks.
- Guest code runs in the **userscript sandbox** (an isolated world), not in the page's JS world.
  The page cannot see `chrome`, the guest's variables or its storage.
- Storage lives in the userscript manager (`GM_setValue`), split by extension ID. It is shared across tabs, and
  `storage.onChanged` fires across tabs.

### Supported

| Area | Status |
|---|---|
| Install | `.crx` (v2/v3) and `.zip` files, Web Store URL or ID, direct URL. Extension ID is derived from the CRX3 header, the public key or `manifest.key`. Manifest comments are tolerated. |
| Content scripts | `matches`, `exclude_matches`, `include_globs`/`exclude_globs`, `all_frames`, `run_at` (start/end/idle), CSS (with `__MSG_*__` and `url()` rewriting), `world: "MAIN"`. All isolated-world files of one extension share **one scope**, as in Chrome, using a generator that yields between run_at phases. |
| Background | MV3 `service_worker` (static `importScripts` inlined; `window`/`document` hidden) and MV2 `scripts`/`page`. Runs in a hidden `about:blank` frame, started lazily (like a service worker waking up), and only in the top frame. |
| Messaging | `runtime.sendMessage`/`onMessage` (callbacks, `return true`, Promises), `runtime.connect`/`onConnect` ports, `tabs.sendMessage`/`tabs.connect` to content scripts. |
| Storage | `local`, `sync`, `session`, `managed` (empty), `onChanged` (including across tabs). |
| i18n | `getMessage` with `$1` and named placeholders, `@@extension_id`, UI-locale fallback chain. |
| Pages | Popup, options and `tabs.create({url:'page.html'})` open as overlays in a closed shadow root. Scripts run against the iframe's `window`, which makes them **immune to the site's CSP**. Styles use constructable stylesheets. `localStorage` is backed by GM storage. |
| Other APIs | `runtime.getURL` (blob URLs), privileged `fetch` (cross-origin via `GM_xmlhttpRequest`), `scripting.executeScript` (func+args / files / MAIN), `insertCSS`, `tabs.query/get/create/update`, `alarms`, `contextMenus` (become userscript menu commands), `notifications` (GM_notification), `downloads.download` (GM_download), `action.*` (`onClicked` comes from a menu command), `permissions` (always granted), `windows`. |
| Anything else | Becomes a stub that resolves to `undefined` and logs "not emulated" once. |

### Not supported (same as or worse than CRXLauncher)

`webRequest`, `declarativeNetRequest`, `proxy`, `cookies`, `debugger`, `nativeMessaging`, `history`, `bookmarks`,
`tabCapture`, `offscreen`, `sidePanel`, DevTools pages and ES-module background workers or pages (`import`).
Each tab runs its own copy of the background script, so global state is per tab; only storage is shared.
In sub-frames, content scripts have no background to message. Packaged files are kept in userscript storage,
which the manager loads into every page, so very large extensions slow page loads.

## Usage

1. Install Tampermonkey or Violentmonkey, then add `crx-runner.user.js`. In Chrome MV3 Tampermonkey, turn on
   *Allow User Scripts* for the extension, because the script needs `new Function`.
2. On any page, open the manager menu: **⚙ CRX Runner: manage extensions**.
3. Install from a file, or paste a Web Store link or ID. Reload the tab.
4. For each extension, the manager menu gets **▶ Name** (popup or action click), **⚙ Name: options** and one entry per
   `contextMenus` item.

## Tests

`test/run.sh` loads the userscript into Chromium (Playwright) with a GM_* polyfill. It installs
`test/fixture-extension`, an MV3 extension that exercises every emulated area, and checks 39 assertions.
If `CRX=/path/to/crxlauncher.crx` is set, it also checks CRX3 header parsing and ID derivation against the
real package.

```bash
npm i jszip playwright   # or use a global playwright
CRX=./crxlauncher.crx userscripts/crxlauncher/test/run.sh
```
