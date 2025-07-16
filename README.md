# 🎥 Video Summarizer

A web application that transcribes video files and generates AI-powered meeting summaries using OpenAI Whisper and Google Gemini.

## ✨ Features

- 📁 **Video Upload**: Support for MP4, MOV, AVI, MKV, WMV, FLV formats
- 🎙️ **Audio Transcription**: Uses OpenAI Whisper for accurate speech-to-text
- 🤖 **AI Summarization**: Google Gemini generates structured meeting summaries
- 📏 **Multiple Summary Lengths**: Very Short, Short, Medium, Long options
- 🔄 **Regenerate Summaries**: Try different lengths without re-processing video
- 📋 **Copy to Clipboard**: Easy copying of transcripts and summaries
- 💾 **Download Results**: Save transcripts and summaries as text files
- 🔑 **API Key Testing**: Verify your Gemini API key before processing

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- FFmpeg (for video processing)
- Google Gemini API key

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/video-summarizer.git
   cd video-summarizer
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install FFmpeg**
   ```bash
   # macOS
   brew install ffmpeg
   
   # Ubuntu/Debian
   sudo apt update
   sudo apt install ffmpeg
   
   # Windows
   # Download from https://ffmpeg.org/download.html
   ```

4. **Get Gemini API Key**
   - Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create a new API key
   - Keep it secure!

### Running the Application

1. **Start the server**
   ```bash
   python app.py
   ```

2. **Open your browser**
   Navigate to `http://localhost:3000`

3. **Upload and process**
   - Select your video file
   - Enter your Gemini API key
   - Choose summary length
   - Click "Process Video"

## 📖 Usage

### Processing a Video

1. **Upload Video**: Click "Choose File" and select your video
2. **API Key**: Enter your Gemini API key and test it
3. **Summary Length**: Choose from Very Short, Short, Medium, or Long
4. **Process**: Click "Process Video" and wait for completion
5. **Results**: View transcript and summary, copy or download as needed

### Summary Formats

The app generates structured summaries in this format:

```
Talking points:
1. Main discussion topic
   • Key point or decision
   • Next steps or action items
2. Another topic
   • Important details
   • Team member contributions
```

### Summary Lengths

- **Very Short**: 3-5 main points, 1-2 bullets each (critical decisions only)
- **Short**: 5-8 main points, 2-3 bullets each (key decisions and discussions)
- **Medium**: 8-12 main points, 3-4 bullets each (detailed with context)
- **Long**: 12+ main points, 4+ bullets each (comprehensive coverage)

## 🔧 Configuration

### Environment Variables

You can set these in your environment:

```bash
export GEMINI_API_KEY=your_api_key_here
export FLASK_ENV=development
export FLASK_DEBUG=1
```

### Whisper Model

By default, the app uses Whisper's "base" model. You can change this in `app.py`:

```python
whisper_model = whisper.load_model("base")  # tiny, base, small, medium, large
```

## 🚀 Deployment

### Heroku

1. **Create Procfile**
   ```
   web: gunicorn app:app
   ```

2. **Deploy**
   ```bash
   git add .
   git commit -m "Initial commit"
   heroku create your-app-name
   git push heroku main
   ```

### Railway

1. **Connect GitHub repository**
2. **Add environment variables** (if using)
3. **Deploy automatically**

### Docker

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN apt-get update && apt-get install -y ffmpeg

COPY . .
EXPOSE 3000
CMD ["python", "app.py"]
```

## 📁 Project Structure

```
video-summarizer/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── .gitignore            # Git ignore patterns
└── static/               # Static files (if any)
```

## 🔍 API Endpoints

- `GET /` - Main application interface
- `POST /test_api` - Test Gemini API key
- `POST /process` - Process video file
- `GET /progress` - Check processing status
- `POST /regenerate_summary` - Regenerate summary
- `GET /results` - Get processing results

## 🛠️ Technical Details

### Video Processing Pipeline

1. **Upload**: Video file uploaded to temporary storage
2. **Convert**: FFmpeg converts video to MP3 audio
3. **Transcribe**: Whisper processes audio to text
4. **Summarize**: Gemini generates structured summary
5. **Cleanup**: Temporary files are deleted

### Security

- API keys are handled client-side only
- Temporary files are automatically cleaned up
- No persistent storage of sensitive data

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [OpenAI Whisper](https://github.com/openai/whisper) for speech recognition
- [Google Gemini](https://deepmind.google/technologies/gemini/) for AI summarization
- [Flask](https://flask.palletsprojects.com/) for the web framework
- [FFmpeg](https://ffmpeg.org/) for video processing

## 📞 Support

If you encounter any issues:

1. Check the [Issues](https://github.com/yourusername/video-summarizer/issues) page
2. Create a new issue with detailed description
3. Include error messages and system information

---

**Made with ❤️ for better meeting productivity**