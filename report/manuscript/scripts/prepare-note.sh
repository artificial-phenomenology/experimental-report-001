#!/usr/bin/env bash
set -Eeuo pipefail

source_note="$1"
revision_file="$2"
output_file="$3"
revision="$(<"${revision_file}")"
short_revision="${revision:0:12}"
source_url="https://github.com/leoferres/ai-native-practice/blob/main/ai-native-practice-note.md"

mkdir -p "$(dirname "${output_file}")"
{
  printf '\\newpage\n\n'
  printf '# AI-Native Practice Note {.unnumbered}\n\n'
  printf '*Automatically synchronized from [ai-native-practice-note.md](%s); revision `%s`.*\n\n' \
    "${source_url}" "${short_revision}"
  cat "${source_note}"
  printf '\n'
} > "${output_file}"
