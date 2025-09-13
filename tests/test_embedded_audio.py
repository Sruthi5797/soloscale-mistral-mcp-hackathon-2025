#!/usr/bin/env python3

"""
Test script for embedded audio functionality in the Yoga MCP server.

This script tests the core audio generation functionality by directly 
calling the helper functions, bypassing the MCP tool wrapper.

Tests all three output formats:
1. embedded - Base64 data URI for immediate embedding
2. download - Local WAV file for download  
3. both - Both embedded and downloadable formats
"""

import asyncio
import json
import os
import base64
import sys

# Add the current directory to Python path to import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the core functions directly (not the MCP tools)
from main import call_piper_tts_api, create_simple_calming_script, generate_pose_procedure

async def test_embedded_audio_core():
    """Test embedded audio generation using core functions."""
    
    print("🧘 Testing Embedded Audio Generation with Piper TTS (Core Functions)")
    print("=" * 70)
    
    # Test basic Piper TTS functionality first
    print("\n🔧 Step 1: Testing Core Piper TTS Function")
    print("-" * 50)
    
    test_text = "Welcome to Mountain Pose. Stand tall with your feet together. Take a deep breath in through your nose, and slowly exhale through your mouth. Feel grounded and strong."
    
    try:
        audio_result = await call_piper_tts_api(
            text=test_text,
            voice="en_US-amy-medium"
        )
        
        if audio_result.get("success"):
            print(f"✅ Piper TTS working: {audio_result['size_bytes']} bytes generated")
            print(f"✅ Voice: {audio_result.get('voice', 'N/A')}")
            print(f"✅ Format: WAV audio with base64 encoding")
            
            # Test the core embedded audio functionality
            await test_embedded_formats(audio_result)
            
        else:
            print(f"❌ Piper TTS failed: {audio_result.get('error', 'Unknown error')}")
            return
            
    except Exception as e:
        print(f"❌ Core test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return

async def test_embedded_formats(audio_result):
    """Test different output formats using the generated audio."""
    
    print("\n🎯 Step 2: Testing Output Formats")
    print("-" * 50)
    
    audio_base64 = audio_result["audio_base64"]
    audio_size = audio_result["size_bytes"]
    
    test_cases = [
        {
            "name": "Embedded Format",
            "format": "embedded",
            "description": "Base64 data URI for immediate HTML5 playback"
        },
        {
            "name": "Download Format", 
            "format": "download",
            "description": "WAV file saved to local directory"
        },
        {
            "name": "Both Formats",
            "format": "both", 
            "description": "Both embedded and downloadable formats"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. Testing {test_case['name']} ({test_case['format']})")
        print(f"   Purpose: {test_case['description']}")
        print("-" * 40)
        
        try:
            # Simulate the different output format logic
            result = await simulate_output_format(
                audio_base64=audio_base64,
                audio_size=audio_size,
                output_format=test_case['format'],
                pose_name="Mountain Pose",
                voice="en_US-amy-medium"
            )
            
            # Test embedded format
            if test_case['format'] in ["embedded", "both"]:
                if "embedded_audio" in result and result["embedded_audio"].get("playback_ready"):
                    embedded = result["embedded_audio"]
                    print(f"   ✅ Embedded audio ready: {len(embedded['data_uri'])} chars")
                    print(f"   ✅ HTML5 element: {embedded['html_element'][:100]}...")
                    print(f"   ✅ Format: {embedded['format']}")
                    
                    # Validate data URI
                    if embedded['data_uri'].startswith("data:audio/wav;base64,"):
                        print(f"   ✅ Valid data URI format")
                    else:
                        print(f"   ❌ Invalid data URI format")
                else:
                    print(f"   ❌ Embedded audio failed")
            
            # Test download format
            if test_case['format'] in ["download", "both"]:
                if "download_file" in result and result["download_file"].get("download_ready"):
                    download = result["download_file"]
                    print(f"   ✅ Download file ready: {download['filename']}")
                    print(f"   ✅ File size: {download['file_size_bytes']} bytes")
                    print(f"   ✅ Saved to: {download['filepath']}")
                    
                    # Verify file exists
                    if os.path.exists(download['filepath']):
                        print(f"   ✅ File exists on disk")
                        
                        # Verify file content
                        with open(download['filepath'], 'rb') as f:
                            file_content = f.read()
                            if len(file_content) > 0:
                                print(f"   ✅ File content: {len(file_content)} bytes")
                            else:
                                print(f"   ❌ File is empty")
                    else:
                        print(f"   ❌ File not found on disk")
                else:
                    print(f"   ❌ Download failed")
            
            # Test basic audio data
            if "audio_data" in result:
                audio_data = result["audio_data"]
                print(f"   ✅ Audio size: {audio_data.get('size_bytes', 0)} bytes")
                print(f"   ✅ Voice: {audio_data.get('voice', 'N/A')}")
            
        except Exception as e:
            print(f"   ❌ Format test failed: {str(e)}")
            import traceback
            traceback.print_exc()
    
    # Create HTML example
    await create_html_example(audio_base64)

async def simulate_output_format(audio_base64, audio_size, output_format, pose_name, voice):
    """Simulate the output format logic from the main function."""
    
    audio_directory = "./test_audio_output"
    
    result = {
        "audio_data": {
            "audio_content": audio_base64,
            "format": "wav",
            "voice": voice,
            "size_bytes": audio_size,
            "duration_estimate": "30-60 seconds"
        },
        "pose_info": {
            "name": pose_name,
            "type": "Free offline calming instruction"
        }
    }
    
    # Handle different output formats
    should_save = output_format in ["download", "both"]
    should_embed = output_format in ["embedded", "both"]
    
    if should_save:
        try:
            # Create audio directory if it doesn't exist
            os.makedirs(audio_directory, exist_ok=True)
            
            # Create safe filename
            safe_name = pose_name.replace(" ", "_").replace("/", "_").lower()
            filename = f"yoga_{safe_name}_{voice}.wav"
            filepath = os.path.join(audio_directory, filename)
            
            # Decode and save audio
            audio_data = base64.b64decode(audio_base64)
            with open(filepath, "wb") as f:
                f.write(audio_data)
            
            result["download_file"] = {
                "saved": True,
                "filepath": filepath,
                "filename": filename,
                "directory": audio_directory,
                "file_size_bytes": len(audio_data),
                "download_ready": True
            }
            
        except Exception as save_error:
            result["download_file"] = {
                "saved": False,
                "error": str(save_error),
                "attempted_path": audio_directory,
                "download_ready": False
            }
    
    if should_embed:
        try:
            # Create embedded audio data URI
            data_uri = f"data:audio/wav;base64,{audio_base64}"
            
            # Generate HTML5 audio element
            html_audio = f'<audio controls><source src="{data_uri}" type="audio/wav">Your browser does not support the audio element.</audio>'
            
            result["embedded_audio"] = {
                "data_uri": data_uri,
                "html_element": html_audio,
                "format": "base64_wav",
                "playback_ready": True,
                "usage_instructions": "Use data_uri for direct embedding or html_element for immediate HTML5 playback"
            }
        except Exception as embed_error:
            result["embedded_audio"] = {
                "error": f"Failed to create embedded audio: {str(embed_error)}",
                "playback_ready": False
            }
    
    return result

async def create_html_example(audio_base64):
    """Create an HTML example showing embedded audio."""
    
    print("\n📱 Step 3: Creating HTML5 Embedded Audio Example")
    print("-" * 50)
    
    try:
        data_uri = f"data:audio/wav;base64,{audio_base64}"
        html_audio = f'<audio controls><source src="{data_uri}" type="audio/wav">Your browser does not support the audio element.</audio>'
        
        # Create sample HTML page
        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>🧘 Embedded Yoga Audio Test</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
        .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #2c5530; }}
        audio {{ width: 100%; margin: 20px 0; }}
        .details {{ background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0; }}
        .success {{ color: #28a745; font-weight: bold; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🧘 Mountain Pose Audio - Embedded Test</h1>
        <p>This audio is embedded directly in the HTML using base64 data URI:</p>
        
        {html_audio}
        
        <div class="details">
            <h2>✅ Technical Details:</h2>
            <ul>
                <li><strong>Format:</strong> base64_wav</li>
                <li><strong>Data URI Length:</strong> {len(data_uri):,} characters</li>
                <li><strong>Voice:</strong> en_US-amy-medium (Piper TTS)</li>
                <li><strong>Usage:</strong> Direct embedding without file dependencies</li>
                <li><strong>Compatibility:</strong> All modern browsers with HTML5 audio support</li>
            </ul>
        </div>
        
        <div class="details">
            <h2>🎯 Integration Examples:</h2>
            <h3>HTML5 Audio Element:</h3>
            <pre>&lt;audio controls&gt;&lt;source src="data:audio/wav;base64,..." type="audio/wav"&gt;&lt;/audio&gt;</pre>
            
            <h3>JavaScript Usage:</h3>
            <pre>const audio = new Audio('data:audio/wav;base64,...');
audio.play();</pre>
            
            <h3>React/Vue Component:</h3>
            <pre>&lt;audio src={{`data:audio/wav;base64,${{audioData}}`}} controls /&gt;</pre>
        </div>
        
        <p class="success">🎉 Embedded audio test completed successfully!</p>
    </div>
</body>
</html>"""
        
        # Save example HTML
        html_file = "./test_audio_output/embedded_audio_example.html"
        os.makedirs("./test_audio_output", exist_ok=True)
        with open(html_file, 'w') as f:
            f.write(html_content)
        
        print(f"✅ Created HTML example: {html_file}")
        print("✅ You can open this file in a browser to test embedded audio!")
        print(f"✅ Data URI length: {len(data_uri):,} characters")
        
        # Test data URI validity
        if data_uri.startswith("data:audio/wav;base64,"):
            base64_content = data_uri.split(',')[1]
            try:
                audio_bytes = base64.b64decode(base64_content)
                print(f"✅ Data URI is valid: {len(audio_bytes):,} bytes of audio data")
            except Exception as decode_error:
                print(f"❌ Data URI decode failed: {decode_error}")
        else:
            print(f"❌ Invalid data URI format")
        
    except Exception as e:
        print(f"❌ HTML example failed: {str(e)}")

if __name__ == "__main__":
    print("🚀 Starting Embedded Audio Core Functionality Test")
    asyncio.run(test_embedded_audio_core())
