#!/bin/sh
# sniper: the facts a repository map starts from, read-only, from git and the tracker
# the repo already has. Nothing is installed, indexed or written.
#
#   sh repo-facts.sh [repo] [months] [prs]     defaults: . 12 30 ; prs=0 skips the tracker
#
# Sections (each omitted when empty):
#   [layout] [languages] [hotspots] [authors] [commits] [checks] [instructions]   from git
#   [prs] [reviewers] [reviewer-comments]                                         from gh (GitHub)
# Bots keep their [bot] suffix so the caller can weight humans separately.

repo=$(cd -P "${1:-.}" 2>/dev/null && pwd) || { echo "none=1"; exit 0; }
months=${2:-12}; prs=${3:-30}
cd "$repo" || exit 0
git rev-parse --is-inside-work-tree >/dev/null 2>&1 || { echo "none=1"; exit 0; }
since="$months months ago"
top() { sort | uniq -c | sort -rn | head -"$1" | sed 's/^ *//'; }

echo "[layout]"
git ls-files | awk -F/ 'NF>1{print $1"/"} NF==1{print "."}' | top 20

echo "[languages]"
git ls-files | grep -E '\.[A-Za-z0-9]+$' | sed -E 's/.*\.([A-Za-z0-9]+)$/\1/' \
  | grep -vE '^(md|json|yaml|yml|lock|txt|svg|png|jpg|jpeg|gif|ico|snap|map|toml|xml|csv|po|pem|zip)$' | top 12

echo "[hotspots]"
git log --since="$since" --name-only --pretty=format: 2>/dev/null | grep -v '^$' | top 25

echo "[authors]"
git shortlog -sn --no-merges --since="$since" HEAD 2>/dev/null | head -15 | sed 's/^ *//'

echo "[commits]"
total=$(git rev-list --count --no-merges --since="$since" HEAD 2>/dev/null)
conv=$(git log --no-merges --since="$since" --pretty=%s 2>/dev/null | grep -cE '^(feat|fix|chore|docs|refactor|test|build|ci|perf|style|revert)(\([^)]*\))?!?:')
merges=$(git rev-list --count --merges --since="$since" HEAD 2>/dev/null)
echo "commits=${total:-0} conventional=${conv:-0} merges=${merges:-0}"
git log --no-merges --since="$since" --pretty=%s 2>/dev/null | awk '{print length($0)}' | sort -n | awk '{a[NR]=$1} END{if(NR) print "subject_median_chars=" a[int((NR+1)/2)]}'
git log --no-merges --since="$since" --pretty=%s 2>/dev/null | grep -oE '^[a-z]+(\([^)]*\))?!?:' | sed -E 's/\(.*//; s/!?:$//' | top 8

echo "[checks]"
git ls-files | grep -iE '(^|/)(tests?|__tests__|specs?)/' | sed -E 's#((^|/)(tests?|__tests__|specs?)/).*#\1#' | top 10
git ls-files | grep -E '^(\.github/workflows/|\.gitlab-ci\.yml|azure-pipelines|\.circleci/|Jenkinsfile|\.pre-commit-config|\.eslintrc|eslint\.config|\.prettierrc|ruff\.toml|\.editorconfig|mypy\.ini|\.golangci|rustfmt\.toml|\.clang-format|Directory\.Build\.props|nx\.json|turbo\.json)' | head -15

echo "[instructions]"
git ls-files | grep -iE '(^|/)(AGENTS\.md|AGENTS\.override\.md|CLAUDE\.md|CONTRIBUTING\.md|CODEOWNERS|adr/|decisions/|docs/solutions/|docs/sniper/)' | head -15

# tracker-backed sections (GitHub through gh; other forges are read by the skill itself)
[ "$prs" -gt 0 ] 2>/dev/null || exit 0
url=$(git remote get-url origin 2>/dev/null)
case "$url" in *github.com*) ;; *) exit 0;; esac
command -v gh >/dev/null 2>&1 || exit 0
slug=$(printf '%s' "$url" | sed -e 's#.*github\.com[:/]##' -e 's#\.git$##')
list=$(gh api --cache 1h "repos/$slug/pulls?state=closed&per_page=$prs&sort=updated&direction=desc" \
       --jq '.[] | select(.merged_at != null) | "\(.number) \(.user.login) \(.merged_at[:10]) \(.base.ref)"' 2>/dev/null)
[ -n "$list" ] || exit 0
numbers=$(printf '%s\n' "$list" | awk '{print $1}')

echo "[prs]"
for n in $numbers; do
  gh api --cache 1h "repos/$slug/pulls/$n" --jq '"\(.number) \(.additions + .deletions) \(.review_comments) \(.comments) \(.changed_files)"' 2>/dev/null
done | awk '{n++; s+=$2; rc+=$3; c+=$4; f+=$5} END{if(n) printf "merged=%d mean_lines=%d mean_files=%d review_comments_per_pr=%.1f comments_per_pr=%.1f\n", n, s/n, f/n, rc/n, c/n}'
printf '%s\n' "$list" | awk '{a[$2]++; b[$4]++} END{for(k in a) printf "author %d %s\n", a[k], k; for(k in b) printf "base %d %s\n", b[k], k}' | sort -k1,1 -k2,2rn

echo "[reviewers]"
for n in $numbers; do
  gh api --cache 1h "repos/$slug/pulls/$n/reviews" --jq '.[] | "\(.user.login) \(.state)"' 2>/dev/null
done | top 12

echo "[reviewer-comments]"
for n in $numbers; do
  gh api --cache 1h "repos/$slug/pulls/$n/comments" --jq '.[] | .user.login' 2>/dev/null
done | top 10
exit 0
