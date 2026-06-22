# 10 — 权限系统

Claude Code 的权限系统有三层防护：注册过滤、调用检查、交互询问。本章拆解 7 种运行模式、8 级优先级和 ML 分类器。

## 目录

| # | 文章 | 内容 |
|---|------|------|
| 01 | [三层防护](./01-three-layers.md) | 注册过滤、调用检查、交互询问 |
| 02 | [7 模式 8 优先级](./02-modes-priority.md) | default/auto/plan 等模式、规则冲突解决 |
| 03 | [ML 分类器与 Bash 安全](./03-ml-classifier.md) | auto 模式分类器、23 项 Bash 检查、18 个屏蔽命令 |

> 学完本章后，请继续阅读 [11 — 扩展机制](../11-extensibility/README.md)，看 Hook/Skill/Plugin/MCP 如何扩展 Agent 能力。
