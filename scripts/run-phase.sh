#!/usr/bin/env bash
# Starts Codex on one build phase.
# Usage: ./scripts/run-phase.sh <phase-number> [--exec]
#   no flag : opens Codex interactively with the phase prompt (recommended)
#   --exec  : runs Codex non-interactively and exits when the phase is done

set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
phase="${1:-}"
mode="${2:-}"

if [[ -z "$phase" ]]; then
  echo "usage: $0 <phase-number 0-8> [--exec]" >&2
  exit 1
fi

if ! command -v codex >/dev/null 2>&1; then
  echo "codex is not installed or not on PATH" >&2
  exit 1
fi

matches=("$root"/prompts/phase-"$phase"-*.md)
if [[ ! -f "${matches[0]}" ]]; then
  echo "no prompt file found for phase $phase" >&2
  exit 1
fi

prompt_file="${matches[0]}"
echo "Phase $phase: $(basename "$prompt_file")"

cd "$root"
if [[ "$mode" == "--exec" ]]; then
  codex exec "$(cat "$prompt_file")"
else
  codex "$(cat "$prompt_file")"
fi
