# 06 — 系统提示词

## 核心问题
Claude Code 的 53KB 系统提示词如何动态组装？缓存冻结策略是什么？

## 关键源码
- `src/constants/prompts.ts` (914 行) — 提示词模板
- `src/constants/systemPromptSections.ts` — 模块化片段
- `src/utils/queryContext.ts` — 上下文装配

## 主要内容

### 1. 模块化组装
```typescript
// 系统提示词 = 数百个碎片动态拼装
systemPrompt = [
  ...getBasePrompt(),           // 基础指令
  ...getSafetyRules(),          // 安全守则（~5677 token）
  ...getToolDescriptions(),     // 工具描述
  ...getProjectContext(),       // 项目上下文（CLAUDE.md）
  ...getModeSpecificRules(),    // 模式特定规则
  ...getUserPreferences(),      // 用户偏好
];
```

### 2. 缓存冻结策略
- **冻结区**：System Prompt 前缀（~50K token）
- **动态区**：用户上下文、工具结果
- 设计目的：最大化 Prompt Cache 命中率

### 3. DYNAMIC_BOUNDARY 概念
```typescript
// 标记动态内容的边界
const DYNAMIC_BOUNDARY = '<!-- DYNAMIC_CONTENT_START -->';
// 边界前的内容可以缓存
// 边界后的内容每次重新计算
```

### 4. 安全守则（5677 token）
- 代码安全规范
- 数据隐私保护
- 权限边界说明
- 危险操作警告

### 5. 模式特定规则
| 模式 | 额外规则 |
|------|---------|
| Plan Mode | 只读，不修改文件 |
| Coordinator Mode | 多 Agent 协调规则 |
| Auto Mode | ML 分类器自动判断 |

### 6. CLAUDE.md 的特殊地位
- 每次从磁盘重新读取（不存内存）
- 享有"永不删除"特权（压缩时保留）
- 社区共识：最重要的规则写在 CLAUDE.md

## 学习目标
- 理解模块化提示词管理的设计
- 掌握缓存冻结的工程意义
- 明白 CLAUDE.md 为何如此重要
