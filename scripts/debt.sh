#!/bin/sh
# sniper: harvest every `ceiling:` shortcut comment into a ledger, so a deliberate
# shortcut with a known ceiling gets revisited instead of rotting into permanent.
# Read-only.
#
#   sh debt.sh [repo]
#
# One row per marker, grouped by file:
#   <file>:<line>  <text after the marker>   [no-trigger when no upgrade path is named]
# Then: markers=<N> no-trigger=<M>. Nothing found: none=1.
# Convention: `ceiling: <limit>, upgrade <trigger>` in any comment style (#, //, --, /* */, <!-- -->).

repo=$(cd -P "${1:-.}" 2>/dev/null && pwd) || { echo "none=1"; exit 0; }
cd "$repo" || exit 0
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  hits=$(git grep -nE '(#|//|--|/\*|<!--)[[:space:]]*ceiling:' -- . ':!*.md' ':!node_modules' 2>/dev/null)
else
  hits=$(grep -rnE '(#|//|--|/\*|<!--)[[:space:]]*ceiling:' . --exclude-dir=.git --exclude-dir=node_modules --exclude='*.md' 2>/dev/null)
fi
[ -n "$hits" ] || { echo "none=1"; exit 0; }
n=0; m=0
printf '%s\n' "$hits" | while IFS= read -r line; do
  file=${line%%:*}; rest=${line#*:}; ln=${rest%%:*}
  text=$(printf '%s' "$rest" | sed -E 's/^[0-9]+:.*ceiling:[[:space:]]*//; s/[[:space:]]*(\*\/|-->)[[:space:]]*$//')
  tag=""
  printf '%s' "$text" | grep -qiE 'upgrade| if | when | until | once ' || tag="  [no-trigger]"
  printf '%s:%s  %s%s\n' "$file" "$ln" "$text" "$tag"
done
n=$(printf '%s\n' "$hits" | wc -l | tr -d ' ')
m=$(printf '%s\n' "$hits" | sed -E 's/^[^:]+:[0-9]+:.*ceiling:[[:space:]]*//' | grep -vciE 'upgrade| if | when | until | once ')
echo "markers=$n no-trigger=$m"
exit 0
