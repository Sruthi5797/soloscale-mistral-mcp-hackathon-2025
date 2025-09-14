#!/usr/bin/env python3
"""
Run Audio Generator Script

This script provides a way to run the generate_pose_audio_with_piper function
from the main module directly, bypassing the MCP tool wrapper.
"""

import os
import sys
import asyncio
from typing import Dict

# Import the necessary modules and functions from demo_audio_generator
try:
    from tests.demo_audio_generator import create_yoga_instruction_audio, create_demo_audio
except ImportError:
    print("Error: Could not import demo_audio_generator module.")
    print("Please ensure demo_audio_generator.py is in the current directory.")
    sys.exit(1)

async def run_audio_generator(
    asana_name: str, 
    voice: str = "en_US-amy-medium",
    include_breathing_cues: bool = True,
    output_dir: str = "./audio_files",
    output_filename: str = "",
    custom_description: str = ""
) -> Dict:
    """
    Run the audio generator directly without going through the MCP tool.
    
    This function mimics the behavior of generate_pose_audio_with_piper
    but can be called directly from Python code.
    
    Args:
        asana_name: Name of the yoga pose/asana
        voice: Voice model to use
        include_breathing_cues: Whether to include breathing guidance
        output_dir: Directory to save the WAV file
        output_filename: Custom filename (optional)
        custom_description: Custom description for the demo
        
    Returns:
        Dict with the result information
    """
    # Use the demo_audio_generator functions directly
    try:
        # If custom description is provided, use that directly
        if custom_description:
            result = create_demo_audio(
                description=custom_description,
                output_dir=output_dir
            )
        else:
            # Otherwise, generate standard yoga instruction
            result = create_yoga_instruction_audio(
                pose_name=asana_name,
                output_dir=output_dir,
                voice=voice,
                include_breathing=include_breathing_cues,
                custom_instruction=None
            )
        
        # Check if audio generation was successful
        if not result.get("success", False):
            return {
                "error": result.get("error", "Unknown error generating audio"),
                "suggestion": "Check the Piper TTS installation and voice model availability",
                "script_text": result.get("instruction_text", "")
            }
        
        # Get file information from the result
        file_path = result["file_path"]
        filename = result["file_name"]
        file_size = result["file_size_bytes"]
        audio_script = result["instruction_text"]
        
        # Return a detailed response
        return {
            "audio_info": {
                "voice": voice,
                "breathing_cues_included": include_breathing_cues,
                "file_path": file_path,
                "file_name": filename,
                "file_size_bytes": file_size,
                "file_size_mb": round(file_size / (1024 * 1024), 2)
            },
            "script_text": audio_script,
            "google_drive_info": {
                "upload_ready": True,
                "suggested_mime_type": "audio/wav",
                "absolute_path": os.path.abspath(file_path)
            },
            "generated_by": "Yoga Audio Generator - Direct Call"
        }
            
    except ImportError as e:
        return {
            "error": "Piper TTS not installed",
            "suggestion": "Install with: pip install piper-tts",
            "script_text": custom_description or f"Instruction for {asana_name}"
        }
    except Exception as e:
        # More detailed error handling
        error_msg = str(e)
        suggestion = "Check if the models directory exists and contains voice models"
        
        if "bytes-like object is required" in error_msg:
            suggestion = "The WAV file creation is being fixed. Please try again with the updated code."
        elif "not found" in error_msg.lower():
            suggestion = "Make sure the Piper voice model exists in the specified path."
            
        return {
            "error": f"Piper TTS error: {error_msg}",
            "script_text": custom_description or f"Instruction for {asana_name}",
            "suggestion": suggestion
        }

# Execute the function if run directly
if __name__ == "__main__":
    # Parse command line arguments
    if len(sys.argv) < 2:
        print("Usage: python run_audio_generator.py <pose_name> [custom_description]")
        sys.exit(1)
    
    pose_name = sys.argv[1]
    custom_description = sys.argv[2] if len(sys.argv) > 2 else ""
    
    # Run the function
    result = asyncio.run(run_audio_generator(
        asana_name=pose_name,
        custom_description=custom_description
    ))
    
    print("Result:", result)
    
    # Print a summary of the results
    if "error" in result:
        print(f"❌ Error: {result['error']}")
        print(f"💡 Suggestion: {result.get('suggestion', 'None')}")
    else:
        print(f"✅ Audio file created: {result['audio_info']['file_path']}")
        print(f"📊 File size: {result['audio_info']['file_size_mb']} MB")
        print(f"📝 Script text: {result['script_text']}")
