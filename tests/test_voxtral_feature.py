#!/usr/bin/env python3
"""
Test script for the Mistral Voxtral integration in the Yoga MCP Server.

This script tests the new read_pose_procedure_with_voxtral feature to ensure
it properly integrates with Mistral's API for text-to-speech functionality.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import read_pose_procedure_with_voxtral, format_text_for_speech

def test_voxtral_integration():
    """Test the Mistral Voxtral integration feature."""
    
    print("🧘 Testing Mistral Voxtral Integration for Yoga Poses")
    print("=" * 60)
    
    # Test 1: Basic pose procedure generation
    print("\n1. Testing basic pose procedure with Voxtral...")
    result = read_pose_procedure_with_voxtral(
        asana_name="Mountain Pose",
        voice_style="calm",
        language="english",
        include_breathing_cues=True,
        narration_speed="normal"
    )
    
    print(f"✅ Pose: {result['pose_info']['name']}")
    print(f"✅ Sanskrit: {result['pose_info']['sanskrit_name']}")
    print(f"✅ Audio Status: {result['audio_generation']['status']}")
    print(f"✅ Voice Style: {result['audio_generation']['voice_style']}")
    print(f"✅ Duration: {result['audio_generation']['duration_seconds']} seconds")
    
    # Test 2: Test with Sanskrit pronunciation
    print("\n2. Testing with Sanskrit pronunciation...")
    result_sanskrit = read_pose_procedure_with_voxtral(
        asana_name="Warrior I",
        voice_style="meditative",
        language="sanskrit_pronunciation",
        include_breathing_cues=True,
        narration_speed="slow"
    )
    
    print(f"✅ Pose: {result_sanskrit['pose_info']['name']}")
    print(f"✅ Sanskrit: {result_sanskrit['pose_info']['sanskrit_name']}")
    print(f"✅ Language: {result_sanskrit['audio_generation']['language']}")
    print(f"✅ Speed: {result_sanskrit['audio_generation']['speed']}")
    
    # Test 3: Test text formatting
    print("\n3. Testing text formatting for speech...")
    formatted_text = format_text_for_speech(
        pose_name="Child's Pose",
        sanskrit_name="Balasana",
        procedure="**POSE SETUP:** Kneel on the floor, touch your big toes together...",
        language="bilingual",
        include_breathing_cues=True
    )
    
    print("✅ Formatted text preview:")
    print(formatted_text[:200] + "..." if len(formatted_text) > 200 else formatted_text)
    
    # Test 4: Error handling
    print("\n4. Testing error handling...")
    error_result = read_pose_procedure_with_voxtral(
        asana_name="NonexistentPose",
        voice_style="calm"
    )
    
    if "error" in error_result:
        print(f"✅ Error handling works: {error_result['error']}")
    else:
        print("⚠️  Error handling might need attention")
    
    print("\n" + "=" * 60)
    print("🎉 Mistral Voxtral integration test completed!")
    print("\nNote: To use real audio generation, set MISTRAL_API_KEY environment variable")
    print("Example: export MISTRAL_API_KEY='your-api-key-here'")

if __name__ == "__main__":
    test_voxtral_integration()
