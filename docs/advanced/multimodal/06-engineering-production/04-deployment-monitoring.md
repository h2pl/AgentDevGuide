# 生产部署与监控

> 前面所有章节学到的能力——视觉理解、语音交互、图像视频生成——如果不部署到线上，只是你笔记本上的 demo。本文把从"能跑"到"能上线"的关键步骤串起来：架构设计、灰度策略、可观测性、fallback 降级、上线 checklist。

## 目录

- [多模态应用的架构模式](#多模态应用的架构模式)
- [灰度发布：别一把梭哈](#灰度发布别一把梭哈)
- [可观测性：你知道线上在发生什么吗](#可观测性你知道线上在发生什么吗)
- [Fallback 策略：当一切出错时](#fallback-策略当一切出错时)
- [上线 Checklist](#上线-checklist)
- [总结](#总结)

你好，我是江小湖。成本控制帮你省下了钱。但省钱的前提是系统在线上好好跑着。这一篇面对所有工程师最焦虑的问题——怎么把多模态 AI 从"在我电脑上能跑"变成"用户在用还没崩"。

## 多模态应用的架构模式

多模态应用有三类典型架构，选择取决于你的场景：

### 模式一：同步实时管道

```
用户请求 → API Gateway → 多模态处理服务 → 返回结果
                           ├── 图片/音频预处理
                           ├── VLM/STT推理
                           └── 结果后处理

适合: 实时对话、图片分析、UI审查
延迟: < 3秒
```

关键设计：预处理异步化。图片缩放、格式转换、Base64 编码在请求进入推理前先完成——推理时间已经是瓶颈，不要让预处理再增加延迟。

### 模式二：异步批处理管道

```
用户请求 → 任务队列 → Worker集群 → 结果存储 → 用户查询结果
                ↓
          进度通知（WebSocket/轮询）

适合: 批量图片审核、视频分析、大规模文档处理
延迟: 分钟到小时级
```

关键设计：任务优先级。P0 用户请求优先处理，P1 内部数据回填排队。队列长度监控——队列堆积超过阈值自动扩容 Worker。

### 模式三：混合架构

对大多数产品最实用的架构——**实时处理轻量任务 + 异步处理重量任务**：

```python
async def handle_user_request(image, task):
    # 先判断任务复杂度
    if is_simple_task(task):
        return await realtime_pipeline(image, task)  # <2秒
    
    # 复杂任务进队列
    task_id = await enqueue_task(image, task)
    return {"status": "processing", "task_id": task_id, 
            "eta": estimate_time(task)}
```

## 灰度发布：别一把梭哈

多模态模型的升级风险比纯文本模型更大——视觉理解中的一个微小退化可能不被 Benchmark 检测到，但在用户场景中引发批量问题。

### 灰度策略

**百分比灰度**。按用户 ID 哈希，前 5% 用户先上新模型。观察 24 小时后无异常扩大至 20%，逐步到 100%。

```python
def select_model_version(user_id):
    hash_val = hashlib.md5(user_id.encode()).hexdigest()
    rollout_pct = get_current_rollout_percentage()  # 从配置中心读取
    
    if int(hash_val[:8], 16) % 100 < rollout_pct:
        return "new_model_v2"
    return "stable_model_v1"
```

**按场景灰度**。高风险场景（财报分析、医疗影像）走旧模型，低风险场景（社交媒体配图分析）走新模型。渐进验证新模型的能力。

### 灰度监控指标

灰度期间重点监控的指标：

| 指标 | 旧模型基线 | 新模型 | 异常阈值 |
|------|:--:|:--:|:--:|
| 回答准确率（人工抽检） | 94% | ≥ 93% | < 90% 自动回滚 |
| 平均延迟 | 2.1s | ≤ 2.5s | > 3s 告警 |
| 用户投诉率 | 0.3% | ≤ 0.5% | > 1% 自动回滚 |
| 空响应率 | 0.1% | ≤ 0.2% | > 1% 告警 |

## 可观测性：你知道线上在发生什么吗

### 三类必监控指标

**业务指标**。用户实际感知到的质量：
- 每个场景的回答准确率（人工抽检 + 自动化评估）
- 用户主动"踩"或投诉的比例
- 任务完成率（用户没有在中间放弃的会话比例）

**性能指标**：
- P50/P95/P99 延迟（按模态和模型分组）
- 队列深度和处理积压
- 缓存命中率

**成本指标**：
- 每个模型每小时的 Token 消耗和花费
- 不同灰度分组的成本差异
- cost per successful task（每次成功任务的成本）

### 全链路追踪

多模态请求链路长——图片预处理 → 模型推理 → 后处理 → 缓存读写 → 数据库。一个请求慢，是哪个环节的问题？

```python
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

async def process_multimodal_request(image, text):
    with tracer.start_as_current_span("multimodal_request") as span:
        span.set_attribute("image.size", len(image))
        span.set_attribute("text.length", len(text))
        
        # 预处理
        with tracer.start_as_current_span("preprocessing"):
            processed = preprocess(image)
            span.set_attribute("preprocess.duration_ms", ...)
        
        # 推理
        with tracer.start_as_current_span("inference"):
            result = await model.generate(processed, text)
            span.set_attribute("model", "gpt-4o")
            span.set_attribute("tokens", result.usage.total_tokens)
        
        # 后处理
        with tracer.start_as_current_span("postprocessing"):
            final = format_result(result)
        
        return final
```

每个 Span 记录开始时间、持续时间、成功/失败状态。所有 Span 形成一棵调用树，可视化全链路的耗时分布。

## Fallback 策略：当一切出错时

多模态 API 的失败模式比纯文本多：

| 失败类型 | 概率 | Fallback |
|---------|:--:|------|
| API 超时（>30s） | ~1% | 重试 1 次 → 降级到小模型 |
| 速率限制 | ~0.5% | 排队等待 → 返回"处理中" |
| 图片过大拒绝 | ~3% | 自动压缩/降分辨率重试 |
| 内容安全拦截 | ~2% | 返回"内容不符合安全策略" |
| 模型返回空/格式错误 | ~1% | 重试 → 小模型兜底 |

```python
async def resilient_multimodal_call(model, image, task, max_retries=2):
    for attempt in range(max_retries + 1):
        try:
            if attempt > 0:
                await asyncio.sleep(2 ** attempt)  # 指数退避
            
            if attempt == max_retries:
                model = FALLBACK_MODEL  # 最后一次重试用小模型兜底
            
            return await model.generate(image, task, timeout=25)
            
        except RateLimitError:
            if attempt < max_retries:
                continue
            return {"status": "busy", "message": "请稍后重试"}
        
        except TimeoutError:
            if attempt < max_retries:
                continue
            return {"status": "timeout", "message": "处理超时，请上传更小的图片"}
        
        except SafetyBlockError:
            return {"status": "blocked", "message": "内容不符合安全策略"}
```

## 上线 Checklist

部署到生产前，逐项核对：

```
□ 灰度策略已配置（5% → 20% → 50% → 100%）
□ 自动回滚条件已设定（准确率 < 90% 或 延迟 > 3s）
□ 全链路追踪已接入（预处理/推理/后处理三段式 Span）
□ 监控面板已搭建（业务/性能/成本三类指标可视化）
□ P0 告警已配置（空响应率 > 1% / 成本超过日预算 / 队列堆积 > 500）
□ Fallback 策略已测试（超时/限流/图片过大/安全拦截）
□ 负载测试已完成（预估峰值 QPS 的 2 倍连续 30 分钟无异常）
□ 回滚预案已确认（可一键切回旧模型）
□ 用户通知模板已准备（如遇降级或故障时告知用户）
```

## 总结

- 多模态应用有三类架构模式：**实时管道、异步批处理、混合架构**——轻量实时+重量异步是通用解法
- 灰度发布对多模态尤其重要——**视觉理解的退化可能不被 Benchmark 检测到**，需要按用户百分比+按场景双维度灰度
- 可观测性要覆盖三类指标：**业务质量（用户感知）、性能延迟、成本消耗**——缺一不可
- Fallback 策略是最后的保险——每个 API 调用都要有"如果这一步失败了怎么办"的预案
- 上线 Checklist 的每一项都应该在上线前被验证过——不在上线后第一次遇到问题
- 最后一篇：[安全与治理](./05-safety-governance.md)

## 参考链接

- [OpenTelemetry Python SDK](https://opentelemetry.io/docs/languages/python/)
- [OpenAI 速率限制文档](https://platform.openai.com/docs/guides/rate-limits)
- [Grafana 监控面板构建](https://grafana.com/docs/)
