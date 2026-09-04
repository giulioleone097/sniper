#!/bin/sh
# sniper: name the checks a path's own project already has, so prove/review/simplify
# run the repository's commands instead of guessing. No plugin, no config.
#
#   sh checks.sh [path]      path defaults to . ; walks up to the nearest project file
#
# Prints one key=value per line, in the order a proof ladder runs them:
#   project=<dir that owns the path>
#   typecheck=<cmd> | lint=<cmd> | test=<cmd> | build=<cmd>     only the ones that exist
#   none=1                                                      when nothing is configured
# Every command is printed for the caller to run from `project=`; nothing runs here.

start=$(cd "${1:-.}" 2>/dev/null && pwd) || { echo "none=1"; exit 0; }
[ -f "$start" ] && start=$(dirname "$start")

dir="$start"
while [ "$dir" != "/" ]; do
  if [ -f "$dir/project.json" ] || [ -f "$dir/package.json" ] || [ -f "$dir/pyproject.toml" ] || \
     [ -f "$dir/Cargo.toml" ] || [ -f "$dir/go.mod" ] || [ -f "$dir/Makefile" ] || \
     ls "$dir"/*.csproj >/dev/null 2>&1 || ls "$dir"/*.sln >/dev/null 2>&1; then
    break
  fi
  dir=$(dirname "$dir")
done
[ "$dir" = "/" ] && { echo "none=1"; exit 0; }
echo "project=$dir"

found=0
emit() { echo "$1=$2"; found=1; }

# nx workspace project: targets in project.json, run from the workspace root
if [ -f "$dir/project.json" ] && command -v python3 >/dev/null 2>&1; then
  root="$dir"; while [ "$root" != "/" ] && [ ! -f "$root/nx.json" ]; do root=$(dirname "$root"); done
  name=$(python3 -c "import json,sys;print(json.load(open(sys.argv[1])).get('name',''))" "$dir/project.json" 2>/dev/null)
  targets=$(python3 -c "import json,sys;print(' '.join(json.load(open(sys.argv[1])).get('targets',{}).keys()))" "$dir/project.json" 2>/dev/null)
  if [ -n "$name" ] && [ -f "$root/nx.json" ]; then
    for t in typecheck lint test build; do
      case " $targets " in *" $t "*) emit "$t" "cd $root && npx nx run $name:$t";; esac
    done
  fi
fi

# package.json scripts
if [ "$found" -eq 0 ] && [ -f "$dir/package.json" ] && command -v python3 >/dev/null 2>&1; then
  scripts=$(python3 -c "import json,sys;print(' '.join(json.load(open(sys.argv[1])).get('scripts',{}).keys()))" "$dir/package.json" 2>/dev/null)
  pm=npm; [ -f "$dir/pnpm-lock.yaml" ] && pm=pnpm; [ -f "$dir/yarn.lock" ] && pm=yarn; [ -f "$dir/bun.lockb" ] && pm=bun
  for t in typecheck lint test build; do
    case " $scripts " in *" $t "*) emit "$t" "$pm run $t";; esac
  done
  case " $scripts " in *" typecheck "*) ;; *) [ -f "$dir/tsconfig.json" ] && emit typecheck "npx tsc --noEmit -p $dir/tsconfig.json";; esac
fi

# python project
if [ "$found" -eq 0 ] && [ -f "$dir/pyproject.toml" ]; then
  runner="python -m"; [ -f "$dir/uv.lock" ] && runner="uv run"
  grep -qE '^\[tool\.(pytest|pytest\.ini_options)\]' "$dir/pyproject.toml" 2>/dev/null && emit test "$runner pytest -q"
  grep -qE '^\[tool\.(mypy|pyright)\]' "$dir/pyproject.toml" 2>/dev/null && emit typecheck "$runner mypy ."
  grep -qE '^\[tool\.ruff' "$dir/pyproject.toml" 2>/dev/null && emit lint "$runner ruff check ."
  [ "$found" -eq 0 ] && [ -d "$dir/tests" ] && emit test "$runner pytest -q"
fi

# .NET
if [ "$found" -eq 0 ] && { ls "$dir"/*.csproj >/dev/null 2>&1 || ls "$dir"/*.sln >/dev/null 2>&1; }; then
  proj=$(ls "$dir"/*.sln 2>/dev/null | head -1); [ -z "$proj" ] && proj=$(ls "$dir"/*.csproj | head -1)
  emit build "dotnet build \"$proj\" --nologo -v q"
  case "$proj" in *Test*|*Tests*|*UnitTest*) emit test "dotnet test \"$proj\" --nologo -v q";; esac
fi

# rust, go, make
[ "$found" -eq 0 ] && [ -f "$dir/Cargo.toml" ] && { emit typecheck "cargo check"; emit test "cargo test"; }
[ "$found" -eq 0 ] && [ -f "$dir/go.mod" ] && { emit build "go build ./..."; emit test "go test ./..."; }
if [ "$found" -eq 0 ] && [ -f "$dir/Makefile" ]; then
  for t in lint test build check; do grep -qE "^$t:" "$dir/Makefile" && emit "$t" "make $t"; done
fi

[ "$found" -eq 0 ] && echo "none=1"
exit 0
