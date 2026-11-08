# 三件自研插件（发布形态）

这套协作体系在本机靠三件自研插件补三块能力：**把库变成工具**（MCP 工具面）、**跨会话投递与叫醒**、**侧栏自愈**。它们不是方法论的一部分——没有它们，体系退化成轮询也能跑（见 `原理` §7.2）；但有了它们才是「自动叫醒」的那一档。

包名一律 `dsh-` 前缀，无 scope；`id` 与包名不是同一个东西，见下。

| 包名 | 版本 | 字节 | sha256 | 作用 |
|---|---|---|---|---|
| `dsh-kbhub` | 0.0.3 | 9,991 | `5abcccd26667a275828412bf9ae044286199b3e4b6bfa7a358ec39e4ebfc4956` | stdio MCP 服务，工具名 `kbhub_*`：读库、列收件箱、跑自检、写探针 |
| `dsh-session-mesh` | 0.0.2 | 40,614 | `a30ece5c4c1d1c8ebbde9e43441aa1e9ad921407cd28dc80cde6eb843fb65843` | 把消息投进对方信箱并叫醒；带侧栏自愈 |
| `dsh-session-auto-refresh` | 0.0.2 | 7,032 | `74d72bda5f38b8fb8304303b99c14182004e80361d75c8a5de3dd89c2648b07d` | 侧栏缺会话时重载一次 |

## 装法

```bash
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
