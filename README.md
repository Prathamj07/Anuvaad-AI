# 🎬 Anuvaad AI - AI-Powered Video Dubbing Platform

Transform your videos across languages with professional AI dubbing, translation, and creative tools.

## ✨ Features

- 🎥 **Video Dubbing** - AI-powered dubbing in 50+ languages
- 📺 **YouTube Summarizer** - Get instant AI summaries of videos  
- 📖 **Word to Story** - Transform words into creative stories
- 🎙️ **Article to Podcast** - Convert articles to audio
- 🗣️ **Text to Speech** - Natural voice synthesis
- 🎤 **Speech to Text** - Accurate transcription
- 🌐 **Text Translation** - AI-powered translation

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- FFmpeg

### Installation

1. **Clone the repository**
   ```bash
   cd anuvaad-ai
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   ```

3. **Activate virtual environment**
   - Windows: `venv\Scripts\activate`
   - Mac/Linux: `source venv/bin/activate`

4. **Install dependencies**
   ```bash
   pip install -r app_requirements.txt
   ```

5. **Configure API keys**
   ```bash
   cp .env.example .env
   ```
   Then edit `.env` and add your API keys:
   - Get ElevenLabs key: https://elevenlabs.io/app/settings/api-keys
   - Get Gemini key: https://ai.google.dev/

### Run the App

Just one command:

```bash
python start.py
```

That's it! 🎉

The app will be available at **http://localhost:5000**

Press `Ctrl+C` to stop.

## 📁 Project Structure

```
anuvaad-ai/
├── start.py              # 🚀 Single command to start everything
├── .env.example          # Template for API keys
├── .env                  # Your API keys (create this)
├── app_requirements.txt  # Python dependencies
├── backend.py            # Flask backend
├── frontend/             # React frontend
└── ...
```

## 🔑 API Keys

You need:

1. **ElevenLabs** (AI voice generation)
   - Sign up: https://elevenlabs.io/
   - Get key: https://elevenlabs.io/app/settings/api-keys

2. **Google Gemini** (AI translation)
   - Get key: https://ai.google.dev/

## 📖 Documentation

See `setup_guide.txt` for detailed setup instructions and troubleshooting.

## 🛠️ Tech Stack

- **Frontend**: React + Vite
- **Backend**: Flask (Python)
- **AI**: ElevenLabs + Google Gemini
- **Processing**: MoviePy, FFmpeg, Pydub

## 💡 Usage Tips

- First-time setup takes 2-5 minutes (dependency installation)
- Video processing is resource-intensive
- Requires stable internet for AI APIs
- Keep your `.env` file secure

## 🐛 Common Issues

**Module not found?**
```bash
pip install -r app_requirements.txt
```

**FFmpeg not found?**
Install FFmpeg and add to PATH

**Port in use?**
Stop other apps using ports 5000/5001

## 📝 License

All rights reserved.

---

Made with ❤️ by Anuvaad AI Team
