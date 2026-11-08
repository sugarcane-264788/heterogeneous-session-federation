#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""发布包脱敏自检：扫整个仓库，命中作者机器信息就非零退出。

用法（在仓库根目录跑）：
    python plugins/_sanitize_check.py            # 扫当前目录（默认仓库根 = 本文件上一级）
    python plugins/_sanitize_check.py --root .   # 指定根
    python plugins/_sanitize_check.py --verbose  # 打印每一处命中

判据：
- 0 = 干净；
- 3 = 有命中（逐条列出 `文件:行 内容`）。

规则（宁可误报，不许漏）：
- Windows 盘符绝对路径：`X:\\` 或 `X:/`（含 `C:\\Users`、`D:\\DSH`、`D:\\USTB`）；
- 用户名与内网个人标记：`zhy34532`、`WeChatAgent`；
- 会话 id 片段：`session-` 后跟 6 位以上十六进制（发布物里不该出现真会话 id）。

排除：`.git/`、`node_modules/`、本文件自身。
"""
import io
import os
import re
import sys

# 文档里用来演示格式的假 id（不是真会话）。新增假 id 要同时改这里和文档。
PLACEHOLDER_IDS = {"1a2b3c4d"}

RULES = [
    ("盘符绝对路径", re.compile(r"(?<![A-Za-z0-9_])[A-Za-z]:[\\/](?![\\/])")),
    ("个人目录", re.compile(r"zhy34532|WeChatAgent")),
    ("会话 id", re.compile(r"session-(?!%s\b)[0-9a-f]{6,}" % "|".join(PLACEHOLDER_IDS))),
]
SKIP_DIRS = {".git", "node_modules", "__pycache__"}
SKIP_FILES = {"_sanitize_check.py"}
TEXT_EXT = {".md", ".py", ".js", ".mjs", ".json", ".yml", ".yaml", ".txt", ".sh", ".cmd", ".ps1", ""}


def walk(root):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            if name in SKIP_FILES:
                continue
            ext = os.path.splitext(name)[1].lower()
            if ext in TEXT_EXT:
                yield os.path.join(dirpath, name)


def main(argv):
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    verbose = "--verbose" in argv
    if "--root" in argv:
        i = argv.index("--root")
        root = os.path.abspath(argv[i + 1])

    hits = []
    for path in walk(root):
        try:
            with io.open(path, encoding="utf-8", errors="replace") as fh:
                for lineno, line in enumerate(fh, 1):
                    for label, pat in RULES:
                        m = pat.search(line)
                        if m:
                            rel = os.path.relpath(path, root).replace("\\", "/")
                            hits.append((rel, lineno, label, m.group(0)))
                            break
        except OSError as exc:
            print("[WARN] 读不了 %s：%s" % (path, exc))

    if not hits:
        print("[PASS] 脱敏自检：%d 个文件里没有命中作者机器信息" % sum(1 for _ in walk(root)))
        return 0

    print("[FAIL] 脱敏自检：%d 处命中" % len(hits))
    for rel, lineno, label, text in hits:
        if verbose or len(hits) <= 40:
            print("       - %s:%d  [%s] %s" % (rel, lineno, label, text))
    print("       规则：盘符绝对路径 / 个人目录 / 会话 id。要么改成占位符，要么从包里去掉该文件。")
    return 3


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
