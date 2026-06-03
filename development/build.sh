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

rm -rf dist build *.egg-info src/*.egg-info

python -m build --outdir dist

echo "Build complete. Artifacts are in dist/"
