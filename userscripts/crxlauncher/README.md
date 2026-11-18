# Running Chrome extensions from a userscript

There are two scripts, one per browser. They differ because the browsers differ.

| Script | Browser | How it works | Lines |
|---|---|---|---|
| `crx-installer-firefox.user.js` | Firefox family | Converts the CRX into an XPI. **Firefox runs it natively**, so nothing is emulated. | ~100 |
| `crx-runner.user.js` | Chrome / Chromium | Emulates the core of `chrome.*` inside the userscript sandbox. | ~500 |

## The two upstream extensions

They are **different projects** with the same goal.

**CRXLauncher** (Chrome, `kiilhncajadbgbmdbdcopdpnmdhlbdle`) is closed source and bundled with React. It emulates `chrome.*`
for one guest extension and injects the guest's content scripts into the **page's own JS world**
on every site. It sends GA4 telemetry (hard-coded `G-Z14126F651`, a persistent client ID in `storage.sync`):
installs, the name and version of the guest extension every 2 h, page views, and **the hostname of every
site where any JS error fires**. crxlauncher.com can tell it to install or uninstall things through
`externally_connectable`.

**CRX Installer** (Firefox, `XPIPorter@XPIPorter`, v3.3) is about 200 lines of readable code with no telemetry.
It adds an "Add to Firefox" button on the Chrome Web Store, downloads the CRX, patches `manifest.json`, and
hands the result to Firefox's installer:
- `background.service_worker` → `background.scripts`, with static `importScripts()` files listed first
- a `browser_specific_settings.gecko.id` of `<id>@CWS_CRXInstaller`
- `update_url` removed, and `chrome-extension://` entries removed from `web_accessible_resources`

Before converting, it checks Mozilla's `browser-mappings` API for an official Firefox port.
Unsigned XPIs need `xpinstall.signatures.required=false`, which only works on Nightly, Developer Edition,
ESR, LibreWolf, Floorp and Zen.

The Firefox userscript ports this behaviour. It also strips `//` comments from manifests, which Chrome accepts but
the original add-on fails on.

## crx-runner (Chrome): what it emulates

Chrome won't install CRXs from outside the Web Store, so emulation is the only option. The core is done properly.
Everything else is deliberately simple:

| Real thing | Emulation |
|---|---|
| Content scripts, CSS, `run_at` | Real: matching rules, one shared scope across files (a generator that yields between phases), CSS from constructable stylesheets (immune to CSP). |
| Isolated world | The userscript sandbox. The page never sees `chrome` or the guest's variables. |
| Service worker / background page | Code in a hidden `about:blank` iframe in the top frame, started when first needed. One copy per tab. |
| Popup / options | Overlay iframe in a closed shadow root. Scripts run with `with (iframeWindow)`, so the site's CSP can't block them. |
| Messaging, ports | In-tab event bus. |
| `storage` | GM storage; `onChanged` fires across tabs. |
| `i18n`, `getURL` | Locale fallback chain; packaged files served as `blob:` URLs. |
| `alarms` | `setTimeout`, lives while the tab lives. |
| `contextMenus` | Userscript menu commands. |
| `permissions` | Always granted. |
| Any other API | A stub that resolves to `undefined` and whose events never fire. |

Not possible from a userscript: `webRequest`, `declarativeNetRequest`, `cookies`, `proxy`, other tabs
and windows, and ES-module background or page scripts.

## Tests

```bash
npm i jszip playwright
CRX=./some.crx userscripts/crxlauncher/test/run.sh   # CRX is optional
```

The suite loads the scripts into Chromium with a `GM_*` polyfill and runs 40 checks against
`test/fixture-extension`, which exercises every row above, plus the Firefox manifest conversion.
It doesn't run them inside a real userscript manager.
