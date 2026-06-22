# 06 — 系统提示词

CC 系统提示词的组装流程——systemPrompt.ts 与 constants/prompts.ts，前缀缓存冻结策略与 SYSTEM_PROMPT_DYNAMIC_BOUNDARY 设计。

## 目录

| # | 文章 | 内容 |
|---|------|------|
| 01 | [系统提示词源码分析](./01-system-prompt-source.md) | 提示组装流程、前缀缓存冻结、动态边界策略 |

## 涉及源码

- `systemPrompt.ts`
- `constants/prompts.ts`

## 对应理论章节

> [04 — 提示词工程](../../../04-prompt-engineering/README.md) — 系统提示词是提示词工程的核心应用，决定了 Agent 的行为边界。
