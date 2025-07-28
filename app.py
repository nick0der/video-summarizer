#!/usr/bin/env python3
from flask import Flask, request, render_template_string, jsonify, send_from_directory
import subprocess
import whisper
import warnings
import os
import tempfile
import threading
from google import genai
import time

# Silence warnings
warnings.filterwarnings("ignore")

app = Flask(__name__)

# Global variables
processing_status = {"status": "ready", "progress": 0, "message": "Ready"}
whisper_model = None
current_transcript = ""
current_summary = ""

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Video Summarizer</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            max-width: 800px; 
            margin: 0 auto; 
            padding: 15px; 
            background-color: #f5f5f5;
        }
        .container { 
            background: white; 
            padding: 20px; 
            border-radius: 10px; 
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 { 
            color: #333; 
            text-align: center; 
            margin-bottom: 20px;
            margin-top: 0;
        }
        .section { 
            margin-bottom: 18px; 
            padding: 15px; 
            border: 1px solid #ddd; 
            border-radius: 8px; 
            background-color: #fafafa;
        }
        .section h3 { 
            margin-top: 0; 
            margin-bottom: 12px;
            color: #555;
        }
        input[type="file"], input[type="password"] { 
            width: 100%; 
            padding: 8px; 
            margin: 8px 0; 
            border: 1px solid #ddd; 
            border-radius: 5px; 
            font-size: 14px;
        }
        button { 
            background-color: #4CAF50; 
            color: white; 
            padding: 10px 20px; 
            border: none; 
            border-radius: 5px; 
            cursor: pointer; 
            font-size: 16px; 
            margin: 8px 4px;
        }
        button:hover { 
            background-color: #45a049; 
        }
        button:disabled { 
            background-color: #cccccc; 
            cursor: not-allowed; 
        }
        .progress-bar { 
            width: 100%; 
            height: 20px; 
            background-color: #f0f0f0; 
            border-radius: 10px; 
            overflow: hidden; 
            margin: 8px 0;
        }
        .progress-fill { 
            height: 100%; 
            background-color: #4CAF50; 
            transition: width 0.3s ease;
        }
        .status { 
            padding: 8px; 
            margin: 8px 0; 
            border-radius: 5px; 
            font-weight: bold;
        }
        .status.ready { background-color: #d4edda; color: #155724; }
        .status.processing { background-color: #fff3cd; color: #856404; }
        .status.complete { background-color: #d4edda; color: #155724; }
        .status.error { background-color: #f8d7da; color: #721c24; }
        textarea { 
            width: 100%; 
            height: 180px; 
            padding: 8px; 
            border: 1px solid #ddd; 
            border-radius: 5px; 
            font-family: monospace; 
            font-size: 12px;
            resize: vertical;
            margin-bottom: 8px;
        }
        .hidden { display: none; }
        .save-btn { 
            background-color: #007bff; 
            font-size: 14px; 
            padding: 8px 16px;
        }
        .save-btn:hover { 
            background-color: #0056b3; 
        }
        label input[type="radio"] {
            margin-right: 5px;
        }
        label {
            cursor: pointer;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎥 Video Summarizer</h1>
        
        <div class="section">
            <h3>📁 Select Video File</h3>
            <input type="file" id="videoFile" accept="video/*" />
            <div id="fileName" style="margin-top: 10px; color: #666;"></div>
        </div>
        
        <div class="section">
            <h3>🔑 Gemini API Key</h3>
            <input type="password" id="apiKey" placeholder="Enter your Gemini API key here..." />
            <div style="margin-top: 10px;">
                <button onclick="testApiKey()">Test API Key</button>
                <button onclick="clearApiKey()" style="background-color: #dc3545; margin-left: 10px;">Clear Saved Key</button>
            </div>
            <div id="apiKeyStatus" style="margin-top: 5px; font-size: 12px; color: #666;"></div>
        </div>
        
        <div class="section">
            <button id="processBtn" onclick="processVideo()">🚀 Process Video</button>
            <div id="status" class="status ready">Ready</div>
            <div class="progress-bar">
                <div id="progressFill" class="progress-fill" style="width: 0%"></div>
            </div>
        </div>
        
        <div class="section">
            <h3>📝 Transcript</h3>
            <textarea id="transcript" placeholder="Transcript will appear here..."></textarea>
            <div style="margin-top: 10px;">
                <button class="save-btn" onclick="saveText('transcript')">💾 Save Transcript</button>
                <button class="save-btn" onclick="copyToClipboard('transcript')" style="background-color: #6c757d; margin-left: 10px;">📋 Copy Transcript</button>
            </div>
        </div>
        
        <div class="section">
            <h3>📏 Summary Length</h3>
            <div style="margin: 10px 0;">
                <label style="margin-right: 20px;">
                    <input type="radio" name="summaryLength" value="very short" checked> Very Short
                </label>
                <label style="margin-right: 20px;">
                    <input type="radio" name="summaryLength" value="short"> Short
                </label>
                <label style="margin-right: 20px;">
                    <input type="radio" name="summaryLength" value="medium"> Medium
                </label>
                <label>
                    <input type="radio" name="summaryLength" value="long"> Long
                </label>
            </div>
        </div>
        
        <div class="section">
            <h3>📋 Summary Format</h3>
            <div style="margin: 10px 0;">
                <label style="display: block; margin-bottom: 15px; padding: 10px; border: 1px solid #ddd; border-radius: 5px; background-color: #f9f9f9;">
                    <input type="radio" name="summaryFormat" value="format 1" checked style="margin-right: 10px;"> 
                    <strong>Format 1 (Executive Summary):</strong><br>
                    <span style="font-family: monospace; font-size: 12px; color: #666; margin-left: 25px; display: block; margin-top: 5px;">
                        Talking points:<br>
                        • Two parallel initiatives are underway: enhancing...<br>
                        • The documentation initiative introduces a new...<br>
                        • The collaboration workflow initiative encourages proactive...
                    </span>
                </label>
                <label style="display: block; margin-bottom: 15px; padding: 10px; border: 1px solid #ddd; border-radius: 5px; background-color: #f9f9f9;">
                    <input type="radio" name="summaryFormat" value="format 2" style="margin-right: 10px;"> 
                    <strong>Format 2 (Structured Meeting Notes):</strong><br>
                    <span style="font-family: monospace; font-size: 12px; color: #666; margin-left: 25px; display: block; margin-top: 5px;">
                        Talking points:<br>
                        • Workout recommendation engine update entering limited release January 10–11:<br>
                        &nbsp;&nbsp;• Results show dramatic quality improvement over current system<br>
                        &nbsp;&nbsp;• Production environment has critical infinite loop issue<br>
                        •  New “Today’s Focus” module under development for user homepage prototype:<br>
                        &nbsp;&nbsp;• Objective is to validate behavior triggers ahead of the Q2 personalized coaching launch
                    </span>
                </label>
                <label style="display: block; padding: 10px; border: 1px solid #ddd; border-radius: 5px; background-color: #f9f9f9;">
                    <input type="radio" name="summaryFormat" value="format 3" style="margin-right: 10px;"> 
                    <strong>Format 3 (Executive Summary - Narrative):</strong><br>
                    <span style="font-family: monospace; font-size: 12px; color: #666; margin-left: 25px; display: block; margin-top: 5px;">
                        The meeting centered around recent product performance metrics and strategic shifts in the roadmap...<br><br>
                        To maintain velocity on core initiatives, current engineering staffing levels will be preserved....
                    </span>
                </label>
            </div>
        </div>
        
        <div class="section">
            <h3>📋 Summary</h3>
            <textarea id="summary" placeholder="Summary will appear here..."></textarea>
            <div style="margin-top: 10px;">
                <button class="save-btn" onclick="saveText('summary')">💾 Save Summary</button>
                <button class="save-btn" onclick="copyToClipboard('summary')" style="background-color: #6c757d; margin-left: 10px;">📋 Copy Summary</button>
                <button id="regenerateBtn" class="save-btn" onclick="regenerateSummary()" style="background-color: #28a745; margin-left: 10px;" disabled>🔄 Regenerate Summary</button>
            </div>
        </div>
        
        <div class="section">
            <button onclick="clearAll()">🗑️ Clear All</button>
        </div>
    </div>

    <script>
        let processingInterval;
        
        // Load saved API key on page load
        window.addEventListener('load', function() {
            const savedApiKey = localStorage.getItem('gemini_api_key');
            if (savedApiKey) {
                document.getElementById('apiKey').value = savedApiKey;
                document.getElementById('apiKeyStatus').textContent = '✓ API key loaded from previous session';
                document.getElementById('apiKeyStatus').style.color = '#28a745';
            }
        });
        
        // Save API key when it changes
        document.getElementById('apiKey').addEventListener('input', function() {
            const apiKey = this.value;
            if (apiKey.trim()) {
                localStorage.setItem('gemini_api_key', apiKey);
                document.getElementById('apiKeyStatus').textContent = '💾 API key saved for next session';
                document.getElementById('apiKeyStatus').style.color = '#007bff';
            } else {
                localStorage.removeItem('gemini_api_key');
                document.getElementById('apiKeyStatus').textContent = '';
            }
        });
        
        function clearApiKey() {
            localStorage.removeItem('gemini_api_key');
            document.getElementById('apiKey').value = '';
            document.getElementById('apiKeyStatus').textContent = '🗑️ Saved API key cleared';
            document.getElementById('apiKeyStatus').style.color = '#dc3545';
            setTimeout(() => {
                document.getElementById('apiKeyStatus').textContent = '';
            }, 3000);
        }
        
        document.getElementById('videoFile').addEventListener('change', function(e) {
            const fileName = e.target.files[0] ? e.target.files[0].name : 'No file selected';
            document.getElementById('fileName').textContent = fileName;
        });
        
        function updateStatus(message, type = 'ready', progress = 0) {
            const statusEl = document.getElementById('status');
            const progressEl = document.getElementById('progressFill');
            
            statusEl.textContent = message;
            statusEl.className = `status ${type}`;
            progressEl.style.width = `${progress}%`;
        }
        
        function testApiKey() {
            const apiKey = document.getElementById('apiKey').value;
            if (!apiKey) {
                alert('Please enter your API key first');
                return;
            }
            
            updateStatus('Testing API key...', 'processing', 50);
            
            fetch('/test_api', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ api_key: apiKey })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    updateStatus('API key valid!', 'complete', 100);
                    setTimeout(() => updateStatus('Ready', 'ready', 0), 2000);
                } else {
                    updateStatus('API key invalid: ' + data.error, 'error', 0);
                }
            })
            .catch(error => {
                updateStatus('Error testing API key', 'error', 0);
            });
        }
        
        function processVideo() {
            const fileInput = document.getElementById('videoFile');
            const apiKey = document.getElementById('apiKey').value;
            const summaryLength = document.querySelector('input[name="summaryLength"]:checked').value;
            const summaryFormat = document.querySelector('input[name="summaryFormat"]:checked').value;
            
            if (!fileInput.files[0]) {
                alert('Please select a video file');
                return;
            }
            
            if (!apiKey) {
                alert('Please enter your API key');
                return;
            }
            
            const formData = new FormData();
            formData.append('video', fileInput.files[0]);
            formData.append('api_key', apiKey);
            formData.append('summary_length', summaryLength);
            formData.append('summary_format', summaryFormat);
            
            document.getElementById('processBtn').disabled = true;
            document.getElementById('transcript').value = '';
            document.getElementById('summary').value = '';
            
            updateStatus('Starting processing...', 'processing', 10);
            
            fetch('/process', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Start polling for progress
                    processingInterval = setInterval(checkProgress, 1000);
                } else {
                    updateStatus('Error: ' + data.error, 'error', 0);
                    document.getElementById('processBtn').disabled = false;
                }
            })
            .catch(error => {
                updateStatus('Error starting process', 'error', 0);
                document.getElementById('processBtn').disabled = false;
            });
        }
        
        function checkProgress() {
            fetch('/progress')
            .then(response => response.json())
            .then(data => {
                updateStatus(data.message, data.status === 'error' ? 'error' : 'processing', data.progress);
                
                if (data.status === 'complete') {
                    clearInterval(processingInterval);
                    document.getElementById('processBtn').disabled = false;
                    updateStatus('Processing complete!', 'complete', 100);
                    
                    // Get results
                    fetch('/results')
                    .then(response => response.json())
                    .then(results => {
                        document.getElementById('transcript').value = results.transcript;
                        document.getElementById('summary').value = results.summary;
                        
                        // Enable regenerate button after transcript is complete
                        document.getElementById('regenerateBtn').disabled = false;
                    });
                } else if (data.status === 'error') {
                    clearInterval(processingInterval);
                    document.getElementById('processBtn').disabled = false;
                }
            });
        }
        
        function regenerateSummary() {
            const apiKey = document.getElementById('apiKey').value;
            const summaryLength = document.querySelector('input[name="summaryLength"]:checked').value;
            const summaryFormat = document.querySelector('input[name="summaryFormat"]:checked').value;
            const transcript = document.getElementById('transcript').value;
            
            if (!apiKey) {
                alert('Please enter your API key');
                return;
            }
            
            if (!transcript.trim()) {
                alert('No transcript available to summarize');
                return;
            }
            
            // Disable regenerate button
            document.getElementById('regenerateBtn').disabled = true;
            document.getElementById('regenerateBtn').textContent = '🔄 Regenerating...';
            
            updateStatus('Regenerating summary...', 'processing', 50);
            
            fetch('/regenerate_summary', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    api_key: apiKey,
                    summary_length: summaryLength,
                    summary_format: summaryFormat,
                    transcript: transcript
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    document.getElementById('summary').value = data.summary;
                    updateStatus('Summary regenerated!', 'complete', 100);
                    setTimeout(() => updateStatus('Ready', 'ready', 0), 2000);
                } else {
                    updateStatus('Error regenerating summary: ' + data.error, 'error', 0);
                }
            })
            .catch(error => {
                updateStatus('Error regenerating summary', 'error', 0);
            })
            .finally(() => {
                // Re-enable regenerate button
                document.getElementById('regenerateBtn').disabled = false;
                document.getElementById('regenerateBtn').textContent = '🔄 Regenerate Summary';
            });
        }
        
        function copyToClipboard(type) {
            const text = document.getElementById(type).value;
            if (!text.trim()) {
                alert(`No ${type} to copy`);
                return;
            }
            
            navigator.clipboard.writeText(text).then(() => {
                // Show temporary success message
                const button = document.querySelector(`button[onclick="copyToClipboard('${type}')"]`);
                const originalText = button.textContent;
                button.textContent = '✓ Copied!';
                button.style.backgroundColor = '#28a745';
                
                setTimeout(() => {
                    button.textContent = originalText;
                    button.style.backgroundColor = '#6c757d';
                }, 1500);
            }).catch(err => {
                alert('Failed to copy to clipboard');
                console.error('Copy failed:', err);
            });
        }
        
        function saveText(type) {
            const text = document.getElementById(type).value;
            if (!text.trim()) {
                alert(`No ${type} to save`);
                return;
            }
            
            const blob = new Blob([text], { type: 'text/plain' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `${type}.txt`;
            a.click();
            URL.revokeObjectURL(url);
        }
        
        function clearAll() {
            document.getElementById('videoFile').value = '';
            // Don't clear API key - it should persist
            document.getElementById('transcript').value = '';
            document.getElementById('summary').value = '';
            document.getElementById('fileName').textContent = '';
            document.getElementById('regenerateBtn').disabled = true;
            updateStatus('Ready', 'ready', 0);
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/test_api', methods=['POST'])
def test_api():
    try:
        data = request.json
        api_key = data.get('api_key')
        
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents="Hello, this is a test. Please respond with 'API key works!'"
        )
        
        return jsonify({"success": True, "response": response.text})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/process', methods=['POST'])
def process():
    try:
        global processing_status, current_transcript, current_summary
        
        video_file = request.files['video']
        api_key = request.form['api_key']
        summary_length = request.form['summary_length']
        summary_format = request.form['summary_format']
        
        # Reset status
        processing_status = {"status": "processing", "progress": 20, "message": "Processing started..."}
        current_transcript = ""
        current_summary = ""
        
        # Save uploaded file
        temp_dir = tempfile.gettempdir()
        video_path = os.path.join(temp_dir, video_file.filename)
        video_file.save(video_path)
        
        # Start processing in background thread
        thread = threading.Thread(target=process_video_thread, args=(video_path, api_key, summary_length, summary_format))
        thread.daemon = True
        thread.start()
        
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/progress')
def progress():
    return jsonify(processing_status)

@app.route('/regenerate_summary', methods=['POST'])
def regenerate_summary():
    try:
        data = request.json
        api_key = data.get('api_key')
        summary_length = data.get('summary_length')
        summary_format = data.get('summary_format')
        transcript = data.get('transcript')
        
        if not api_key or not transcript:
            return jsonify({"success": False, "error": "Missing API key or transcript"})
        
        client = genai.Client(api_key=api_key)
        
        prompt = f"""I need to make you the summary of the meeting. It should look like the example.

Format (format 1 or format 2 or format 3): {summary_format}
Length of the summary (very short, short, medium, long): {summary_length}

Format guidelines:
- Format 1 (Executive Summary): Organized with bullet points. All bullet points at the equal level. Always starts with 'Talking points:'. Each bullet points starts with character •
- Format 2 (Structured Meeting Notes): Organized with bullet points. one bullet point can have one or few subbullet points. Always starts with 'Talking points:'. Each bullet points starts with character •
- Format 3 (Executive Summary): A concise narrative format, divided by paragraphs. Do NOT use any bullet points or asterisk (*)!
Length guidelines:
- Very short: Maximum 3-5 main talking points, each with only 1-2 bullet points. Focus on the most critical decisions and next steps only.
- Short: 5-8 main talking points with 2-3 bullet points each. Include key decisions, main discussions, and important next steps.
- Medium: 8-12 main talking points with 3-4 bullet points each. Include detailed discussions, background context, and comprehensive next steps.
- Long: 12+ main talking points with 4+ bullet points each. Include all discussions, full context, detailed explanations, and comprehensive action items.

Please format it as an example and in your answer and just write summary, nothing like 'here you go:

EXAMPLE Format 1:
Talking points:
• Two parallel initiatives are underway: enhancing internal documentation practices and refining cross-team collaboration workflows.
• The documentation initiative introduces a new Notion-based template system, designed to improve onboarding and reduce duplicate knowledge. Early feedback highlights better clarity and discoverability.
• The collaboration workflow initiative encourages proactive alignment during planning phases. The pilot use case is the re-architecture of the Notification Queue, coordinated by Priya.
• The Web team is evaluating whether to refactor the current alert system now or wait until the Q4 performance sprint to consolidate efforts.
• The Slackbot automation pilot has concluded after three iterations. Insights were captured in Confluence, and the team agreed to sunset the bot. The underlying scripts will be deprecated to reduce maintenance overhead.

EXAMPLE Format 2:
Talking points:
• Workout recommendation engine update entering limited release January 10–11:
  • Early tests show strong accuracy improvements over legacy logic
  • Deployment pipeline has a critical timeout issue that must be resolved before rollout
  • Maya will collaborate with Leo to debug deployment blocker offline
• New “Today’s Focus” module under development for user homepage prototype:
  • Objective is to validate behavior triggers ahead of the Q2 personalized coaching launch
  • Initial version will act as a dynamic widget with A/B support for motivational prompts
  • Jenna will finalize feature specs after her strategy sync in San Francisco this week
• Team member updates:
  • Leo: Wrapped backend latency audit, now focused on error tracing for batch endpoints
  • Sarah: Completing frontend edge-case QA for hydration tracker
  • James: Finalizing Android biometric auth issues, then resuming image compression tasks
  • Ren: Investigating user session drop-offs and preparing patch for event queue instability
  • Tanya: Implementing new calendar sync logic and cross-platform UI consistency checks
  • Marcus: Workout summary redesign in final stages, polishing animation timing and layout spacing

EXAMPLE Format 3:
The meeting centered around recent product performance metrics and strategic shifts in the roadmap. A decline in user engagement on the mobile app prompted the leadership team to pause development on two lesser-used features and reallocate resources.

To maintain velocity on core initiatives, current engineering staffing levels will be preserved. The team discussed shifting ownership of parts of the Analytics pipeline and Notification System to ensure better alignment with growth goals.

The Helix and Orbit integrations will be sunsetted next quarter, which will reduce complexity but temporarily limit some partner functionality. Over the next month, the team will join cross-functional sessions to help shape the updated product vision and long-term KPIs.

Leadership acknowledged ongoing tensions around roadmap clarity, reiterating that near-term focus will be on initiatives tied directly to user retention and daily active usage growth.

Here is the transcript to summarize:
{transcript}"""
        
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        
        return jsonify({"success": True, "summary": response.text})
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/results')
def results():
    return jsonify({"transcript": current_transcript, "summary": current_summary})

def process_video_thread(video_path, api_key, summary_length, summary_format):
    global processing_status, current_transcript, current_summary, whisper_model
    
    try:
        print(f"Starting video processing for: {video_path}")
        
        # Check if FFmpeg is available
        try:
            ffmpeg_check = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True, timeout=10)
            if ffmpeg_check.returncode != 0:
                raise Exception("FFmpeg not found")
            print("FFmpeg is available")
        except Exception as e:
            print(f"FFmpeg check failed: {e}")
            processing_status = {"status": "error", "progress": 0, "message": f"FFmpeg not available: {str(e)}"}
            return
        
        # Step 1: Convert to audio
        print("Converting video to audio...")
        processing_status = {"status": "processing", "progress": 30, "message": "Converting video to audio..."}
        audio_path = os.path.join(tempfile.gettempdir(), "temp_audio.mp3")
        
        cmd = ["ffmpeg", "-y", "-i", video_path, "-vn", "-acodec", "mp3", "-ar", "16000", audio_path]
        print(f"Running FFmpeg command: {' '.join(cmd)}")
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)  # 5 minute timeout
        
        if result.returncode != 0:
            print(f"FFmpeg stderr: {result.stderr}")
            raise Exception(f"FFmpeg error: {result.stderr}")
        
        print(f"Audio conversion complete: {audio_path}")
        
        # Check if audio file was created
        if not os.path.exists(audio_path):
            raise Exception("Audio file was not created")
        
        # Step 2: Transcribe
        print("Loading Whisper model...")
        processing_status = {"status": "processing", "progress": 60, "message": "Transcribing audio..."}
        
        if whisper_model is None:
            print("Loading Whisper base model...")
            whisper_model = whisper.load_model("base")
            print("Whisper model loaded")
        
        print("Starting transcription...")
        result = whisper_model.transcribe(audio_path)
        current_transcript = result["text"]
        print(f"Transcription complete. Length: {len(current_transcript)} characters")
        
        # Step 3: Summarize
        print("Generating summary...")
        processing_status = {"status": "processing", "progress": 80, "message": "Generating summary..."}
        
        client = genai.Client(api_key=api_key)
        
        prompt = f"""I need to make you the summary of the meeting. It should look like the example.

Format (format 1 or format 2 or format 3): {summary_format}
Length of the summary (very short, short, medium, long): {summary_length}

Format guidelines:
- Format 1 (Executive Summary): Organized with bullet points. All bullet points at the equal level. Always starts with 'Talking points:'. Each bullet points starts with character •
- Format 2 (Structured Meeting Notes): Organized with bullet points. one bullet point can have one or few subbullet points. Always starts with 'Talking points:'. Each bullet points starts with character •
- Format 3 (Executive Summary): A concise narrative format, divided by paragraphs. Do NOT use any bullet points or asterisk (*)!
Length guidelines:
- Very short: Maximum 3-5 main talking points, each with only 1-2 bullet points. Focus on the most critical decisions and next steps only.
- Short: 5-8 main talking points with 2-3 bullet points each. Include key decisions, main discussions, and important next steps.
- Medium: 8-12 main talking points with 3-4 bullet points each. Include detailed discussions, background context, and comprehensive next steps.
- Long: 12+ main talking points with 4+ bullet points each. Include all discussions, full context, detailed explanations, and comprehensive action items.

Please format it as an example and in your answer and just write summary, nothing like 'here you go:

EXAMPLE Format 1:
Talking points:
• Two parallel initiatives are underway: enhancing internal documentation practices and refining cross-team collaboration workflows.
• The documentation initiative introduces a new Notion-based template system, designed to improve onboarding and reduce duplicate knowledge. Early feedback highlights better clarity and discoverability.
• The collaboration workflow initiative encourages proactive alignment during planning phases. The pilot use case is the re-architecture of the Notification Queue, coordinated by Priya.
• The Web team is evaluating whether to refactor the current alert system now or wait until the Q4 performance sprint to consolidate efforts.
• The Slackbot automation pilot has concluded after three iterations. Insights were captured in Confluence, and the team agreed to sunset the bot. The underlying scripts will be deprecated to reduce maintenance overhead.

EXAMPLE Format 2:
Talking points:
• Workout recommendation engine update entering limited release January 10–11:
  • Early tests show strong accuracy improvements over legacy logic
  • Deployment pipeline has a critical timeout issue that must be resolved before rollout
  • Maya will collaborate with Leo to debug deployment blocker offline
• New “Today’s Focus” module under development for user homepage prototype:
  • Objective is to validate behavior triggers ahead of the Q2 personalized coaching launch
  • Initial version will act as a dynamic widget with A/B support for motivational prompts
  • Jenna will finalize feature specs after her strategy sync in San Francisco this week
• Team member updates:
  • Leo: Wrapped backend latency audit, now focused on error tracing for batch endpoints
  • Sarah: Completing frontend edge-case QA for hydration tracker
  • James: Finalizing Android biometric auth issues, then resuming image compression tasks
  • Ren: Investigating user session drop-offs and preparing patch for event queue instability
  • Tanya: Implementing new calendar sync logic and cross-platform UI consistency checks
  • Marcus: Workout summary redesign in final stages, polishing animation timing and layout spacing

EXAMPLE Format 3:
The meeting centered around recent product performance metrics and strategic shifts in the roadmap. A decline in user engagement on the mobile app prompted the leadership team to pause development on two lesser-used features and reallocate resources.

To maintain velocity on core initiatives, current engineering staffing levels will be preserved. The team discussed shifting ownership of parts of the Analytics pipeline and Notification System to ensure better alignment with growth goals.

The Helix and Orbit integrations will be sunsetted next quarter, which will reduce complexity but temporarily limit some partner functionality. Over the next month, the team will join cross-functional sessions to help shape the updated product vision and long-term KPIs.

Leadership acknowledged ongoing tensions around roadmap clarity, reiterating that near-term focus will be on initiatives tied directly to user retention and daily active usage growth.

Here is the transcript to summarize:
{current_transcript}"""
        
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        current_summary = response.text
        print(f"Summary generated. Length: {len(current_summary)} characters")
        
        # Cleanup
        try:
            if os.path.exists(video_path):
                os.remove(video_path)
                print("Video file cleaned up")
            if os.path.exists(audio_path):
                os.remove(audio_path)
                print("Audio file cleaned up")
        except Exception as cleanup_error:
            print(f"Cleanup error: {cleanup_error}")
        
        processing_status = {"status": "complete", "progress": 100, "message": "Processing complete!"}
        print("Processing completed successfully!")
        
    except Exception as e:
        print(f"Error in process_video_thread: {e}")
        processing_status = {"status": "error", "progress": 0, "message": f"Error: {str(e)}"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    debug = os.environ.get("FLASK_ENV") == "development"
    
    print("Starting Video Summarizer Web App...")
    print("Install required packages: pip install -r requirements.txt")
    print("Make sure ffmpeg is installed")
    print("")
    print(f"Server will start on port {port}")
    print("Once started, try these URLs:")
    print(f"- http://localhost:{port}")
    print(f"- http://127.0.0.1:{port}")
    print("")
    
    # Production-ready Flask settings
    app.run(debug=debug, host='0.0.0.0', port=port, threaded=True)