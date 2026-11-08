# 三件自研插件（发布形态）

这套协作体系在本机靠三件自研插件补三块能力：**把库变成工具**（MCP 工具面）、**跨会话投递与叫醒**、**侧栏自愈**。它们不是方法论的一部分——没有它们，体系退化成轮询也能跑（见 `原理` §7.2）；但有了它们才是「自动叫醒」的那一档。

包名一律 `dsh-` 前缀，无 scope；`id` 与包名不是同一个东西，见下。

| 包名 | 版本 | 字节 | sha256 | 作用 |
|---|---|---|---|---|
| `dsh-kbhub` | 0.0.3 | 9,991 | `5abcccd26667a275828412bf9ae044286199b3e4b6bfa7a358ec39e4ebfc4956` | stdio MCP 服务，工具名 `kbhub_*`：读库、列收件箱、跑自检、写探针 |
| `dsh-session-mesh` | 0.0.2 | 40,614 | `a30ece5c4c1d1c8ebbde9e43441aa1e9ad921407cd28dc80cde6eb843fb65843` | 把消息投进对方信箱并叫醒；带侧栏自愈 |
| `dsh-session-auto-refresh` | 0.0.2 | 7,032 | `74d72bda5f38b8fb8304303b99c14182004e80361d75c8a5de3dd89c2648b07d` | 侧栏缺会话时重载一次 |

## 前提（缺一条就别装）

1. 已经装好 DSH 桌面版或 CLI，并且 `dsh --help` 能跑（包里不含宿主）。
2. 知道自己的 profile 名（默认 `desktop`；`ls $DSH_HOME/profiles` 能看到）。
3. **命令必须带 `DSH_HOME`**：不带会装进默认的 `~/.dsh`，等于白装（这是实测踩过的坑，见 `docs/使用指南.md` §7 表末两行）。

## 装法

```bash
export DSH_HOME=<你的 DSH_HOME>            # 例：D:/dsh ；不带会装进 ~/.dsh
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

## 已知限制（v1.0.1 如实标注）

- 三件 tgz 的内部脚本（`kbhub_server.py`、`mesh.py` 的调用方、配置里的默认目录）是在作者机上写成的，含写死的绝对路径与目录约定；换机器要按 `docs/使用指南.md` §9 的隔离清单改配置。
- `mesh.py`（命令行投递脚本）不在 tgz 里，也不在这个发布包里——tgz 只是插件包。要用命令行投递，先用信箱配合 `starter/mailbox_min.py`；等我们把它单独发布再补。
- 三件插件只保证在 DSH `0.2.2-rc.1` 上实测过；其他宿主没有对应实现。
