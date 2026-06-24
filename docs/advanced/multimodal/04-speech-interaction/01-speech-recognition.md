# 语音识别（STT）

> 把声音变成文字——这件事看似简单，实际上涉及声学、语言学、信号处理的交叉。本文拆解语音识别的技术栈、主流方案的真实表现，以及在不同场景下怎么选工具。

## 目录

- [语音识别为什么难](#语音识别为什么难)
- [STT 的技术演进：从管道到端到端](#stt-的技术演进从管道到端到端)
- [Whisper：开源语音识别的标杆](#whisper开源语音识别的标杆)
- [DeepGram：实时识别的速度之王](#deepgram实时识别的速度之王)
- [中文语音识别专项](#中文语音识别专项)
- [实战：搭建生产级语音转写流水线](#实战搭建生产级语音转写流水线)
- [方案选型：不同场景的最佳选择](#方案选型不同场景的最佳选择)
- [总结](#总结)
- [参考链接](#参考链接)

你好，我是江小湖。前几章都在讲"看"——VLM、视频、文档理解。这一章把焦点转到"听"——让 AI 把你说的话变成文字。这不是一个已经解决的问题，尤其是在中文环境下。

## 语音识别为什么难

语音识别（Speech-to-Text, STT）表面上不难——Whisper 装好，一行代码就能转写。但在真实场景下，你会碰到这些坑：

### 同音词和语境歧义

```
语音："我想买股票" vs "我想买骨瓢"
声学层面完全一样。
差异在于语言模型是否知道"股票"比"骨瓢"更常见。
```

中文的同音词密度远高于英文——普通话只有 400 多个音节（带声调约 1300 个），但有数万个常用词。平均每个音节对应几十个可能的字——没有语言模型辅助，纯声学识别正确率不到 30%。

### 噪音环境

安静录音室里 Whisper 的 WER（词错误率）约 3-5%，但到了咖啡厅、马路边、工厂车间，这个数字可能跳到 20-30%。每一种噪音环境（人声、引擎声、风声、回音）都需要不同的降噪策略。

### 多人对话和说话人分离

一段两个人的对话录音——AI 需要同时做三件事：
1. 把音频转成文字
2. 分辨"哪段话是谁说的"
3. 保持每句话的上下文连贯

现有的开源方案在这三项能力上的差距很大：转写 ≈95% 准确率，说话人分离 ≈85%，上下文连贯 ≈75%。

### 口音和专业术语

- 四川话"鞋子"发音接近普通话的"孩子"
- 医学录音中的"窦性心律不齐"、"二尖瓣反流"——通用模型根本不认识这些词
- 编程场景中的"React Hook"、"Docker Container"——Whisper 可能转成"react hook"、拖课 container"

## STT 的技术演进：从管道到端到端

### 传统管道架构

```
音频 → [声学模型] → 音素序列 → [语言模型] → 文字
           ↑                        ↑
      语音→发音单元              音素→有意义的句子
```

传统的 STT 系统由多个独立模块串联：
- **声学模型**：把声波转换成音素（语言的最小发音单元）
- **发音词典**：音素→单词的映射
- **语言模型**：根据上下文选择最可能的单词序列

问题很明显：**错误在管道中传播**——声学模型听错了，后面的模块全跑偏，整个过程不会自我纠正。

### 端到端架构（Whisper 的方式）

```
音频 → [单个 Transformer] → 文字
          ↑
    声学+语言学+语言模型
    全部在一个网络中联合优化
```

Whisper 等现代 STT 系统把声学理解、语言建模、文本生成全部塞进一个 Transformer。68 万小时的训练数据让模型自己学会了从声波到文字的端到端映射。

**端到端的优势**：不会因为声学模型的错误而"锁死"后续处理——Transformer 可以在一层推理中同时考虑声学特征和语言习惯，做出全局最优的判断。

## Whisper：开源语音识别的标杆

OpenAI 的 Whisper 是 2022 年开源的语音识别模型，至今仍然是开源社区的标准方案。它用 68 万小时的**多语言、多任务**音频数据训练——不只是"听写"，还包括翻译（X→英语）、语种检测、时间戳生成。

### Whisper 的核心指标

| 版本 | 参数量 | 英文 WER | 中文 WER | 推理速度 (RTF) | 显存需求 |
|------|:--:|:--:|:--:|:--:|:--:|
| tiny | 39M | 8.5% | 18.2% | 0.03 | 1 GB |
| base | 74M | 6.7% | 15.8% | 0.05 | 1 GB |
| small | 244M | 4.8% | 12.4% | 0.10 | 2 GB |
| medium | 769M | 3.8% | 10.1% | 0.20 | 5 GB |
| large-v3 | 1.55B | 3.2% | 8.7% | 0.35 | 10 GB |

### 基础使用

```python
import whisper

# 加载模型（首次自动下载）
model = whisper.load_model("large-v3")

# 转写音频
result = model.transcribe(
    "meeting.mp3",
    language="zh",              # 指定中文，也可以自动检测
    task="transcribe",          # "transcribe" 或 "translate"（翻译为英文）
    verbose=False
)

# 获取完整结果
print(result["text"])           # 完整转写文本
for segment in result["segments"]:
    print(f"[{segment['start']:.1f}s - {segment['end']:.1f}s] {segment['text']}")
```

### 生产级 Whisper：faster-whisper

原版 Whisper 的推理速度在 CPU 上很慢（一段 10 分钟的音频可能需要 5-10 分钟处理）。faster-whisper 是社区对 Whisper 的 C++ 重写，速度提升 4 倍：

```python
from faster_whisper import WhisperModel

model = WhisperModel("large-v3", device="cuda", compute_type="float16")

segments, info = model.transcribe(
    "meeting.mp3",
    language="zh",
    beam_size=5,               # 搜索宽度，越大越准但越慢
    vad_filter=True,           # 自动跳过静音段
    vad_parameters=dict(
        min_silence_duration_ms=500  # 停顿超过500ms切分新句子
    )
)

for segment in segments:
    print(f"[{segment.start:.1f}s → {segment.end:.1f}s] {segment.text}")
```

**faster-whisper 的优化要点**：
- `beam_size=5`：搜索 5 条候选路径选最优，中文场景推荐 5（英文 1 即可）
- `vad_filter=True`：跳过静音段落，对会议录音加速 30-50%
- `compute_type="int8"`：CPU 推理用 8-bit 量化，精度损失极小但速度快 3 倍

### 本地部署 vs API 调用

| 维度 | 本地 Whisper | OpenAI Whisper API |
|------|------------|-------------------|
| 成本 | GPU 电费（一次投入） | $0.006/分钟 |
| 延迟 | 2-20秒（取决于GPU） | 1-3秒 |
| 10小时音频 | ~$0（GPU已投入） | ~$3.60 |
| 隐私 | 数据不出本地 | 数据上传 OpenAI |
| 中文准确度 | 8-10% WER | 5-7% WER（云版本有额外优化） |

## DeepGram：实时识别的速度之王

Whisper 的设计目标是"高精度转写"，不是"实时对话"。它的处理方式是离线批量式——先录完，再转写。DeepGram 走的是另一条路：**流式实时识别**。

### DeepGram 的核心差异

```python
# Whisper 的处理模式
record_audio(file="meeting.mp3")  # 先录完
transcribe(file="meeting.mp3")    # 再转写
# 延迟：录音时长 + 转写时长

# DeepGram 的实时流式处理
connection = deepgram.listen.live({
    "model": "nova-2",
    "language": "zh-CN",
    "interim_results": True,     # 实时返回中间结果
    "smart_format": True,        # 自动格式化数字/日期/货币
    "diarize": True,             # 说话人分离
})
# 延迟：<300ms —— 边说边出字
```

DeepGram 的实时模式对语音助手、实时字幕、在线会议转写等场景是必须的——用户不可能等你说完 30 秒再看到文字。

### 实时转写的代码

```python
from deepgram import DeepgramClient, LiveTranscriptionEvents
import asyncio
import pyaudio

dg_client = DeepgramClient("YOUR_API_KEY")
dg_connection = dg_client.listen.live()

# 处理实时结果
def on_transcript(self, result, **kwargs):
    sentence = result.channel.alternatives[0].transcript
    if len(sentence) > 0:
        is_final = result.speech_final
        print(f"{'[最终]' if is_final else '[中间]'}: {sentence}")

dg_connection.on(LiveTranscriptionEvents.Transcript, on_transcript)

# 启动连接
dg_connection.start({
    "model": "nova-2",
    "language": "zh-CN",
    "interim_results": True,
    "encoding": "linear16",
    "sample_rate": 16000
})

# 持续发送音频流
audio_stream = pyaudio.PyAudio().open(
    format=pyaudio.paInt16, channels=1, rate=16000,
    input=True, frames_per_buffer=3200
)
while True:
    data = audio_stream.read(3200)
    dg_connection.send(data)
```

## 中文语音识别专项

中文 STT 有自己独特的挑战和最佳方案。

### 通义听悟：中文会议的端到端方案

通义听悟不只是"把录音转成文字"——它是专门为会议场景设计的全流程服务：

```
上传会议录音
    ↓
通义听悟自动识别：说话人 / 中英文 / 专业术语
    ↓
输出：逐字稿 + 自动分段 + 关键信息提取 + 会议纪要 + 待办事项
```

这是它不是 STT，是"会议理解"。对于中文用户来说，通义听悟是目前体验最完整的语音转写方案。

### PaddleSpeech：百度飞桨的开源方案

对于需要本地部署且对中文有高要求的场景：

```python
from paddlespeech.cli.asr.infer import ASRExecutor

asr = ASRExecutor()
result = asr(audio_file="meeting.wav", model="conformer_wenetspeech", lang="zh")
print(result)
```

PaddleSpeech 的中文模型在新闻和会议场景的 WER 约 5-8%，接近商业方案水平，且完全本地运行。

### Whisper 的中文优化技巧

如果你用 Whisper 做中文识别，几个提升效果的关键参数：

```python
model.transcribe(
    "audio.mp3",
    language="zh",                    # 明确指定中文
    initial_prompt="这是一段技术会议的录音，讨论的话题是微服务架构设计。"
                                      # 给模型语言背景线索
    word_timestamps=True,             # 获取逐字时间戳
    condition_on_previous_text=False, # 中文禁用上下文依赖——容易错上加错
    no_speech_threshold=0.6,          # 提高静音判断阈值
)
```

- `initial_prompt`：最关键的中文优化技巧。告诉 Whisper"这是在讨论什么话题"，它能更准确地选择同音异义词
- `condition_on_previous_text=False`：中文场景的一个反直觉经验——上下文依赖反而容易把错误放大

## 实战：搭建生产级语音转写流水线

```python
class ProductionSTTPipeline:
    """生产级语音转写流水线"""

    def __init__(self, use_gpu=True):
        self.device = "cuda" if use_gpu else "cpu"
        self.fast_model = WhisperModel("small", device=self.device)
        self.precise_model = WhisperModel("large-v3", device=self.device)

    def transcribe(self, audio_path, quality="auto", context=None):
        """智能转写：自动选择模型和参数"""
        import librosa

        # 分析音频特征
        duration = librosa.get_duration(path=audio_path)
        y, sr = librosa.load(audio_path)
        rms = librosa.feature.rms(y=y).mean()

        # 根据音频质量和时长自动选模型
        if quality == "high" or duration < 120:
            model = self.precise_model  # 短音频或要求高质量
        elif rms > 0.1:                 # 信号强，质量较好
            model = self.fast_model
        else:
            model = self.precise_model  # 弱信号，用大模型补偿

        # 转写
        segments, info = model.transcribe(
            audio_path,
            language="zh" if self._detect_chinese(audio_path) else None,
            initial_prompt=context,
            vad_filter=True,
            beam_size=5
        )

        # 后处理：分段 + 去重
        results = []
        prev_end = 0
        for seg in segments:
            if seg.start - prev_end < 0.3 and results:
                results[-1]["text"] += seg.text
                results[-1]["end"] = seg.end
            else:
                results.append({
                    "start": seg.start, "end": seg.end, "text": seg.text.strip()
                })
            prev_end = seg.end

        return {"segments": results, "language": info.language, "duration": duration}

    def _detect_chinese(self, audio_path):
        # 用fast模型快速判断语种
        segments, info = self.fast_model.transcribe(audio_path, vad_filter=True)
        return info.language == "zh"
```

## 方案选型：不同场景的最佳选择

| 你的场景 | 推荐方案 | 理由 |
|---------|---------|------|
| 离线批量转写（高精度）| faster-whisper large-v3 | 最高精度开源方案 |
| 实时对话/语音助手 | DeepGram Nova-2 | <300ms延迟，流式输出 |
| 中文会议 | 通义听悟 | 说话人分离+自动纪要不是通用STT能替代的 |
| 本地隐私+中文 | PaddleSpeech 或 faster-whisper medium | 精度够用，数据不出本地 |
| 预算极度敏感 | faster-whisper small + int8 量化 | CPU也能跑 |
| 多语言混合 | Whisper large-v3 | 自动语种检测+多语言模型 |
| 编程/技术录音 | Whisper large-v3 + initial_prompt | 提示词提供术语语境 |

## 总结

- 语音识别的核心挑战在中文场景放大了：**同音词密度高、口音差异大、专业术语多、噪音环境普遍**
- STT 从管道架构演进到端到端 Transformer，**单个模型同时学会声学→语言→文字的全链路**
- **Whisper** 是开源方案的标杆：large-v3 中文 WER 8.7%，faster-whisper 提供 4 倍加速
- **DeepGram** 以 <300ms 延迟的实时流式输出填补了离线转写的空白
- 中文场景有专属优势：**通义听悟**的全流程会议理解和 **PaddleSpeech** 的本地部署方案
- **不要用一种方案覆盖所有场景**——离线用 Whisper、实时用 DeepGram、中文会议用通义听悟
- 下一篇从"听"转向"说"：[语音合成与实时交互](./02-speech-synthesis.md)

## 参考链接

- [Whisper GitHub](https://github.com/openai/whisper)
- [faster-whisper GitHub](https://github.com/SYSTRAN/faster-whisper)
- [DeepGram 实时语音识别](https://deepgram.com/)
- [通义听悟官网](https://tingwu.aliyun.com/)
- [PaddleSpeech GitHub](https://github.com/PaddlePaddle/PaddleSpeech)

> 能听了，但 AI 怎么说话？下一篇 [语音合成与实时交互](./02-speech-synthesis.md) 拆解 TTS 的技术方案和 Realtime API 的完整架构。
