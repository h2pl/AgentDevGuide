# 11 — 扩展机制

Claude Code 提供 4 种扩展机制：Hook、Skill、Plugin、MCP，每种有明确的成本分级。本章拆解它们的实现和选型策略。

## 目录

| # | 文章 | 内容 |
|---|------|------|
| 01 | [四种扩展方式对比](./01-extension-types.md) | Hook/Skill/Plugin/MCP 成本与适用场景 |
| 02 | [Skill 系统](./02-skills.md) | Skill 注册、加载、执行、与工具的关系 |
| 03 | [MCP 集成](./03-mcp.md) | MCP Client/Server、工具发现、动态加载 |

> 学完本章后，请继续阅读 [12 — 会话持久化](../12-session-persistence/README.md)，看长任务如何 resume。
