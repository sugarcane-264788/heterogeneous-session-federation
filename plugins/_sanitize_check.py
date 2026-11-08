#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""发布包脱敏自检：扫整个仓库（含 .tgz 内部文件），命中作者机器信息就非零退出。

用法（在仓库根目录跑）：
    python plugins/_sanitize_check.py            # 扫当前目录（默认仓库根 = 本文件上一级）
    python plugins/_sanitize_check.py --root .   # 指定根
    python plugins/_sanitize_check.py --verbose  # 打印每一处命中

判据：
- 0 = 干净；
- 3 = 有命中（逐条列出 `文件:行 内容`，tgz 内文件写成 `包.tgz::内部路径:行`）。

规则（宁可误报，不许漏）：
- Windows 盘符绝对路径：`X:\\`、`X:/`、以及被转义成 `X:\\\\` 的写法（JSON／YAML 里常见）；
- UNC 路径 `\\\\server\\share`；
- Unix 个人目录：`/home/<非占位符>`、`/Users/<非占位符>`；
- 用户名与内网个人标记：`zhy34532`、`WeChatAgent`；
- 会话 id：`session-` 后跟 6 位以上十六进制（白名单 `PLACEHOLDER_IDS` 里的假 id 除外）。

覆盖：文本文件按扩展名收录；**`.tgz`／`.tar.gz` 会解压后逐成员扫**（发布包里最该扫的就是它们）。
排除：`.git/`、`node_modules/`、`__pycache__/`、本文件自身。
"""
import io
import os
import re
import sys
import tarfile

# 文档里用来演示格式的假 id（不是真会话）。新增假 id 要同时改这里和文档。
PLACEHOLDER_IDS = {"1a2b3c4d"}
# 文档里用来演示格式的假用户名。
PLACEHOLDER_USERS = {"you", "user", "alice", "example"}

RULES = [
    ("盘符绝对路径", re.compile(r"(?<![A-Za-z0-9_])[A-Za-z]:[\\/](?=[^\\/\s])")),
    ("转义后的盘符路径", re.compile(r"(?<![A-Za-z0-9_])[A-Za-z]:[\\/]{2,}")),
    ("UNC 路径", re.compile(r"(?:^|(?<=[\s\"'=(]))\\\\[A-Za-z0-9_.-]+\\[A-Za-z0-9_.$-]+")),
    ("Unix 个人目录",
     re.compile(r"/(?:home|Users)/(?!(?:%s)(?:[/\"'\s]|$))[A-Za-z0-9_.-]+" % "|".join(PLACEHOLDER_USERS))),
    ("个人目录", re.compile(r"zhy34532|WeChatAgent")),
    ("会话 id", re.compile(r"session-(?!%s\b)[0-9a-f]{6,}" % "|".join(PLACEHOLDER_IDS))),
]
SKIP_DIRS = {".git", "node_modules", "__pycache__"}
SKIP_FILES = {"_sanitize_check.py"}
TEXT_EXT = {
    ".md", ".py", ".js", ".mjs", ".cjs", ".ts", ".tsx", ".json", ".yml", ".yaml",
    ".txt", ".sh", ".bash", ".cmd", ".bat", ".ps1", ".toml", ".ini", ".cfg", ".env", "",
}
ARCHIVE_SUFFIX = (".tgz", ".tar.gz")


def is_text(name):
    return os.path.splitext(name)[1].lower() in TEXT_EXT


def scan_text(text, where, hits):
    """逐行扫；一行内所有规则都跑（不 break，避免漏报）。"""
    for lineno, line in enumerate(text.splitlines(), 1):
        for label, pat in RULES:
            for m in pat.finditer(line):
                hits.append((where, lineno, label, m.group(0)))
                break  # 同一行同一规则只报一次，够定位


def scan_file(path, rel, hits):
    try:
        with io.open(path, encoding="utf-8", errors="replace") as fh:
            scan_text(fh.read(), rel, hits)
    except OSError as exc:
        print("[WARN] 读不了 %s：%s" % (rel, exc))


def scan_tgz(path, rel, hits):
    try:
        with tarfile.open(path, "r:gz") as tar:
            for member in tar.getmembers():
                if not member.isfile() or not is_text(member.name):
                    continue
                fh = tar.extractfile(member)
                if fh is None:
                    continue
                data = fh.read().decode("utf-8", "replace")
                scan_text(data, "%s::%s" % (rel, member.name), hits)
                # 元数据也要干净：非 root 属主名／真用户名放进 uname
                if member.uname and member.uname not in ("root", "0", ""):
                    hits.append((rel, 0, "包内属主名", member.uname))
    except (tarfile.TarError, OSError) as exc:
        print("[WARN] 打不开 %s：%s" % (rel, exc))


def walk(root):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            if name in SKIP_FILES:
                continue
            full = os.path.join(dirpath, name)
            rel = os.path.relpath(full, root).replace("\\", "/")
            yield full, rel, name


def main(argv):
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    verbose = "--verbose" in argv
    if "--root" in argv:
        i = argv.index("--root")
        root = os.path.abspath(argv[i + 1])

    hits = []
    files = 0
    archives = 0
    for full, rel, name in walk(root):
        files += 1
        if name.endswith(ARCHIVE_SUFFIX):
            archives += 1
            scan_tgz(full, rel, hits)
        elif is_text(name):
            scan_file(full, rel, hits)

    if not hits:
        print("[PASS] 脱敏自检：%d 个文件（其中 %d 个压缩包已解包扫描）里没有命中作者机器信息"
              % (files, archives))
        return 0

    print("[FAIL] 脱敏自检：%d 处命中（扫描 %d 个文件，%d 个压缩包）" % (len(hits), files, archives))
    for where, lineno, label, text in hits:
        if verbose or len(hits) <= 60:
            loc = "%s:%d" % (where, lineno) if lineno else where
            print("       - %s  [%s] %s" % (loc, label, text))
    print("       规则：盘符绝对路径／UNC／Unix 个人目录／用户名／会话 id（含 .tgz 内部）。")
    return 3


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
