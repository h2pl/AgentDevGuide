# 视觉 AI 实战与成本优化

> API 调通了只是开始。把视觉 AI 跑在生产环境里，你需要面对分辨率怎么选、Token 怎么算、缓存怎么用、成本怎么控——这篇文章把整个链路的工程经验和成本账一次性算清楚。

## 目录

- [分辨率策略：不是越高越好](#分辨率策略不是越高越好)
- [Token 计算：一张图值多少字](#token-计算一张图值多少字)
- [缓存策略：省大钱的隐藏操作](#缓存策略省大钱的隐藏操作)
- [模型路由：小模型先筛，大模型精判](#模型路由小模型先筛大模型精判)
- [批量处理：异步化降低延迟](#批量处理异步化降低延迟)
- [完整实战：搭建一个视觉审查流水线](#完整实战搭建一个视觉审查流水线)
- [成本模型：不同规模的实际账单](#成本模型不同规模的实际账单)
- [总结](#总结)
- [参考链接](#参考链接)

你好，我是江小湖。这一章从 CLIP 讲到 GPT-4o，从视频讲到文档——现在把所有这些理论落地。看完这篇，你就能把视觉 AI 真的跑在生产环境里，并且知道每分钱花在哪里。

## 分辨率策略：不是越高越好

视觉 API 的分辨率设置直接影响两个东西：**精度和成本**。而且它们的关系不是线性的。

### OpenAI 的分辨率档位

| 档位 | 设置 | 每张图 Token 数 | 适用场景 |
|------|------|:--:|------|
| **low** | 512×512 | 85 | 简单物体识别、颜色判断、快速扫描 |
| **high (默认)** | 自适应（最长边≤2048） | 170-1105 | 文档阅读、图表分析、UI 审查 |
| **high (细节)** | 手动指定高分辨率 | 自定义 Tile 数 | OCR、小字、精细图表 |

```python
# 控制分辨率的三种方式
response_low = client.chat.completions.create(
    model="gpt-4o",
    messages=[{
        "role": "user",
        "content": [{
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{image_base64}",
                "detail": "low"  # 85 Token，成本最低
            }
        }]
    }]
)

response_high = client.chat.completions.create(
    model="gpt-4o",
    messages=[{
        "role": "user",
        "content": [{
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{image_base64}",
                "detail": "high"  # 默认，按图片尺寸自动算 Token
            }
        }]
    }]
)
```

### 分辨率选择的实战法则

```
你的需求：
  只是判断"图里有没有猫"？
    → low (85 Token)，精度 ≥ 95%
  
  在文档里找特定段落？
    → high (约500 Token)，能读到12pt字体
  
  提取财务表格里每个单元格的精确数值？
    → high + 确保原始图片清晰度够 (300dpi 扫描)
  
  10 张产品图快速分类？
    → low (85×10=850 Token)，分类任务不需要高分辨率
```

**关键经验**：大多数产品的默认 high 设置是合理的。low 只在简单识别场景下用，比 high 省约 5-10 倍成本但丢掉的细节在复杂场景里不可接受。

## Token 计算：一张图值多少字

视觉 API 的计费不是按"一张图"计，是按 Token 计。理解这个换算，你才知道钱花在哪。

### OpenAI 的图片 Token 计算公式

```
high 模式下，OpenAI 的计算逻辑：

1. 先把图片缩放到 fit 2048×2048
2. 再缩放到短边 768px
3. 切分成 512×512 的 Tile
4. 每个 Tile = 170 Token
5. 基础开销 = 85 Token
6. 总 Token = 85 + (Tile数 × 170)
```

例子：

| 原始图片 | 处理后尺寸 | Tile 数 | Token 数 |
|---------|-----------|:--:|:--:|
| 512×512 | 512×512 | 1 | 255 |
| 1024×1024 | 1024×1024 | 4 | 765 |
| 1920×1080 | 1920×1080 | 8 | 1445 |
| 4K 图片 | 2048×2048 (上限) | 16 | 2805 |

**要点**：一张 4K 图片 2805 Token，GPT-4o 的输入价格 $2.50/1M Token，一次调用成本 = 2805/1M × $2.50 ≈ **$0.007**。很便宜，但一天 1 万次调用就是 $70。

### 多图片的成本叠加

```python
# 一次调用传了 5 张高清图片
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{
        "role": "user",
        "content": [
            {"type": "text", "text": "对比这5张产品图的差异"},
            *[{"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img}"}, "detail": "high"}
              for img in five_images]
        ]
    }]
)
# 5 张 high 模式图 ≈ 5 × 1100 = 5500 Token + 文字 Token
# 成本 ≈ 5500/1M × $2.50 ≈ $0.014
```

## 缓存策略：省大钱的隐藏操作

视觉 API 的 Prompt Caching 和文本场景一样能省大钱——一张固定的系统图（如品牌 Logo、固定的参考图）可以被缓存。

### 哪些适合缓存

- **固定的参考图片**：每次请求都传的"标准对比图"或商标检测参考图
- **长的系统提示词**：相同的图片分析指令在每次请求中复用
- **模板化的 Prompt 前缀**：标准的图片分析流程描述

```python
# 使用缓存减少重复图片上传
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {
            "role": "system",
            "content": [
                {"type": "text", "text": "你是UI审查专家，以以下标准设计稿为参考基准。"},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{reference_design}"}, "detail": "high"}
            ]
            # 这段 system message 会在多次调用中被缓存
        },
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "对比这个实际实现的截图和参考设计稿的差异"},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{actual_screenshot}"}, "detail": "high"}
            ]
        }
    ]
)
# 参考设计图在多次调用中只计一次费，后续调用享受 50% 折扣
```

### 缓存的收益

对于每天重复处理相似类型图片的场景（如电商商品审核、UI 设计审查、文档格式检查），合理使用缓存可以将视觉 API 成本降低 30-50%。

## 模型路由：小模型先筛，大模型精判

不是每张图都需要 GPT-4o 的推理能力。很多图片只需要简单的"有/没有""是/不是"判断。

```python
class SmartVisionRouter:
    """智能路由：小模型快速筛选 + 大模型深度分析"""

    def __init__(self):
        self.fast_model = "gpt-4o-mini"   # $0.15/1M Token — 便宜
        self.power_model = "gpt-4o"        # $2.50/1M Token — 贵但强

    def analyze(self, image, task):
        """根据任务复杂度自动分流"""

        # 简单任务：直接用小模型
        if self._is_simple_task(task):
            return self._call_model(self.fast_model, image, task)

        # 复杂任务：先让小模型预判，必要时升级
        pre_result = self._call_model(
            self.fast_model, image,
            f"快速判断：{task}。如果不确定，回答 UNCERTAIN。"
        )

        if "UNCERTAIN" in pre_result or self._needs_deep_analysis(task):
            return self._call_model(self.power_model, image, task)

        return pre_result

    def _is_simple_task(self, task):
        simple_patterns = ["识别", "分类", "有/没有", "是不是", "几个"]
        return any(p in task for p in simple_patterns)

# 使用
router = SmartVisionRouter()

# 简单任务 → 自动用小模型
result = router.analyze(image, "这张图里有二维码吗？")
# 成本: ~$0.0001 (mini) vs ~$0.002 (4o)，节省 20 倍

# 复杂任务 → 用小模型预判，必要时升级
result = router.analyze(image, "分析这张财报的趋势并指出风险点")
# 小模型预判成本 ~$0.0005，确认复杂后升级到大模型 ~$0.005
# 总共 ~$0.0055，比直接大模型 ~$0.01 节省约 45%
```

### 模型路由的适用条件

| 条件 | 路由策略 | 节省幅度 |
|------|---------|:--:|
| 80% 的图片是简单识别 | mini → 不确定才转 4o | 60-70% |
| 50% 简单 50% 复杂 | mini 预判 + 分级 | 30-45% |
| 全部需要复杂推理 | 直接用 4o，不路由 | 0% |

## 批量处理：异步化降低延迟

视觉 API 的推理延迟比文本高很多（一张图的处理时间约 1-3 秒）。批处理场景下，同步处理是性能杀手。

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor
from openai import AsyncOpenAI

async_client = AsyncOpenAI()

async def analyze_image_async(client, image, task):
    """单个图片的异步分析"""
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{
            "role": "user",
            "content": [
                {"type": "image_url", "image_url": {"url": image}},
                {"type": "text", "text": task}
            ]
        }]
    )
    return response.choices[0].message.content

async def batch_analyze(images, task, max_concurrent=10):
    """批量异步处理"""
    semaphore = asyncio.Semaphore(max_concurrent)  # 控制并发

    async def bounded_analyze(image):
        async with semaphore:
            return await analyze_image_async(async_client, image, task)

    tasks = [bounded_analyze(img) for img in images]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return results

# 使用
images = load_100_product_images()
results = asyncio.run(batch_analyze(images, "这个商品图片是否包含违禁内容？"))

# 同步处理 100 张图 ≈ 100 × 2s = 200s
# 异步并发 10 ≈ 100/10 × 2s = 20s，加速 10 倍
```

## 完整实战：搭建一个视觉审查流水线

把一个前文讲的所有优化策略整合到一个生产级流水线里：

```python
class ProductionVisionPipeline:
    """生产级视觉审查流水线"""

    def __init__(self):
        self.cheap_model = "gpt-4o-mini"
        self.strong_model = "gpt-4o"
        self.reference_image = load_base64("reference_design.png")
        self.cache = {}

    async def review_ui_screenshots(self, screenshots, rules):
        """审查一批UI截图"""
        results = []

        for screenshot in screenshots:
            # 第一步：低分辨率预检（low模式，85 Token）
            precheck = await self._call_vision(
                self.cheap_model, screenshot,
                "这个截图是否明显违反UI规范或有布局崩溃？只需回答YES/NO。",
                detail="low"  # 省钱
            )

            if "NO" in precheck:
                # 没明显问题，跳过深度检查
                results.append({"status": "pass", "method": "fast_precheck"})
                continue

            # 第二步：高分辨率深度分析（high模式，~1100 Token）
            # 用缓存的参考设计图为基准
            detailed = await self._call_vision(
                self.strong_model, screenshot,
                f"对比参考设计图，详细列出所有差异。审查规则：{rules}",
                detail="high",
                system_image=self.reference_image  # 这张参考图被缓存
            )

            results.append({
                "status": "issues_found" if "差异" in detailed else "pass",
                "method": "deep_analysis",
                "details": detailed
            })

        return results

    async def _call_vision(self, model, image, prompt, detail="high", system_image=None):
        """统一的视觉API调用"""
        content = [{"type": "text", "text": prompt}]
        content.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/png;base64,{image}", "detail": detail}
        })

        messages = []
        if system_image:
            messages.append({
                "role": "system",
                "content": [{"type": "image_url", "image_url": {"url": system_image}}]
            })
        messages.append({"role": "user", "content": content})

        response = await async_client.chat.completions.create(
            model=model, messages=messages
        )
        return response.choices[0].message.content
```

### 这个流水线同时用了四种优化

1. **分辨率分级**：预检用 low (85 Token)，深度分析用 high (~1100 Token)
2. **模型路由**：预检用 mini，有问题的才送 4o
3. **缓存**：参考设计图在多次调用中只计一次费
4. **异步并发**：多个截图并行处理

## 成本模型：不同规模的实际账单

### 场景一：轻量使用（个人开发者）

```
每天 50 张图片分析，GPT-4o-mini (high模式)
每张图 ~500 Token × 50 = 25,000 Token/天
月成本 = 25,000 × 30 / 1,000,000 × $0.15
        ≈ $0.11/月
加上文字对话 ≈ $1-3/月
```

### 场景二：中型产品（SaaS 创业）

```
每天 5000 张图片分析
90% 简单任务 → mini (low模式)：4500 × 85 Token = 382,500 Token
10% 复杂任务 → 4o (high模式)：500 × 1100 Token = 550,000 Token
月成本 = (382.5K + 550K) × 30 / 1M × $0.15/2.50
        = 11.475M × $0.15/1M + 16.5M × $2.50/1M
        = $1.72 + $41.25
        ≈ $43/月
```

### 场景三：大规模（企业级）

```
每天 100,000 张图片处理
使用混合路由 + 缓存优化
缓存命中率估计 40% → 相当于只处理 60,000 张
月成本 ≈ 60,000 × 30 × 500 Token / 1M × $0.20 (混合均价)
        ≈ $180/月（有缓存时）
        ≈ $300/月（无缓存时）
```

## 总结

- **分辨率不是越高越好**——判断"有没有猫"用 low、读财务报表用 high、OCR 关键信息用 high+高DPI源图
- **图片 Token 计算公式**：85 + (Tile数 × 170)，一张 4K 图约 2805 Token ≈ $0.007/次
- **缓存是最大的省钱利器**——固定的参考图和系统 Prompt 在重复调用中享受 50% 折扣
- **模型路由是最智能的省钱策略**——小模型预筛 + 大模型精判，在 80% 简单场景下节省 60-70%
- **异步批量处理**：10 并发可以将 100 张图的处理从 200 秒降到 20 秒
- **个人开发者月费 < $5，SaaS 产品约 $50/月，企业级数百美元/月**——视觉 AI 的成本已经不构成推广障碍
- 03 章全部结束。下一章从理解转向交互：[04 语音交互](../04-speech-interaction/README.md) —— AI 怎么听、怎么说

## 参考链接

- [OpenAI Vision API 定价](https://openai.com/api/pricing/)
- [OpenAI Prompt Caching 文档](https://platform.openai.com/docs/guides/prompt-caching)
- [OpenAI 图片 Token 计算说明](https://platform.openai.com/docs/guides/vision/calculating-costs)
- [Google Gemini 定价](https://ai.google.dev/pricing)
- [Anthropic Claude 定价](https://www.anthropic.com/pricing)

> 视觉 AI 的实践指南全部讲完。从 CLIP 到 GPT-4o 的技术演进、从 API 调用到生产部署的工程经验——你现在有了把视觉 AI 真正落地的完整能力栈。下一篇转入语音交互专题：[04 语音交互](../04-speech-interaction/README.md)。
