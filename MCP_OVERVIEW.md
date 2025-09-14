# Yoga Class Sequencing MCP Server - Component Overview

## Server Description

The Yoga Class Sequencing MCP Server is an intelligent yoga instruction assistant that generates personalized yoga class sequences with free offline Piper TTS integration. It creates structured sequences, provides embeddable calming audio instructions, and generates inspiring class themes with complete privacy and no API costs.

## MCP Components

### 🛠️ Tools (5)

#### `create_yoga_sequence`
**Purpose**: Generate a complete, personalized yoga class sequence

**Inputs**:
- `duration_minutes` (5-90): Total class duration
- `level`: Student experience (beginner/intermediate/advanced)
- `style`: Practice type (hatha/vinyasa/stress_relief)
- `focus`: Optional specialization (hip_opening, backbends, strength, flexibility)

**Output**: Structured sequence including:
- Class metadata (duration, level, style, focus)
- Time-allocated sections with enhanced pose data (including Sanskrit names)
- Total pose count and time breakdown
- Ready for audio instruction integration

**Key Features**:
- Intelligent time distribution based on yoga style
- Enhanced pose data with Sanskrit names and expertise levels
- Automatic pose selection for optimal pacing
- Validation of inputs with helpful error messages
- Style-appropriate section organization

#### `generate_pose_procedure`
**Purpose**: Generate detailed step-by-step instructions for yoga poses using AI

**Inputs**:
- `pose_name`: English name of the yoga pose
- `sanskrit_name`: Sanskrit name (optional)
- `expertise_level`: Difficulty level (Beginner/Intermediate/Advanced)
- `include_modifications`: Include modifications and variations (true/false)

**Output**: Comprehensive pose information including:
- Detailed step-by-step procedure text
- Alignment cues and safety tips
- Breathing guidance
- Modifications and variations
- Benefits and contraindications

**Key Features**:
- Enhanced with OpenAI TTS model integration
- Professional yoga instruction formatting
- Expertise-level appropriate instructions
- Safety-focused guidance

#### `generate_pose_audio_with_piper`
**Purpose**: Generate free offline calming audio instructions for yoga poses with user-friendly delivery options

**Inputs**:
- `asana_name`: Name of the yoga pose
- `voice`: Calming voice selection (en_US-amy-medium)
- `include_breathing_cues`: Add simple breathing guidance (true/false)
- `output_preference`: How to deliver audio ('download_link', 'base64_data', 'save_to_user_path')
- `user_save_path`: User's preferred save directory (only used if output_preference is 'save_to_user_path')

**Output**: User-friendly audio package including:
- **Download Link**: Simple download instructions for generated audio file
- **Base64 Data**: Encoded audio data for direct application use
- **User Save Path**: Audio saved to user's specified directory
- **Metadata**: Audio format details and usage instructions

**Key Features**:
- **Completely Free**: No API costs - runs entirely offline
- **Multiple Output Formats**: Embedded, downloadable, or both
- **Web-Ready**: Direct HTML5 audio element generation
- **Cross-Platform**: Works on any device with WAV support
- **Privacy-First**: All processing happens locally
- **High Quality**: 22.05 kHz, 16-bit, mono WAV audio
- **Streaming Capable**: In-memory processing without disk dependencies
- **Calming Voices**: Multiple soothing voice options for relaxation

#### `generate_tts_script`
**Purpose**: Generate TTS-compatible scripts for yoga poses that work with any text-to-speech service (Mistral LeChat Compatible)

**Inputs**:
- `asana_name`: Name of the yoga pose
- `include_breathing_cues`: Add breathing guidance (true/false)
- `output_format`: Script format ('ssml', 'plain_text', 'timed_markers', 'json_structured')
- `voice_instructions`: Voice guidance ('slow_calm', 'gentle_female', 'meditation_style')
- `duration_target`: Target duration in seconds (15-90)

**Output**: Multiple format options including:
- **SSML Format**: Speech Synthesis Markup Language for advanced TTS
- **Plain Text**: Clean text ready for any TTS service
- **Timed Markers**: Text with pause and emphasis markers
- **JSON Structured**: Structured data for programmatic TTS integration
- **Mistral LeChat Ready**: Formatted specifically for Mistral's TTS capabilities

**Key Features**:
- **Universal Compatibility**: Works with any TTS service or AI assistant
- **Multiple Output Formats**: Choose the best format for your platform
- **Mistral LeChat Optimized**: Special formatting for Mistral's text-to-speech
- **Timing Control**: Adjustable pace and pauses for meditation
- **Voice Guidance**: Instructions for different voice styles
- **No Dependencies**: Pure text output, no audio files needed
- **Copy-Paste Ready**: Direct integration with external TTS services

