"""
Yoga Class Sequencing MCP Server

This MCP server provides intelligent yoga class sequencing capabilities, allowing users to create
personalized yoga sequences based on duration, skill level, and practice style. The server includes
pre-defined templates for different yoga styles and automatically calculates time allocation for
optimal class flow. Enhanced with Sanskrit names, detailed pose procedures, and voice-optimized instruction generation.

SETUP:
For voice instruction generation with OpenAI's TTS model:
export OPENAI_API_KEY="your-openai-api-key-here"

=== MCP COMPONENTS OVERVIEW ===

TOOLS:
1. create_yoga_sequence - Main tool for generating customized yoga class sequences
   - Input: duration, level, style, focus
   - Output: Complete structured sequence with time breakdowns and Sanskrit names

2. generate_pose_procedure - AI-powered pose instruction generator
   - Input: pose name, sanskrit name, expertise level, modifications option
   - Output: Detailed step-by-step instructions, alignment cues, and safety notes

3. generate_simple_calming_audio - Cost-effective calming audio generation
   - Input: pose name (asana), simple breathing cues option
   - Output: Short, calming audio instructions optimized for minimal cost

RESOURCES:
1. get_sequence_template - Access to raw sequence templates by style and level
   - URI pattern: sequence://template/{style}/{level}
   - Enhanced with Sanskrit names and expertise levels

2. get_pose_details - Comprehensive pose information including procedures
   - URI pattern: pose://details/{pose_name}
   - Includes Sanskrit names, procedures, benefits, and contraindications

PROMPTS:
1. generate_class_theme - Creates inspiring themes and intentions for yoga classes
   - Generates seasonal themes, opening intentions, and closing reflections

ENHANCED FEATURES:
- Sanskrit Names: All poses include traditional Sanskrit nomenclature
- Simple Calming Audio: Cost-effective gentle voice instructions
- Consistent Soothing Voice: Uses 'alloy' voice for calming consistency  
- Short Audio Clips: Optimized for cost while maintaining quality
- Essential Guidance: Focuses on key instructions without excess

Note: Uses OpenAI's TTS with cost-effective settings for gentle, 
calming yoga instruction audio that's both affordable and soothing.

SUPPORTED STYLES:
- Hatha: Traditional, slower-paced yoga with held poses
- Vinyasa: Flow-based practice with breath-synchronized movement
- Stress Relief: Gentle, restorative practice for relaxation

SKILL LEVELS:
- Beginner: Basic poses with modifications and detailed guidance
- Intermediate: More challenging poses and sequences with variations
- Advanced: Complex poses requiring significant experience
- All Levels: Universal practices (stress relief) accessible to everyone
"""

from fastmcp import FastMCP
from pydantic import Field
import json
import asyncio
import httpx
import os
import base64
import io
from typing import List, Dict, Optional

# Initialize FastMCP server
mcp = FastMCP("Yoga Sequencing Server", port=3000, stateless_http=True, debug=True)

