# 07 — 上下文工程

## 核心问题
Claude Code 的 5 层压缩机制如何工作？CLAUDE.md 为何永不删除？

## 关键源码
- `src/services/compact/compact.ts` (1581 行) — 主压缩逻辑
- `src/services/compact/autoCompact.ts` (313 行) — 自动压缩
- `src/services/compact/microCompact.ts` (480 行) — 微压缩
- `src/services/compact/contextCollapse.ts` — 上下文折叠
- `src/services/compact/snipCompact.ts` — 历史片段删除

## 主要内容

### 1. 5 层压缩机制（从便宜到贵）
| 层次 | 触发条件 | 操作粒度 | 成本 |
|------|---------|---------|------|
| Budget reduction | 每轮检查 | 削减工具输出预览 | 最低 |
| Snip | HISTORY_SNIP flag | 删除中间历史片段 | 低 |
| Microcompact | 每轮检查 | 压缩特定段落 | 中 |
| Context collapse | CONTEXT_COLLAPSE flag | 细粒度折叠+还原 | 高 |
| Auto-compact | token > 阈值 | 全对话压缩为摘要 | 最高 |

### 2. 关键阈值配置
```typescript
AUTOCOMPACT_BUFFER_TOKENS = 13000;        // 触发前留白
MAX_OUTPUT_TOKENS_FOR_SUMMARY = 20000;    // p99.99 摘要长度
MAX_CONSECUTIVE_AUTOCOMPACT_FAILURES = 3; // 连续失败熔断
```

### 3. 熔断机制
- BQ 2026-03-10 数据：1,279 sessions 有 50+ 连续失败
- 最多浪费 ~250K API calls/day globally
- MAX_CONSECUTIVE_AUTOCOMPACT_FAILURES = 3 防止死循环

### 4. CLAUDE.md 永不删除
```typescript
// CLAUDE.md 不在内存里，每次从磁盘重新读取
// 压缩时不会被删除
// 这是架构层面的特权，不是功能设计
```

### 5. Reactive Compact（API 413 兜底）
- 收到 prompt_too_long 错误时被动触发
- 先尝试 collapse drain
- 失败再走 full compact

### 6. Token Budget 管理
- 跨 compact 追踪 taskBudgetRemaining
- 防止压缩后超预算

## 学习目标
- 理解 5 层压缩的设计哲学
- 掌握关键阈值的工程意义
- 明白 CLAUDE.md 的特殊地位
