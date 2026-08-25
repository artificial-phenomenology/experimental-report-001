#!/usr/bin/env bash
set -Eeuo pipefail

paper_file="$1"
note_file="$2"
output_file="$3"

mkdir -p "$(dirname "${output_file}")"
{
  cat "${paper_file}"
  printf '\n\n'
  cat "${note_file}"
} > "${output_file}"