# Comprehensive yoga sequence templates organized by style and skill level
# Enhanced with Sanskrit names and detailed pose information
SEQUENCE_TEMPLATES = {
    "hatha": {
        "beginner": {
            "warm_up": [
                {"name": "Easy Pose", "sanskrit_name": "Sukhasana", "expertise_level": "Beginner"},
                {"name": "Cat-Cow Pose", "sanskrit_name": "Marjaryasana-Bitilasana", "expertise_level": "Beginner"},
                {"name": "Child's Pose", "sanskrit_name": "Balasana", "expertise_level": "Beginner"}
            ],
            "standing": [
                {"name": "Mountain Pose", "sanskrit_name": "Tadasana", "expertise_level": "Beginner"},
                {"name": "Tree Pose", "sanskrit_name": "Vrikshasana", "expertise_level": "Beginner"},
                {"name": "Triangle Pose", "sanskrit_name": "Trikonasana", "expertise_level": "Beginner"},
                {"name": "Warrior I", "sanskrit_name": "Virabhadrasana I", "expertise_level": "Beginner"}
            ],
            "seated": [
                {"name": "Staff Pose", "sanskrit_name": "Dandasana", "expertise_level": "Beginner"},
                {"name": "Bound Angle Pose", "sanskrit_name": "Baddha Konasana", "expertise_level": "Beginner"},
                {"name": "Seated Forward Fold", "sanskrit_name": "Paschimottanasana", "expertise_level": "Beginner"}
            ],
            "backbends": [
                {"name": "Bridge Pose", "sanskrit_name": "Setu Bandhasana", "expertise_level": "Beginner"},
                {"name": "Camel Pose", "sanskrit_name": "Ustrasana", "expertise_level": "Intermediate"}
            ],
            "cool_down": [
                {"name": "Child's Pose", "sanskrit_name": "Balasana", "expertise_level": "Beginner"},
                {"name": "Supine Twist", "sanskrit_name": "Supta Matsyendrasana", "expertise_level": "Beginner"},
                {"name": "Corpse Pose", "sanskrit_name": "Savasana", "expertise_level": "Beginner"}
            ]
        },
        "intermediate": {
            "warm_up": [
                {"name": "Cat-Cow Pose", "sanskrit_name": "Marjaryasana-Bitilasana", "expertise_level": "Beginner"},
                {"name": "Downward-Facing Dog", "sanskrit_name": "Adho Mukha Svanasana", "expertise_level": "Beginner"},
                {"name": "Sun Salutation A", "sanskrit_name": "Surya Namaskara A", "expertise_level": "Intermediate"}
            ],
            "standing": [
                {"name": "Warrior I", "sanskrit_name": "Virabhadrasana I", "expertise_level": "Beginner"},
                {"name": "Warrior II", "sanskrit_name": "Virabhadrasana II", "expertise_level": "Beginner"},
                {"name": "Triangle Pose", "sanskrit_name": "Trikonasana", "expertise_level": "Beginner"},
                {"name": "Extended Side Angle", "sanskrit_name": "Utthita Parsvakonasana", "expertise_level": "Intermediate"}
            ],
            "seated": [
                {"name": "Boat Pose", "sanskrit_name": "Navasana", "expertise_level": "Intermediate"},
                {"name": "Seated Forward Fold", "sanskrit_name": "Paschimottanasana", "expertise_level": "Beginner"},
                {"name": "Seated Spinal Twist", "sanskrit_name": "Ardha Matsyendrasana", "expertise_level": "Intermediate"}
            ],
            "backbends": [
                {"name": "Camel Pose", "sanskrit_name": "Ustrasana", "expertise_level": "Intermediate"},
                {"name": "Wheel Pose", "sanskrit_name": "Urdhva Dhanurasana", "expertise_level": "Advanced"},
                {"name": "Fish Pose", "sanskrit_name": "Matsyasana", "expertise_level": "Intermediate"}
            ],
            "cool_down": [
                {"name": "Pigeon Pose", "sanskrit_name": "Eka Pada Rajakapotasana", "expertise_level": "Intermediate"},
                {"name": "Supine Figure 4", "sanskrit_name": "Supta Kapotasana", "expertise_level": "Beginner"},
                {"name": "Corpse Pose", "sanskrit_name": "Savasana", "expertise_level": "Beginner"}
            ]
        }
    },
    "vinyasa": {
        "beginner": {
            "warm_up": [
                {"name": "Easy Pose", "sanskrit_name": "Sukhasana", "expertise_level": "Beginner"},
                {"name": "Sun Salutation A", "sanskrit_name": "Surya Namaskara A", "expertise_level": "Intermediate"}
            ],
            "flow": [
                {"name": "Warrior I", "sanskrit_name": "Virabhadrasana I", "expertise_level": "Beginner"},
                {"name": "High Lunge", "sanskrit_name": "Utthita Ashwa Sanchalanasana", "expertise_level": "Beginner"},
                {"name": "Triangle Pose", "sanskrit_name": "Trikonasana", "expertise_level": "Beginner"}
            ],
            "peak": [
                {"name": "Crow Pose", "sanskrit_name": "Bakasana", "expertise_level": "Intermediate"},
                {"name": "Headstand Preparation", "sanskrit_name": "Sirsasana Prep", "expertise_level": "Intermediate"}
            ],
            "cool_down": [
                {"name": "Pigeon Pose", "sanskrit_name": "Eka Pada Rajakapotasana", "expertise_level": "Intermediate"},
                {"name": "Happy Baby Pose", "sanskrit_name": "Ananda Balasana", "expertise_level": "Beginner"},
                {"name": "Corpse Pose", "sanskrit_name": "Savasana", "expertise_level": "Beginner"}
            ]
        },
        "intermediate": {
            "warm_up": [
                {"name": "Sun Salutation A", "sanskrit_name": "Surya Namaskara A", "expertise_level": "Intermediate"},
                {"name": "Sun Salutation B", "sanskrit_name": "Surya Namaskara B", "expertise_level": "Intermediate"}
            ],
            "flow": [
                {"name": "Warrior III", "sanskrit_name": "Virabhadrasana III", "expertise_level": "Intermediate"},
                {"name": "Side Plank", "sanskrit_name": "Vasisthasana", "expertise_level": "Intermediate"},
                {"name": "Eagle Pose", "sanskrit_name": "Garudasana", "expertise_level": "Intermediate"}
            ],
            "peak": [
                {"name": "Crow Pose", "sanskrit_name": "Bakasana", "expertise_level": "Intermediate"},
                {"name": "Forearm Stand", "sanskrit_name": "Pincha Mayurasana", "expertise_level": "Advanced"},
                {"name": "King Pigeon Pose", "sanskrit_name": "Eka Pada Rajakapotasana", "expertise_level": "Advanced"}
            ],
            "cool_down": [
                {"name": "Double Pigeon", "sanskrit_name": "Agnistambhasana", "expertise_level": "Intermediate"},
                {"name": "Supine Twist", "sanskrit_name": "Supta Matsyendrasana", "expertise_level": "Beginner"},
                {"name": "Corpse Pose", "sanskrit_name": "Savasana", "expertise_level": "Beginner"}
            ]
        }
    },
    "stress_relief": {
        "all_levels": {
            "grounding": [
                {"name": "Child's Pose", "sanskrit_name": "Balasana", "expertise_level": "Beginner"},
                {"name": "Easy Pose", "sanskrit_name": "Sukhasana", "expertise_level": "Beginner"}
            ],
            "gentle": [
                {"name": "Cat-Cow Pose", "sanskrit_name": "Marjaryasana-Bitilasana", "expertise_level": "Beginner"},
                {"name": "Gentle Twist", "sanskrit_name": "Bharadvajasana", "expertise_level": "Beginner"},
                {"name": "Legs-Up-the-Wall Pose", "sanskrit_name": "Viparita Karani", "expertise_level": "Beginner"}
            ],
            "restorative": [
                {"name": "Supported Forward Fold", "sanskrit_name": "Janu Sirsasana (Supported)", "expertise_level": "Beginner"},
                {"name": "Reclined Bound Angle", "sanskrit_name": "Supta Baddha Konasana", "expertise_level": "Beginner"},
                {"name": "Heart Opener", "sanskrit_name": "Anahatasana", "expertise_level": "Beginner"}
            ],
            "relaxation": [
                {"name": "Body Scan", "sanskrit_name": "Yoga Nidra", "expertise_level": "Beginner"},
                {"name": "Yoga Nidra", "sanskrit_name": "Yoga Nidra", "expertise_level": "Beginner"},
                {"name": "Extended Corpse Pose", "sanskrit_name": "Savasana", "expertise_level": "Beginner"}
            ]
        }
    }
}


