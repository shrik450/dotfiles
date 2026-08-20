#!/bin/sh
# Keeps ~/.claude/skills/herdr/SKILL.md in sync with the installed herdr binary.
# Rewrites the skill only when `herdr --version` changes, so normal sessions do
# no work. Not managed by herdr; safe to edit.

set -eu

skill_dir="${HOME}/.claude/skills/herdr"
skill_file="${skill_dir}/SKILL.md"
stamp_file="${skill_dir}/.version"

command -v herdr >/dev/null 2>&1 || exit 0

version="$(herdr --version 2>/dev/null)" || exit 0
[ -n "$version" ] || exit 0

if [ -f "$skill_file" ] && [ -f "$stamp_file" ]; then
  [ "$(cat "$stamp_file" 2>/dev/null)" = "$version" ] && exit 0
fi

mkdir -p "$skill_dir" || exit 0
tmp_file="$(mktemp "${skill_dir}/.SKILL.XXXXXX")" || exit 0
if herdr --skill >"$tmp_file" 2>/dev/null && [ -s "$tmp_file" ]; then
  mv "$tmp_file" "$skill_file"
  printf '%s\n' "$version" >"$stamp_file"
else
  rm -f "$tmp_file"
fi

exit 0
