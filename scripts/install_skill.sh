#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
skill_source="${repo_root}/skills/paper-explainer"
skills_home="${CODEX_HOME:-${HOME}/.codex}/skills"
skill_target="${skills_home}/paper-explainer"

if [[ ! -d "${skill_source}" ]]; then
  echo "missing skill source: ${skill_source}" >&2
  exit 1
fi

mkdir -p "${skills_home}"

if [[ -L "${skill_target}" ]]; then
  current_target="$(readlink "${skill_target}")"
  if [[ "${current_target}" == "${skill_source}" ]]; then
    echo "skill already installed: ${skill_target}"
    exit 0
  fi
  echo "refusing to replace existing symlink: ${skill_target} -> ${current_target}" >&2
  exit 1
fi

if [[ -e "${skill_target}" ]]; then
  echo "refusing to replace existing skill path: ${skill_target}" >&2
  exit 1
fi

ln -s "${skill_source}" "${skill_target}"
echo "installed skill: ${skill_target} -> ${skill_source}"
