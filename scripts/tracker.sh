#!/bin/sh
# sniper: detect the work tracker this repository actually has, with no plugin,
# no MCP server and no configuration. Prints one key=value per line:
#   forge   github | gitlab | azure | none      (from the origin remote)
#   cli     gh | glab | az | none               (the binary that is installed)
#   auth    ok | missing | unknown              (whether that binary is logged in)
#   repo    owner/name | project path | -       (what the cli needs to address it)
#   local   <dir>                               (fallback: tickets as files)
# `cli=none` or `auth=missing` is not an error: the caller falls back to `local`.
# Any read here is read-only; nothing is created.

cd -P "${1:-.}" 2>/dev/null || { echo "forge=none"; echo "cli=none"; echo "auth=unknown"; echo "repo=-"; echo "local=docs/tickets"; exit 0; }

url=$(git remote get-url origin 2>/dev/null || echo "")
forge=none; cli=none; auth=unknown; repo=-

case "$url" in
  *github.com*)
    forge=github
    repo=$(printf '%s' "$url" | sed -e 's#.*github\.com[:/]##' -e 's#\.git$##')
    if command -v gh >/dev/null 2>&1; then
      cli=gh
      if gh auth status >/dev/null 2>&1; then auth=ok; else auth=missing; fi
    fi
    ;;
  *gitlab*)
    forge=gitlab
    repo=$(printf '%s' "$url" | sed -e 's#.*gitlab[^:/]*[:/]##' -e 's#\.git$##')
    if command -v glab >/dev/null 2>&1; then
      cli=glab
      if glab auth status >/dev/null 2>&1; then auth=ok; else auth=missing; fi
    fi
    ;;
  *dev.azure.com*|*visualstudio.com*)
    forge=azure
    repo=$(printf '%s' "$url" | sed -e 's#^.*[:/]v3/##' -e 's#.*dev\.azure\.com/##' -e 's#.*@##' -e 's#/_git/#/#' -e 's#\.git$##')
    if command -v az >/dev/null 2>&1; then
      cli=az
      if az account show >/dev/null 2>&1; then auth=ok; else auth=missing; fi
    fi
    ;;
esac

echo "forge=$forge"
echo "cli=$cli"
echo "auth=$auth"
echo "repo=$repo"
echo "local=docs/tickets"
