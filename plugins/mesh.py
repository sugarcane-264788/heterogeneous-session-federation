#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""mesh.py —— 会话网格插件的命令行通道（M67）

为什么要有它：插件把 mesh_send / mesh_inbox / mesh_status 三个工具注册在宿主里，
但已存在的会话（包括老会话、子代理）拿不到这些工具（见 `_优化清单` O39）。
插件自带一个 HTTP 调试口 `POST /api/local-mesh/send`，头部要求 `x-mesh-token`，
token 由插件在加载时写到 `40-协作\_machine\mesh-token.txt`。这个脚本就是那条口子的薄封装，
让**任何**会话（含受限会话、含派出去的子代理）都能用一条命令发消息。

用法：
    python plugins/mesh.py status
    python plugins/mesh.py journal -n 8
    python plugins/mesh.py send --to session-xxxx [--mode queue|interrupt|passive] ^
        --from <发送方> [--urgent] [--text "……"]
    echo "正文" | python plugins/mesh.py send --to session-xxxx
    python plugins/mesh.py send --to session-xxxx --text "……" --dry-run

退出码：0 成功／2 参数或环境问题（找不到 token、找不到宿主）／3 宿主拒绝／4 网络失败。
"""

import argparse
import io
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request

MACHINE = os.environ.get('DSH_MESH_MACHINE') or os.path.join(
    os.path.expanduser('~'), '.dsh-mesh', 'machine')
# token 不再放在协作库（会随备份走）：插件写在 DSH 自己的目录，这里先看新位置，
# 再看旧位置兜底，最后才认环境变量 DSH_MESH_TOKEN_FILE。
DSH_HOME = os.environ.get('DSH_HOME') or ''
TOKEN_FILE = os.environ.get('DSH_MESH_TOKEN_FILE') or (
    os.path.join(DSH_HOME, 'mesh', 'mesh-token.txt') if DSH_HOME else os.path.join(MACHINE, 'mesh-token.txt')
)
LEGACY_TOKEN_FILE = os.path.join(MACHINE, 'mesh-token.txt')
LEGACY_BASE_FILE = os.path.join(MACHINE, 'mesh-base.txt')
# 端口缓存也是「这台机器的事」，不是协作库的内容：和 token 一样放 DSH 目录，旧位置只读兜底。
BASE_FILE = os.environ.get('DSH_MESH_BASE_FILE') or (
    os.path.join(DSH_HOME, 'mesh', 'mesh-base.txt') if DSH_HOME else LEGACY_BASE_FILE
)
JOURNAL = os.path.join(MACHINE, 'deliveries.jsonl')
MODES = ('queue', 'interrupt', 'passive')
STATE_PATH = '/api/local-mesh/state'
SEND_PATH = '/api/local-mesh/send'
RESCAN_PATH = '/api/local-mesh/rescan'


def die(code, message):
    sys.stderr.write(message.rstrip() + '\n')
    raise SystemExit(code)


def read_token():
    for path in (TOKEN_FILE, LEGACY_TOKEN_FILE):
        if not os.path.exists(path):
            continue
        token = open(path, encoding='utf-8').read().strip()
        if not token:
            die(2, '[环境] token 文件是空的：%s' % path)
        return token
    die(2, '[环境] 找不到 token 文件：先看 %s，再看旧位置 %s' % (TOKEN_FILE, LEGACY_TOKEN_FILE))


def probe(base, timeout=1.0):
    try:
        with urllib.request.urlopen(base + STATE_PATH, timeout=timeout) as response:
            data = json.loads(response.read().decode('utf-8'))
    except Exception:
        return None
    if isinstance(data, dict) and 'journal' in data:
        return data
    return None


def listening_ports():
    """本机 LISTENING 端口（只靠 netstat，不引第三方库）。顺序：先高号端口。"""
    try:
        output = subprocess.run(['netstat', '-ano'], capture_output=True, timeout=15).stdout.decode('utf-8', 'replace')
    except Exception:
        return []
    ports = set()
    for line in output.splitlines():
        match = re.search(r'127\.0\.0\.1:(\d+)\s+\S+\s+LISTENING', line)
        if match:
            ports.add(int(match.group(1)))
    return sorted(ports, reverse=True)


def discover():
    override = os.environ.get('MESH_BASE')
    if override:
        data = probe(override)
        if data is None:
            die(2, '[环境] MESH_BASE=%s 上没找到 mesh 路由' % override)
        return override, data
    candidates = []
    for cache in (BASE_FILE, LEGACY_BASE_FILE):
        if not os.path.exists(cache):
            continue
        cached = open(cache, encoding='utf-8').read().strip()
        if cached:
            candidates.append(cached)
            break
    ports = listening_ports()
    candidates.extend('http://127.0.0.1:%d' % port for port in ports[:60])
    for base in candidates:
        data = probe(base, timeout=0.4)
        if data is not None:
            try:
                os.makedirs(os.path.dirname(BASE_FILE), exist_ok=True)
                open(BASE_FILE, 'w', encoding='utf-8', newline='\n').write(base + '\n')
            except Exception:
                pass
            return base, data
    die(2, '[环境] 没找到在跑网格插件的宿主（探了 %d 个本地端口）。宿主没开？还是插件没加载？' % len(candidates))


def passive_holds():
    """读 mesh-state.json 里的 holds（passive 待升级项）。读不到就当空。"""
    path = os.path.join(MACHINE, 'mesh-state.json')
    try:
        with io.open(path, encoding='utf-8') as f:
            data = json.load(f)
    except Exception:
        return []
    holds = data.get('holds')
    if not isinstance(holds, dict):
        return []
    out = []
    for key, value in holds.items():
        if isinstance(value, dict):
            item = dict(value)
            item.setdefault('msg_id', key)
            out.append(item)
    return out


def cmd_status(args):
    base, data = discover()
    print('base：%s' % base)
    print('config：%s' % json.dumps(data.get('config', {}), ensure_ascii=False, sort_keys=True))
    print('clients：%s（浏览器半段连着几个）' % data.get('clients'))
    # M82：原来这一行打印的是宿主侧「投递占用」（按 sessionId、holdMs 30 秒），
    # 与 state.holds 里的「passive 待升级项」同名不同物，读数会被误判。
    passive = passive_holds()
    print('dispatch holds：%s（投递占用，按会话计，holdMs 内有效）' % data.get('holds'))
    print('passive holds：%d（mesh-state.json 里等待升级的 passive）' % len(passive))
    for item in passive[:5]:
        to = str(item.get('session_id', '?'))[:20]
        due = item.get('due_at')
        left = '-'
        if isinstance(due, (int, float)):
            left = '%d 秒' % max(0, int((due - time.time() * 1000) / 1000))
        print('    · %s → %s  剩余 %s' % (str(item.get('msg_id', '?'))[:24], to, left))
    if args.raw:
        print(json.dumps(data, ensure_ascii=False, indent=2))
    return 0


def rotated_journals():
    """跨月切档后的历史账本（deliveries-YYYY-MM.jsonl），新的在前。"""
    try:
        names = sorted(
            (n for n in os.listdir(MACHINE) if re.match(r'^deliveries-\d{4}-\d{2}(?:-\d+)?\.jsonl$', n)),
            reverse=True,
        )
    except OSError:
        return []
    return [os.path.join(MACHINE, n) for n in names]


def cmd_journal(args):
    if not os.path.exists(JOURNAL):
        history = rotated_journals()
        if not history:
            die(2, '[环境] 没有账本文件：%s' % JOURNAL)
        print('[提示] 当月的 deliveries.jsonl 还没写；历史账本在：')
        for path in history[:5]:
            print('  %s' % os.path.basename(path))
        return 0
    rows = [json.loads(line) for line in open(JOURNAL, encoding='utf-8') if line.strip()]
    for row in rows[-args.n:]:
        print('%s  %-9s %-9s %-11s %s -> %s  %dms  %d字' % (
            row.get('ts', ''),
            row.get('mode', ''),
            row.get('status', ''),
            row.get('presence', '') or '-',
            (row.get('from') or '?')[:14],
            (row.get('to') or '?')[:22],
            int(row.get('elapsed_ms') or 0),
            int(row.get('text_chars') or 0),
        ))
    history = rotated_journals()
    if history:
        print('（更早的账本：%s）' % '、'.join(os.path.basename(p) for p in history[:3]))
    return 0


def cmd_send(args):
    text = args.text
    if text is None and not sys.stdin.isatty():
        text = sys.stdin.read().strip()
    if not text:
        die(2, '[参数] 缺正文：用 --text "……" 或从 stdin 喂')
    if args.mode not in MODES:
        die(2, '[参数] --mode 只能是 %s' % '／'.join(MODES))
    sender = (args.from_ or '').strip()
    if not sender:
        die(2, '[参数] 缺 --from：本机没有可自动推断的会话身份，请显式写是谁发的（一般用名册「角色」列的名字）。\n'
               '  可复制：python plugins/mesh.py send --from 主对话 --to <session-id> --text "……"')
    if len(sender) > 60:
        die(2, '[参数] --from 太长（%d 字符，上限 60）' % len(sender))
    base, data = discover()
    token = read_token()
    body = json.dumps({
        'to': args.to,
        'text': text,
        'mode': args.mode,
        'from': sender,
        'urgent': bool(args.urgent),
        'urgentReason': args.urgent_reason,
    }).encode('utf-8')
    if args.dry_run:
        print('[干跑] 会 POST %s；body=%s' % (base + SEND_PATH, body.decode('utf-8')))
        print('[干跑] logOnly=%s，token 前 8 位=%s' % ((data.get('config') or {}).get('logOnly'), token[:8]))
        return 0
    request = urllib.request.Request(
        base + SEND_PATH,
        data=body,
        headers={'content-type': 'application/json', 'x-mesh-token': token},
        method='POST',
    )
    try:
        with urllib.request.urlopen(request, timeout=args.timeout) as response:
            code = response.status
            payload = json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as error:
        code = error.code
        try:
            payload = json.loads(error.read().decode('utf-8'))
        except Exception:
            payload = {'accepted': False, 'error': 'HTTP %d' % error.code}
    except Exception as error:
        die(4, '[网络] POST 失败：%s' % error)
    if code == 200 and payload.get('accepted'):
        print('已投：%s  %s  seq %s→%s  presence=%s  目标=%s' % (
            payload.get('msg_id'),
            payload.get('mode'),
            payload.get('seq_before'),
            payload.get('seq_after'),
            payload.get('presence'),
            payload.get('sessionId'),
        ))
        return 0
    print('被拒（HTTP %d）：%s' % (code, json.dumps(payload, ensure_ascii=False)), file=sys.stderr)
    return 3


def cmd_rescan(args):
    base, _data = discover()
    token = read_token()
    request = urllib.request.Request(
        base + RESCAN_PATH,
        data=b'{}',
        headers={'content-type': 'application/json', 'x-mesh-token': token},
        method='POST',
    )
    try:
        with urllib.request.urlopen(request, timeout=args.timeout) as response:
            payload = json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as error:
        die(3, '[拒绝] HTTP %d：%s' % (error.code, error.read().decode('utf-8', 'replace')[:200]))
    except Exception as error:
        die(4, '[网络] POST 失败：%s' % error)
    print('已让宿主重扫：本次新注册 %s 个会话（当前 roots=%s），工具 %s' % (
        payload.get('registered_now'), payload.get('roots'), '／'.join(payload.get('tools') or [])))
    print('提示：M68 实测＝宿主侧已注册（本 Agent 的 Tool.listTools 能看到 mesh_*），但模型侧工具表是会话建立时定版的，正在跑的会话当轮不一定看得见；看不见就用本脚本 send，等价。')
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description='会话网格插件的命令行通道（POST /api/local-mesh/send 薄封装）')
    sub = parser.add_subparsers(dest='cmd', required=True)

    status = sub.add_parser('status', help='看宿主侧状态（config/clients/holds）')
    status.add_argument('--raw', action='store_true', help='连同原始 JSON 一起打')
    status.set_defaults(func=cmd_status)

    journal = sub.add_parser('journal', help='看投递账本尾部')
    journal.add_argument('-n', type=int, default=5, help='看最后几条，默认 5')
    journal.set_defaults(func=cmd_journal)

    send = sub.add_parser('send', help='给某个会话投一条消息')
    send.add_argument('--to', required=True, help='目标会话 id（session-…）')
    send.add_argument('--text', default=None, help='正文；不给就从 stdin 读')
    send.add_argument('--mode', default='queue', choices=MODES, help='默认 queue（排队，不打断）')
    send.add_argument('--from', dest='from_', default=None,
                      help='发送方标识（必填：一般写名册「角色」列的名字，例如 主对话／协作库维护）')
    send.add_argument('--urgent', action='store_true', help='紧急：可越过每对每小时 20 条限流，留审计')
    send.add_argument('--urgent-reason', dest='urgent_reason', default=None, help='紧急理由（写进审计）')
    send.add_argument('--timeout', type=float, default=30.0, help='秒，默认 30')
    send.add_argument('--dry-run', dest='dry_run', action='store_true', help='只打请求不真发')
    send.set_defaults(func=cmd_send)

    rescan = sub.add_parser('rescan', help='让宿主立刻重扫一次 roots，给还没注册工具的活会话补上')
    rescan.add_argument('--timeout', type=float, default=15.0, help='秒，默认 15')
    rescan.set_defaults(func=cmd_rescan)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == '__main__':
    raise SystemExit(main())
