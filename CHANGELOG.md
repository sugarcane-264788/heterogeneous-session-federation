# 变更记录

体例照 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，版本号照 [SemVer](https://semver.org/lang/zh-CN/)。

## [Unreleased]

- `docs/demos/`：三个可复跑的真实协作实录（防丢信／热拔插续跑／拒绝无证据的「已修好」）。
- `README.md` 内嵌一张与 `docs/工作原理.md` 同源的 Mermaid 全貌图。
- 跨厂商实测：在 DSH 之外再跑一套（Claude Code／Codex 之一），把「换 harness」从设计意图变成实测结论。

## [1.0.4] - 2026-11-08

第四轮冷读（同一判法、只给 v1.0.3 解压副本）确认 v1.0.3 的三条阻断与三条「会骗人」已清零，另提 4 处摩擦；同时按「L3 要能被别人直接装用、能被开发者照抄、且不含作者机器信息」重打三件插件包。

### Changed

- **L3 插件包脱敏**：`plugins/` 三件 tgz 重打，不含作者机器的绝对路径、用户名、真会话 id——`dsh-kbhub` 出厂是 `__KBHUB_SERVER__`／`__PYTHON__`／`__KBHUB_AW__` 占位符（装前必须跑 `install.py`）；`dsh-session-mesh` 未设 `DSH_MESH_MACHINE` 时把账本落在 `~/.dsh-mesh/`；两份插件 README 里的本机路径全部换成 `$DSH_HOME`／`$DSH_MESH_MACHINE` 口径；删除只对作者有意义的内部报告与测试脚本。
- 版本号统一 `v1.0.4`；README、两份 docs、插件表与 `CHANGELOG` 对齐。

### Fixed

- `dsh-kbhub` 的 `install.py --check` 之前只校验 `--aw` 下有 `协作库/`，不校验 `工具/` ⇒ 只有「半个工作区」时也报「库根 已就绪」，装上去工具静默不可用（假绿灯）。现在 `工具/` 缺失直接 `rc=1` 并给出 WARN。
- `plugins/mesh.py` 文档串与用例里的示例命令仍写 `python 工具\mesh\mesh.py`（包里是 `plugins/mesh.py`）；`MACHINE`／`DSH_HOME` 回退仍写死作者机器路径 ⇒ 全部改为环境变量与 `~/.dsh-mesh/` 口径。
- `plugins/README.md` 一处自相矛盾（既说「`mesh.py` 随包附带」又说「不在这个发布包里」）⇒ 改为「不在 tgz 里、但在这个发布包里」，并补前提「需要 DSH 宿主在跑且插件已加载」。
- `docs/使用指南.md` 第 8 步的「无宿主降级判法」偏松（造占位文件就能宣布通过）⇒ 改成三条必须做的真动作（建一张真卡、真投一封并 digest、开工语里点名的三样必须是你写过内容的真文件）。

### Added

- `plugins/_sanitize_check.py`：发布包脱敏自检（盘符绝对路径／用户名／会话 id 三条规则），干净 `rc=0`、有命中 `rc=3` 并列出 `文件:行`。文档里若要用假会话 id 演示格式，写进脚本的 `PLACEHOLDER_IDS` 白名单（当前 `1a2b3c4d`）。

## [1.0.3] - 2026-11-08

第三轮冷读（同一判法、只给解压副本）抓到 3 条阻断、3 条「看起来对但会骗人」、5 处口径不一致，全部修掉。

### Fixed

- **丢信（真 bug，v1.0.2 的修法只覆盖了同一发件人）**：两个**不同发件人**在同一秒投进同一箱时，文件名时间戳相同、只能靠发件人名排序；游标一旦推过字典序靠后的那封，靠前那封**永久读不到**（实测：`alice`／`zoe` 同秒，`digest` 推进到 `zoe`，再投 `bob`（同秒）落在 `zoe` 之前，`status` 报「未读 0 / 共 3」）。改成：**该秒内箱里已有任何信就往后挪一秒**，与发件人无关。
- `docs/使用指南.md` 第 8 步「开新会话演练」需宿主才能做，纯终端环境永远「卡住」；补「前提」与**无宿主时的降级判法**（逐条对照 `boot-template.md` 要的文件、列出缺哪几份）。
- `skills/session-handoff/SKILL.md` 的替换表给错两处：命令相对**包根**而不是库根（`cd` 到包根再跑）、`docs/原理` 实际叫 `docs/工作原理.md`；0.2 那条补 `--root`，并写明 `--root` 必须写在子命令前。
- `skills/layered-self-check/SKILL.md`、`skills/human-machine-dual-track/SKILL.md` 里「`kb_check` 全 PASS／`--doctor` PASS」在发布包里不可能发生（没有 `工具/`）；各加包内替代判法与「等脚本补齐再换回机器判据」。
- `docs/使用指南.md` 关于 `--root` 位置的说法（原写「会被当成信的内容」，实测是 `unrecognized arguments: --root …` 直接退出 2）。
- 版本号统一 `v1.0.3`（根 README 还停在 v1.0.1、两份 docs 停在 v1.0——上一版 CHANGELOG 声称修了，实际没改）。
- 「更新计划」表里 `CHANGELOG／贡献指南／安全策略 | 缺` 与事实相反（v1.0.0 起已随包）→ 改成「已有短版，缺流程细节」。
- 斜杠口径自相矛盾（原理 §约定 写「统一用反斜杠」、全书用正斜杠）→ 统一正斜杠，仅命令行示例保留反斜杠。
- 名册位置两处说法不一（原理写 `10-主对话/会话名册.md`、指南让建在库根 `名册.md`）→ 原理补「完整库在哪、最小库放哪」。
- `skills/multi-session-workspace/SKILL.md` 的「四行头（含 `给：`）」与实际实现（三行头＋正文）不符。

### Added

- `plugins/mesh.py`：命令行投递与观测（`status`／`journal`／`send`／`rescan`，纯标准库，读 `$DSH_HOME/mesh`）。之前只有会话内的 MCP 工具，shell、cron、排障都没有入口。
- `plugins/README.md` 增「kbhub 装前必须做一步」：tgz 里的补丁带本机绝对路径，直接装到别的机器会**静默缺工具**（`failOnStartupError: false`），装前需 `install.py --restore` 再 `--python/--aw` 写本机值。

## [1.0.2] - 2026-11-08

第二轮冷读复查又抓到一条自己改出来的硬伤，以及三处口径不一致。

### Fixed

- `starter/mailbox_min.py`：v1.0.1 用 `-2` 后缀避免覆盖，但 `-`(0x2D) 排在 `.`(0x2E) 之前，`…-boss-2.md` 成了「比游标更旧」的信——读者推进过游标后**永远读不到它**，等于把丢信换了个形式。改成「撞名就把时间戳往后挪一秒」，文件名保持同一形状、顺序单调，`open(..., "x")` 仍然不覆盖。（两轮都是冷读者抓的，这类 bug 自己读代码很难看出来。）
- `skills/session-handoff/SKILL.md`、`skills/card-ledger-workflow/SKILL.md`：原文里的 `..\工具\…`、`00-规范\…` 是完整库路径，照抄会断。各加一段「只有发布包时按这个对应关系替换」，`skills/README.md` 补一张对照表。
- `README.md`：版本号没跟着升（仍写 v1.0）、构成行漏 `skills/` 且用了反斜杠；已知不足第 2 条说「贡献指南／CHANGELOG／安全策略仍缺失」，其实 v1.0.0 就随包给了——改成「制度面不深」。
- `starter/README.md`：「故意没做」里还写着「真需要时加 `O_EXCL`」，与已实现的 `open(..., "x")` 矛盾；改成如实说明单机单进程已兜住、多进程并发仍是 L2 的事。
- `plugins/README.md`：`mesh.py` 那条原写「从源码目录取」，但发布包没有源码目录；改成「不在包里，先用信箱配合 `starter/mailbox_min.py`」。

## [1.0.1] - 2026-11-08

一次冷读复查（让一个只看发布包的人照 README 从零搭 L1）暴露的问题修复。

### Added

- `skills/`：七个工作法的全文（`session-handoff`／`card-ledger-workflow`／`layered-self-check`／`delegate-and-reclaim`／`human-machine-dual-track`／`proposal-gate`／`multi-session-workspace`），L1 七条改成带路径的引用；`skills/README.md` 给索引与两种用法（有 skills 机制的宿主／手抄进会话）。
- `README.md`「运行前提」一行：命令是 bash 语法，Windows 需 Git Bash 或 WSL。
- `plugins/README.md`「前提」与「已知限制」两节：必须带 `DSH_HOME`；三件 tgz 内部脚本带着作者机路径，`mesh.py` 不在包内。

### Fixed

- `starter/mailbox_min.py`：同一秒连发两封会撞同名并覆盖第一封（命令还打印「已投递」）。改成撞名加 `-2`／`-3` 序号、`open(..., "x")` 不覆盖——这正是「防丢信」要防的那件事，谢谢冷读者抓到。
- `docs/工作原理.md` §8「最小验证」：原文七条命令全指库内 `工具/`（发布包不带），照做的人一条都跑不了。改成包内可跑的 `starter` 三条＋文件存在性清单，库内自检移到 §8.1 并注明前提。
- `starter/README.md`：删掉指向包内不存在的 `01-设计全景.md`／`04-落地清单.md` 的引用；`status` 期望值改成实际输出（没有信的箱不列出）；补「同秒第二封加 `-2`」；`card-template.md`／`closeout.sh` 加「命令假设完整库」的说明。
- `docs/使用指南.md`：`--as`／`repair` 在随包最小实现里没有，L1 验收改成「一箱一线＋`--peek` 不推进」的等价判法，并写明这两个开关属完整库。

## [1.0.0] - 2026-11-08

首个公开版本。

### Added

- `README.md`：定位与采用成本、核心思想两条、作者自述、四段真实协作（一封信十二分钟／播报被判没发改判据／交接／数据库提案被驳回）、现状数字（全部标 as-of 与取数命令）、已知不足九条、更新计划四组。
- `docs/工作原理.md`：七个文件面（格子／信箱／名册／台账／计划卡／交接包／播报）、一次协作的生命周期与七处落点、三条铁律及机器判据、故障矩阵、与宿主的边界、最小验证命令、它不保证的四条边界。
- `docs/使用指南.md`：L1 七个工作法、L2 七个文件面的最小形态与验收、L3 自动叫醒、从零搭起来的八步（每步带命令与「看到什么算正常」）、常见故障、升级宿主与回滚。
- `starter/`：零依赖最小实现（`mailbox_min.py` 信箱 80 行、卡模板、接手模板、收尾脚本），`python starter/mailbox_min.py --selftest` 可直接复跑。
- `plugins/`：三件自研插件的 tgz 与名称／版本／字节／sha256 清单。
- `docs/assets/selftest.txt`：README 首屏那段输出的原文。
- `CONTRIBUTING.md`／`SECURITY.md`／`CODE_OF_CONDUCT.md`／`.gitignore`／`docs/README.md`。

### Known limitations

- 全部实测在单一 harness（DeepSeek Harness `0.2.2-rc.1`）内；跨厂商协作一次没跑过。
- L3（自动叫醒那层）没有安装器：插件有 tgz，配置与叫醒参数仍靠人照文档配。
- 适用范围：个人或小团体；组织级、多人跨部门、合规审计场景未验证。
