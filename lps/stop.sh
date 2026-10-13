#!/bin/sh
# Stop supervisor first (so it cannot respawn), then the engine; verify.
cd "$(dirname "$0")"
if [ -f search.pid ]; then
  awk '/supervisor/ {print $2}' search.pid | xargs -r kill 2>/dev/null
  sleep 1
  awk '/engine/ {print $2}' search.pid | xargs -r kill 2>/dev/null
fi
pkill -f 'engine734 12000' 2>/dev/null
sleep 7   # longer than the supervisor's 5s respawn window
if pgrep -f 'engine734|run\.sh' > /dev/null; then
  echo "STILL RUNNING:"; pgrep -fl 'engine734|run\.sh'; exit 1
fi
rm -f search.pid
echo "stopped cleanly"
./status.sh
