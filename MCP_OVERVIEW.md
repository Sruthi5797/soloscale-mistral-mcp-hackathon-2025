# Yoga Class Sequencing MCP Server - Component Overview

## Server Description

The Yoga Class Sequencing MCP Server is an intelligent yoga instruction assistant that generates personalized yoga class sequences with OpenAI TTS integration. It creates structured sequences, provides cost-effective calming audio instructions, and generates inspiring class themes.

## MCP Components

### 🛠️ Tools (3)

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

#### `generate_simple_calming_audio`
**Purpose**: Generate cost-effective calming audio instructions for yoga poses

**Inputs**:
- `asana_name`: Name of the yoga pose
- `voice`: Fixed to 'alloy' for consistent calming tone
- `include_breathing_cues`: Add simple breathing guidance (true/false)

**Output**: Simple audio package including:
- Short, calming audio instructions
- Base64 encoded MP3 audio content
- Cost-optimized script text
- Metadata about audio generation

**Key Features**:
- Cost-effective with short, essential instructions
- Consistent calming 'alloy' voice for soothing tone
- Optimized speech speed (0.9x) for relaxation
- Simple, gentle language perfect for yoga practice

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

### 🔊 OpenAI TTS Integration
- **Cost-Effective Audio**: Optimized text-to-speech using OpenAI's TTS-1 model
- **Consistent Calming Voice**: Fixed 'alloy' voice for soothing, consistent tone
- **Simplified Parameters**: No complex customization to minimize costs
- **Essential Instructions**: 70% text reduction for cost optimization while maintaining quality

### ⚡ Intelligent Automation
- **Time-Aware Sequencing**: Automatic pose selection based on available time
- **Style-Specific Logic**: Different algorithms for Hatha, Vinyasa, and Stress Relief
- **Error Handling**: Graceful fallback when API services unavailable

## API Configuration

This server requires an OpenAI API key for generating cost-effective calming audio instructions:

### Required Environment Variables:
```bash
export OPENAI_API_KEY="your_openai_api_key_here"
```

### Setting up the environment:
1. Get your OpenAI API key from [OpenAI Platform](https://platform.openai.com/api-keys)
2. Add the API key to your environment:
   ```bash
   # For bash/zsh
   echo 'export OPENAI_API_KEY="your_key_here"' >> ~/.bashrc
   source ~/.bashrc
   
   # Or for current session only
   export OPENAI_API_KEY="your_key_here"
   ```

### Cost Optimization:
- The server uses OpenAI's TTS-1 model with optimized parameters
- Fixed 'alloy' voice for consistent calming tone
- Reduced text length (70% cost savings) for essential instructions only
- Speech speed optimized at 0.9x for relaxation

## Quick Start Examples

### Create a Basic Sequence
```
"Create a 30-minute beginner hatha yoga sequence focused on strength"
```

### Get Simple Calming Audio
```
"Generate simple calming audio for Mountain Pose with breathing cues"
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

### 🔊 Simple Audio Instruction
- "Generate simple calming audio for Child's Pose with breathing cues"
- "Create cost-effective audio guidance for Mountain Pose"
- "Simple audio for final relaxation with gentle voice"

### 🎨 Complete Class Planning
- "Plan 45-minute stress relief class with theme and simple audio cues"
- "Design progressive hatha series with calming voice instructions"

## Setup Requirements

### Basic Functionality
- All core features work immediately
- Pose library and sequence generation ready
- Class theme creation available

### Audio Features (Optional)
- Set `OPENAI_API_KEY` environment variable
- Enable cost-effective TTS integration for simple audio instructions
- Fallback to text-only when API unavailable

## Integration Benefits

- **For Yoga Instructors**: Quick sequence generation with cost-effective calming audio instructions
- **For Students**: Personalized practice with simple guided audio cues and Sanskrit learning
- **For Apps**: Structured yoga content with optimized audio integration capabilities  
- **For AI Assistants**: Rich yoga knowledge with OpenAI TTS for gentle, calming instruction

This MCP server combines traditional yoga wisdom with modern AI capabilities, providing intelligent sequencing and cost-effective calming audio instruction through OpenAI's TTS integration.
