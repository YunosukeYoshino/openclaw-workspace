# マルチモーダル音声合成エージェント 🔊

Text-to-speech agent with multiple voices and emotion support

複数のボイスと感情表現をサポートする音声合成エージェント

## Features

- **Multimodal AI Processing**: Analyze images, videos, and audio
- **High Confidence Results**: AI-powered analysis with confidence scores
- **Tag Management**: Automatic tagging and manual tag management
- **Search & Filter**: Search entries by tags or content type
- **Statistics**: View detailed statistics of analyzed content

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Discord Bot Commands

```
!multimodal-text-to-speech-agent [media_url]    # Analyze media from URL or attachment
!multimodal-text-to-speech-agent-list [limit]   # List recent entries (default: 10)
!multimodal-text-to-speech-agent-stats          # Show statistics
```

### Python API

```python
from agent import MultimodalTextToSpeechAgent

agent = MultimodalTextToSpeechAgent(bot)
result = agent.analyze_media("path/to/media.jpg")
print(result)
```

## Database Schema

```sql
tts_generations (id INTEGER PRIMARY KEY, text TEXT, voice_id TEXT, emotion TEXT, audio_path TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)
```

## Requirements

- discord.py>=2.3.0
- opencv-python>=4.8.0
- pillow>=10.0.0
- speechrecognition>=3.10.0
- pydub>=0.25.0
- torch>=2.0.0
- torchvision>=0.15.0
- transformers>=4.30.0
- openai-whisper>=20230314
- numpy>=1.24.0

## License

MIT
