# 15 — CLI 命令系统

## 核心问题
Claude Code 的 40+ slash 命令如何注册与分发？命令生命周期是什么？

## 关键源码
- `src/commands/` — 40+ 命令实现
- `src/commands.ts` — 命令注册中心
- `src/commands/advisor.ts` — 命令顾问
- `src/commands/init.ts` — 初始化命令

## 主要内容

### 1. 命令注册中心
```typescript
// commands.ts 统一管理
// 类似 tools.ts 的设计
// 统一注册、按需加载
// 支持 feature flag 动态开关
```

### 2. 40+ 命令分类
| 类别 | 命令示例 | 数量 |
|------|---------|------|
| 会话管理 | /clear, /compact, /resume | 5 |
| 配置管理 | /config, /model, /permissions | 6 |
| 工具管理 | /mcp, /hooks, /skills, /plugins | 4 |
| 任务管理 | /tasks, /plan, /review | 3 |
| 系统命令 | /doctor, /status, /usage | 5 |
| 其他 | /vim, /voice, /theme, /stickers | 17 |

### 3. 命令生命周期
```typescript
// 1. 解析用户输入（/command args）
// 2. 查找命令注册表
// 3. 执行 PreCommand hooks
// 4. 执行命令逻辑
// 5. 执行 PostCommand hooks
// 6. 通知命令完成
```

### 4. 命令系统不是装饰品
```typescript
// 命令不只是快捷操作
// 是系统能力的暴露
// 是用户控制 Agent 的接口
// 是调试和审计的入口
```

### 5. 命令与工具的协作
```typescript
// 命令可以调用工具
// 工具可以触发命令
// 但职责清晰：
// - 命令：用户主动触发
// - 工具：Agent 自主调用
```

## 学习目标
- 理解命令注册中心的设计
- 掌握命令生命周期
- 明白命令系统的工程意义
