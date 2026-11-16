#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  bash ./build-all.sh

Build every .tex file in the repository tree, starting from the parent of this script.
EOF
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

if [[ $# -gt 0 ]]; then
  usage >&2
  exit 1
fi

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
repo_root="$(cd -- "$script_dir/.." && pwd -P)"
build_script="$script_dir/build-latex.sh"

if [[ ! -f "$build_script" ]]; then
  echo "Missing build script: $build_script" >&2
  exit 1
fi

mapfile -t tex_files < <(
  find "$repo_root" \
    -type f \
    -name '*.tex' \
    ! -path "$repo_root/.git/*" \
    ! -path "$repo_root/trash/*" \
    | sort -V
)

if [[ ${#tex_files[@]} -eq 0 ]]; then
  echo "No .tex files found under $repo_root."
  exit 0
fi

built_count=0

for tex_file in "${tex_files[@]}"; do
  echo "Building: ${tex_file#$repo_root/}"
  bash "$build_script" "$tex_file"
  built_count=$((built_count + 1))
done

echo "Built $built_count .tex file(s)."
