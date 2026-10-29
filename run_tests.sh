#!/bin/sh
# Run every automated check in the repository (≈ 1–2 minutes).
set -e
cd "$(dirname "$0")"
echo "== Python unit tests (agrawal/, clc/ scanners, theorem identities)"
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m pytest -q tests
echo "== k=4 enumerator self-tests and end-to-end checks"
make -C clc/k4 test
echo "ALL CHECKS PASSED"
