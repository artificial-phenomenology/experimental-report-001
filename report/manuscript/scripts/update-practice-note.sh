#!/usr/bin/env bash
set -Eeuo pipefail

root_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
output_file="${1:-${root_dir}/.cache/ai-native-practice-note.md}"
revision_file="${2:-${root_dir}/.cache/ai-native-practice-note.revision}"
repo_url="${AI_NATIVE_PRACTICE_REPO:-https://github.com/leoferres/ai-native-practice.git}"
branch="${AI_NATIVE_PRACTICE_BRANCH:-main}"
note_path="ai-native-practice-note.md"
repo_cache="${root_dir}/.cache/ai-native-practice"
vendored_note="${root_dir}/vendor/ai-native-practice-note.md"
vendored_revision="${root_dir}/vendor/ai-native-practice-note.revision"

mkdir -p "$(dirname "${output_file}")" "$(dirname "${revision_file}")"
tmp_note="$(mktemp "${output_file}.tmp.XXXXXX")"
tmp_revision="$(mktemp "${revision_file}.tmp.XXXXXX")"
trap 'rm -f "${tmp_note}" "${tmp_revision}"' EXIT

write_result() {
  local source_note="$1"
  local revision="$2"
  test -s "${source_note}" || {
    echo "Practice note is empty: ${source_note}" >&2
    return 1
  }
  if [[ "${source_note}" != "${tmp_note}" ]]; then
    cp "${source_note}" "${tmp_note}"
  fi
  printf '%s\n' "${revision}" > "${tmp_revision}"
  mv "${tmp_note}" "${output_file}"
  mv "${tmp_revision}" "${revision_file}"
  echo "Practice note revision: ${revision}"
}

if [[ -n "${AI_NATIVE_PRACTICE_SOURCE:-}" ]]; then
  local_source="${AI_NATIVE_PRACTICE_SOURCE}"
  if [[ -d "${local_source}" ]]; then
    source_note="${local_source}/${note_path}"
    revision="local-$(git -C "${local_source}" rev-parse HEAD 2>/dev/null || printf 'working-copy')"
  else
    source_note="${local_source}"
    revision="local-file"
  fi
  write_result "${source_note}" "${revision}"
  exit 0
fi

mkdir -p "${repo_cache}"
if [[ ! -d "${repo_cache}/.git" ]]; then
  git -C "${repo_cache}" init --quiet
  git -C "${repo_cache}" remote add origin "${repo_url}"
else
  git -C "${repo_cache}" remote set-url origin "${repo_url}"
fi

if git -C "${repo_cache}" fetch --quiet --depth=1 origin "${branch}"; then
  revision="$(git -C "${repo_cache}" rev-parse FETCH_HEAD)"
  git -C "${repo_cache}" show "FETCH_HEAD:${note_path}" > "${tmp_note}"
  write_result "${tmp_note}" "${revision}"
  exit 0
fi

if [[ -s "${output_file}" && -s "${revision_file}" ]]; then
  echo "Warning: GitHub is unavailable; retaining cached practice note." >&2
  exit 0
fi

echo "Warning: GitHub is unavailable; using the vendored practice note." >&2
write_result "${vendored_note}" "$(<"${vendored_revision}")"