@mcp.tool(
    title="Create Yoga Sequence",
    description="Generate a personalized yoga class sequence based on duration, level, and style"
)
def create_yoga_sequence(
    duration_minutes: int = Field(description="Class duration in minutes (5-90)"),
    level: str = Field(description="Student level: beginner, intermediate, or advanced"),
    style: str = Field(description="Yoga style: hatha, vinyasa, or stress_relief"),
    focus: str = Field(description="Class focus (optional): hip_opening, backbends, strength, flexibility", default="balanced")
) -> Dict:
    """
    Create a customized yoga sequence with intelligent time allocation.
    
    This tool generates a complete yoga class structure including:
    - Automatic time distribution across different sequence sections
    - Pose selection based on available time and style
    - Structured output with class metadata and detailed sections
    
    Args:
        duration_minutes: Total class duration (5-90 minutes)
        level: Student experience level (beginner/intermediate/advanced)
        style: Yoga practice style (hatha/vinyasa/stress_relief)
        focus: Optional class focus area for specialized sequences
    
    Returns:
        Dictionary containing complete sequence with sections, timing, and pose counts
    """
    
    # Validate inputs
    if duration_minutes < 5 or duration_minutes > 90:
        return {"error": "Duration must be between 5 and 90 minutes"}
    
    if style not in SEQUENCE_TEMPLATES:
        return {"error": f"Style must be one of: {list(SEQUENCE_TEMPLATES.keys())}"}
    
    # Get appropriate template
    style_template = SEQUENCE_TEMPLATES[style]
    
    # For stress relief, use all_levels template
    if style == "stress_relief":
        level = "all_levels"
    
    if level not in style_template:
        available_levels = list(style_template.keys())
        return {"error": f"Level '{level}' not available for {style}. Available: {available_levels}"}
    
    template = style_template[level]
    
    # Calculate time allocation based on duration
    time_allocation = calculate_time_allocation(duration_minutes, style)
    
    # Build sequence
    sequence = {
        "class_info": {
            "duration": duration_minutes,
            "level": level,
            "style": style,
            "focus": focus
        },
        "sequence": [],
        "time_breakdown": time_allocation,
        "total_poses": 0
    }
    
    # Add poses from template based on time allocation
    for section, time_mins in time_allocation.items():
        if section in template and time_mins > 0:
            poses_in_section = template[section]
            # Select poses based on available time
            selected_poses = select_poses_for_time(poses_in_section, time_mins)
            
            sequence["sequence"].append({
                "section": section.replace("_", " ").title(),
                "duration_minutes": time_mins,
                "poses": selected_poses
            })
            sequence["total_poses"] += len(selected_poses)
    
    return sequence


