# 05 — LLM 调用层

## 核心问题
Claude Code 如何统一管理 LLM 调用？Sticky-on Latch 如何保护 50-70K token 缓存？

## 关键源码
- `src/services/api/claude.ts` (3212 行) — 统一调用层
- `src/services/api/client.ts` — 客户端管理
- `src/services/api/withRetry.ts` — 重试逻辑
- `src/services/api/errors.ts` — 错误处理

## 主要内容

### 1. 统一调用架构
```typescript
// claude.ts 核心职责
- 流式 SSE 调用
- 重试策略（指数退避）
- Token 用量追踪
- 多模型路由（Opus/Sonnet/Haiku）
- Fallback 模型切换
```

### 2. Prompt Cache 经济学
- Cache Key 包含 7 个维度：
  - System Prompt
  - Tools + Schema
  - Beta Headers
  - Model
  - cache_control (scope/TTL)
  - Fast Mode
  - Effort
- 任一维度变化 → Cache bust → 50-70K token 重新计算

### 3. Sticky-on Latch 机制
```typescript
// state.ts:226-230
// 一旦 Beta Header 被激活，锁定不变
// 直到 /clear 或 /compact 才重置
afkModeHeaderLatched: boolean;
fastModeHeaderLatched: boolean;
```
- 设计目的：保护 Prompt Cache 命中率
- 实现方式：单向锁存器（Latch）概念来自数字电路

### 4. FallbackTriggeredError 回退
```typescript
// 模型调用失败时：
1. 切换到 fallbackModel
2. ANT only：清除 thinking block 签名
3. 创建新的 StreamingToolExecutor（防止孤立 tool_results）
4. 打遥测，yield 系统提示消息
```

### 5. 流式优先设计
- 默认 SSE 流式调用
- 失败时降级为非流式（最多一次）
- 代价：单次输出上限降至 64K tokens

### 6. 多模型路由
| 模型 | 用途 | 特点 |
|------|------|------|
| Opus | 复杂推理 | 最贵，最强 |
| Sonnet | 日常编码 | 性价比最高 |
| Haiku | 简单任务 | 最便宜，最快 |

## 学习目标
- 理解 Prompt Cache 的 7 个维度
- 掌握 Sticky-on Latch 的设计哲学
- 明白 Fallback 机制的工程意义
