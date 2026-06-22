# 14 — 设计哲学

## 核心问题
Claude Code 的 5 大价值观和 13 条设计原则是什么？Undercover Mode 是什么？

## 关键源码
- 全局设计理念（贯穿所有模块）
- `src/constants/` — 常量定义
- 代码注释中的设计思考

## 主要内容

### 1. 5 大价值观
| 价值观 | 核心含义 |
|--------|---------|
| Human Decision Authority | 人类保有最终决策权 |
| Safety, Security & Privacy | 即使用户疏忽也要保护 |
| Reliable Execution | 跨会话保持连贯 |
| Capability Amplification | 27% 的任务是"没有工具就不会尝试" |
| Contextual Adaptability | 系统适配用户项目/工具/惯例 |

### 2. 13 条设计原则
| # | 原则 | 服务的价值观 |
|---|------|------------|
| 1 | Deny-first with human escalation | 权威、安全 |
| 2 | Graduated trust spectrum | 权威、适应性 |
| 3 | Defense in depth | 安全、权威、可靠 |
| 4 | Externalized programmable policy | 安全、权威、适应性 |
| 5 | Context as scarce resource | 可靠、能力 |
| 6 | Append-only durable state | 可靠、权威 |
| 7 | Minimal scaffolding, maximal harness | 能力、可靠 |
| 8 | Values over rules | 能力、权威 |
| 9 | Composable multi-mechanism extensibility | 能力、适应性 |
| 10 | Reversibility-weighted risk | 能力、安全 |
| 11 | Transparent file-based config & memory | 适应性、权威 |
| 12 | Isolated subagent boundaries | 安全、可靠 |
| 13 | Observable by default | 可靠、适应性 |

### 3. Undercover Mode（卧底模式）
```typescript
// 隐藏内部代号
// process.env.USER_TYPE === 'ant' 时有特殊分支
// ANT 版有更严格的注释规范、报告规范
// 外部包完全看不到 ANT 分支
// 通过构建时 --define 注入
```

### 4. 监督悖论
- Anthropic 自己的调查发现了"监督悖论"
- 过度依赖 AI 可能侵蚀监督所需的技能
- 独立研究发现 AI 辅助条件下开发者理解测试得分低 17%

### 5. 设计原则到技术实现的映射
```
价值观 → 设计原则 → 具体实现
例如：
Safety → Defense in depth → 三层权限检查
Reliable → Append-only → 会话持久化
Capability → Minimal scaffolding → 88 行 while 循环
```

## 学习目标
- 理解 5 大价值观的内涵
- 掌握 13 条设计原则
- 明白 Undercover Mode 的设计意图