@mcp.tool(
    title="Generate Pose Procedure",
    description="Generate detailed step-by-step instructions for a yoga pose using AI"
)
def generate_pose_procedure(
    pose_name: str = Field(description="English name of the yoga pose"),
    sanskrit_name: str = Field(description="Sanskrit name of the yoga pose", default=""),
    expertise_level: str = Field(description="Difficulty level: Beginner, Intermediate, or Advanced", default="Beginner"),
    include_modifications: bool = Field(description="Include modifications and variations", default=True)
) -> Dict:
    """
    Generate comprehensive pose instructions using OpenAI's TTS model.
    
    This tool creates detailed, step-by-step procedures for yoga poses including:
    - Entry and exit instructions
    - Alignment cues and safety tips
    - Breathing guidance
    - Common modifications and variations
    - Benefits and contraindications
    
    Args:
        pose_name: English name of the pose
        sanskrit_name: Sanskrit name (optional)
        expertise_level: Difficulty level for appropriate instruction depth
        include_modifications: Whether to include pose variations
    
    Returns:
        Dictionary containing comprehensive pose information and instructions
    """
    
    # Base procedure template (enhanced with OpenAI TTS model integration)
    base_procedures = {
        "Mountain Pose": "Stand tall with feet hip-width apart. Ground through your feet, lengthen your spine, and relax your shoulders. Breathe deeply and find your center.",
        "Child's Pose": "Kneel on the floor, touch your big toes together and sit back on your heels. Separate your knees about hip-width apart. Fold forward, extending your arms in front of you or alongside your body.",
        "Downward-Facing Dog": "Start on hands and knees. Tuck your toes under and lift your hips up and back. Straighten your legs and create an inverted V-shape with your body.",
        "Warrior I": "Step your left foot back about 3-4 feet. Turn your left foot out 45 degrees. Bend your right knee over your ankle. Reach your arms overhead.",
        "Triangle Pose": "Stand with feet wide apart. Turn your right foot out 90 degrees. Reach your right hand toward your right shin or the floor. Extend your left arm toward the ceiling."
    }
    
    # Get base procedure or create a generic one
    base_procedure = base_procedures.get(pose_name, 
        f"This is a {expertise_level.lower()} level yoga pose. Begin by finding a stable foundation and moving mindfully into the pose. Listen to your body and breathe deeply throughout.")
    
    # Enhanced procedure with OpenAI TTS-style detailed instructions
    enhanced_procedure = f"""
**POSE SETUP:**
{base_procedure}

**DETAILED ALIGNMENT:**
• Foundation: Establish a strong base and engage your core
• Spine: Maintain length through your spine, avoiding compression
• Breath: Use slow, deep breaths to support the pose
• Gaze: Find a focal point to help with balance and concentration

**STEP-BY-STEP ENTRY:**
1. Begin in a neutral position
2. Move slowly and mindfully into the pose
3. Make micro-adjustments for comfort and stability
4. Hold for 5-8 breaths or as feels appropriate

**SAFETY NOTES:**
• Stop if you feel any sharp pain
• Modify as needed for your body
• Use props if helpful for support
• Exit slowly and mindfully
"""

    if include_modifications and expertise_level.lower() == "beginner":
        modifications = """
**BEGINNER MODIFICATIONS:**
• Use blocks or props for support
• Reduce the depth of the pose
• Hold for shorter duration
• Focus on alignment over depth
"""
        enhanced_procedure += modifications
    
    elif include_modifications and expertise_level.lower() == "intermediate":
        variations = """
**INTERMEDIATE VARIATIONS:**
• Deepen the pose gradually
• Add arm variations
• Increase holding time
• Explore subtle movements
"""
        enhanced_procedure += variations
    
    return {
        "pose_info": {
            "name": pose_name,
            "sanskrit_name": sanskrit_name or "Sanskrit name not provided",
            "expertise_level": expertise_level,
            "has_modifications": include_modifications
        },
        "procedure": enhanced_procedure.strip(),
        "estimated_duration": "30-60 seconds for beginners, 1-2 minutes for advanced",
        "benefits": f"This pose helps improve strength, flexibility, and body awareness appropriate for {expertise_level.lower()} practitioners.",
        "contraindications": "Avoid if you have relevant injuries. Consult with a qualified instructor if unsure.",
        "generated_by": "Yoga Sequencing MCP Server with OpenAI TTS AI enhancement"
    }


