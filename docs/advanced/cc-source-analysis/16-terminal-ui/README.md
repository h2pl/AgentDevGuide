# 16 — 终端 UI 框架

## 核心问题
Claude Code 如何用 React + Ink 渲染终端 UI？自研 TUI 框架有什么独特设计？

## 关键源码
- `src/ink/` — 96 文件，自研 Ink 框架
- `src/components/` — 389 文件，React 组件
- `src/hooks/` — 104 文件，React hooks
- `src/screens/` — 界面屏幕

## 主要内容

### 1. 为什么用 React 渲染终端
- 终端不是文本输出，是前端容器
- React 组件化：状态驱动 UI
- Ink：React 到终端的渲染器
- 支持动画、焦点管理、键盘交互

### 2. 自研 Ink 框架
- 基于 Yoga（Facebook 的 Flexbox 引擎）
- 支持 CSS 布局（flex、padding、margin）
- 纯 TypeScript 实现（无 native 依赖）
- 终端渲染优化（增量更新）

### 3. 核心组件树
```
<App>
  ├── <Header>          — 状态栏（模型、token、成本）
  ├── <MessageList>     — 消息列表
  │   ├── <UserMessage>
  │   ├── <AssistantMessage>
  │   └── <ToolMessage>
  ├── <InputBar>        — 输入框
  ├── <PermissionDialog> — 权限确认
  └── <Footer>          — 帮助信息
</App>
```

### 4. 焦点与动画系统
- 焦点管理：Tab 切换、键盘导航
- 动画：进度条、加载状态、过渡效果
- 终端重绘优化（避免闪烁）

### 5. 键盘快捷键
- Vim 模式支持（/vim 命令）
- 自定义快捷键（/keybindings）
- 全局快捷键 vs 上下文快捷键

### 6. 多端适配
- 终端宽度自适应
- 颜色主题（/theme）
- 无障碍支持

## 学习目标
- 理解 React + Ink 的设计
- 掌握终端 UI 的工程挑战
- 明白为什么"终端不是文本输出"
