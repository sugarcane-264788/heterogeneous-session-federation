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

## 用法

- **有 skills 机制的宿主**（如 DSH）：把 `skills/` 整个目录丢进宿主的 skills 路径，它会按 `description` 自动召回。
- **没有 skills 机制的宿主**：挑要用的那份，把正文整段贴进会话开头，当规矩执行。
- 两份以上同时用就先读 `session-handoff`——它是其它六份的入口。
