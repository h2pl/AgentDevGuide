# 成本建模与优化

> 多模态 API 的成本是纯文本的 10-100 倍。一张图的处理可能花掉你半本书的 Token。本文给你一套完整的成本建模框架和优化策略——让你在精度和预算之间找到最优平衡点。

## 目录

- [多模态的成本结构](#多模态的成本结构)
- [延迟预算：用户愿意等多久](#延迟预算用户愿意等多久)
- [模型路由：小模型先筛大模型精判](#模型路由小模型先筛大模型精判)
- [缓存优化](#缓存优化)
- [预算管控框架](#预算管控框架)
- [优化清单](#优化清单)
- [总结](#总结)

你好，我是江小湖。前面讲了评估和 RAG，这两件事都在烧钱——评估跑 Benchmark 要钱，RAG 的每次检索要钱。不控成本，你的多模态应用可能上线第一个月就收到一张让你血压升高的账单。

## 多模态的成本结构

### Token ≠ Token

一个需要刻进脑子里的公式：**一张高清图片 ≈ 1000+ Token ≈ 一段 500 字的文字。**

```
纯文本请求：2000 Token 输入 + 500 Token 输出 = 2500 Token
    GPT-4o: $2.50/1M → $0.006
    GPT-4o-mini: $0.15/1M → $0.0004

带一张高清图片：2805 Token（图）+ 500 Token（文字）= 3305 Token
    GPT-4o: $2.50/1M → $0.008
    GPT-4o-mini: $0.15/1M → $0.0005

带视频（抽帧16张）：16 × 500 + 500 = 8500 Token
    GPT-4o: $2.50/1M → $0.02
    Gemini Flash: $0.075/1M → $0.0006
```

看起来单次成本很小。但一天 1 万次图片分析就是 $80（GPT-4o）或 $5（mini）。一个月 $2400 vs $150。

### 各模态的成本权重

| 模态 | 典型Token消耗 | 相对文本成本 |
|------|:--:|:--:|
| 纯文字（2000 Token） | 2000 | 1× |
| 低分辨率图（low模式） | 85 | 0.04× |
| 标准图片（1024×1024） | 765 | 0.4× |
| 高分辨率图（4K） | 2805 | 1.4× |
| 5张标准图片 | 3825 | 1.9× |
| 视频（抽样16帧） | ~8000 | 4× |
| 视频（Gemini原生，5分钟） | ~50000 | 25× |

### 用户画像的成本预估

```
轻量用户（每天 10 次图片分析 + 文字对话）
  GPT-4o: 10 × 2805 × 30 / 1M × $2.50 ≈ $2.10/月
  GPT-4o-mini: 10 × 2805 × 30 / 1M × $0.15 ≈ $0.13/月

中度用户（每天 100 次图片分析）
  GPT-4o: 100 × 2805 × 30 / 1M × $2.50 ≈ $21/月
  建议：90% mini + 10% 4o ≈ $2/月

重度用户（每天 100次图片 + 50次视频分析）
  GPT-4o: ≈ $300-500/月
  必须：模型路由 + 缓存 + 分辨率分级
```

## 延迟预算：用户愿意等多久

成本优化的目标是降低花费，但同时不能把用户体验搞崩。延迟预算是总优化约束。

```
用户可接受的延迟预算：
  实时对话：< 1 秒（语音助手的硬约束）
  聊天应用：< 3 秒（用户感觉"即时的"）
  分析工具：< 10 秒（用户看着进度条可以等）
  批量处理：> 10 秒（后台运行，不实时反馈）

各模态的处理延迟：
  纯文本 2000 Token：0.5-1 秒
  图片理解（标准大小）：1-3 秒
  视频理解（抽帧16帧）：5-15 秒
  视频理解（Gemini原生）：10-60 秒
```

延迟预算决定你能用多大的模型和高分辨率。实时语音助手只能用 GPT-4o-mini 或专门的快速模型。分析工具可以用 GPT-4o + high 分辨率慢慢处理。

## 模型路由：小模型先筛大模型精判

这是成本优化最有效的策略。原理很简单：大部分图片不需要最强模型的处理能力。

### 路由决策树

```
输入请求
    ↓
[简单任务？]
  ├── 物体识别、颜色判断、数量统计 → mini (成本 1/16)
  ├── 文字提取、简单问答 → mini + high分辨率 (成本 1/8)
  └── [需求复杂？]
        ├── mini预判 "如果回答不了就标记"
        ├── 标记了 → 升级到 GPT-4o (仅 20% 的请求)
        └── 没标记 → 返回 mini 的结果
```

```python
class CostOptimizedRouter:
    def __init__(self, budget_per_day=5.0):
        self.cheap = GPT4oMini()  # $0.15/1M
        self.strong = GPT4o()     # $2.50/1M
        self.budget = budget_per_day
        self.daily_cost = 0
    
    def route(self, image, task):
        if self.daily_cost > self.budget:
            return self.cheap.analyze(image, task)  # 超预算，全用小模型
        
        # 简单任务
        if self._is_simple(task):
            return self.cheap.analyze(image, task)
        
        # 小模型预判
        precheck = self.cheap.analyze(image, 
            f"快速判断：你能准确回答'{task}'吗？能就回答，不能就说 NEED_BETTER_MODEL。"
        )
        
        if "NEED_BETTER_MODEL" in precheck:
            return self.strong.analyze(image, task)
        
        return precheck
    
    def _is_simple(self, task):
        return any(kw in task for kw in [
            "是什么", "有没有", "是不是", "几个", "识别", "分类"
        ])
```

### 路由效果预估

```
场景：每天 1000 次图片分析，80% 简单 + 20% 复杂

全部用 GPT-4o: 1000 × 2805 / 1M × $2.50 = $7.01/天
路由优化后: 800 × mini + 200 × 4o
  = 800 × 2805 / 1M × $0.15 + 200 × 2805 / 1M × $2.50
  = $0.34 + $1.40 = $1.74/天

节省: ($7.01 - $1.74) / $7.01 = 75%
```

## 缓存优化

### 两种缓存维度

**Prompt 缓存**。相同的系统提示和参考图片在多次请求中只计一次费：

```python
# 每次请求都传同一张品牌 Logo 和设计规范
# 不使用缓存：每次请求都计费
# 使用缓存：第一次全额计费，后续 50% 折扣

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": [
            {"type": "text", "text": "你是UI审查专家"},
            {"type": "image_url", "image_url": brand_logo}  # 被缓存
        ]},
        {"role": "user", "content": [...]}
    ]
)
# 1000 次请求：首次 1× Logo + 999 次 × 0.5× Logo = 节省约 50%
```

**结果缓存**。相同的图片+相同的问题 → 直接返回缓存结果：

```python
cache = {}

def analyze_with_cache(image_hash, task):
    cache_key = f"{image_hash}:{hash(task)}"
    
    if cache_key in cache:
        return cache[cache_key]  # 命中缓存，零成本
    
    result = llm.analyze(image, task)
    cache[cache_key] = result
    return result
```

## 预算管控框架

### 日预算与熔断

```python
class BudgetController:
    def __init__(self, daily_budget=10.0, alert_threshold=0.8):
        self.budget = daily_budget
        self.alert = alert_threshold
        self.daily_spending = 0
        self.resets_at = datetime.now() + timedelta(days=1)
    
    def check_and_charge(self, estimated_cost):
        if self.daily_spending + estimated_cost > self.budget:
            if self.daily_spending < self.budget * self.alert:
                # 还没到告警线就开始熔断 → 可能有问题
                raise BudgetExceededError(
                    f"异常: 预算 {self.budget} 即将耗尽"
                )
            else:
                raise BudgetExceededError(
                    f"今日预算 {self.budget} 已用完"
                )
        
        self.daily_spending += estimated_cost
    
    def estimate_cost(self, model, images, text_tokens=500):
        image_cost = sum(
            self._image_token_cost(img, model) for img in images
        )
        text_cost = text_tokens * model.price_per_1M_input / 1_000_000
        return image_cost + text_cost
```

### 分级预算策略

| 优先级 | 用哪个模型 | 预算占比 | 典型场景 |
|:--:|------|:--:|------|
| P0 关键 | GPT-4o + high分辨率 | 30% | 财报分析、合同审查 |
| P1 重要 | GPT-4o + standard | 40% | 产品图片审核、UI审查 |
| P2 常规 | GPT-4o-mini | 25% | 分类、标签、简单问答 |
| P3 低优 | 批量异步 | 5% | 历史数据回填 |

## 优化清单

| 优化策略 | 节省幅度 | 实施难度 | 推荐优先级 |
|---------|:--:|:--:|:--:|
| 模型路由 | 60-75% | 中 | ⭐⭐⭐⭐⭐ |
| Prompt 缓存 | 30-50% | 低 | ⭐⭐⭐⭐⭐ |
| low 分辨率（简单任务） | 50-80% | 低 | ⭐⭐⭐⭐ |
| 异步批量处理 | 0% (只降延迟) | 中 | ⭐⭐⭐⭐ |
| 结果缓存 | 20-40% | 低 | ⭐⭐⭐⭐ |
| 本地部署小模型 | 90%+ (高频时) | 高 | ⭐⭐⭐ |

## 总结

- 多模态 API 成本是纯文本的 **10-100 倍**——一张高清图 = 2805 Token = 一段长文章
- **模型路由是最有效的优化**——80% 简单任务用 mini，总成本降低 60-75%
- Prompt 缓存和结果缓存在重复调用场景能节省 20-50%
- **预算管控要设熔断**——避免一个 bug 循环的 API 调用刷爆账单
- 轻量用户月费 < $5，中度用户 < $50，重度用户必须实施全套优化
- 下一篇：[生产部署与监控](./04-deployment-monitoring.md)

## 参考链接

- [OpenAI 定价](https://openai.com/api/pricing/)
- [Google Gemini 定价](https://ai.google.dev/pricing)
- [Anthropic 定价](https://www.anthropic.com/pricing)
- [OpenAI Prompt Caching 文档](https://platform.openai.com/docs/guides/prompt-caching)
