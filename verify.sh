#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

inventory_tmp="$(mktemp)"
manifest_paths_tmp="$(mktemp)"
actual_paths_tmp="$(mktemp)"
trap 'rm -f "${inventory_tmp}" "${manifest_paths_tmp}" "${actual_paths_tmp}"' EXIT

find . -type f \
  -not -path './.git/*' \
  -not -path './report/manuscript/build/*' \
  -not -path './report/manuscript/.cache/*' \
  -not -path '*/__pycache__/*' \
  -not -name '*.pyc' \
  -not -path './FILE_INVENTORY.txt' \
  -not -path './MANIFEST.sha256' \
  -printf '%s\t%P\n' | LC_ALL=C sort -k2,2 > "${inventory_tmp}"
cmp FILE_INVENTORY.txt "${inventory_tmp}"
echo 'file inventory: PASS'

sed -E 's/^[0-9a-f]{64}  //' MANIFEST.sha256 | LC_ALL=C sort > "${manifest_paths_tmp}"
find . -type f \
  -not -path './.git/*' \
  -not -path './report/manuscript/build/*' \
  -not -path './report/manuscript/.cache/*' \
  -not -path '*/__pycache__/*' \
  -not -name '*.pyc' \
  -not -path './MANIFEST.sha256' \
  -printf './%P\n' | LC_ALL=C sort > "${actual_paths_tmp}"
cmp "${manifest_paths_tmp}" "${actual_paths_tmp}"
echo 'manifest coverage: PASS'

sha256sum --check MANIFEST.sha256
python3 tools/recompute_core_claims.py
