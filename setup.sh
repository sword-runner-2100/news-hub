#!/bin/bash
# 一键把本仓库推到 GitHub 并开启 Pages。
# 用法：在终端里执行  bash setup.sh
set -e

GH="/opt/homebrew/bin/gh"
cd "$(dirname "$0")"

if [ ! -x "$GH" ]; then GH="$(command -v gh || true)"; fi
if [ -z "$GH" ]; then
  echo "没找到 gh，请先安装：brew install gh"
  exit 1
fi

echo ""
echo "【1/4】登录 GitHub"
echo "      接下来会显示一个一次性代码，并自动打开浏览器。"
echo "      在浏览器里粘贴代码并点授权即可（只需做这一次）。"
echo ""
"$GH" auth login --web --git-protocol https

echo ""
echo "【2/4】创建仓库并推送"
echo "      仓库名默认 news-hub。想改名就改下面这行的 --public 前面的名字。"
echo ""
# 已存在同名仓库时 gh 会报错，这里给个提示
if "$GH" repo view news-hub >/dev/null 2>&1; then
  echo "  检测到你已有 news-hub 仓库，改用 news-hub-$(date +%m%d)"
  REPO_NAME="news-hub-$(date +%m%d)"
else
  REPO_NAME="news-hub"
fi
"$GH" repo create "$REPO_NAME" --public --source=. --remote=origin --push

FULL="$("$GH" repo view --json nameWithOwner -q .nameWithOwner)"

echo ""
echo "【3/4】开启 GitHub Pages"
if "$GH" api -X POST "repos/$FULL/pages" \
     -f "source[branch]=main" -f "source[path]=/" >/dev/null 2>&1; then
  echo "  Pages 已开启（main 分支根目录）"
else
  echo "  Pages 可能已开启；若没有，请手动到"
  echo "  Settings → Pages → Source 选 Deploy from a branch → main / (root)"
fi

echo ""
echo "【4/4】完成"
echo "  仓库：https://github.com/$FULL"
echo "  网址：https://$(echo "$FULL" | cut -d/ -f1).github.io/$(echo "$FULL" | cut -d/ -f2)/"
echo ""
echo "  Pages 首次发布需 1–2 分钟。想立刻验证，到仓库的 Actions 页"
echo "  手动点一次「刷新新闻汇总台」即可。"
echo ""
