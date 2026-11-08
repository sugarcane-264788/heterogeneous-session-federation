# skills：七个工作法的可执行版

这里放 `使用指南.md` L1 那七个工作法的原文。每份是一份 `SKILL.md`，可以直接当提示词交给会读写文件的 agent；文件头的 `name`／`description` 是给支持 skills 机制的宿主用的，手工使用时看正文即可。

| 工作法 | 文件 | 一句话 |
|---|---|---|
| 接手交接 | `skills/session-handoff/SKILL.md` | 新会话进场先交接：三十秒清单＋真会话演练，卡住＝没接上 |
| 留痕记账 | `skills/card-ledger-workflow/SKILL.md` | 改共用库前先写卡，改完记台账，收尾七连 |
| 四层自检 | `skills/layered-self-check/SKILL.md` | 结构、一致性、机器层、真会话演练，外加假 FAIL 判读 |
| 委派子代理 | `skills/delegate-and-reclaim/SKILL.md` | 审计先派子代理、只回结论，干完回收会话 |
| 人机双轨 | `skills/human-machine-dual-track/SKILL.md` | 人读 md、机读薄快照，生成物不手改，doctor 对账 |
| 提案门槛 | `skills/proposal-gate/SKILL.md` | 加机制前先说「现在哪里会疼」，被否的进否决账 |
| 多会话协作 | `skills/multi-session-workspace/SKILL.md` | 格子分开、一箱一条线、名册记谁是谁 |

这些文件是从一个真跑过十七天的库里抽出来的，例子里的 `<工作区根>`、`<DSH_HOME>`、`session-<id 前缀>` 都是占位符，照自己的环境替换。

**一句话前提**：七份 SKILL.md 是**完整库**里的原文，里面 `..\工具\…`（体检、台账、索引那套脚本）、`00-规范\…`、`40-协作\_模板\…` 指的都不是这个发布包。发布包只有 `starter/mailbox_min.py` 这一件可执行物，最小等价做法：

| SKILL 里的命令 | 只有发布包时用什么 |
|---|---|
| `python ..\工具\kb\kb_check.py`（全库体检） | `python starter/mailbox_min.py --selftest`（只验信箱能跑） |
| `python ..\工具\mailbox\mailbox.py digest --for <箱>` | `python starter/mailbox_min.py digest --for <箱>` |
| `python ..\工具\kb\read_state.py --me …`（认自己） | 在你自己的名册 md 里查自己那一行 |
| `verify --card`／`ledger add` | 先按 SKILL 里的表格手工记（路径／字节／sha256），脚本等你把库长起来再加 |

读法不变：把它们当规矩照做，遇到命令换成上面这一列即可。

## 用法

- **有 skills 机制的宿主**（如 DSH）：把 `skills/` 整个目录丢进宿主的 skills 路径，它会按 `description` 自动召回。
- **没有 skills 机制的宿主**：挑要用的那份，把正文整段贴进会话开头，当规矩执行。
- 两份以上同时用就先读 `session-handoff`——它是其它六份的入口。
