# 🎥 Video Summarizer

A web application that transcribes video files and generates AI-powered meeting summaries using OpenAI Whisper and Google Gemini.

## ✨ Features

- 📁 **Video Upload**: Support for MP4, MOV, AVI, MKV, WMV, FLV formats
- 🎙️ **Audio Transcription**: Uses OpenAI Whisper for accurate speech-to-text
- 🤖 **AI Summarization**: Google Gemini generates structured meeting summaries
- 📏 **Multiple Summary Lengths**: Very Short, Short, Medium, Long options
- 📋 **3 Summary Formats**: Executive Summary, Structured Meeting Notes, or Narrative style
- 🔄 **Regenerate Summaries**: Try different lengths and formats without re-processing video
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
   # Use pip3 if pip doesn't work
   pip install -r requirements.txt
   # OR
   pip3 install -r requirements.txt
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

#### Option 1: Double-click the Launcher (Easiest)

Simply double-click `launcher.sh` in your file manager. This should:
- Automatically start the Flask server
- Open your browser to the application
- Handle cleanup when closed

*Note: This works on most macOS and Linux systems. If it doesn't work, try Option 2.*

#### Option 2: Command Line Launcher

1. **Make the launcher executable**
   ```bash
   chmod +x launcher.sh
   ```

2. **Run the launcher**
   ```bash
   ./launcher.sh
   ```
   
   The launcher will:
   - Automatically start the Flask server
   - Kill any existing processes on port 3000
   - Open your browser automatically
   - Handle cleanup when you press Ctrl+C

#### Option 3: Manual Start

1. **Start the server**
   ```bash
   # Use python3 if python doesn't work
   python app.py
   # OR
   python3 app.py
   ```

2. **Open your browser**
   Navigate to `http://localhost:3000`

3. **Upload and process**
   - Select your video file
   - Enter your Gemini API key
   - Choose summary length and format
   - Click "Process Video"

## 📖 Usage

### Processing a Video

1. **Upload Video**: Click "Choose File" and select your video
2. **API Key**: Enter your Gemini API key and test it
3. **Summary Length**: Choose from Very Short, Short, Medium, or Long
4. **Summary Format**: Select from 3 available formats
5. **Process**: Click "Process Video" and wait for completion
6. **Results**: View transcript and summary, copy or download as needed

### Summary Formats

Choose from 3 different summary formats:

#### Format 1 (Executive Summary)
Bullet points at equal level, focusing on key talking points:
```
Talking points:
• Two parallel initiatives are underway: enhancing internal documentation practices...
• The documentation initiative introduces a new Notion-based template system...
• The engineering leadership experiment aims to empower engineers...
```

#### Format 2 (Structured Meeting Notes)
Hierarchical bullet points with main topics and sub-points:
```
Talking points:
• Workout recommendation engine update entering limited release January 10–11:
  • Results show dramatic quality improvement over current system
  • Deployment pipeline has a critical timeout issue that must be resolved before rollout
• New “Today’s Focus” module under development for user homepage prototype:
  • Objective is to validate behavior triggers ahead of the Q2 personalized coaching launch
  • Initial version will act as a dynamic widget with A/B support for motivational prompts
```

#### Format 3 (Executive Summary - Narrative)
Narrative format in paragraphs without bullet points:
```
The meeting centered around recent product performance metrics and strategic shifts in the roadmap. A decline in user engagement on the mobile app prompted the leadership team to pause development on two lesser-used features and reallocate resources.

Leadership acknowledged ongoing tensions around roadmap clarity, reiterating that near-term focus will be on initiatives tied directly to user retention and daily active usage growth.
```

### Summary Lengths

- **Very Short**: 3-5 main points, 1-2 bullets each (critical decisions only)
- **Short**: 5-8 main points, 2-3 bullets each (key decisions and discussions)
- **Medium**: 8-12 main points, 3-4 bullets each (detailed with context)
- **Long**: 12+ main points, 4+ bullets each (comprehensive coverage)

## 🔧 Configuration

### Whisper Model

By default, the app uses Whisper's "base" model. You can change this in `app.py`:

```python
whisper_model = whisper.load_model("base")  # tiny, base, small, medium, large
```

## 📁 Project Structure

```
video-summarizer/
├── app.py                 # Main Flask application
├── launcher.sh            # Convenient launcher script
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

## 🙏 Acknowledgments

- [OpenAI Whisper](https://github.com/openai/whisper) for speech recognition
- [Google Gemini](https://deepmind.google/technologies/gemini/) for AI summarization
- [Claude AI](https://claude.ai) for development assistance
- [Flask](https://flask.palletsprojects.com/) for the web framework
- [FFmpeg](https://ffmpeg.org/) for video processing

## 📞 Support

If you encounter any issues:

1. Check the [Issues](https://www.youtube.com/watch?v=dQw4w9WgXcQ) page
2. Create a new issue with detailed description
3. Include error messages and system information

---

**Made with Claude AI for better meeting productivity**