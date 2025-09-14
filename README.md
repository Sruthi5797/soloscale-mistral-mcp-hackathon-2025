# Yoga Class Sequencing MCP Server

An MCP server that generates personalized yoga class sequences with free offline audio instructions using Piper TTS.

## Features

- **Create yoga sequences** for different styles, levels, and durations
- **Generate pose instructions** with detailed alignment and safety cues
- **Create audio instructions** with free offline text-to-speech
- **Generate class themes** with seasonal focus and intentions

## Quick Setup

1. Install dependencies:

```bash
uv add fastmcp piper-tts
uv sync
```

2. Create `models` directory and download Piper voice model

3. Start the server:

```bash
uv run main.py
```

## Testing

Test the server using the MCP inspector:

```bash
npx @modelcontextprotocol/inspector
```

Connect to: http://127.0.0.1:3000/mcp

## Important Notes

- All processing happens locally - no internet needed
- No API keys required
- Voice models download automatically on first use
- For cloud deployment, use "base64_data" output preference to avoid file system issues

See `MCP_OVERVIEW.md` for detailed documentation.

    return f"You are a friendly assistant, help the user and don't forget to {prompt_param}."

```
