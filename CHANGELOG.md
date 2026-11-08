# 变更记录

体例照 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，版本号照 [SemVer](https://semver.org/lang/zh-CN/)。

## [Unreleased]

- `docs/demos/`：三个可复跑的真实协作实录（防丢信／热拔插续跑／拒绝无证据的「已修好」）。
- `README.md` 内嵌一张与 `docs/工作原理.md` 同源的 Mermaid 全貌图。
- 跨厂商实测：在 DSH 之外再跑一套（Claude Code／Codex 之一），把「换 harness」从设计意图变成实测结论。

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
