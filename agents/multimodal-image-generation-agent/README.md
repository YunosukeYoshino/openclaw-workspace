# マルチモーダル画像生成エージェント 🖼️

Image generation agent with text and reference image inputs

テキストと参照画像入力に対応した画像生成エージェント

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
!multimodal-image-generation-agent [media_url]    # Analyze media from URL or attachment
!multimodal-image-generation-agent-list [limit]   # List recent entries (default: 10)
!multimodal-image-generation-agent-stats          # Show statistics
```

### Python API

```python
from agent import MultimodalImageGenerationAgent

agent = MultimodalImageGenerationAgent(bot)
result = agent.analyze_media("path/to/media.jpg")
print(result)
```

## Database Schema

```sql
image_generations (id INTEGER PRIMARY KEY, prompt TEXT, reference_image TEXT, output_path TEXT, parameters TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)
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
