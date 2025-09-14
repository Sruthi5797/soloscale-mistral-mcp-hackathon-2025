"""
Piper Web Demo Integration for Yoga MCP Server.

This module provides integration with the Piper web demo at
https://rhasspy.github.io/piper-samples/demo.html to allow for browser-based
audio generation without requiring local Piper installation.
"""

import urllib.parse
import json
from typing import Dict, Optional, List
import hashlib

# Piper web demo URL
PIPER_WEB_DEMO_URL = "https://rhasspy.github.io/piper-samples/demo.html"

def create_clickable_link(pose_name: str, include_breathing: bool = True, format_type: str = "markdown") -> str:
    """
    Create a ready-to-use clickable link for the given pose.
    
    This is a convenience function that creates a formatted clickable link
    in either Markdown or HTML format.
    
    Args:
        pose_name: The name of the yoga pose
        include_breathing: Whether to include breathing cues
        format_type: Type of link format, either "markdown" or "html"
    
    Returns:
        A formatted clickable link
    """
    # Format the text for TTS
    yoga_text = format_yoga_text_for_piper(pose_name, include_breathing)
    
    # Create the URL
    url = create_piper_web_demo_link(yoga_text)
    
    # Format the link according to the requested type
    link_text = f"Generate Audio for {pose_name}"
    if format_type.lower() == "html":
        return f'<a href="{url}" target="_blank">{link_text}</a>'
    else:  # Default to markdown
        return f"[{link_text}]({url})"

def try_shorten_url(long_url: str) -> Optional[str]:
    """
    Try to shorten a URL using an integrated approach.
    
    Since we don't have access to external URL shortening APIs,
    this function returns a simplified representation of the long URL
    by creating a hash of the parameters and using that as a reference.
    
    Args:
        long_url: The long URL to shorten
    
    Returns:
        A shortened representation if possible, otherwise None
    """
    try:
        # In a real implementation, you would call a URL shortening service
        # like TinyURL, Bitly, etc. Since we can't make those API calls here,
        # we'll just return the original URL with a note that in a production
        # environment, this would be shortened.
        
        # For demonstration purposes only - not actually shortening
        # In a real implementation, replace this with an actual API call
        
        # Create a hash of the URL to represent what would be a shortened ID
        url_hash = hashlib.md5(long_url.encode()).hexdigest()[:8]
        
        # This is just for illustration - not actually shortened
        # In production, implement a proper URL shortening service integration
        
        return long_url
    except Exception:
        # If any error occurs, return None to fall back to the long URL
        return None

def create_piper_web_demo_link(
    text: str, 
    speaker: str = "en_US-amy-medium",
    noise_scale: float = 0.667,
    noise_w: float = 0.8,
    length_scale: float = 1.0,
    use_shortened_url: bool = False
) -> str:
    """
    Create a link to the Piper web demo with pre-filled text and parameters.
    
    Args:
        text: The text to synthesize
        speaker: The speaker voice model to use
        noise_scale: Controls variation in voice (0.0-1.0)
        noise_w: Controls variation in speaking style (0.0-1.0)
        length_scale: Controls speaking speed (lower is faster)
        use_shortened_url: Whether to attempt to shorten the URL (if available)
    
    Returns:
        URL to the Piper web demo with query parameters set
    """
    # Encode text and parameters for URL
    params = {
        "text": text,
        "speaker": speaker,
        "noiseScale": str(noise_scale),
        "noiseW": str(noise_w),
        "lengthScale": str(length_scale)
    }
    
    # Build query string
    query_string = urllib.parse.urlencode(params)
    
    # Construct full URL
    full_url = f"{PIPER_WEB_DEMO_URL}?{query_string}"
    
    # If shortened URL is requested, try to shorten it
    if use_shortened_url:
        shortened_url = try_shorten_url(full_url)
        if shortened_url:
            return shortened_url
    
    return full_url

def format_yoga_text_for_piper(
    pose_name: str,
    include_breathing_cues: bool = True,
    voice_style: str = "gentle"
) -> str:
    """
    Format yoga pose instructions for optimal TTS using Piper web demo.
    
    Args:
        pose_name: Name of the yoga pose
        include_breathing_cues: Whether to include breathing instructions
        voice_style: Style of voice instructions (gentle, energetic, etc.)
        
    Returns:
        Formatted text for TTS
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
    
    # Get simple instruction or create a gentle generic one
    instruction = basic_instructions.get(pose_name, 
        "Move into this pose slowly and gently. Listen to your body.")
    
    # Simple breathing guidance if requested
    breathing = ""
    if include_breathing_cues:
        breathing = " Breathe slowly and deeply."
    
    # Gentle conclusion
    conclusion = " Stay here for a few breaths. Come out gently when ready."
    
    # Combine into short, calming script
    script = f"{intro} {instruction}{breathing}{conclusion}"
    
    return script

def get_available_voices() -> List[Dict]:
    """
    Get a list of available voices in the Piper web demo.
    
    Returns:
        List of voice dictionaries with name and language information
    """
    return [
        {"name": "en_US-amy-medium", "language": "English (US)", "gender": "Female", "quality": "Medium"},
        {"name": "en_US-lessac-medium", "language": "English (US)", "gender": "Female", "quality": "Medium"},
        {"name": "en_US-lessac-low", "language": "English (US)", "gender": "Female", "quality": "Low"},
        {"name": "en_US-libritts-high", "language": "English (US)", "gender": "Male", "quality": "High"},
        {"name": "de_DE-thorsten-medium", "language": "German", "gender": "Male", "quality": "Medium"},
        {"name": "es_ES-carlfm-medium", "language": "Spanish", "gender": "Male", "quality": "Medium"},
        {"name": "fr_FR-siwis-medium", "language": "French", "gender": "Female", "quality": "Medium"},
        {"name": "nl_NL-rdh-medium", "language": "Dutch", "gender": "Male", "quality": "Medium"},
    ]

def generate_piper_web_instructions(pose_name: str, include_breathing_cues: bool = True, voice: str = "en_US-amy-medium") -> Dict:
    """
    Generate complete instructions for using Piper web demo for a yoga pose.
    
    Args:
        pose_name: Name of the yoga pose
        include_breathing_cues: Whether to include breathing guidance
        voice: The voice model to use for synthesis
        
    Returns:
        Dictionary with formatted text, link, and usage instructions
    """
    # Format the text for TTS based on the pose
    yoga_text = format_yoga_text_for_piper(pose_name, include_breathing_cues)
    
    # Create direct link to web demo with pre-filled text and voice
    web_link = create_piper_web_demo_link(
        text=yoga_text,
        speaker=voice
    )
    
    # Create simple, clear instructions for the user
    instructions = [
        f"1. Click the link below to open Piper TTS with pre-filled instructions for {pose_name}",
        "2. On the webpage, click the 'Synthesize' button to generate the audio",
        "3. Listen to the yoga instructions",
        "4. To save the audio, click the download button (arrow pointing down)",
        "5. You can adjust the voice or other parameters if desired"
    ]
    
    # Return a simple, structured response that MCP clients can easily display
    return {
        "pose_name": pose_name,
        "description": yoga_text,
        "audio_link": web_link,
        "display_text": f"Generate audio instructions for {pose_name}",
        "instructions": instructions,
        "voice": voice,
        "html_display": f'<a href="{web_link}" target="_blank">Generate audio for {pose_name} ▶️</a>',
        "markdown_display": f"[Generate audio for {pose_name} ▶️]({web_link})"
    }

if __name__ == "__main__":
    # Example usage
    result = generate_piper_web_instructions("Mountain Pose")
    print(json.dumps(result, indent=2))
