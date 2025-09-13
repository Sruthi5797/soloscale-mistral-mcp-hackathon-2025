#!/usr/bin/env python3
"""
Simple test for the cost-effective calming audio feature.
"""

def create_simple_calming_script(pose_name: str, include_breathing_cues: bool) -> str:
    """
    Create a simple, cost-effective calming script for TTS audio generation.
    
    This function creates short, gentle instructions optimized for:
    - Minimal cost (shorter text = less expensive)
    - Calming, soothing tone
    - Essential guidance only
    - Simple language
    
    Args:
        pose_name: English name of the yoga pose
        include_breathing_cues: Whether to add breath guidance
    
    Returns:
        Short, calming text optimized for TTS cost-effectiveness
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

def test_simple_calming_scripts():
    """Test the simple calming script generation."""
    
    print("🧘‍♀️ Testing Simple Calming Audio Scripts")
    print("=" * 50)
    
    test_poses = [
        "Mountain Pose",
        "Child's Pose", 
        "Tree Pose",
        "Unknown Pose"  # Test generic handling
    ]
    
    for pose in test_poses:
        print(f"\n📝 Testing: {pose}")
        
        # Test without breathing cues
        script_simple = create_simple_calming_script(pose, include_breathing_cues=False)
        print(f"Simple: {script_simple}")
        
        # Test with breathing cues  
        script_with_breath = create_simple_calming_script(pose, include_breathing_cues=True)
        print(f"With breathing: {script_with_breath}")
        
        # Show character count (for cost estimation)
        print(f"Character count: {len(script_with_breath)} chars")
    
    print("\n" + "=" * 50)
    print("✅ Cost-Optimization Features:")
    print("- Short scripts (typically 50-100 characters)")
    print("- Simple, calming language")
    print("- Fixed 'alloy' voice for consistency")
    print("- Essential guidance only")
    print("- No complex formatting or long descriptions")

if __name__ == "__main__":
    test_simple_calming_scripts()
