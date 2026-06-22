# 03 — Agent 循环

## 核心问题
query.ts 的 while(true) 状态机如何驱动 Agent 运行？7 种 transition.reason 分别是什么？

## 关键源码
- `src/query.ts` (1729 行) — 核心循环
- `src/QueryEngine.ts` (1295 行) — 会话引擎
- `src/query/config.ts` — 循环配置
- `src/query/stopHooks.ts` — 停止钩子
- `src/query/tokenBudget.ts` — Token 预算

## 主要内容

### 1. 两层架构分工
- **上层 QueryEngine**：会话级控制器（状态管理、参数组装、持久化）
- **下层 query()**：请求级执行引擎（模型调用、工具执行、错误恢复）

### 2. State 类型定义
```typescript
type State = {
  messages: Message[]                    // 对话历史
  toolUseContext: ToolUseContext         // 工具执行上下文
  autoCompactTracking: ...               // 自动压缩追踪
  maxOutputTokensRecoveryCount: number   // 输出截断恢复计数 (≤3)
  hasAttemptedReactiveCompact: boolean   // 是否尝试过响应式压缩
  turnCount: number                      // 当前轮次
  transition: Continue | undefined       // 上次循环的继续原因
}
```

### 3. 7 种 transition.reason
| 原因 | 触发条件 |
|------|----------|
| next_turn | 正常继续（工具调用后） |
| reactive_compact_retry | 响应式压缩后重试 |
| collapse_drain_retry | 上下文折叠后重试 |
| max_output_tokens_escalate | 输出截断，扩大 max_tokens |
| max_output_tokens_recovery | 输出截断恢复 |
| stop_hook_blocking | Stop Hook 阻塞 |
| token_budget_continuation | Token 预算续行 |

### 4. 消息预处理流水线（5 步）
1. applyToolResultBudget — 削减工具输出预览
2. snip — 删除中间历史片段
3. microcompact — 压缩特定段落
4. contextCollapse — 细粒度折叠+还原
5. autocompact — 全对话压缩为摘要

### 5. Withholding 机制（错误扣留）
- API 返回 prompt_too_long 时，不立即 yield 给调用方
- 先尝试 collapse drain，再 reactive compact
- 两者都失败才释放错误
- 原因：避免 SDK 调用方因中间错误终止会话

### 6. StreamingToolExecutor 并发模型
- 工具 A (isConcurrencySafe=true) → 立即执行
- 工具 B (isConcurrencySafe=true) → 并行执行
- 工具 C (isConcurrencySafe=false) → 等 A、B 完成后串行
- siblingAbortController：Bash 出错时 abort 兄弟进程

## 学习目标
- 理解 while(true) 状态机的设计哲学
- 掌握 7 种 continue 原因的语义
- 明白 Withholding 机制的工程意义