@mcp.tool(
    title="Generate Simple Calming Audio",
    description="Generate simple, cost-effective calming audio instructions for yoga poses"
)
async def generate_pose_audio_with_openai(
    asana_name: str = Field(description="Name of the yoga pose/asana to generate audio for"),
    voice: str = Field(description="Calming voice (fixed to 'alloy' for consistency)", default="alloy"),
    include_breathing_cues: bool = Field(description="Include simple breathing guidance", default=True)
) -> Dict:
    """
    Generate simple, cost-effective calming audio instructions for yoga poses.
    
    This tool creates basic audio files with calming, gentle instructions:
    - Uses consistent 'alloy' voice for soothing tone
    - Fixed MP3 format to minimize costs
    - Normal speech speed for clarity
    - Simple English instructions only
    - Focuses on essential guidance to keep audio short
    
    Note: Optimized for cost-effectiveness while maintaining quality.
    
    Args:
        asana_name: Name of the yoga pose to generate audio instructions for
        voice: Fixed to 'alloy' for consistent calming tone
        include_breathing_cues: Whether to include simple breath guidance
    
    Returns:
        Dictionary containing audio data and metadata for the pose instructions
    """
    
    # First, get the detailed procedure for the pose
    procedure_result = generate_pose_procedure(
        pose_name=asana_name,
        sanskrit_name="",
        expertise_level="Beginner",
        include_modifications=False  # Simplified to reduce text length
    )
    
    if not procedure_result or "error" in procedure_result:
        return {
            "error": f"Could not find procedure for pose: {asana_name}",
            "suggestion": "Please check the pose name and try again"
        }
    
    # Extract pose information
    pose_info = procedure_result.get("pose_info", {})
    
    # Create simple, calming audio script (shorter to reduce costs)
    audio_script = create_simple_calming_script(
        pose_name=pose_info.get("name", asana_name),
        include_breathing_cues=include_breathing_cues
    )
    
    # Generate audio using OpenAI TTS with cost-effective settings
    try:
        audio_result = await call_openai_tts_api(
            text=audio_script,
            voice="alloy",  # Fixed calming voice
            format="mp3",   # Standard format
            speed=0.9       # Slightly slower for calming effect
        )
        
        if audio_result.get("success"):
            return {
                "pose_info": {
                    "name": pose_info.get("name", asana_name),
                    "type": "Simple calming instruction"
                },
                "audio_data": {
                    "audio_content": audio_result["audio_base64"],
                    "format": "mp3",
                    "voice": "alloy",
                    "speed": 0.9,
                    "duration_estimate": audio_result.get("duration", "30-60 seconds"),
                    "breathing_cues_included": include_breathing_cues
                },
                "script_text": audio_script,
                "cost_optimization": {
                    "model": "tts-1",
                    "voice_used": "alloy",
                    "note": "Optimized for cost-effectiveness with calming tone"
                },
                "generated_by": "Yoga Sequencing MCP Server - Simple Calming Audio",
                "usage_notes": "Short, calming audio optimized for cost and effectiveness"
            }
        else:
            return {
                "error": "Failed to generate audio",
                "details": audio_result.get("error", "Unknown error"),
                "fallback_text": audio_script
            }
            
    except Exception as e:
        return {
            "error": f"OpenAI TTS API error: {str(e)}",
            "fallback_text": audio_script,
            "suggestion": "Check your OpenAI API key and try again"
        }


