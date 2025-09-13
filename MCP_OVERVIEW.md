# Yoga Class Sequencing MCP Server - Component Overview

## Server Description

The Yoga Class Sequencing MCP Server is an intelligent yoga instruction assistant that generates personalized yoga class sequences with Mistral Voxtral integration. It creates structured sequences, provides audio instructions using text-to-speech, and generates inspiring class themes.

## MCP Components

### 🛠️ Tools (2)

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

#### `read_pose_procedure_with_voxtral`
**Purpose**: Generate detailed pose instructions with Mistral Voxtral audio integration

**Inputs**:
- `pose_name`: Name of the yoga pose
- `language`: Output language (english/sanskrit_pronunciation/bilingual)
- `voice_style`: Voice character (calm/energetic/meditative/neutral)
- `include_breathing_cues`: Add breath timing guidance (true/false)
- `speed`: Speech speed (slow/normal/fast)
- `quality`: Audio quality (standard/high/premium)

**Output**: Complete instruction package including:
- Detailed step-by-step procedure text
- Sanskrit name and pronunciation guide
- Audio synthesis via Mistral Voxtral API
- Estimated duration and cost information

**Key Features**:
- Mistral Voxtral integration for natural speech synthesis
- Multiple language options including Sanskrit pronunciation
- Customizable voice styles and speech parameters
- Professional yoga instruction formatting
- Graceful fallback to text when API unavailable

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

### 🔊 Mistral Voxtral Integration
- **Natural Speech**: High-quality text-to-speech using Mistral's Voxtral model
- **Voice Customization**: Multiple voice styles (calm, energetic, meditative, neutral)
- **Language Options**: English, Sanskrit pronunciation, or bilingual instruction
- **Professional Audio**: Studio-quality audio for yoga instruction

### ⚡ Intelligent Automation
- **Time-Aware Sequencing**: Automatic pose selection based on available time
- **Style-Specific Logic**: Different algorithms for Hatha, Vinyasa, and Stress Relief
- **Error Handling**: Graceful fallback when API services unavailable

## Quick Start Examples

### Create a Basic Sequence
```
"Create a 30-minute beginner hatha yoga sequence focused on strength"
```

### Get Audio Instructions
```
"Generate audio instructions for Warrior I pose in calm voice with breathing cues"
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

### 🧘 Basic Requests
- "30-minute beginner hatha sequence for strength"
- "Generate audio for Downward Dog with Sanskrit pronunciation"  
- "Create spring theme for 60-minute vinyasa class"

### 🔊 Audio-Enhanced Instruction
- "Read Child's Pose procedure in calm voice with breathing cues"
- "Bilingual instructions for Sun Salutation sequence"
- "Meditative voice for final relaxation guidance"

### 🎨 Complete Class Planning
- "Plan 45-minute stress relief class with theme and audio cues"
- "Design progressive hatha series with voice instructions"

## Setup Requirements

### Basic Functionality
- All core features work immediately
- Pose library and sequence generation ready
- Class theme creation available

### Audio Features (Optional)
- Set `MISTRAL_API_KEY` environment variable
- Enable Voxtral integration for audio instructions
- Fallback to text-only when API unavailable

## Integration Benefits

- **For Yoga Instructors**: Quick sequence generation with professional audio instructions
- **For Students**: Personalized practice with guided audio cues and Sanskrit learning
- **For Apps**: Structured yoga content with audio integration capabilities  
- **For AI Assistants**: Rich yoga knowledge with Mistral Voxtral speech synthesis

This MCP server combines traditional yoga wisdom with modern AI capabilities, providing intelligent sequencing and natural audio instruction through Mistral's Voxtral integration.
