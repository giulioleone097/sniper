#!/bin/sh
# sniper: print the design tokens a repository actually defines, with counts, so UI
# work reuses the system that exists instead of inventing one. Read-only.
#
#   sh tokens.sh [path]     path defaults to . ; scans css/scss/less/ts/js/json under it
#
# Sections (each capped, most frequent first):
#   custom-properties   --name: value       from stylesheets
#   theme-keys          tailwind / theme object keys, when a config file exists
#   colours             hex values seen in stylesheets
#   fonts               font-family declarations and @font-face / loaded faces
#   sizes               px / rem values in spacing, font-size, radius, shadow
# Nothing found in a section: that section is omitted. Nothing at all: prints `none=1`.

root=$(cd "${1:-.}" 2>/dev/null && pwd) || { echo "none=1"; exit 0; }
files=$(find "$root" -type f \( -name '*.css' -o -name '*.scss' -o -name '*.less' -o -name '*.sass' \) \
        -not -path '*/node_modules/*' -not -path '*/dist/*' -not -path '*/.angular/*' -not -path '*/coverage/*' 2>/dev/null | head -400)
cfg=$(find "$root" -maxdepth 3 -type f \( -name 'tailwind.config.*' -o -name 'theme.ts' -o -name 'theme.js' -o -name 'tokens.json' -o -name 'design-tokens.json' \) \
      -not -path '*/node_modules/*' 2>/dev/null | head -5)
[ -z "$files" ] && [ -z "$cfg" ] && { echo "none=1"; exit 0; }

section() { [ -n "$2" ] && { echo "[$1]"; printf '%s\n' "$2"; }; }
top() { sort | uniq -c | sort -rn | head -"$1" | sed 's/^ *//'; }

[ -n "$files" ] && {
  section custom-properties "$(cat $files 2>/dev/null | grep -ohE '(^|[;{[:space:]])--[a-zA-Z0-9_-]+:[[:space:]]*[^;{}]{1,60};' | sed -e 's/^[;{[:space:]]*//' -e 's/;$//' -e 's/:[[:space:]]*/: /' | top 30)"
  section colours "$(cat $files 2>/dev/null | grep -ohE '#[0-9a-fA-F]{6}\b|#[0-9a-fA-F]{3}\b' | tr 'A-F' 'a-f' | top 20)"
  section fonts "$(cat $files 2>/dev/null | grep -ohE 'font-family:\s*[^;]{1,80}' | sed 's/font-family:[[:space:]]*//' | top 10)"
  section sizes "$(cat $files 2>/dev/null | grep -ohE '(^|[;{[:space:]])(margin|padding|gap|font-size|border-radius|line-height|letter-spacing)[a-z-]*:[[:space:]]*[^;{}]{1,40};' | sed -e 's/^[;{[:space:]]*//' -e 's/;$//' -e 's/:[[:space:]]*/: /' | top 30)"
}
[ -n "$cfg" ] && section theme-keys "$(for c in $cfg; do echo "# $c"; grep -oE '^\s{2,8}[a-zA-Z][a-zA-Z0-9]*\s*:' "$c" | sed 's/[[:space:]:]//g' | top 25; done)"
exit 0
