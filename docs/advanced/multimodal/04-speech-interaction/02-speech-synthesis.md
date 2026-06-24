# 语音合成与实时交互

> 让 AI 说话——这比让它听话更难。STT 是"把连续信号变成离散文字"，TTS 是倒过来——从离散文字重建连续的自然语音。这中间的差距，就是为什么你听过很多 AI 语音助手，但只有少数几个让你感觉"像真人"。

## 目录

- [TTS 的难度：为什么 AI 说话好听这么难](#tts-的难度为什么-ai-说话好听这么难)
- [TTS 技术三代演进](#tts-技术三代演进)
- [ElevenLabs：语音合成的天花板](#elevenlabs语音合成的天花板)
- [OpenAI TTS 与 Realtime API](#openai-tts-与-realtime-api)
- [开源中文方案：Fish Audio 与 GPT-SoVITS](#开源中文方案fish-audio-与-gpt-sovits)
- [实时语音交互：技术架构全拆](#实时语音交互技术架构全拆)
- [方案选型](#方案选型)
- [总结](#总结)
- [参考链接](#参考链接)

你好，我是江小湖。上一篇讲了 AI 怎么"听"——从声波到文字。这一篇反转过来：AI 怎么"说"。以及更重要的——怎么做到让 AI 像真人一样跟你实时对话。

## TTS 的难度：为什么 AI 说话好听这么难

TTS（Text-to-Speech）不止是把文字逐字念出来。一个"好听"的 AI 语音需要具备：

**自然的韵律**。真人的停顿不是在每个标点符号都停顿，而是根据语义来断句。"我去银行取钱"和"我去银行取钱然后去了超市"——前者的停顿点和后者完全不同。

**情感注入**。"这个方案我觉得不太行"——用婉转犹豫的语气说出来，和用直接否定的语气，听起来是两段截然不同的语音。这段话对应的声学参数（音高曲线、语速变化、能量分布）完全不同——而输入的文字完全一样。

**跨语言自然度**。AI 读中文"顺便说一下，这个 feature 我们已经 implemented 了"——中英混读需要两个语言的发音模型无缝衔接。

**少样本克隆**。只用 30 秒的语音样本就克隆一个人的声音——声带振动频率、口腔共鸣特征、说话习惯，全部从几十秒的音频里提取。

## TTS 技术三代演进

### 第一代：拼接式（Concatenative）

```
文字 → 切分成音素 → 从预录音库找对应的发音片段 → 拼接成完整语音
```

就像用单个汉字录音拼成一句话——每个字单独念都清楚，但连起来机械感极重。因为每个字的发音都是"独立录制"的，字与字之间的自然过渡被切断了。

### 第二代：参数式（Parametric）

```
文字 → 声学参数（F0、时长、频谱包络） → 声码器合成 → 语音
```

用统计模型预测每个音素的声学参数（基频、持续时间等），然后用声码器从参数合成语音。比拼接式连贯，但音质闷，频谱细节丢失。

### 第三代：神经 TTS（Neural TTS）

```
文字 → Transformer/扩散模型 → 梅尔频谱图 → 神经声码器 → 高保真语音
```

直接把文字映射到高维频谱表示，用生成式模型从频谱"重建"自然语音。

**代表架构**：
- **Tacotron 2 + WaveNet**（2017-2018, Google）：奠定神经 TTS 基础
- **FastSpeech 2**（2020, 微软）：并行合成，比自回归方案快 270 倍
- **VITS**（2021, Kakao）：端到端——文字直接到波形，不需要中间频谱
- **Bark**（2023, Suno）：文字到音频的生成式模型，能生成非语言的音效和音乐

### 零样本语音克隆：第三代的最大突破

传统语音克隆需要录制几个小时的语音数据。2024-2026 年的零样本方案只需要几十秒：

```
上传 30 秒的语音样本
    ↓
模型提取说话人的"声纹特征"：
  音高范围 / 音色 / 说话节奏 / 呼吸模式 / 口音
    ↓
用这些特征"驱动"TTS 模型
    ↓
任意文本都能用这个人的声音读出
```

## ElevenLabs：语音合成的天花板

ElevenLabs 是目前 TTS 领域的标杆产品——不是因为它用了别人没有的技术，而是它在"自然度"这个单一维度上做到了无人能及。

### ElevenLabs 的核心能力

**零样本语音克隆**。1 分钟音频 → 克隆。支持 29 种语言，跨语言克隆保留原始音色——你用中文录音，ElevenLabs 能用你的声音说出流利的英文。

**情感参数控制**。ElevenLabs 不只是"生成语音"，而是让你精细控制：

```python
from elevenlabs import VoiceSettings, generate, play

audio = generate(
    text="这个方案我觉得不太行，但可以再讨论一下。",
    voice="cloned_voice_id",
    model="eleven_multilingual_v2",
    voice_settings=VoiceSettings(
        stability=0.50,         # 稳定性：0=更富有表现力，1=更单调
        similarity_boost=0.75,  # 和原始声音的相似度
        style=0.30,             # 风格夸张度：0=平淡，1=戏剧化
        use_speaker_boost=True  # 增强声音清晰度
    )
)
play(audio)
```

### ElevenLabs 的局限

- **价格不便宜**：专业版 $99/月，免费版额度有限
- **数据上云**：你的语音样本和文本上传 ElevenLabs 服务器
- **延迟偏高**：不适合实时对话（约 1-2 秒延迟），更适合配音和内容制作

## OpenAI TTS 与 Realtime API

OpenAI 在语音领域有两套方案——常规 TTS API 和 Realtime API。

### 常规 TTS API

简单的文字→语音转换，适合配音和内容制作：

```python
from openai import OpenAI

client = OpenAI()
response = client.audio.speech.create(
    model="tts-1-hd",              # tts-1: 更快, tts-1-hd: 更高音质
    voice="nova",                  # alloy/echo/fable/onyx/nova/shimmer
    input="你好，欢迎来到 LearnAgent 多模态指南。",
    speed=1.0                      # 0.25-4.0
)
response.stream_to_file("output.mp3")
```

六个预置声音各有特点：alloy（中性）、echo（柔和男声）、fable（英式）、onyx（低沉权威）、nova（温暖女声）、shimmer（清晰女声）。

### Realtime API：真正的实时对话

OpenAI Realtime API 把 STT + LLM 推理 + TTS 整合成一个 WebSocket 连接，实现 <500ms 的端到端延迟：

```
客户端（你的 App）
    ↓  WebSocket 连接
OpenAI 实时服务器
    ├── 接收音频流
    ├── GPT-4o 推理（看到图片和听到音频）
    └── 流式返回音频回复
```

**关键设计**：

- **音频→Token 直通**：GPT-4o 不先做 STT——它直接理解音频，然后直接输出音频 Token。整个链条没有文字中转，情绪、语气、重音全部保留
- **打断机制**：你说"等一下，我不是这个意思"——Realtime API 检测到新的语音输入后中断正在生成的回复音频
- **事件驱动**：VAD（语音活动检测）自动判断用户是否在说话、说完了吗

```python
import asyncio
import websockets
import json

async def realtime_conversation():
    async with websockets.connect(
        "wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview",
        extra_headers={"Authorization": f"Bearer {OPENAI_API_KEY}"}
    ) as ws:
        # 配置会话
        await ws.send(json.dumps({
            "type": "session.update",
            "session": {
                "modalities": ["text", "audio"],
                "instructions": "你是语音助手，用中文简洁回答",
                "voice": "nova",
                "input_audio_format": "pcm16",
                "output_audio_format": "pcm16",
                "turn_detection": {
                    "type": "server_vad",
                    "threshold": 0.5,
                    "prefix_padding_ms": 300,
                    "silence_duration_ms": 500
                }
            }
        }))

        # 发送音频数据
        while True:
            audio_chunk = microphone.read()
            await ws.send(json.dumps({
                "type": "input_audio_buffer.append",
                "audio": base64.b64encode(audio_chunk).decode()
            }))

            # 接收回复
            response = await ws.recv()
            event = json.loads(response)
            if event["type"] == "response.audio.delta":
                play_audio(event["delta"])  # 边收边播
```

## 开源中文方案：Fish Audio 与 GPT-SoVITS

### Fish Audio

Fish Audio 是目前中文开源 TTS 社区最活跃的项目。它的零样本语音克隆效果在开源方案中领先：

```python
from fish_audio_sdk import FishAudioSDK

sdk = FishAudioSDK(api_key="your_key")

# 上传声音样本 → 创建克隆声音
voice_id = sdk.create_voice(
    name="my_voice",
    samples=["sample_1.wav", "sample_2.wav"]
)

# 用克隆的声音生成语音
audio = sdk.tts(
    text="你好，这是我的AI克隆声音。",
    voice_id=voice_id,
    format="mp3"
)
```

### GPT-SoVITS

GPT-SoVITS 是另一个活跃的中文语音克隆开源项目，特点是**极低的样本需求**——5 秒音频就可以开始克隆：

```python
# GPT-SoVITS 的推理流程（简化）
from GPT_SoVITS.inference import TTS

tts = TTS(
    gpt_model="pretrained/gpt_model.ckpt",
    sovits_model="pretrained/sovits_model.ckpt",
    ref_audio="my_voice_sample.wav",    # 参考音频
    ref_text="参考音频对应的文字"        # 提高克隆精度
)

audio = tts.inference(
    text="这是用GPT-SoVITS生成的中文语音。",
    text_language="zh"
)
```

### 开源 vs 商业 TTS

| 维度 | ElevenLabs | OpenAI TTS | Fish Audio | GPT-SoVITS |
|------|:--:|:--:|:--:|:--:|
| 语音自然度 | ★★★★★ | ★★★★☆ | ★★★☆☆ | ★★★☆☆ |
| 中文支持 | ★★★★☆ | ★★★☆☆ | ★★★★★ | ★★★★★ |
| 零样本克隆 | ★★★★★ | ❌ | ★★★★☆ | ★★★★☆ |
| 情感控制 | ★★★★★ | ★★☆☆☆ | ★★☆☆☆ | ★★☆☆☆ |
| 实时对话 | ❌ | ★★★★★ | ❌ | ❌ |
| 本地部署 | ❌ | ❌ | ✅ | ✅ |
| 成本 | 高 | 中 | 低/免费 | 免费 |

## 实时语音交互：技术架构全拆

一个完整的实时语音助手需要四个子系统协同工作：

```
用户说话
    ↓
[VAD 语音活动检测]  ← 判断"用户开始说话了吗？说完了吗？"
    ↓ 音频流
[STT / 直接音频推理] ← 将语音转为文字或直接理解音频
    ↓ 文字或音频Token
[LLM 推理]           ← 理解意图，生成回复
    ↓ 文字回复
[TTS 合成]           ← 将文字转为自然语音
    ↓ 音频流
[流式播放]            ← 边生成边播放，降低延迟
```

### VAD：听出谁在说话

语音活动检测（Voice Activity Detection）是实时对话的守门员——它判断"现在是用户在说话"还是"这是背景噪音"。

```python
import webrtcvad
import collections

class VoiceActivityDetector:
    def __init__(self, aggressiveness=2):
        self.vad = webrtcvad.Vad(aggressiveness)
        self.speech_frames = collections.deque(maxlen=30)  # 300ms缓冲区
        self.is_speaking = False

    def process_frame(self, audio_frame):
        """每20ms调用一次"""
        is_speech = self.vad.is_speech(audio_frame, 16000)
        self.speech_frames.append(is_speech)

        # 超过60%的帧检测到语音 → 认为用户在说话
        speech_ratio = sum(self.speech_frames) / len(self.speech_frames)

        if speech_ratio > 0.6 and not self.is_speaking:
            self.is_speaking = True
            return "SPEECH_START"
        elif speech_ratio < 0.2 and self.is_speaking:
            self.is_speaking = False
            return "SPEECH_END"
        return None
```

### 打断机制

打断是实时语音助手的刚需——GPT-4o Realtime API 的原生支持大幅简化了这个需求：

```
用户："帮我查一下..."
    → GPT-4o 开始生成回复
    → 用户打断："等一下，不用查了"
    → VAD 检测到新的语音开始
    → 取消当前生成 → 处理新的指令
```

传统方案（STT→LLM→TTS 流水线）要实现打断非常复杂——需要同时管理三个异步任务并支持任意节点的中断。GPT-4o Realtime API 的"音频→音频"端到端模式让打断变成了一个内部事件——不需要外部协调。

## 方案选型

| 你的场景 | 推荐方案 | 理由 |
|---------|---------|------|
| 高质量的配音/有声书 | ElevenLabs | 自然度和情感控制最优 |
| 快速集成 TTS 到你的 App | OpenAI TTS API | 最简单，文档最好 |
| 实时语音助手 | OpenAI Realtime API + GPT-4o | <500ms 端到端延迟+原生打断 |
| 中文语音克隆（本地免费）| GPT-SoVITS 或 Fish Audio | 开源、可定制、数据不离本地 |
| 产品级中文语音助手 | 通义听悟 + 通义千问 TTS | 中文识别+合成的完整方案 |

## 总结

- TTS 比 STT 更难——**从离散文字重建连续自然语音**，需要同时解决韵律、情感、跨语言、少样本克隆四个挑战
- TTS 三代演进：拼接式（机械）→ 参数式（连贯但闷）→ 神经 TTS（自然），**零样本语音克隆是第三代的最大突破**
- **ElevenLabs** 在自然度和情感控制上是绝对标杆，但价格高、不支持实时对话
- **OpenAI Realtime API** 是唯一支持 <500ms 端到端延迟的实时语音对话方案，原生打断机制
- **中文开源 TTS** 社区活跃：Fish Audio 和 GPT-SoVITS 提供免费的语音克隆方案
- 实时语音助手的架构核心是四个子系统：**VAD → STT → LLM → TTS**，GPT-4o 将它们整合为一条音频到音频的直通管线
- 04 章全部结束。下一篇进入创造而非感知的领域：[05 多模态生成](../05-multimodal-generation/README.md)

## 参考链接

- [ElevenLabs API 文档](https://elevenlabs.io/docs/api-reference)
- [OpenAI TTS 文档](https://platform.openai.com/docs/guides/text-to-speech)
- [OpenAI Realtime API 文档](https://platform.openai.com/docs/guides/realtime)
- [Fish Audio](https://fish.audio/)
- [GPT-SoVITS GitHub](https://github.com/RVC-Boss/GPT-SoVITS)
- [WebRTC VAD 文档](https://webrtc.googlesource.com/src/)

> 听完说完了。下一章进入创造层面——AI 怎么画图、做视频、写歌。从 [05 多模态生成](../05-multimodal-generation/README.md) 开始。
