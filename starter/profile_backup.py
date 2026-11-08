#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""profile_backup.py —— 动 L3 之前先做「回滚包」，并且让它自证。

为什么要有它：L3（插件层）崩起来是整个宿主起不来，你连进 GUI 修的机会都没有。
唯一稳妥的办法是**动手之前**就把「能启动的那一份」完整存下来，并证明它确实能还原。

用法（在发布包根目录执行）：

    # 1) 存回滚包（用你真实的 DSH_HOME／profile 名）
    python starter/profile_backup.py save --home "$DSH_HOME" --profile desktop --out ./rollback-before-l3

    # 2) 自证：逐文件比哈希（不改盘上任何东西）
    python starter/profile_backup.py verify --dir ./rollback-before-l3

    # 3) 演练还原（只打印要做的事，不写盘）——动手前必须跑一次，看输出对不对
    python starter/profile_backup.py restore --dir ./rollback-before-l3 --home "$DSH_HOME" --profile desktop --dry-run

    # 4) 真还原（出事了才用；会把现文件改名成 *.pre-restore-<时间戳> 再写回）
    python starter/profile_backup.py restore --dir ./rollback-before-l3 --home "$DSH_HOME" --profile desktop

    # 5) 检查脚本本身没毛病（在临时目录里自造一份 profile）
    python starter/profile_backup.py selftest