### 📚 Resources (2)

#### `pose_library`
**URI Pattern**: `pose://library/{style}/{level}`

**Purpose**: Access comprehensive yoga pose database with Sanskrit names and expertise levels

**Use Cases**:
- Browse poses by style and difficulty level
- Access Sanskrit names and pronunciations
- Understand pose modifications and variations

**Output**: Enhanced pose data including English names, Sanskrit names, and expertise levels

#### `sequence_templates`
**URI Pattern**: `sequence://template/{style}/{level}`

**Purpose**: Access raw sequence templates for inspection and customization

**Use Cases**:
- Understanding the structure of different yoga styles
- Inspecting available poses for each level
- Template-based customization for specialized classes

**Output**: JSON representation of enhanced pose templates organized by sequence sections

### 💡 Prompts (1)

#### `generate_class_theme`
**Purpose**: Create inspiring themes and intentions for yoga classes

**Inputs**:
- `style`: Yoga practice style
- `duration`: Class length in minutes
- `season`: Current season for theming (spring/summer/fall/winter)
- `intention`: Desired focus or intention

**Output**: Complete theme package including:
- Seasonal-appropriate class title
- Opening intention with guidance
- Closing reflection for integration
- Music suggestions that complement the theme

**Features**:
- Season-aware theming with appropriate energy
- Style-specific theme selection
- Professional language for yoga instruction
- Complete class arc from opening to closing

## Key Features

### 🎯 Enhanced Pose Data
- **Sanskrit Integration**: All poses include traditional Sanskrit names
- **Expertise Levels**: Clear difficulty classifications (Beginner/Intermediate/Advanced)
- **Professional Structure**: Organized by practice style and sequence sections

### 🔊 Free Offline Piper TTS Integration
- **Zero Cost Audio**: Completely free offline text-to-speech using Piper TTS
- **Multiple Output Formats**: Embedded, downloadable, or both formats
- **Web-Ready Integration**: Direct HTML5 audio elements and data URIs
- **Privacy-First**: All processing happens locally with no external API calls
- **High-Quality Voices**: Multiple calming voice options (lessac, amy)
- **Streaming Capable**: In-memory audio processing for immediate playback
- **Cross-Platform**: WAV format compatible with all modern devices and browsers

### ⚡ Intelligent Automation
- **Time-Aware Sequencing**: Automatic pose selection based on available time
- **Style-Specific Logic**: Different algorithms for Hatha, Vinyasa, and Stress Relief
- **Error Handling**: Graceful fallback when API services unavailable

## Setup Requirements

### Basic Functionality
- All core features work immediately
- Pose library and sequence generation ready
- Class theme creation available

### Audio Features (Free Offline)
- **No API Keys Required**: Audio generation works completely offline
- **Automatic Setup**: Piper TTS models download automatically when needed
- **Zero Ongoing Costs**: Free audio generation with no usage limits
- **Privacy-First**: All audio processing happens locally on your device

### Piper TTS Voice Models (Auto-Downloaded)
- **en_US-lessac-medium**: Calm, clear female voice (recommended)
- **en_US-amy-medium**: Gentle, soothing female voice
- **Additional voices**: Easy to add more voices as needed

## Integration Benefits

- **For Yoga Instructors**: Free sequence generation with unlimited embedded audio instructions
- **For Students**: Personalized practice with offline audio guidance and Sanskrit learning
- **For Web Apps**: Ready-to-embed HTML5 audio elements with no external dependencies
- **For Mobile Apps**: High-quality WAV audio files for native playback integration
- **For AI Assistants**: Rich yoga knowledge with free, privacy-first audio capabilities

This MCP server combines traditional yoga wisdom with modern offline AI capabilities, providing intelligent sequencing and completely free embedded audio instruction through Piper TTS integration.

## Quick Start Examples

### Create a Basic Sequence
```
"Create a 30-minute beginner hatha yoga sequence focused on strength"
```

### Get Embedded Audio Instructions
```
"Generate embedded audio for Mountain Pose with breathing cues using generate_pose_audio_with_piper"
```

### Generate Class Theme
```
"Create a spring-themed class intention for 45-minute vinyasa practice"
```

## Supported Yoga Styles

### Hatha Yoga
- **Focus**: Traditional poses held with mindful breathing
- **Sections**: Warm-up → Standing → Seated → Backbends → Cool-down
- **Levels**: Beginner, Intermediate

### Vinyasa Yoga  
- **Focus**: Flowing movement synchronized with breath
- **Sections**: Warm-up → Flow → Peak → Cool-down
- **Levels**: Beginner, Intermediate

