#!/bin/sh
# sniper test-guard: fixture suite for scripts/guard.sh. Feeds each command as
# PreToolUse(Bash) hook JSON on stdin; DENY commands must get a deny decision,
# ALLOW commands must produce no output. Prints one line per mismatch, then
# "guard: N/N ok"; exits 1 on any mismatch.

cd "$(dirname "$0")/.." || exit 1
pass=0
total=0

run() {
  total=$((total + 1))
  out=$(python3 -c 'import sys,json;sys.stdout.write(json.dumps({"hook_event_name":"PreToolUse","tool_name":"Bash","tool_input":{"command":sys.argv[1]}}))' "$1" | sh scripts/guard.sh)
  case "$out" in
    *'"permissionDecision": "deny"'*) got=deny ;;
    *) got=allow ;;
  esac
  if [ "$got" = "$2" ]; then pass=$((pass + 1)); else echo "FAIL (want $2, got $got): $1"; fi
}

NL='
'
DENY="git commit --no-verify -m x${NL}git -C /tmp/r commit --no-verify -m x${NL}echo ok && git push --no-verify${NL}git push --force origin main${NL}git push -f${NL}git push -uf origin main${NL}git push origin +main${NL}git reset --hard HEAD~1${NL}git clean -fdx${NL}git checkout .${NL}git checkout -- .${NL}git checkout HEAD -- .${NL}git checkout -f .${NL}git restore .${NL}git restore -- .${NL}git restore --staged --worktree .${NL}rm -rf /${NL}rm -rf ~${NL}rm -rf ~/${NL}rm -rf \$HOME${NL}rm -rf \${HOME}${NL}rm -rf .${NL}rm -rf ..${NL}rm -rf *${NL}rm -rf /*${NL}rm -fr ./${NL}rm -r -f .${NL}echo x; rm -rf /"
ALLOW="git commit -m \"document the --no-verify flag\"${NL}git commit -m \"cleanup | rm -rf . now\"${NL}npm test -- --no-verify-ssl${NL}git push --force-with-lease${NL}git push -u origin main${NL}git checkout main${NL}git checkout -b feature${NL}git restore --staged .${NL}git clean -n${NL}rm -rf node_modules${NL}rm -rf dist/${NL}rm -rf ./build${NL}rm -f file.txt${NL}ls -la${NL}git diff HEAD"

OLDIFS=$IFS
IFS=$NL
set -f
for line in $DENY; do run "$line" deny; done
for line in $ALLOW; do run "$line" allow; done
set +f
IFS=$OLDIFS

total=$((total + 1))
[ -z "$(printf '{not json' | sh scripts/guard.sh)" ] && pass=$((pass + 1)) || echo "FAIL: malformed JSON produced output"
total=$((total + 1))
[ -z "$(printf '' | sh scripts/guard.sh)" ] && pass=$((pass + 1)) || echo "FAIL: empty stdin produced output"

echo "guard: $pass/$total ok"
[ "$pass" -eq "$total" ] || exit 1
