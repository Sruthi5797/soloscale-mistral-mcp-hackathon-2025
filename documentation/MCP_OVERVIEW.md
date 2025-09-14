# Yoga Class Sequencing MCP Server - Quick Guide

## What This Does

The Yoga Class Sequencing MCP Server generates personalized yoga class sequences with free offline text-to-speech audio instructions. It runs completely locally with no API costs.

## Key Tools

### 1. `create_yoga_sequence`
- Creates complete yoga sequences based on duration, level, and style
- Supports hatha, vinyasa, and stress relief yoga styles
- Includes Sanskrit names and proper time allocation

### 2. `generate_pose_procedure`
- Provides detailed step-by-step instructions for any yoga pose
- Includes alignment cues, breathing guidance, and safety tips
- Adapts to beginner, intermediate, or advanced levels

### 3. `generate_pose_audio_with_piper`
- Creates audio instructions using free offline Piper TTS
- Delivers audio as base64 data, download link, or saved file
- No internet required, completely private

### 4. `generate_piper_web_demo_link`
- Creates a link to the Piper web demo with pre-filled yoga instructions
- Browser-based alternative to local Piper installation
- Simple click-to-generate workflow for users

### 5. `generate_class_theme`
- Creates seasonal themes and intentions for yoga classes
- Provides opening and closing guidance text

## Setup Requirements

### Basic Setup
1. Install required packages: `pip install fastmcp piper-tts`
2. Download voice models: Create a `models` directory and download the en_US-amy-medium.onnx model
3. Run server: `python main.py`

### Important Notes
- All processing happens locally - no internet needed
- No API keys required
- Voice models are downloaded automatically on first use

## Quick Examples

```
# Create a yoga sequence
"Create a 30-minute beginner hatha sequence for strength"

# Generate audio for a pose
"Generate audio for Mountain Pose with breathing cues"

# Create a class theme
"Create a spring-themed intention for 45-minute vinyasa practice"
```

## Supported Yoga Styles
- **Hatha**: Traditional poses with longer holds (beginner, intermediate)
- **Vinyasa**: Flow-based practice with breath synchronization (beginner, intermediate)
- **Stress Relief**: Gentle, restorative practice (all levels)

## Audio Output Options

### Base64 Data
- Returns audio as base64-encoded data
- Best for web applications or direct streaming
- Use output_preference="base64_data"

### Download Link
- Creates a downloadable audio file
- Returns file location and metadata
- Use output_preference="download_link"

### User-Specified Path
- Saves audio to a specified directory
- Allows custom file organization
- Use output_preference="save_to_user_path"

### Piper Web Demo (NEW)
- Creates a link to the Piper web demo with pre-filled text
- No local Piper installation required - runs in browser
- Users click link, then click "Synthesize" on the web page
- Includes fallback description text in case link pre-filling doesn't work
- Use the `generate_piper_web_demo_link` tool

## Troubleshooting

If you encounter "Read-only file system" errors in cloud environments:
- Use "base64_data" output preference instead
- Extract and save base64 data using the client

For timeout errors:
- Reduce audio length
- Ensure voice models are downloaded
- Check server timeout settings

## Resources

- MCP Documentation: https://modelcontextprotocol.github.io/
- Piper TTS: https://github.com/rhasspy/piper
- Voice models: https://huggingface.co/rhasspy/piper-voices

## Client Code Example

### Process Audio in Python
```python
import base64
import json

# Process MCP response
def save_yoga_audio(response_json, output_file="yoga_pose.wav"):
    data = json.loads(response_json)
    
    # Extract base64 content from response
    if "audio_data" in data and "base64_content" in data["audio_data"]:
        audio_base64 = data["audio_data"]["base64_content"]
        
        # Decode and save
        with open(output_file, "wb") as f:
            f.write(base64.b64decode(audio_base64))
        
        print(f"✅ Saved to {output_file}")
    else:
        print("❌ No audio data found")
```

### Using the Piper Web Demo Link
```python
import json
import webbrowser
import pyperclip  # For clipboard operations (pip install pyperclip)

# Open Piper web demo from MCP response
def open_piper_web_demo(response_json):
    data = json.loads(response_json)
    
    # Check if audio link is available
    if "audio" in data and "link" in data["audio"]:
        web_url = data["audio"]["link"]
        print(f"Opening Piper web demo with pre-filled text...")
        webbrowser.open(web_url)
        
        # Copy fallback description to clipboard for easy pasting
        if "fallback" in data and "description_text" in data["fallback"]:
            fallback_text = data["fallback"]["description_text"]
            pyperclip.copy(fallback_text)
            print("✅ Description text copied to clipboard as a fallback")
        
        print("Instructions:")
        print("1. Click 'Synthesize' on the web page")
        print("2. If text is not pre-filled, paste from clipboard")
        print("3. Use the download button (⬇️) to save the audio")
    else:
        print("❌ No web demo link found in response")
```

### LeChat Agent Prompt
For a simple agent to handle audio in Mistral LeChat:

```
You help users create yoga audio files. When asked for pose audio:
1. Call generate_pose_audio_with_piper with output_preference="base64_data"
2. Use code-interpreter to save the file:

```python
import base64
audio_base64 = response["audio_data"]["base64_content"]
with open("pose_name.wav", "wb") as f:
    f.write(base64.b64decode(audio_base64))
```
```
