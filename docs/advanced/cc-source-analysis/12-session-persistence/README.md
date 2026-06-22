# 12 — 会话持久化

## 核心问题
Claude Code 如何实现断点续传？checkpoint 机制如何工作？

## 关键源码
- `src/state/AppState.tsx` — 应用状态
- `src/state/AppStateStore.ts` — 状态存储
- `src/state/store.ts` — Zustand 风格 store
- `src/tasks/` — 任务持久化

## 主要内容

### 1. append-only 设计
```typescript
// 会话历史只追加，不修改
// 类似事件溯源（Event Sourcing）
// 可以回放任意时刻的状态
// 支持断点续传
```

### 2. checkpoint 机制
```typescript
// 定期保存检查点
// 包含：消息历史、工具状态、上下文摘要
// 崩溃后可以从最近的 checkpoint 恢复
```

### 3. resume 完整流程
```typescript
// 1. 检测是否有未完成的会话
// 2. 加载最近的 checkpoint
// 3. 恢复消息历史
// 4. 恢复工具状态
// 5. 继续执行
```

### 4. 状态管理架构
```typescript
// Zustand 风格 store
// 不可变 AppState
// 单向数据流
// 状态变更可追踪
```

### 5. 会话存储格式
```typescript
// ~/.claude/sessions/
// 每个会话一个目录
// 包含：messages.json、state.json、checkpoint.json
// 人类可读（JSON 格式）
```

### 6. 长任务续航
```typescript
// 支持跨天、跨周的长任务
// 定期保存进度
// 可以随时暂停、恢复
// 不会因为崩溃丢失进度
```

## 学习目标
- 理解 append-only 设计的优势
- 掌握 checkpoint 的工程意义
- 明白长任务续航的实现
