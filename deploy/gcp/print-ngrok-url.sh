#!/usr/bin/env bash
# Print public HTTPS URL from a running local ngrok agent (web inspect API on :4040).
set -euo pipefail
if ! curl -sf --max-time 2 http://127.0.0.1:4040/api/tunnels >/dev/null 2>&1; then
  echo "ngrok web inspect API not reachable on 127.0.0.1:4040 (is delphi-ngrok running?)"
  exit 1
fi
curl -sf --max-time 2 http://127.0.0.1:4040/api/tunnels | python3 -c "
import json, sys
d = json.load(sys.stdin)
tunnels = d.get('tunnels', [])
for proto in ('https', 'http'):
    for t in tunnels:
        if t.get('proto') == proto:
            print(t.get('public_url', ''))
            raise SystemExit(0)
print('', end='')
raise SystemExit(1)
"
