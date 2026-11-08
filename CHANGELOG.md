# 变更记录

体例照 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，版本号照 [SemVer](https://semver.org/lang/zh-CN/)。

## [Unreleased]

- `docs/demos/`：三个可复跑的真实协作实录（防丢信／热拔插续跑／拒绝无证据的「已修好」）。
- `README.md` 内嵌一张与 `docs/工作原理.md` 同源的 Mermaid 全貌图。
- 跨厂商实测：在 DSH 之外再跑一套（Claude Code／Codex 之一），把「换 harness」从设计意图变成实测结论。

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