退出码：0 = 成功；3 = 校验不通过（哈希不一致／文件缺失）；2 = 用法或环境错误。
只依赖 Python 标准库；不需要 pnpm、不需要网络。
"""
import argparse
import hashlib
import json
import os
import shutil
import sys
import tempfile
import time

# 回滚包必须收的「三件」：起不来的问题几乎都能通过还原这三件修回去
CORE_FILES = ["package.json", "pnpm-lock.yaml", "cordis.patch.yml"]
MANIFEST = "_manifest.sha256"
META = "_meta.json"


def log(msg):
    sys.stdout.write(msg + "\n")


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def profile_dir(home, profile):
    return os.path.join(home, "profiles", profile)


def save(home, profile, out):
    src = profile_dir(home, profile)
    if not os.path.isdir(src):
        log("[FAIL] 找不到 profile 目录：%s" % src)
        return 2
    os.makedirs(out, exist_ok=True)

    copied, missing = [], []
    for name in CORE_FILES:
        p = os.path.join(src, name)
        if os.path.isfile(p):
            shutil.copy2(p, os.path.join(out, name))
            copied.append(name)
        else:
            missing.append(name)

    # 顺带记一份「当时装了什么」：profile 顶层清单 + node_modules 一级目录名
    top = sorted(os.listdir(src))
    nm = os.path.join(src, "node_modules")
    nm_top = sorted(os.listdir(nm)) if os.path.isdir(nm) else []

    meta = {
        "saved_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "home": os.path.abspath(home),
        "profile": profile,
        "python": sys.version.split()[0],
        "profile_top_level": top,
        "node_modules_top_level": nm_top,
        "core_files": copied,
        "missing_core_files": missing,
    }
    with open(os.path.join(out, META), "w", encoding="utf-8") as fh:
        json.dump(meta, fh, ensure_ascii=False, indent=2)

    lines = []
    for name in copied:
        lines.append("%s  %s" % (sha256(os.path.join(out, name)), name))
    with open(os.path.join(out, MANIFEST), "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines) + "\n")

    log("[OK] 回滚包已存到 %s" % os.path.abspath(out))
    for name in copied:
        log("     - %s" % name)
    if missing:
        log("[WARN] 这些文件在 profile 里不存在（多半是没装过依赖）：%s" % ", ".join(missing))
    if "cordis.patch.yml" in missing:
        log("[WARN] 没有 cordis.patch.yml：说明这个 profile 从没改过插件补丁，回滚时也就不需要它。")
    log("")
    log("下一步（别跳过）：")
    log("  python starter/profile_backup.py verify --dir %s" % out)
    log("  python starter/profile_backup.py restore --dir %s --home \"<你的 DSH_HOME>\" --profile %s --dry-run" % (out, profile))
    return 0


def verify(out):
    mpath = os.path.join(out, MANIFEST)
    if not os.path.isfile(mpath):
        log("[FAIL] 回滚包里没有 %s —— 这份备份不自证，不能用来回滚" % MANIFEST)
        return 3
    bad, ok = [], 0
    with open(mpath, encoding="utf-8") as fh:
        for line in fh:
            line = line.rstrip("\n")
            if not line.strip():
                continue
            want, name = line.split("  ", 1)
            p = os.path.join(out, name)
            if not os.path.isfile(p):
                bad.append("%s：回滚包里没有这个文件" % name)
                continue
            got = sha256(p)
            if got != want:
                bad.append("%s：哈希不一致（记录 %s… 实测 %s…）" % (name, want[:12], got[:12]))
            else:
                ok += 1
    if bad:
        log("[FAIL] 回滚包校验不通过：%d 处问题" % len(bad))
        for b in bad:
            log("     - %s" % b)
        log("     处置：回到「备份」那一步重做；不要用一份自己都证明不了的备份去回滚。")
        return 3
    log("[OK] 回滚包自证通过：%d 个文件哈希全部一致" % ok)
    return 0


def restore(out, home, profile, dry_run):
    if verify(out) != 0:
        return 3
    dst = profile_dir(home, profile)
    stamp = time.strftime("%Y%m%d-%H%M%S")
    plan = []
    for name in CORE_FILES:
        src = os.path.join(out, name)
        if not os.path.isfile(src):
            continue
        tgt = os.path.join(dst, name)
        plan.append((src, tgt, tgt + ".pre-restore-" + stamp))

    if not plan:
        log("[FAIL] 回滚包里没有任何核心文件，无法还原")
        return 3

    log("%s还原计划（profile 目录：%s）" % ("[演练] " if dry_run else "", dst))
    for src, tgt, bak in plan:
        log("  %s -> %s（现有文件改名为 %s）" % (os.path.basename(src), tgt, os.path.basename(bak)))
    log("")
    log("顺序提醒（崩了的时候）：**先摘插件，再换文件**。")
    log("  - 本次还原的 package.json 就是「那时能启动」的那份，bundles 自然回到当时的样子；")
    log("  - 还原后必须真启动一次，并检查启动日志里 `did not activate` 为 0 行；")
    log("  - 还起不来，就说明问题不在 profile，别继续乱改——把启动输出原样贴出来再判断。")

    if dry_run:
        log("")
        log("[演练结束] 没有写任何文件。输出看起来对，才去掉 --dry-run 真正执行。")
        return 0

    if not os.path.isdir(dst):
        log("[FAIL] 目标 profile 目录不存在：%s（先确认 --home 与 --profile）" % dst)
        return 2
    for src, tgt, bak in plan:
        if os.path.exists(tgt):
            shutil.move(tgt, bak)
        shutil.copy2(src, tgt)
        log("[OK] 写回 %s" % tgt)
    log("")
    log("已还原。现在真启动一次 DSH，确认这三样：端口起来、`did not activate` 为 0 行、插件面板在。")
    return 0


def selftest():
    tmp = tempfile.mkdtemp(prefix="pb-selftest-")
    home = os.path.join(tmp, "home")
    prof = os.path.join(home, "profiles", "desktop")
    out = os.path.join(tmp, "rollback")
    os.makedirs(os.path.join(prof, "node_modules", "x"), exist_ok=True)
    with open(os.path.join(prof, "package.json"), "w", encoding="utf-8") as fh:
        fh.write('{"name":"desktop","dsh":{"profile":{"bundles":["a","b"]}}}')
    with open(os.path.join(prof, "pnpm-lock.yaml"), "w", encoding="utf-8") as fh:
        fh.write("lockfileVersion: '9.0'\n")
    with open(os.path.join(prof, "cordis.patch.yml"), "w", encoding="utf-8") as fh:
        fh.write("- id: keep-me\n  name: pkg\n")

    assert save(home, "desktop", out) == 0
    assert verify(out) == 0, "刚存的包应该自证通过"
    assert restore(out, home, "desktop", dry_run=True) == 0

    # 改坏真文件 -> verify 仍通过（验的是备份），restore 能救回来
    with open(os.path.join(prof, "package.json"), "w", encoding="utf-8") as fh:
        fh.write('{"broken":true}')
    assert restore(out, home, "desktop", dry_run=False) == 0
    with open(os.path.join(prof, "package.json"), encoding="utf-8") as fh:
        assert "bundles" in fh.read(), "还原后应回到备份内容"

    # 篡改备份 -> verify 必须报 3
    with open(os.path.join(out, "package.json"), "a", encoding="utf-8") as fh:
        fh.write(" ")
    assert verify(out) == 3, "篡改过的备份必须校验失败"

    shutil.rmtree(tmp, ignore_errors=True)
    log("[PASS] selftest：存包／自证／演练／还原／篡改检测 全部符合预期")
    return 0


def main(argv):
    ap = argparse.ArgumentParser(description="DSH profile 回滚包：save / verify / restore / selftest")
    sub = ap.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("save", help="把 profile 的三件存成回滚包")
    s.add_argument("--home", required=True, help="DSH_HOME，例如 <盘>:\\<你的 DSH 目录>")
    s.add_argument("--profile", default="desktop")
    s.add_argument("--out", required=True, help="回滚包目录（会自动创建）")

    v = sub.add_parser("verify", help="逐文件比哈希，证明备份可用")
    v.add_argument("--dir", required=True)

    r = sub.add_parser("restore", help="从回滚包还原（先把现有文件改名留档）")
    r.add_argument("--dir", required=True)
    r.add_argument("--home", required=True)
    r.add_argument("--profile", default="desktop")
    r.add_argument("--dry-run", action="store_true", help="只打印计划，不写盘")

    sub.add_parser("selftest", help="在临时目录里自检脚本本身")

    args = ap.parse_args(argv)
    if args.cmd == "save":
        return save(args.home, args.profile, args.out)
    if args.cmd == "verify":
        return verify(args.dir)
    if args.cmd == "restore":
        return restore(args.dir, args.home, args.profile, args.dry_run)
    if args.cmd == "selftest":
        return selftest()
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
