# 02 — 启动流程

## 核心问题
Claude Code 如何在 135ms 内完成冷启动？并行预取策略如何优化启动性能？

## 关键源码
- `src/entrypoints/cli.tsx` — 轻量入口分发
- `src/main.tsx` (4683 行) — 完整启动编排
- `src/entrypoints/init.ts` — 初始化环境
- `src/bootstrap/state.ts` — 全局状态（80+ 字段）

## 主要内容

### 1. Fast-path 分发
```typescript
// cli.tsx — 零导入，12ms 退出
if (args[0] === '--version') {
  console.log(`${MACRO.VERSION} (Claude Code)`);
  return;
}
// 正常路径：全部延迟加载
const { main: cliMain } = await import('../main.js');
```

### 2. 并行预取策略
```typescript
// main.tsx 前 20 行
import { profileCheckpoint } from './utils/startupProfiler.js';
profileCheckpoint('main_tsx_entry'); // 第一行开始计时

import { startMdmRawRead } from './utils/settings/mdm/rawRead.js';
startMdmRawRead(); // 并行：MDM 配置子进程

import { startKeychainPrefetch } from './utils/secureStorage/keychainPrefetch.js';
startKeychainPrefetch(); // 并行：Keychain 预读（节省 65ms）
```

### 3. 五阶段启动流程
1. **模块加载期**：并行预热（MDM、Keychain、GrowthBook）
2. **环境检测**：Node 版本、OS 类型、终端能力
3. **配置加载**：~/.claude/ 用户配置、MDM 托管配置
4. **身份认证**：OAuth 令牌校验、Bedrock/Vertex 凭证
5. **REPL 启动**：launchRepl() 进入交互主循环

### 4. 三种运行模式
| 模式 | 入口 | 特点 |
|------|------|------|
| REPL | claude | 完整 React 应用，有 UI |
| Print | claude -p | 纯函数调用链，无 UI |
| SDK | QueryEngine | Headless，供程序调用 |

### 5. Sticky-on Latch 机制
- 保护 50-70K token 的 Prompt Cache
- 一旦 Beta Header 被激活，锁定不变
- 直到 /clear 或 /compact 才重置

## 学习目标
- 理解 import 语句间插入副作用的优化技巧
- 掌握并行预取的设计思路
- 明白三种运行模式的架构差异