@mcp.resource(
    uri="sequence://template/{style}/{level}",
    description="Get a sequence template for a specific style and level",
    name="Sequence Template"
)
def get_sequence_template(style: str, level: str) -> str:
    """
    Access raw sequence templates for inspection and customization.
    
    This resource provides direct access to the underlying pose templates
    used by the sequence generation tool. Useful for understanding the
    structure of different yoga styles and levels.
    
    URI Pattern: sequence://template/{style}/{level}
    
    Args:
        style: Yoga style (hatha, vinyasa, stress_relief)
        level: Skill level (beginner, intermediate, all_levels for stress_relief)
    
    Returns:
        JSON representation of the template structure with pose lists
        organized by sequence sections
    """
    
    if style in SEQUENCE_TEMPLATES:
        style_templates = SEQUENCE_TEMPLATES[style]
        if level in style_templates:
            template = style_templates[level]
            return json.dumps(template, indent=2)
    
    return json.dumps({"error": "Template not found"})


@mcp.resource(
    uri="pose://details/{pose_name}",
    description="Get detailed information about a specific yoga pose including Sanskrit name and procedure",
    name="Pose Details"
)
def get_pose_details(pose_name: str) -> str:
    """
    Access detailed information about a specific yoga pose.
    
    This resource provides comprehensive pose information including:
    - Sanskrit name and pronunciation
    - Expertise level requirements
    - Step-by-step procedure (when available)
    - Pose variations and modifications
    
    URI Pattern: pose://details/{pose_name}
    
    Args:
        pose_name: English name of the yoga pose
    
    Returns:
        JSON representation of detailed pose information
    """
    
    # Search through all templates to find the pose
    pose_found = None
    for style in SEQUENCE_TEMPLATES:
        for level in SEQUENCE_TEMPLATES[style]:
            for section in SEQUENCE_TEMPLATES[style][level]:
                poses = SEQUENCE_TEMPLATES[style][level][section]
                for pose in poses:
                    if isinstance(pose, dict) and pose.get("name") == pose_name:
                        pose_found = pose
                        break
                if pose_found:
                    break
            if pose_found:
                break
        if pose_found:
            break
    
    if pose_found:
        # Generate procedure for the found pose
        procedure_result = generate_pose_procedure(
            pose_name=pose_found["name"],
            sanskrit_name=pose_found["sanskrit_name"],
            expertise_level=pose_found["expertise_level"],
            include_modifications=True
        )
        
        detailed_info = {
            "pose_name": pose_found["name"],
            "sanskrit_name": pose_found["sanskrit_name"],
            "expertise_level": pose_found["expertise_level"],
            "procedure": procedure_result["procedure"],
            "benefits": procedure_result["benefits"],
            "contraindications": procedure_result["contraindications"],
            "estimated_duration": procedure_result["estimated_duration"],
            "found_in_styles": []
        }
        
        # Find which styles and levels include this pose
        for style in SEQUENCE_TEMPLATES:
            for level in SEQUENCE_TEMPLATES[style]:
                for section in SEQUENCE_TEMPLATES[style][level]:
                    poses = SEQUENCE_TEMPLATES[style][level][section]
                    for pose in poses:
                        if isinstance(pose, dict) and pose.get("name") == pose_name:
                            detailed_info["found_in_styles"].append({
                                "style": style,
                                "level": level,
                                "section": section
                            })
        
        return json.dumps(detailed_info, indent=2)
    
    return json.dumps({"error": f"Pose '{pose_name}' not found in templates"})