### Stress Relief Yoga
- **Focus**: Gentle, restorative practice for relaxation
- **Sections**: Grounding → Gentle → Restorative → Relaxation
- **Levels**: All Levels (universal accessibility)

## Sample Use Cases

### 🧘 Basic Sequence Creation
- `"30-minute beginner hatha sequence for strength"`
- `"Create 45-minute vinyasa flow for hip opening"`
- `"Design gentle 20-minute stress relief practice"`
- `"Generate intermediate 60-minute backbend sequence"`

### 🔊 Embedded Audio Generation (Web/App Integration)
- `"Generate embedded audio for Mountain Pose with breathing cues"`
- `"Create embeddable audio for Child's Pose using lessac voice"`
- `"Make HTML5 audio element for Downward Dog with calming instructions"`
- `"Generate web-ready audio for final Savasana relaxation"`

### 💾 Downloadable Audio Creation (Offline Use)
- `"Create downloadable audio for Warrior II with breathing guidance"`
- `"Generate WAV file for Sun Salutation sequence with amy voice"`
- `"Make offline audio instructions for seated meditation"`
- `"Create local audio files for home yoga practice"`

### 🎯 Dual Format Audio (Maximum Flexibility)
- `"Generate both embedded and downloadable audio for Tree Pose"`
- `"Create web and offline audio for complete yoga sequence"`
- `"Make dual-format audio for yoga teacher training materials"`
- `"Generate streaming and download audio for mobile app integration"`

### 🎨 Complete Class Planning with Audio
- `"Plan 45-minute stress relief class with embedded audio for each pose"`
- `"Design hatha sequence with downloadable audio instructions"`
- `"Create themed vinyasa class with web-ready audio elements"`
- `"Generate complete practice with both embedded and offline audio"`

### 🌐 Web Development Integration
- `"Create HTML5 audio elements for yoga website"`
- `"Generate data URIs for React yoga app components"`
- `"Make embeddable audio for online yoga courses"`
- `"Create streaming audio for progressive web app"`

### 📱 Mobile App Development
- `"Generate WAV files for iOS yoga app"`
- `"Create audio assets for Android meditation app"`
- `"Make offline audio library for yoga mobile platform"`
- `"Generate high-quality audio for native app integration"`

### 🏠 Personal Practice
- `"Create personal audio library for home yoga practice"`
- `"Generate offline audio guidance for daily meditation"`
- `"Make custom audio instructions for rehabilitation poses"`
- `"Create personalized breathing exercise audio"`

### 🧑‍🏫 Yoga Instructor Tools
- `"Generate audio demonstrations for yoga teacher training"`
- `"Create instructional audio library for class preparation"`
- `"Make audio cues for virtual yoga class streaming"`
- `"Generate pronunciation guides for Sanskrit pose names"`

### 🔄 Advanced Audio Workflows
- `"Create batch audio generation for complete pose library"`
- `"Generate multi-voice audio comparisons for pose variations"`
- `"Make sequential audio instructions for flow sequences"`
- `"Create layered audio with pose instructions and ambient sounds"`

### 🤖 Mistral LeChat Compatible Audio
- `"Generate TTS script for Mountain Pose in SSML format"`
- `"Create plain text audio script for Child's Pose with breathing cues"`
- `"Make Mistral LeChat ready audio instructions for Warrior II"`
- `"Generate structured JSON audio script for complete sun salutation"`

### 📝 TTS Script Generation (Universal)
- `"Create SSML script for Tree Pose with voice emphasis markers"`
- `"Generate plain text audio for meditation sequence"`
- `"Make timed audio script for breathing exercise with pause markers"`
- `"Create copy-paste ready TTS text for yoga class introduction"`

### 🔄 Multi-Platform Audio Scripts
- `"Generate audio scripts in multiple formats for Downward Dog"`
- `"Create TTS-ready content for Google Cloud Speech"`
- `"Make Amazon Polly compatible script for relaxation sequence"`
- `"Generate Azure Speech Service ready audio instructions"`

## Technical Specifications

### Audio Output Formats

#### Base64 Data Format (`output_preference="base64_data"`)
```json
{
  "audio_data": {
    "base64_content": "UklGRiR6BwBXQVZF...",
    "encoding": "base64",
    "format": "wav",
    "size_bytes": 490028,
    "usage_instructions": "Decode base64 to get WAV audio data",
    "ready_for_streaming": true
  }
}
```

#### Download Link Format (`output_preference="download_link"`)
```json
{
  "download_info": {
    "message": "Audio file ready for download",
    "filename": "yoga_mountain_pose_en_US-amy-medium.wav",
    "file_size_kb": 478.5,
    "download_ready": true,
    "user_instructions": "Your audio file has been generated and is ready for download",
    "file_location": "Saved in temp_downloads directory"
  }
}
```

