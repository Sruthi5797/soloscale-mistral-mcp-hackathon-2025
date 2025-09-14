# Yoga Sequencing MCP Server

A Model Context Protocol (MCP) server for generating personalized yoga class sequences and audio instructions. This project builds an MCP server specifically designed for yoga practitioners and teachers.

## Overview

This MCP server integrates with Mistral LeChat and other MCP clients to provide yoga sequencing tools that help users create personalized yoga sessions with high-quality instructions and audio guidance.

## MCP Components

### Tools
- `create_yoga_sequence`: Generate custom sequences based on duration, level, style, and focus
- `generate_pose_procedure`: Create detailed step-by-step instructions for yoga poses
- `generate_pose_audio_with_piper`: Generate audio instructions with embedded HTML player
- `generate_piper_web_demo_link`: Create links to Piper web demo with pre-filled text

### Resources
- `sequence://template/{style}/{level}`: Access sequence templates by style and level
- `pose://details/{pose_name}`: Get detailed information about specific poses

### Prompts
- `generate_class_theme`: Create inspiring themes and intentions for yoga classes
## Setup

```bash
# Add dependencies
uv add <package-name>

# Sync dependencies
uv sync

# Run the server
uv run main.py --reload
```

The server runs on http://localhost:3000/mcp

## Local MCP Inspector

For local testing and inspection of MCP interactions, use the [MCP Inspector](https://github.com/mistralco/mcp-inspector) repo:


## Remote Deployment using Alpine and integration with LeChat
The server is deployed remotely using [Alpic](https://alpic.io) and integrated with Mistral LeChat. The MCP connect name for this deployment is `SoloScale-LeYogaSeqEnz`. 

## Usage Examples

1. Create a yoga sequence:
   - "Create a 20-minute beginner hatha sequence focusing on flexibility"
   - "Design a 15-minute gentle sequence for stress relief"

2. Get pose instructions:
   - "Generate instructions for Warrior I pose"
   - "Show me detailed steps for Triangle Pose with modifications"
   - "What's the proper alignment for Downward-Facing Dog?"

3. Generate audio:
   - "Create audio instructions for Child's Pose"
   - "Generate calming audio guidance for Corpse Pose with breathing cues"
   - "I need audio instructions for Tree Pose"

4. Access resources:
   - "Show me the template for intermediate vinyasa sequences"
   - "Get detailed information about Bridge Pose"

5. Create class themes:
   - "Generate a summer theme for a 60-minute hatha class focused on grounding"
   - "Create an intention for a winter solstice yoga practice"

## Implementation Notes

- Built with FastMCP for Mistral LeChat integration
- Audio generation via Piper TTS (offline, no API costs)
- Code development assisted by Claude Sonnet 4 (Wanted to really try Vibe-Coding it :D)

## Troubleshooting

For environments without local TTS, the server provides links to the Piper web demo with pre-filled instructions.

---

See [MCP_OVERVIEW.md](MCP_OVERVIEW.md) for detailed documentation.