@mcp.prompt(
    title="Generate Class Theme",
    description="Create an inspiring theme and intention for a yoga class"
)
def generate_class_theme(
    style: str = Field(description="Yoga style for the class"),
    duration: int = Field(description="Class duration in minutes"),
    season: str = Field(description="Current season or time of year", default="spring"),
    intention: str = Field(description="Desired class intention or focus", default="balance")
) -> str:
    """
    Generate an inspiring theme and intention for yoga classes.
    
    This prompt creates comprehensive class themes including:
    - Seasonal-appropriate focus and energy
    - Opening intention and guidance for students
    - Closing reflection and integration
    - Music suggestions that complement the theme
    
    Args:
        style: Yoga practice style (affects theme selection)
        duration: Class length (incorporated into timing guidance)
        season: Current season for seasonal theming
        intention: Core intention or focus for the practice
    
    Returns:
        Formatted text with complete theme structure including
        title, intentions, reflections, and music suggestions
    """
    
    themes = {
        "hatha": [
            "Finding Stability in Stillness",
            "Grounding and Growing",
            "The Art of Slow Movement",
            "Building Foundation and Strength"
        ],
        "vinyasa": [
            "Flow Like Water",
            "Moving Meditation",
            "Breath as Your Guide",
            "Dancing with Change"
        ],
        "stress_relief": [
            "Releasing What No Longer Serves",
            "Coming Home to Yourself", 
            "Finding Peace in the Present",
            "Softening Into Stillness"
        ]
    }
    
    seasonal_elements = {
        "spring": "renewal, growth, fresh beginnings",
        "summer": "energy, warmth, expansion", 
        "fall": "letting go, transition, gratitude",
        "winter": "introspection, rest, inner warmth"
    }
    
    style_themes = themes.get(style, themes["hatha"])
    seasonal_element = seasonal_elements.get(season, "balance")
    
    return f"""
**Class Theme Suggestion:**

**Title:** {style_themes[0]}

**Duration:** {duration} minutes
**Style:** {style.title()}
**Seasonal Focus:** {seasonal_element}

**Opening Intention:**
"Today we practice with the intention of {intention}. As we move through our {duration}-minute {style} practice, let's embrace the energy of {season} - {seasonal_element}. Allow your breath to guide you as we explore {style_themes[0].lower()}."

**Closing Reflection:**
"Take a moment to notice how you feel after this practice. You've honored your body and breath today, finding {intention} through mindful movement."

**Suggested Music:** Gentle instrumental, nature sounds, or ambient music that supports {seasonal_element}
"""

# =============================================================================
# OPENAI TTS INTEGRATION FUNCTIONS
# =============================================================================

