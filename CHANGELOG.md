# 变更记录

体例照 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，版本号照 [SemVer](https://semver.org/lang/zh-CN/)。

## [Unreleased]

- `docs/demos/`：三个可复跑的真实协作实录（防丢信／热拔插续跑／拒绝无证据的「已修好」）。
- `README.md` 内嵌一张与 `docs/工作原理.md` 同源的 Mermaid 全貌图。
- 跨厂商实测：在 DSH 之外再跑一套（Claude Code／Codex 之一），把「换 harness」从设计意图变成实测结论。

## [1.0.9] - 2026-11-08

### Added
- `docs/L3-动手前必读.md`：动插件层之前的必读页。八条真实事故（各自带原始报错）、动手前四道闸、崩了之后的回滚顺序（先摘插件再换目录）。
- `README.md` / `docs/使用指南.md` §5 / `docs/工作原理.md` §7.2 各加醒目警告并指向该页。

### 背景
- 一位读者用他自己的 agent 调他的 L3，把 DSH 调崩了。我们的参考实现在同一层上崩过八次，事故都在那份文件里，故把「先看这页」提到 L3 的入口处。

## [1.0.8] - 2026-11-08

来源：新增两个「文档自检」工具后对真包做的第一次机器核对（`doc_assert.py` 静态断言 8 类、`doc_probe.py` 把 bash 块真跑）。它们抓出 3 条**文档与实现不符**——全是人读几轮都没看出来的。

### Fixed

- **行数说法过期**：`README.md` 与 `starter/README.md` 说「信箱约 150 行」，实际 `starter/mailbox_min.py` 已 233 行（v1.0.6 加了归档与 `--as`）。两处改成「约 230 行」。
- **`docs/工作原理.md` §8.1 的命令在 bash 下跑不了**：写的 `python ..\工具\kb\kb_check.py`，bash 把反斜杠当转义符，实际落到 `..工具kbkb_check.py`。改成正斜杠 `../工具/kb/…`，并加一句「Windows 的 cmd／PowerShell 可用反斜杠，本文档统一正斜杠」。
- **`starter/README.md` 的「顺序」不能复制即跑**：命令写 `python mailbox_min.py …`，但那是假设读者已经 `cd starter`。改成在**发布包根目录**执行、命令写 `python starter/mailbox_min.py …`，并说明 `cd starter` 后要去掉前缀。

### Changed

- `docs/工作原理.md` §8.1 的块首加 `# no-run: 这一块只能在完整库（有 工具/ 的那台机器）里跑`——它验证的是完整库的自检，不是发布包；标了之后，机器探针会按「跳过＋说明」处理，而不是假装失败。

## [1.0.7] - 2026-11-08

来源：作者定了层级投入策略——**L0（环境测试）、L1、L2 是维护重点；L3 降级为参考实现**，不再投入打磨。
本版把这条策略写进文档，并把「这台机器能不能跑」做成一等公民。

### Added

- `starter/env_check.py`（L0 环境自检）：逐条报 `PASS／WARN／FAIL`——Python ≥3.8、`TEMP` 普通目录可写、**0700 私有目录**（失败即提示「是档位不是故障」，并指向受限沙箱）、`bash`／`sha256sum`／`tar` 有无、外网、是否管理员。退出码 0＝python 单进程路线可用，2＝连这条路都不行。输出全 ASCII（避开 Windows 控制台乱码）。
- `README.md` 新增「第 0 步：环境自检（L0）」与层级表里的 L0 行；`docs/使用指南.md` §2 表加 L0 行、§6 八步之前加「第 0 步 · 跑一次环境自检」。

### Changed

- **L3 定位改写为「参考实现」**：README 的层级表、已知不足第 3 条与末条，以及 `docs/使用指南.md` §2 表、§5 开头，都写清「L3 不承诺装好即用，作者只维护到 L0–L2；装不通就让你的 agent 照 `plugins/README.md` 自己调」。判据从「装得上」改成「够开发者照抄改」。

## [1.0.6] - 2026-11-08

来源：一位读者把发布包拿到**另一台机器、另一套档位**上照文档从零跑（DSH 默认权限档、机器上没有 Git Bash／WSL）。
本版只改「文档说的事与包里的东西不一致、照做必失败」的地方，不加功能。

### Fixed

- **信箱目录布局与文档不一致（最严重）**：`starter/mailbox_min.py` 原来写 `<root>/boxes/<箱>` 与 `<root>/cursors/<箱>`，而文档（`docs/使用指南.md` §4.1／§4.2、`docs/工作原理.md` §3.2）说的是 `_消息/<箱>`、`_消息/.cursors/<箱>`、`_消息/已处理/<箱>`。结果是照文档建的目录永远是空的、排障会数到 0 封、文档里「手工归档」在最小实现上是空操作。现改成与完整库一致的布局，并真的归档（`os.replace` 搬进 `已处理/<箱>/`，搬成功才推游标）；顺带补了 `digest --as <读者名>` 私有游标。
  - **升级提示**：v1.0.5 及更早建过的 `<root>/boxes`／`<root>/cursors` 会在下次运行时打一行迁移命令（搬过去即可，脚本不自动搬）。
- **`--selftest` 在受限档位必失败**：原来用 `tempfile.mkdtemp`（建 0700 私有目录），在 DSH 默认档这类受限令牌里连目录里的文件都写不进，报 `PermissionError: [WinError 5]`——而它是 README 判「环境够用」的唯一判据。现在改成自建可写临时目录（先探一次写入），实在建不了就明确说「是档位不是故障」并给两条出路。
- **文档没写「宿主档位」**：全篇 bash，而 DSH 默认档里 bash 工具起不来（`SANDBOX_UNSUPPORTED`）。README 与 `docs/使用指南.md` 的运行前提都补了一段：要么开到 `danger-full-access`，要么只用单进程的 `python … mailbox_min.py` 先验证机制。
- **§4.5 计划卡节名与模板不符**：正文写「目标／范围／本卡不做／文件清单／动作／验收／回滚」七项，`starter/card-template.md` 实际是「为什么做／动作／不做／验收／回滚／本卡文件」六节；验收也从「有 `- 文件：` 清单就算过」改成「每行指向真实存在的路径」——照抄模板占位原来也能过。
- **§4.4 台账讲错了失败形态**：原文说「混进逗号分隔的行会让 `awk` 错位」，实测不成立；真正会骗人的是「同一路径两行取末行」和「列数不对时 `awk` 打前一行而不报错」，已改成这两条。
- **§4.7 播报循环发给不存在的箱**：`for b in main email live`，而 §4.1 只建了 `main`／`email`；改成 `main email`。
- **行数写错**：「信箱 80 行」四处 → 按实际改成「约 150 行」（`README.md`、`starter/README.md`）。
- **`starter/closeout.sh` 名实不符**：注释写「收尾七连」，实际是 0/7…7/7 共八段；改成「收尾八段（0/8…7/8）」。

## [1.0.5] - 2026-11-08

第五轮冷读（对象 v1.0.4，只给解压副本）总判「还要再改 6 处」：1 条阻断＋5 条摩擦，全部修掉。

### Fixed

- **阻断：`docs/使用指南.md` 第 8 步「无宿主降级判法」与包内文件不符**（照做必失败）——① 它要填「目标／判据／涉及文件」三节，`starter/card-template.md` 里只有「为什么做／动作／验收」；② 它要「信进 `已处理`」，最小实现根本没有归档目录（digest 后信仍在 `boxes/`）；③ 它说开工语点名「名册／台账／交接包」，而 `starter/boot-template.md` 点名的是 README／九张规范／`_模板/接手交接.md`。改成三条**都能用包内东西做**的动作，并写明判据取自 `mailbox_min.py status` 的三个数。
- `plugins/_sanitize_check.py` 四条盲区：不扫 `.tgz`（最该扫的反而漏）、`.ts` 等扩展名不在白名单、JSON 里被转义成双反斜杠的盘符路径、以及 UNC 路径（两台反斜杠开头的主机共享）不认、一行命中即 `break`。现在会**解包 `.tgz` 逐成员扫**，规则补 UNC 与 Unix `/home/<非占位符>`，并把包内非 root 属主名也当命中。
- `dsh-kbhub` 的 `install.py --check` 只查 `工具/` 目录存在、不查 `工具/kb/kb_check.py`：给一个**空的 `工具/`** 仍报「已就绪」（假绿灯关了一半）。现在直接查 `工具/kb/kb_check.py`，缺了就 rc=1 并在提示里说明「发布包不含 `工具/`，要从完整库带一份」。
- `plugins/README.md` 与 `install.py` 文档串里的示例路径（原来直接举了盘符绝对路径）改成 `<盘>:\<你的路径>` 占位写法——它们不是作者信息，但会把「扫盘符就报」的自检逼出假阳性。
- `docs/使用指南.md` §3.5「怎么验收：doctor 绿」补注：发布包没有 `工具/`，doctor 跑不了，最小库改用「快照与源逐项比」三条。
- `starter/boot-template.md` 里 `verify.py --card` 补「属完整库脚本」注，最小实现改跑 `mailbox_min.py status`。

### Added
- `plugins/_sanitize_check.py` 的规则边界：盘符拆成「常规 / 被转义」两条，UNC 只在行首或空白、引号、括号之后起算（CJK 路径串里的转义分隔符不算 UNC）——第六轮冷读指出 UNC 正则多转义一层后实测修，七例 + 四例自测通过。

- `dsh-kbhub` 支持 `box-map.json`／`KBHUB_BOX_MAP`：别人的库箱目录名不叫「主对话／课表」时不用改代码，配一份映射即可（默认仍用参考实现的中文映射）。

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