#### User Save Path Format (`output_preference="save_to_user_path"`)
```json
{
  "save_info": {
    "saved": true,
    "filepath": "/user/specified/path/yoga_mountain_pose_en_US-amy-medium.wav",
    "filename": "yoga_mountain_pose_en_US-amy-medium.wav",
    "directory": "/user/specified/path",
    "file_size_kb": 478.5,
    "message": "Audio saved to your specified location"
  }
}
```

### Audio Quality Specifications
- **Sample Rate**: 22,050 Hz (high quality for voice)
- **Bit Depth**: 16-bit (CD quality)
- **Channels**: Mono (optimized for voice)
- **Format**: WAV (universal compatibility)
- **Encoding**: Base64 for embedded, binary for download
- **File Size**: ~490 KB for typical 30-60 second instructions

### Voice Options
- **en_US-amy-medium**: Clear, calm female voice (recommended for yoga instruction)
- **en_US-amy-medium**: Gentle, soothing female voice
- **Custom voices**: Easy to add additional Piper TTS voices

### TTS Script Output Formats (Mistral LeChat Compatible)

#### SSML Format (`output_format="ssml"`)
```xml
<speak>
    <emphasis level="moderate">Welcome to Mountain Pose</emphasis>
    <break time="1s"/>
    Stand tall with your feet together
    <break time="2s"/>
    <prosody rate="slow">Take a deep breath in through your nose</prosody>
    <break time="3s"/>
    And slowly exhale through your mouth
    <break time="2s"/>
    Feel grounded and strong
</speak>
```

#### Plain Text Format (`output_format="plain_text"`)
```
Welcome to Mountain Pose. Stand tall with your feet together. Take a deep breath in through your nose... and slowly exhale through your mouth. Feel grounded and strong in this foundational pose.
```

#### Timed Markers Format (`output_format="timed_markers"`)
```
[SLOW] Welcome to Mountain Pose [PAUSE:1s]
Stand tall with your feet together [PAUSE:2s]
[EMPHASIS] Take a deep breath in through your nose [PAUSE:3s]
[GENTLE] And slowly exhale through your mouth [PAUSE:2s]
Feel grounded and strong [END]
```

#### JSON Structured Format (`output_format="json_structured"`)
```json
{
  "pose_name": "Mountain Pose",
  "total_duration": 45,
  "voice_style": "calm_female",
  "segments": [
    {
      "text": "Welcome to Mountain Pose",
      "duration": 3,
      "emphasis": "moderate",
      "pause_after": 1
    },
    {
      "text": "Stand tall with your feet together",
      "duration": 4,
      "pace": "normal",
      "pause_after": 2
    },
    {
      "text": "Take a deep breath in through your nose",
      "duration": 6,
      "pace": "slow",
      "breathing_cue": true,
      "pause_after": 3
    }
  ]
}
```

#### Mistral LeChat Ready Format
```
🧘 Mountain Pose Audio Script

Voice Instructions: Use a calm, gentle female voice at 0.9x speed

Script:
"Welcome to Mountain Pose... [pause for 1 second]
Stand tall with your feet together... [pause for 2 seconds]  
Take a deep breath in through your nose... [pause for 3 seconds]
And slowly exhale through your mouth... [pause for 2 seconds]
Feel grounded and strong in this foundational pose."

Copy this text to Mistral LeChat and request: "Please convert this to speech with the specified voice settings"
```

### Alternative TTS Integration Methods

#### Method 1: Mistral LeChat Direct
1. Generate TTS script using `generate_tts_script`
2. Copy the "Mistral LeChat Ready" output
3. Paste into Mistral LeChat with voice instructions
4. Request audio generation

#### Method 2: External TTS Services
```python
# Google Cloud Text-to-Speech
from google.cloud import texttospeech

script = generate_tts_script(pose="Mountain Pose", format="plain_text")
client = texttospeech.TextToSpeechClient()
audio = client.synthesize_speech(input=script, voice=voice_config)
```

#### Method 3: Browser Speech API
```javascript
// Web Speech API integration
const script = await generateTtsScript("Mountain Pose", "plain_text");
const utterance = new SpeechSynthesisUtterance(script);
utterance.rate = 0.9;
utterance.pitch = 1;
speechSynthesis.speak(utterance);
```

#### Method 4: Open Source TTS
```python
# Using gTTS (Google Text-to-Speech)
from gtts import gTTS
import pygame

script = generate_tts_script(pose="Child's Pose", format="plain_text")
tts = gTTS(text=script, lang='en', slow=True)
tts.save("pose_audio.mp3")
```
