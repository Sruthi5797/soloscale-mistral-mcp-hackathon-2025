"""
Generate HTML demo page for Piper web integration.

This script creates a standalone HTML page with clickable links to generate
audio for different yoga poses using the Piper web demo.
"""

import os
from piper_web_integration import format_yoga_text_for_piper, create_piper_web_demo_link, create_clickable_link

# List of yoga poses with Sanskrit names
POSES = [
    {"name": "Mountain Pose", "sanskrit_name": "Tadasana", "description": "A foundational standing pose that promotes good posture and balance."},
    {"name": "Child's Pose", "sanskrit_name": "Balasana", "description": "A restful pose that gently stretches the lower back and hips."},
    {"name": "Downward-Facing Dog", "sanskrit_name": "Adho Mukha Svanasana", "description": "An energizing pose that stretches the entire back of the body."},
    {"name": "Warrior I", "sanskrit_name": "Virabhadrasana I", "description": "A powerful standing pose that builds strength and focus."},
    {"name": "Tree Pose", "sanskrit_name": "Vrikshasana", "description": "A balancing pose that improves focus and stability."},
    {"name": "Triangle Pose", "sanskrit_name": "Trikonasana", "description": "A standing pose that stretches and strengthens the whole body."},
    {"name": "Corpse Pose", "sanskrit_name": "Savasana", "description": "A deeply relaxing pose typically practiced at the end of a session."}
]

def generate_html_demo(output_file='yoga_audio_demo.html'):
    """
    Generate an HTML demo page with clickable links for all poses.
    
    Args:
        output_file: Path to save the HTML file
    """
    html_head = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Yoga Audio Generator - Piper Web Demo</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            line-height: 1.6;
            color: #333;
        }
        h1, h2 {
            color: #3a7563;
        }
        .yoga-pose {
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 20px;
            background-color: #f9f9f9;
        }
        .btn {
            display: inline-block;
            background-color: #3a7563;
            color: white;
            padding: 10px 15px;
            border-radius: 4px;
            text-decoration: none;
            margin: 10px 0;
        }
        .btn:hover {
            background-color: #2a5547;
        }
        .sanskrit {
            font-style: italic;
            color: #666;
        }
        .voices {
            margin-top: 20px;
            padding: 15px;
            border-top: 1px solid #ddd;
        }
        .voice-option {
            display: inline-block;
            margin-right: 10px;
            margin-bottom: 10px;
            padding: 5px 10px;
            background-color: #f0f0f0;
            border-radius: 4px;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <h1>Yoga Audio Generator</h1>
    <p>Click on any pose below to generate calming audio instructions using the Piper text-to-speech engine.</p>
    """
    
    html_poses = ""
    for pose in POSES:
        # Format the yoga text
        yoga_text = format_yoga_text_for_piper(pose["name"])
        
        # Create the URL
        url = create_piper_web_demo_link(yoga_text)
        
        # Create the HTML for this pose
        html_poses += f"""
    <div class="yoga-pose">
        <h2>{pose["name"]} <span class="sanskrit">({pose["sanskrit_name"]})</span></h2>
        <p>{pose["description"]}</p>
        <a href="{url}" class="btn" target="_blank">Generate Audio Instructions</a>
    </div>
    """
    
    html_footer = """
    <h2>Instructions</h2>
    <ol>
        <li>Click on "Generate Audio Instructions" for any pose</li>
        <li>On the Piper web page, click the "Synthesize" button</li>
        <li>Listen to the audio instructions</li>
        <li>Use the download button (⬇️) to save the audio file if desired</li>
    </ol>
    
    <div class="voices">
        <h3>Available Voices</h3>
        <div class="voice-option">en_US-amy-medium (English, Female)</div>
        <div class="voice-option">en_US-lessac-medium (English, Female)</div>
        <div class="voice-option">en_US-libritts-high (English, Male)</div>
        <div class="voice-option">de_DE-thorsten-medium (German, Male)</div>
        <div class="voice-option">es_ES-carlfm-medium (Spanish, Male)</div>
        <div class="voice-option">fr_FR-siwis-medium (French, Female)</div>
    </div>
    
    <p><small>Created using the Yoga MCP Server with Piper Web Demo integration.</small></p>
</body>
</html>
    """
    
    # Combine all parts
    html_content = html_head + html_poses + html_footer
    
    # Write to file
    with open(output_file, 'w') as f:
        f.write(html_content)
    
    print(f"HTML demo created: {output_file}")
    print(f"Open this file in a browser to test the Piper web integration.")

if __name__ == "__main__":
    generate_html_demo()
