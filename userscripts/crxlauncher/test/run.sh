#!/usr/bin/env bash
# Usage: test/run.sh   (needs node, python3, zip, npm packages: playwright, jszip)
# Optional: put a CRX3 file of CRXLauncher at $WWW/crxlauncher.crx to test CRX header parsing.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
WWW="$(mktemp -d)"
cp "$HERE/index.html" "$HERE/excluded.html" "$WWW/"
(cd "$HERE/fixture-extension" && zip -qr "$WWW/ext.zip" .)
[ -n "${CRX:-}" ] && cp "$CRX" "$WWW/crxlauncher.crx"
PORT=${PORT:-8765}
python3 -m http.server "$PORT" --directory "$WWW" >/dev/null 2>&1 &
SRV=$!
trap 'kill $SRV; rm -rf "$WWW"' EXIT
sleep 1
node "$HERE/run-test.js" "$HERE/../crx-runner.user.js" "$PORT"
