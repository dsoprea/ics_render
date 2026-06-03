#!/usr/bin/env bash
set -euo pipefail

script_directory="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
project_root="$(cd "${script_directory}/.." && pwd)"

cd "${project_root}"

if [[ -f .venv/bin/activate ]]; then
    # shellcheck source=/dev/null
    source .venv/bin/activate
fi

python -m pip install -e ".[build]"

if [[ ! -d dist ]] || [[ -z "$(find dist -maxdepth 1 -type f 2>/dev/null | head -n 1)" ]]; then
    echo "No files in dist/. Run development/build.sh first." >&2
    exit 1
fi

python -m twine check dist/*

python -m twine upload dist/*

echo "Upload complete."
