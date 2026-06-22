# 06 — 系统提示词

Claude Code 的系统提示词不是静态字符串，而是由数百个碎片动态拼装而成。本章拆解模块化组装、缓存冻结和 CLAUDE.md 的特殊地位。

## 目录

| # | 文章 | 内容 |
|---|------|------|
| 01 | [动态拼装](./01-dynamic-assembly.md) | `prompts.ts`、基础指令、安全守则、工具描述、用户偏好 |
| 02 | [缓存冻结](./02-cache-freezing.md) | DYNAMIC_BOUNDARY、静态区 vs 动态区、最大化 Cache 命中率 |
| 03 | [CLAUDE.md 与安全守则](./03-claude-md.md) | CLAUDE.md 永不删除特权、5677 token 安全守则、模式特定规则 |

> 学完本章后，请继续阅读 [07 — 上下文工程](../07-context-engineering/README.md)，看 5 层压缩机制如何管理 200K 上下文窗口。
