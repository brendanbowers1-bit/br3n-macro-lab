#!/usr/bin/env bash
# Publish BR3N Macro Lab to GitHub Pages.
# Prerequisite: gh auth login (one time)
set -euo pipefail
cd "$(dirname "$0")/.."

echo "==> Building site..."
python3 scripts/build_site.py

if ! gh auth status &>/dev/null; then
  echo ""
  echo "GitHub CLI not logged in. Run once:"
  echo "  gh auth login"
  echo "Then re-run:  bash scripts/publish_github.sh"
  exit 1
fi

USER=$(gh api user -q .login)
REPO="${1:-br3n-macro-lab}"

if ! gh repo view "$USER/$REPO" &>/dev/null; then
  echo "==> Creating public repo $USER/$REPO ..."
  gh repo create "$REPO" --public --source=. --remote=origin --description "BR3N Macro Lab — USD/MXN regime research"
else
  if ! git remote get-url origin &>/dev/null; then
    git remote add origin "https://github.com/$USER/$REPO.git"
  fi
fi

git add -A
if git diff --staged --quiet; then
  echo "Nothing new to commit."
else
  git commit -m "Publish BR3N Macro Lab research site"
fi

git branch -M main
git push -u origin main

echo ""
echo "==> Enabling GitHub Pages (Actions)..."
gh api "repos/$USER/$REPO/pages" -X POST -f build_type=workflow 2>/dev/null || true

echo ""
echo "Done. After the workflow finishes (~2 min):"
echo "  https://$USER.github.io/$REPO/"
echo ""
echo "Track deploy: https://github.com/$USER/$REPO/actions"