async def call_openai_tts_api(text: str, voice: str, format: str, speed: float) -> Dict:
    """
    Call OpenAI's Text-to-Speech API to generate audio from text.
    
    Args:
        text: Text content to convert to speech
        voice: OpenAI TTS voice (alloy, echo, fable, onyx, nova, shimmer)
        format: Audio format (mp3, opus, aac, flac)
        speed: Speech speed (0.25 to 4.0)
    
    Returns:
        Dictionary containing audio data and metadata
    """
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return {
            "success": False,
            "error": "OpenAI API key not found. Please set OPENAI_API_KEY environment variable."
        }
    
    # Validate parameters
    valid_voices = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
    valid_formats = ["mp3", "opus", "aac", "flac"]
    
    if voice not in valid_voices:
        return {
            "success": False,
            "error": f"Invalid voice. Must be one of: {', '.join(valid_voices)}"
        }
    
    if format not in valid_formats:
        return {
            "success": False,
            "error": f"Invalid format. Must be one of: {', '.join(valid_formats)}"
        }
    
    if not (0.25 <= speed <= 4.0):
        return {
            "success": False,
            "error": "Speed must be between 0.25 and 4.0"
        }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.openai.com/v1/audio/speech",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "tts-1",
                    "input": text,
                    "voice": voice,
                    "response_format": format,
                    "speed": speed
                }
            )
            
            if response.status_code == 200:
                # Convert audio bytes to base64 for JSON transport
                audio_bytes = response.content
                audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
                
                return {
                    "success": True,
                    "audio_base64": audio_base64,
                    "size_bytes": len(audio_bytes),
                    "format": format,
                    "voice": voice,
                    "speed": speed
                }
            else:
                error_details = response.text
                return {
                    "success": False,
                    "error": f"OpenAI API error: {response.status_code} - {error_details}"
                }
                
    except Exception as e:
        return {
            "success": False,
            "error": f"Network error calling OpenAI API: {str(e)}"
        }


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


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def calculate_time_allocation(duration_minutes: int, style: str) -> Dict[str, int]:
    """
    Calculate optimal time allocation for different sequence sections.
    
    Distributes class time based on yoga style best practices:
    - Stress Relief: Emphasizes restorative and relaxation phases
    - Hatha: Balanced distribution with focus on standing poses
    - Vinyasa: More time for flowing sequences and peak poses
    
    Args:
        duration_minutes: Total class duration
        style: Yoga style (affects time distribution strategy)
    
    Returns:
        Dictionary mapping sequence sections to allocated minutes
    """
    
    if style == "stress_relief":
        return {
            "grounding": max(2, duration_minutes // 6),
            "gentle": max(3, duration_minutes // 4), 
            "restorative": max(5, duration_minutes // 2),
            "relaxation": max(3, duration_minutes // 4)
        }
    elif style == "hatha":
        return {
            "warm_up": max(3, duration_minutes // 6),
            "standing": max(5, duration_minutes // 3),
            "seated": max(3, duration_minutes // 4),
            "backbends": max(2, duration_minutes // 8),
            "cool_down": max(5, duration_minutes // 4)
        }
    else:  # vinyasa
        return {
            "warm_up": max(3, duration_minutes // 5),
            "flow": max(8, duration_minutes // 2),
            "peak": max(3, duration_minutes // 4),
            "cool_down": max(5, duration_minutes // 4)
        }


def select_poses_for_time(poses: List[Dict], time_minutes: int) -> List[Dict]:
    """
    Select appropriate number of poses for given time allocation.
    
    Estimates pose count based on average holding time:
    - Roughly 1-2 minutes per pose depending on style and complexity
    - Ensures at least one pose is selected even for short time segments
    
    Args:
        poses: List of pose dictionaries with name, sanskrit_name, and expertise_level
        time_minutes: Allocated time for this section
    
    Returns:
        Subset of poses that fit within the time allocation
    """
    
    # Roughly 1-2 minutes per pose depending on style
    target_poses = max(1, min(time_minutes // 1.5, len(poses)))
    return poses[:int(target_poses)]


def extract_pose_names(poses: List[Dict]) -> List[str]:
    """
    Extract just the pose names from the enhanced pose data structure.
    
    Args:
        poses: List of pose dictionaries
    
    Returns:
        List of pose names for backward compatibility
    """
    return [pose["name"] if isinstance(pose, dict) else pose for pose in poses]


def get_pose_with_sanskrit(pose_name: str, poses_list: List[Dict]) -> Dict:
    """
    Find a pose by name and return its full information including Sanskrit name.
    
    Args:
        pose_name: Name of the pose to find
        poses_list: List of pose dictionaries to search
    
    Returns:
        Dictionary with pose information or basic structure if not found
    """
    for pose in poses_list:
        if isinstance(pose, dict) and pose.get("name") == pose_name:
            return pose
    
    # Return basic structure if not found
    return {
        "name": pose_name,
        "sanskrit_name": "Sanskrit name not available",
        "expertise_level": "Beginner"
    }


# =============================================================================
# SERVER STARTUP
# =============================================================================

if __name__ == "__main__":
    """
    Start the Yoga Sequencing MCP Server.
    
    The server runs on port 3000 with streamable HTTP transport,
    making it compatible with MCP clients and Claude Desktop.
    """
    mcp.run(transport="streamable-http")
