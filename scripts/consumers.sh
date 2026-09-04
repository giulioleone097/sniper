#!/bin/sh
# sniper: find what consumes this repository outside its own tree, with no registry,
# no config and no network. Read-only.
#
#   sh consumers.sh [repo] [search-root]
#     repo         defaults to . ; search-root defaults to the repo's parent directory
#
# Prints one key=value per line:
#   name=<published name>               every name this repo publishes (package.json, pyproject,
#                                       Cargo.toml, go.mod, *.csproj PackageId/AssemblyName, the git remote)
#   consumer=<path> (<manifest> -> <name>)   a sibling repository whose dependency manifest names it
#   consumer=<path> (workspace)         a sibling that lists this repo as a workspace member
#   none=1                              nothing publishes, or nothing outside depends on it
# The list is a starting point for the integrator's cross-repository sweep, never proof by itself.

repo=$(cd "${1:-.}" 2>/dev/null && pwd -P) || { echo "none=1"; exit 0; }
root=$(cd "${2:-$(dirname "$repo")}" 2>/dev/null && pwd -P) || root=$(dirname "$repo")
names=""
add() { [ -n "$1" ] && case " $names " in *" $1 "*) ;; *) names="$names $1"; echo "name=$1";; esac; }

[ -f "$repo/package.json" ] && add "$(python3 -c "import json,sys;print(json.load(open(sys.argv[1])).get('name',''))" "$repo/package.json" 2>/dev/null)"
[ -f "$repo/pyproject.toml" ] && add "$(grep -m1 -E '^name[[:space:]]*=' "$repo/pyproject.toml" | sed -E 's/^name[[:space:]]*=[[:space:]]*"([^"]+)".*/\1/')"
for c in "$repo/Cargo.toml" "$repo"/*/Cargo.toml "$repo"/crates/*/Cargo.toml; do
  [ -f "$c" ] && add "$(grep -m1 -E '^name[[:space:]]*=' "$c" | sed -E 's/^name[[:space:]]*=[[:space:]]*"([^"]+)".*/\1/')"
done
[ -f "$repo/go.mod" ] && add "$(grep -m1 -E '^module ' "$repo/go.mod" | awk '{print $2}')"
for c in "$repo"/*.csproj "$repo"/src/*/*.csproj; do
  [ -f "$c" ] || continue
  add "$(grep -oE '<(PackageId|AssemblyName)>[^<]+' "$c" | head -1 | sed 's/<[^>]*>//')"
  add "$(basename "$c" .csproj)"
done
remote=$(git -C "$repo" remote get-url origin 2>/dev/null | sed -E -e 's#\.git$##' -e 's#.*[:/]([^/]+/[^/]+)$#\1#')
[ -n "$remote" ] && add "$remote"
[ -z "$names" ] && { echo "none=1"; exit 0; }

found=0
# dependency manifests in sibling repositories, two levels under the search root
for m in $(find "$root" -mindepth 1 -maxdepth 4 -type f \( -name package.json -o -name pyproject.toml -o -name requirements.txt -o -name Cargo.toml -o -name go.mod -o -name '*.csproj' -o -name 'pnpm-workspace.yaml' -o -name '*.sln' \) \
           -not -path "$repo/*" -not -path '*/node_modules/*' -not -path '*/.git/*' -not -path '*/dist/*' -not -path '*/target/*' 2>/dev/null); do
  for n in $names; do
    if grep -qF -- "$n" "$m" 2>/dev/null; then
      d=$(dirname "$m")
      case "$m" in *pnpm-workspace.yaml|*.sln) echo "consumer=$d (workspace)";; *) echo "consumer=$d ($(basename "$m") -> $n)";; esac
      found=1; break
    fi
  done
done
[ "$found" -eq 0 ] && echo "none=1"
exit 0
