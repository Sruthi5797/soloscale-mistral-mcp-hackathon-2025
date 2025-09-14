#!/usr/bin/env python3
"""
Demo Audio Generator for Yoga Pose Instructions

This script generates WAV audio files for yoga pose instructions using Piper TTS.
It focuses on creating properly formatted WAV files ready for demo purposes and
for upload to Google Drive.
"""

import os
import datetime
import wave
import io
from typing import Dict, Optional

def create_yoga_instruction_audio(
    pose_name: str,
    output_dir: str = "./audio_files",
    voice: str = "en_US-amy-medium",
    include_breathing: bool = True,
    custom_instruction: str = None
) -> Dict:
    """
    Create a yoga pose instruction audio file in WAV format.
    
    This function generates a clean, properly formatted WAV file that's ready for demo
    purposes and for upload to Google Drive.
    
    Args:
        pose_name: Name of the yoga pose
        output_dir: Directory to save the WAV file
        voice: Voice model to use
        include_breathing: Whether to include breathing cues
        custom_instruction: Custom instruction text (if None, will generate automatically)
        
    Returns:
        Dict with file information and status
    """
    try:
        # Create directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate filename with timestamp for uniqueness
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = pose_name.replace(" ", "_").replace("/", "_").lower()
        filename = f"yoga_{safe_name}_{timestamp}.wav"
        file_path = os.path.join(output_dir, filename)
        
        # Generate the script text
        if custom_instruction is None:
            instruction = generate_simple_instruction(pose_name, include_breathing)
        else:
            instruction = custom_instruction
            
        # Import Piper here to make it optional for testing
        try:
            from piper import PiperVoice
            
            # Look for the voice model
            voice_model_path = f"./models/{voice}.onnx"
            
            # Check if the model exists
            if not os.path.exists(voice_model_path):
                return {
                    "success": False,
                    "error": f"Voice model not found: {voice_model_path}",
                    "instruction_text": instruction
                }
                
            # Load the voice model
            piper_voice = PiperVoice.load(voice_model_path)
            
            # Create WAV file - Method 1: Using BytesIO and wave module
            audio_buffer = io.BytesIO()
            
            # Set WAV parameters correctly
            with wave.open(audio_buffer, "wb") as wav_file:
                wav_file.setnchannels(1)  # Mono
                wav_file.setsampwidth(2)  # 16-bit
                wav_file.setframerate(22050)  # Standard Piper rate
                
                # Synthesize audio
                if hasattr(piper_voice, "synthesize_wav"):
                    piper_voice.synthesize_wav(instruction, wav_file)
                else:
                    # Fallback if synthesize_wav doesn't exist
                    audio_data = b''
                    for chunk in piper_voice.synthesize(instruction):
                        if chunk is not None:
                            audio_data += chunk
                    wav_file.writeframes(audio_data)
            
            # Write the WAV data to file
            with open(file_path, "wb") as f:
                f.write(audio_buffer.getvalue())
                
            # Get file size
            file_size = os.path.getsize(file_path)
            
            return {
                "success": True,
                "file_path": file_path,
                "file_name": filename,
                "file_size_bytes": file_size,
                "file_size_mb": round(file_size / (1024 * 1024), 2),
                "instruction_text": instruction,
                "absolute_path": os.path.abspath(file_path)
            }
                
        except ImportError:
            return {
                "success": False,
                "error": "Piper TTS not installed. Install with: pip install piper-tts",
                "instruction_text": instruction
            }
                
    except Exception as e:
        return {
            "success": False,
            "error": f"Error generating audio: {str(e)}",
            "instruction_text": custom_instruction or f"Instruction for {pose_name}"
        }

def generate_simple_instruction(pose_name: str, include_breathing: bool) -> str:
    """
    Generate a simple instruction text for a yoga pose.
    
    Args:
        pose_name: Name of the yoga pose
        include_breathing: Whether to include breathing cues
        
    Returns:
        Instruction text
    """
    # Simple, gentle introduction
    intro = f"Let's gently move into {pose_name}."
    
    # Basic instruction based on common poses
    basic_instructions = {
        "Mountain Pose": "Stand tall and steady. Feel your feet on the ground.",
        "Child's Pose": "Kneel down gently. Rest your forehead on the ground.",
        "Downward-Facing Dog": "Place your hands down. Lift your hips up gently.",
        "Warrior I": "Step one foot back. Reach your arms up toward the sky.",
        "Triangle Pose": "Step your feet wide. Reach one hand down, one hand up.",
        "Tree Pose": "Stand on one foot. Place the other foot on your leg.",
        "Cat-Cow Pose": "Move gently between arching and rounding your back.",
        "Bridge Pose": "Lie down. Gently lift your hips up.",
        "Corpse Pose": "Lie down comfortably. Let your whole body relax."
    }
    
    # Get instruction or use generic
    instruction = basic_instructions.get(
        pose_name, "Move into this pose slowly and gently. Listen to your body."
    )
    
    # Add breathing cue if requested
    breathing = " Breathe slowly and deeply." if include_breathing else ""
    
    # Add closing
    closing = " Stay here for a few breaths. Come out gently when ready."
    
    return f"{intro} {instruction}{breathing}{closing}"

def create_demo_audio(description: str, output_dir: str = "./audio_files") -> Dict:
    """
    Create a demo audio file from a description.
    
    This is a simplified function specifically for demo purposes.
    
    Args:
        description: Description of what the audio should contain
        output_dir: Directory to save the audio
        
    Returns:
        Dict with file information
    """
    # Generate a pose name from the description
    words = description.split()
    pose_name = " ".join(words[:2]) if len(words) > 1 else description
    
    return create_yoga_instruction_audio(
        pose_name=pose_name,
        output_dir=output_dir,
        custom_instruction=description
    )

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python demo_audio_generator.py <pose_name> [output_dir]")
        sys.exit(1)
        
    pose_name = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "./audio_files"
    
    result = create_yoga_instruction_audio(pose_name, output_dir)
    
    if result["success"]:
        print(f"✅ Audio file created: {result['file_path']}")
        print(f"📊 File size: {result['file_size_mb']} MB")
    else:
        print(f"❌ Error: {result['error']}")
        
    print(f"📝 Instruction text: {result['instruction_text']}")
