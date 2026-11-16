#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  bash ./build-latex.sh <path-to-tex>

Build a .tex file inside this repository with latexmk.
Auxiliary files stay under trash/, mirroring the source directory structure.
The resulting PDF is copied beside the original .tex source.

Example:
  bash ./build-latex.sh "Companies/Flexspring/NathanNg_Flexspring_Full_Stack_Developer_co-op_NotProvided_2026-09-30.tex"
EOF
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

if [[ $# -lt 1 ]]; then
  usage >&2
  exit 1
fi

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
source_arg="$1"

if [[ "$source_arg" != /* ]]; then
  source_path="$script_dir/$source_arg"
else
  source_path="$source_arg"
fi

if command -v realpath >/dev/null 2>&1; then
  source_path="$(realpath -m "$source_path")"
fi

if [[ "$source_path" != "$script_dir"* ]]; then
  echo "Choose a .tex source inside this repository." >&2
  exit 1
fi

if [[ "${source_path##*.}" != "tex" ]]; then
  echo "Choose a .tex source inside this repository." >&2
  exit 1
fi

source_dir="$(dirname -- "$source_path")"
source_name="$(basename -- "$source_path")"
relative_dir="${source_dir#$script_dir/}"
relative_dir="${relative_dir#/}"

if [[ -n "$relative_dir" ]]; then
  build_dir="$script_dir/trash/$relative_dir"
else
  build_dir="$script_dir/trash"
fi
mkdir -p "$build_dir"

pdf_name="${source_name%.tex}.pdf"

pushd "$source_dir" >/dev/null
trap 'popd >/dev/null || true' EXIT

latexmk -norc -pdf -interaction=nonstopmode -halt-on-error -file-line-error -synctex=1 \
  "-outdir=$build_dir" "-auxdir=$build_dir" "$source_path"

if [[ $? -ne 0 ]]; then
  echo "LaTeX build failed; see logs in $build_dir" >&2
  exit 1
fi

cp -f "$build_dir/$pdf_name" "$source_dir/$pdf_name"
rm -f "$build_dir/$pdf_name"
echo "PDF: $source_dir/$pdf_name"
