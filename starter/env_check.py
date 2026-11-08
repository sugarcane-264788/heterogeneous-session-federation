#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""L0 环境自检：先确认这台机器能不能跑 L1／L2，再谈别的。

    python starter/env_check.py

退出码：0 = 至少 python 单进程路线可用；2 = 连 python 路线都跑不了。
**打印输出**全 ASCII（避开 Windows 控制台中文乱码；源码注释仍是中文，不影响输出）。

它只读环境、只建一个临时目录试写；不联网（pypi 那条只是 3 秒 TCP 探测，失败不影响结论）。
"""
import os
import platform
import shutil
import socket
import sys
import tempfile
import time

RESULTS = []  # (level, name, detail, fix)


def add(level, name, detail, fix=""):
    RESULTS.append((level, name, detail, fix))


def check_python():
    v = sys.version_info
    ok = (v.major, v.minor) >= (3, 8)
    add("PASS" if ok else "FAIL", "python >= 3.8",
        "%d.%d.%d at %s" % (v.major, v.minor, v.micro, sys.executable),
        "" if ok else "install Python 3.8+ and put it on PATH")


def check_temp_default():
    try:
        d = os.path.join(tempfile.gettempdir(), "l0probe-%d" % int(time.time() * 1000))
        os.makedirs(d, exist_ok=True)
        p = os.path.join(d, "x.txt")
        with open(p, "w", encoding="utf-8") as fh:
            fh.write("ok")
        shutil.rmtree(d, ignore_errors=True)
        add("PASS", "temp dir writable (normal mode)", tempfile.gettempdir(), "")
    except Exception as exc:
        add("FAIL", "temp dir writable (normal mode)",
            "%s: %s" % (type(exc).__name__, exc),
            "point TEMP/TMP to a folder you can write, e.g. set TEMP=%USERPROFILE%\\AppData\\Local\\Temp")


def check_temp_private():
    """0700 私有目录：受限令牌（DSH 默认档之类）里会失败——不是故障，是档位。"""
    try:
        d = tempfile.mkdtemp(prefix="l0priv-")
        p = os.path.join(d, "x.txt")
        with open(p, "w", encoding="utf-8") as fh:
            fh.write("ok")
        shutil.rmtree(d, ignore_errors=True)
        add("PASS", "0700 private dir", "ok", "")
    except Exception as exc:
        add("WARN", "0700 private dir",
            "%s: %s" % (type(exc).__name__, exc),
            "restricted sandbox token (e.g. DSH default permission). "
            "Use the python-only route, or raise the session to danger-full-access")


def check_tool(name, hint):
    p = shutil.which(name)
    add("PASS" if p else "WARN", "tool: %s" % name, p or "not found", "" if p else hint)


def check_network():
    try:
        s = socket.create_connection(("pypi.org", 443), timeout=3)
        s.close()
        add("INFO", "network (pypi:443)", "reachable", "")
    except Exception as exc:
        add("INFO", "network (pypi:443)", "unreachable (%s)" % type(exc).__name__,
            "fine: the L1/L2 minimal path needs no network")


def check_admin():
    try:
        import ctypes
        elevated = bool(ctypes.windll.shell32.IsUserAnAdmin())
        add("INFO", "admin/elevated", str(elevated), "")
    except Exception:
        add("INFO", "admin/elevated", "unknown (non-Windows)", "")


def main(argv):
    try:
        sys.stdout.reconfigure(errors="backslashreplace")
    except Exception:
        pass

    add("INFO", "os", "%s %s" % (platform.system(), platform.release()), "")
    check_python()
    check_temp_default()
    check_temp_private()
    check_tool("bash", "no bash: use the python-only route in docs/using-guide section 6 (host shells like DSH's sandbox may also refuse bash)")
    check_tool("sha256sum", "no sha256sum: use 'python -c \"import hashlib,sys;print(hashlib.sha256(open(sys.argv[1],\\'rb\\').read()).hexdigest())\" FILE'")
    check_tool("tar", "no tar: unzip the release with Explorer / python -m zipfile")
    check_network()
    check_admin()

    print("\nL0 env check  (%s)\n" % time.strftime("%Y-%m-%d %H:%M:%S"))
    counts = {"PASS": 0, "WARN": 0, "FAIL": 0, "INFO": 0}
    for level, name, detail, fix in RESULTS:
        counts[level] += 1
        print("[%-4s] %-28s %s" % (level, name, detail))
        if fix and level in ("WARN", "FAIL"):
            print("       -> %s" % fix)

    fails = counts["FAIL"]
    warns = counts["WARN"]
    print("\nL0: %d PASS / %d WARN / %d FAIL / %d INFO" % (counts["PASS"], warns, fails, counts["INFO"]))
    if fails:
        print("L0 = FAIL: even the python-only route is blocked. Fix the FAIL lines first.")
        return 2
    if warns:
        print("L0 = WARN: python-only route (L1/L2 minimal) works.")
        print("         Two different causes, two different fixes:")
        print("         - bash missing  => install Git Bash or WSL if you want the bash steps;")
        print("         - bash present but 0700/temp failed => you are in a restricted sandbox, not a broken machine:")
        print("           either keep to the python-only route, or move the session to a writable profile (e.g. danger-full-access).")
        return 0
    print("L0 = PASS: bash + python routes both look usable on this machine.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
