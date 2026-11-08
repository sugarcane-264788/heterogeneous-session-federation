#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""最小信箱：一件事只放一个箱，写信/数未读/读信/归档。

    python mailbox_min.py send --to b --from a --text "一句话"
    python mailbox_min.py status
    python mailbox_min.py digest --for b [--peek] [--as 读者名]
    python mailbox_min.py --selftest

默认根目录是 ./_minibox（可用 --root 或环境变量 MAILBOX_ROOT 改）。
目录布局与完整库一致（`--root` 指到 `<协作库>/40-协作/_消息` 即可对齐）：

    <root>/<箱>/<YYYYmmdd-HHMMSS>-from-<发件人>.md   # 未读信
    <root>/已处理/<箱>/<同名>                        # 读过的信（搬过去，不删）
    <root>/.cursors/<箱>                             # 公共游标，谁读谁推
    <root>/.cursors/<箱>@<读者名>                    # 私有游标，一名读者一个

它只做这四件事，故意不做锁、不做合并、不做播报——那些等你真需要了再加。
"""
import argparse
import os
import shutil
import sys
import time

ROOT = os.environ.get("MAILBOX_ROOT") or os.path.join(os.getcwd(), "_minibox")
RESERVED = {".cursors", "已处理"}


def boxes(root):
    if not os.path.isdir(root):
        return []
    return sorted(n for n in os.listdir(root)
                  if n not in RESERVED and os.path.isdir(os.path.join(root, n)))


def letters(root, box):
    d = os.path.join(root, box)
    return sorted(f for f in os.listdir(d) if f.endswith(".md")) if os.path.isdir(d) else []


def _cursor_name(box, reader):
    return box if not reader else "%s@%s" % (box, reader)


def cursor(root, box, reader=None):
    p = os.path.join(root, ".cursors", _cursor_name(box, reader))
    try:
        with open(p, encoding="utf-8") as f:
            return f.read().strip()
    except OSError:
        return ""


def set_cursor(root, box, name, reader=None):
    d = os.path.join(root, ".cursors")
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, _cursor_name(box, reader)), "w", encoding="utf-8", newline="\n") as f:
        f.write(name + "\n")


def unread(root, box, reader=None):
    c = cursor(root, box, reader)
    return [f for f in letters(root, box) if f > c]


def _warn_legacy(root):
    """v1.0.5 及更早用的是 <root>/boxes 与 <root>/cursors（没有点），提示一次怎么搬。"""
    if os.path.isdir(os.path.join(root, "boxes")) or os.path.isdir(os.path.join(root, "cursors")):
        print("[提示] 发现旧布局 <root>/boxes 与 <root>/cursors（v1.0.5 及更早）。"
              "新布局是 <root>/<箱> 与 <root>/.cursors；搬一次即可：\n"
              "       mv \"%s/boxes/\"* \"%s/\" && mkdir -p \"%s/.cursors\" && "
              "mv \"%s/cursors/\"* \"%s/.cursors/\""
              % (root, root, root, root, root), file=sys.stderr)


def _make_root(root):
    try:
        os.makedirs(root, exist_ok=True)
    except PermissionError:
        raise SystemExit(
            "[失败] 建不了 %s（PermissionError）。多半是会话档位受限（例如 DSH 默认档）："
            "换可写目录用 --root，或把会话开到 danger-full-access。" % root)


def send(root, to, frm, text):
    _make_root(root)
    d = os.path.join(root, to)
    os.makedirs(d, exist_ok=True)
    # 文件名即时间线，而读者用字符串比较推进游标（f > cursor）。
    # 所以同一秒连发时不能加后缀（"-2" 会排在 ".md" 之前，反而被判成旧信），
    # 只能把时间戳往后挪一秒：名字保持同一形状，顺序也仍然单调。
    base = time.time()
    for k in range(0, 3600):
        ts = time.strftime("%Y%m%d-%H%M%S", time.localtime(base + k))
        # 该秒内只要箱里已有任何信（不限于同一发件人）就往后挪一秒：
        # 文件名即时间线，读者按字符串比较推进游标；同秒两封会让排在后面的那封永久读不到。
        if any(f.startswith(ts + "-") for f in os.listdir(d)):
            continue
        name = "%s-from-%s.md" % (ts, frm)
        p = os.path.join(d, name)
        if os.path.exists(p):
            continue
        body = "发件人：%s\n收件人：%s\n时间：%s\n\n%s\n" % (frm, to, ts, text.strip())
        try:
            with open(p, "x", encoding="utf-8", newline="\n") as f:
                f.write(body)
            return name
        except FileExistsError:
            continue
    raise RuntimeError("同一秒内同名信件过多，稍后再发")


def archive(root, box, name):
    """搬进 <root>/已处理/<box>/。搬不动就抛异常——调用方据此不推游标（fail-closed）。"""
    dst_dir = os.path.join(root, "已处理", box)
    os.makedirs(dst_dir, exist_ok=True)
    src = os.path.join(root, box, name)
    dst = os.path.join(dst_dir, name)
    if os.path.exists(dst):
        dst = os.path.join(dst_dir, "%s.dup-%d" % (name, int(time.time())))
    os.replace(src, dst)
    return dst


def digest(root, box, peek, reader=None):
    c = cursor(root, box, reader)
    new = unread(root, box, reader)
    if not new:
        print("（%s 箱没有新消息；游标：%s）" % (box, c or "空"))
        return 0
    print("--- %s 箱 %d 封（游标：%s）" % (box, len(new), c or "空"))
    for n in new:
        with open(os.path.join(root, box, n), encoding="utf-8") as f:
            t = f.read()
        print("\n### %s\n%s" % (n, t[t.find("\n\n") + 2:].strip() if "\n\n" in t else t.strip()))
    if peek:
        print("\n（--peek：游标没动，下次还会读到这 %d 封）" % len(new))
        return 0

    done = []
    for n in new:
        try:
            archive(root, box, n)
        except OSError as exc:
            print("\n（归档失败，停在 %s：%s；游标没动，未读仍为 %d 封）" % (n, exc, len(new) - len(done)))
            if done:
                set_cursor(root, box, done[-1], reader)
            return 3
        done.append(n)
    set_cursor(root, box, done[-1], reader)
    print("\n（已归档 %d 封，游标推进到 %s）" % (len(done), done[-1]))
    return 0


def _selftest_root():
    """建一个可写的临时目录。不用 tempfile.mkdtemp：它建 0700，
    在受限令牌（例如 DSH 默认档）里连目录里的文件都写不进。"""
    base = os.environ.get("TEMP") or os.environ.get("TMP") or "/tmp"
    stamp = int(time.time() * 1000)
    for i in range(20):
        p = os.path.join(base, "minibox-selftest-%d-%d" % (stamp, i))
        try:
            os.makedirs(p, exist_ok=True)
            probe = os.path.join(p, ".probe")
            with open(probe, "w", encoding="utf-8") as f:
                f.write("ok")
            os.remove(probe)
            return p
        except OSError:
            continue
    p = os.path.join(os.getcwd(), "_minibox-selftest-%d" % stamp)
    os.makedirs(p, exist_ok=True)
    return p


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=ROOT)
    ap.add_argument("--selftest", action="store_true")
    sub = ap.add_subparsers(dest="cmd")
    s = sub.add_parser("send")
    s.add_argument("--to", required=True)
    s.add_argument("--from", dest="frm", default="main")
    s.add_argument("--text", required=True)
    sub.add_parser("status")
    d = sub.add_parser("digest")
    d.add_argument("--for", dest="box", required=True)
    d.add_argument("--peek", action="store_true")
    d.add_argument("--as", dest="reader", default=None,
                   help="私有游标：同一箱多名读者时各读各的（不给就用公共游标）")
    a = ap.parse_args()

    if a.selftest:
        tmp = _selftest_root()
        try:
            send(tmp, "b", "a", "第一封")
            time.sleep(1.1)  # 文件名按秒排序，睡一下保证名字不同
            send(tmp, "b", "a", "第二封")
            n1 = len(unread(tmp, "b"))
            digest(tmp, "b", peek=True)
            n2 = len(unread(tmp, "b"))
            time.sleep(1.1)
            send(tmp, "b", "a", "第三封")
            n3 = len(unread(tmp, "b"))
            digest(tmp, "b", peek=False)
            n4 = len(unread(tmp, "b"))
            archived = len([f for f in os.listdir(os.path.join(tmp, "已处理", "b"))
                            if f.endswith(".md")])
            ok = (n1 == 2 and n2 == 2 and n3 == 3 and n4 == 0
                  and letters(tmp, "a") == [] and archived == 3)
            print("selftest=%s（依次未读：%d/%d/%d/%d，a 箱信数 %d）"
                  % ("PASS" if ok else "FAIL", n1, n2, n3, n4, len(letters(tmp, "a"))))
            return 0 if ok else 1
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    _warn_legacy(a.root)
    if a.cmd == "send":
        print("已投递 -> %s 箱 [%s]" % (a.to, send(a.root, a.to, a.frm, a.text)))
    elif a.cmd == "status":
        for b in boxes(a.root):
            print("%-8s 未读 %d / 共 %d" % (b, len(unread(a.root, b)), len(letters(a.root, b))))
        print("合计未读 %d" % sum(len(unread(a.root, b)) for b in boxes(a.root)))
    elif a.cmd == "digest":
        return digest(a.root, a.box, a.peek, a.reader)
    else:
        ap.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
