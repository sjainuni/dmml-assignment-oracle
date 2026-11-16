#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
source .venv/bin/activate
python scripts/run_pipeline.py
python scripts/oci_sync.py upload
