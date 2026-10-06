#!/usr/bin/env bash
# Deploy site/dist to a GitHub repository's gh-pages branch.
# Uses a persistent git dir (site/.deploy-git) so repeated deploys push deltas only
# (content-addressed blobs shared with the remote are not re-uploaded).
# Usage: bash scripts/site/deploy_ghpages.sh <git-remote-url> [branch]
set -euo pipefail

REMOTE="${1:?usage: deploy_ghpages.sh <git-remote-url> [branch]}"
BRANCH="${2:-gh-pages}"
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
DIST="$ROOT/site/dist"
GITDIR="$ROOT/site/.deploy-git"

[ -f "$DIST/index.html" ] || { echo "site/dist not built. Run: cd site && npm run build"; exit 1; }

mkdir -p "$GITDIR"
cd "$DIST"
# 首次初始化持久 git 目录；后续仅重写 .git 指针（git init --separate-git-dir 不能作用于已存在仓库）
if [ ! -f "$GITDIR/HEAD" ]; then
  git init --separate-git-dir "$GITDIR" -q
  git config core.autocrlf false
else
  printf 'gitdir: %s\n' "$GITDIR" > .git
fi
export GIT_DIR="$GITDIR"
git symbolic-ref HEAD "refs/heads/$BRANCH" 2>/dev/null || true

git add -A
if git diff --cached --quiet; then
  echo "No changes since last deploy."
else
  git -c user.name="gfl-db deploy" -c user.email="deploy@local" \
    commit -q -m "deploy $(date +%Y-%m-%d_%H:%M) ($(git ls-files | wc -l) files)"
fi
if ! git remote | grep -q '^origin$'; then
  git remote add origin "$REMOTE"
fi
echo "Pushing to $REMOTE:$BRANCH (force)..."
git push -qf origin "$BRANCH"
echo "Done. GitHub Pages will rebuild automatically from $BRANCH."
