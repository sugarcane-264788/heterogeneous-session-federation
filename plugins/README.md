# 三件自研插件（发布形态）

这套协作体系在本机靠三件自研插件补三块能力：**把库变成工具**（MCP 工具面）、**跨会话投递与叫醒**、**侧栏自愈**。它们不是方法论的一部分——没有它们，体系退化成轮询也能跑（见 `原理` §7.2）；但有了它们才是「自动叫醒」的那一档。

包名一律 `dsh-` 前缀，无 scope；`id` 与包名不是同一个东西，见下。

| 包名 | 版本 | 字节 | sha256 | 作用 |
|---|---|---|---|---|
| `dsh-kbhub` | 0.0.3 | 10,223 | `0ab5fb6b3371cac3886d771fec87d725711177827ed294d2d46011c81e167a25` | stdio MCP 服务，工具名 `kbhub_*`：读库、列收件箱、跑自检、写探针 |
| `dsh-session-mesh` | 0.0.2 | 40,731 | `cd496929bd3e3f2edc644332ccf7f3bdac9b712b205d32a970efda651e953192` | 把消息投进对方信箱并叫醒；带侧栏自愈 |
| `dsh-session-auto-refresh` | 0.0.2 | 6,995 | `cfba88d269c7f86c2059e4c40229d34b7713e818fb13f6f0df1b7bcab31ac2ba` | 侧栏缺会话时重载一次 |

## 前提（缺一条就别装）

1. 已经装好 DSH 桌面版或 CLI，并且 `dsh --help` 能跑（包里不含宿主）。
2. 知道自己的 profile 名（默认 `desktop`；`ls $DSH_HOME/profiles` 能看到）。
3. **命令必须带 `DSH_HOME`**：不带会装进默认的 `~/.dsh`，等于白装（这是实测踩过的坑，见 `docs/使用指南.md` §7 表末两行）。

## kbhub 装前必须做一步（否则静默缺工具）

`dsh-kbhub` 的补丁里有两处**必须由你写成本机值**的占位符：`args` 指向 `kbhub_server.py`、`command` 指向解释器、`env.KBHUB_AW` 指向你的库根。**不跑安装器直接装**：MCP 子进程起不来，而补丁里写着 `failOnStartupError: false` ⇒ **插件照常加载、不报错，只是 `mcp__kbhub__*` 整套工具静默消失**，最难查。（v1.0.4 起出厂是占位符形态，不含任何作者机器的绝对路径。）

装之前，在解开的包目录里跑一次安装器，把两处本机值写进去：

```bash
cd <解开的包目录>/package          # 里面应有 install.py 与 kbhub_server.py
python install.py --restore        # 出厂已是占位符；这一步只在「谁都别改过」时保险，幂等
python install.py --python <你的 python.exe> --aw <你的 AI-Workspace 根>
python install.py --check          # 期望：两处都就绪
```

`--aw` 指的那个目录下应同时有 `协作库/` 与 `工具/`（服务靠它定位库）；侦测不到就显式给。装完重启宿主，`dsh --help` 之外再用一句 `kbhub_*` 工具调用验一次「工具真的出现了」。

## 命令行投递：`plugins/mesh.py`

`dsh-session-mesh` 插件给的是**会话内**的 `mesh_send`／`mesh_status`／`mesh_inbox` 工具；想在 shell 里投递或看现场（cron、批处理、排障），用随包附带的 `plugins/mesh.py`（纯标准库，与插件同一套协议）：

```bash
export DSH_HOME=<你的 DSH_HOME>            # 它从 $DSH_HOME/mesh 读 base 与 token
# 前提：DSH 宿主在跑，且 dsh-session-mesh 已装进该 profile（token 由插件加载时写出）
python plugins/mesh.py status             # clients / holds / passive 队列
python plugins/mesh.py send --from 我 --mode queue --to <会话 id> < 正文.txt
```

没有 `DSH_HOME` 时读 `DSH_MESH_BASE_FILE`／`DSH_MESH_TOKEN_FILE` 指定的文件；它只做投递与观测，不参与插件的叫醒逻辑。

## 装法

```bash
export DSH_HOME=<你的 DSH_HOME>            # 例：/home/you/dsh ；不带会装进 ~/.dsh
dsh plugin --profile <profile> add ./plugins/dsh-session-mesh-0.0.2.tgz
```

三个都装完，profile 的依赖里应出现 `dsh-*` 指向 `file:` 或直接进 `node_modules`，`dsh.profile.bundles` 里也应是同样的三个名字；启动日志不应出现 `did not activate`。

## 改名只动三处，`id` 永远不动

| 要改 | 不要改 |
|---|---|
| 包 `package.json` 的 `name` | 插件补丁 `cordis.patch.yml` 的 `id`（配置槽 id） |
| 补丁里 `insert[].name` | 同上 |
| 宿主的依赖列表与 bundle 列表 | 同上 |

`id` 是宿主用来挂用户开关的键；改了它，用户关掉的插件会重新打开、开着的会莫名失效。三件插件当前的 `id` 分别是 `kbhub-mcp`、`session-mesh-lite`、`session-auto-refresh` —— 名字换了，`id` 没换，这是对的。

## 与本地开发环境的关系

本机开发环境把这三件以链接方式指向源码目录，包名与发布形态一致，区别只在「指向源码」还是「指向 tgz」。同一份代码两种挂法，不需要为了发布改代码。

## 脱敏口径（v1.0.4 起）

三件 tgz 里不含作者机器的绝对路径、用户名、会话 id：`dsh-kbhub` 出厂是 `__KBHUB_SERVER__`／`__PYTHON__`／`__KBHUB_AW__` 占位符；`dsh-session-mesh` 在没设 `DSH_MESH_MACHINE` 时把账本落在 `~/.dsh-mesh/`（不指向任何人的盘）。想验证，跑：

```bash
python plugins/_sanitize_check.py     # 扫描整个发布包，命中作者信息即非零退出
```

## 已知限制（v1.0.4 如实标注）

- 三件 tgz 的内部脚本（`kbhub_server.py`、`mesh.py` 的调用方、配置里的默认目录）是在作者机上写成的，含写死的绝对路径与目录约定；换机器要按 `docs/使用指南.md` §9 的隔离清单改配置。
- `plugins/mesh.py` 是随包附带的命令行脚本，**不在 tgz 里**但在这个发布包里（tgz 只是插件包）。它需要 DSH 宿主在跑且插件已加载（token 由插件写出）；没有宿主时只能做参数级检查（`--help` 与缺 token 时的退出码 2）。
- 三件插件只保证在 DSH `0.2.2-rc.1` 上实测过；其他宿主没有对应实现。
