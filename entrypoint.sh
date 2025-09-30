#!/usr/bin/env bash
set -euo pipefail

: "${FAVA_HOST:=0.0.0.0}"
: "${FAVA_PORT:=5000}"
: "${LEDGER_FILE:=}"
: "${FAVA_OPTIONS:=}"

# If a custom ledger is provided, use it; else use the repo example
if [[ -n "$LEDGER_FILE" ]]; then
  LEDGER_PATH="$LEDGER_FILE"
else
  LEDGER_PATH="/opt/fava/contrib/examples/example.beancount"
fi

if [[ ! -f "$LEDGER_PATH" ]]; then
  echo "ERROR: Ledger file not found: $LEDGER_PATH" >&2
  echo "Tip: mount your data dir and set LEDGER_FILE, e.g.:" >&2
  echo "  -v \"\$PWD/data:/data\" -e LEDGER_FILE=/data/ledger.beancount" >&2
  exit 2
fi

echo "Starting Fava:"
echo "  Ledger: $LEDGER_PATH"
echo "  Host:   $FAVA_HOST"
echo "  Port:   $FAVA_PORT"
if [[ -n "$FAVA_OPTIONS" ]]; then
  echo "  Extra:  $FAVA_OPTIONS"
fi

exec fava "$LEDGER_PATH" --host "$FAVA_HOST" --port "$FAVA_PORT" $FAVA_OPTIONS
