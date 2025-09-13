"""
Yoga Class Sequencing MCP Server
Creates personalized yoga class sequences with semantic search from Qdrant database
"""

from mcp.server.fastmcp import FastMCP
from pydantic import Field
import os
import json
from typing import List, Dict, Optional
import mcp.types as types

# Initialize FastMCP server
mcp = FastMCP("Yoga Sequencing Server", port=3000, stateless_http=True, debug=True)

# # Initialize Qdrant client (commented out)
# def get_qdrant_client():
#     """Initialize Qdrant client with environment variables"""
#     qdrant_url = os.getenv("QDRANT_URL")
#     qdrant_api_key = os.getenv("QDRANT_API_KEY")
    
#     if not qdrant_url:
#         raise ValueError("QDRANT_URL environment variable not set")
    
#     return QdrantClient(
#         url=qdrant_url,
#         api_key=qdrant_api_key,
#         timeout=30
#     )

# Yoga sequence templates for different styles and purposes
SEQUENCE_TEMPLATES = {
    "hatha": {
        "beginner": {
            "warm_up": ["Easy Pose", "Neck Rolls", "Shoulder Rolls", "Cat-Cow Pose"],
            "standing": ["Mountain Pose", "Tree Pose", "Warrior I", "Triangle Pose"],
            "seated": ["Staff Pose", "Bound Angle Pose", "Seated Forward Fold", "Easy Twist"],
            "backbends": ["Bridge Pose", "Camel Pose (supported)"],
            "cool_down": ["Child's Pose", "Supine Twist", "Legs Up Wall", "Savasana"]
        },
        "intermediate": {
            "warm_up": ["Cat-Cow Pose", "Downward Dog", "Sun Salutation A"],
            "standing": ["Warrior I", "Warrior II", "Triangle Pose", "Extended Side Angle"],
            "seated": ["Boat Pose", "Marichyasana", "Seated Forward Fold"],
            "backbends": ["Camel Pose", "Wheel Pose", "Fish Pose"],
            "cool_down": ["Pigeon Pose", "Supine Figure 4", "Savasana"]
        }
    },
    "vinyasa": {
        "beginner": {
            "warm_up": ["Easy Pose", "Sun Salutation A (modified)"],
            "flow": ["Warrior I to High Lunge", "Triangle to Extended Side Angle"],
            "peak": ["Crow Pose (supported)", "Headstand prep"],
            "cool_down": ["Pigeon Pose", "Happy Baby", "Savasana"]
        },
        "intermediate": {
            "warm_up": ["Sun Salutation A", "Sun Salutation B"],
            "flow": ["Warrior III flow", "Side Plank variations", "Eagle to Twisted Eagle"],
            "peak": ["Crow Pose", "Forearm Stand", "King Pigeon"],
            "cool_down": ["Double Pigeon", "Supine Twist", "Savasana"]
        }
    },
    "stress_relief": {
        "all_levels": {
            "grounding": ["Child's Pose", "Easy Pose with breathing"],
            "gentle": ["Cat-Cow Pose", "Gentle Twists", "Legs Up Wall"],
            "restorative": ["Supported Forward Fold", "Reclined Bound Angle", "Heart Bench"],
            "relaxation": ["Body Scan", "Yoga Nidra", "Extended Savasana"]
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
    """Create a customized yoga sequence"""
    
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


# @mcp.tool(
#     title="Semantic Pose Search",
#     description="Search yoga poses using natural language descriptions with semantic similarity"
# )
# def semantic_pose_search(
#     query: str = Field(description="Natural language search query (e.g., 'poses for tight hips', 'calming poses for stress')")
# ) -> List[Dict]:
#     """Search poses using semantic similarity from Qdrant vector database"""
    
#     try:
#         client = get_qdrant_client()
#         collection_name = os.getenv("COLLECTION_NAME", "yoga_poses")
        
#         # Convert query to embedding vector
#         query_vector = embedding_model.encode(query).tolist()
        
#         # Perform semantic search using vector similarity
#         search_result = client.search(
#             collection_name=collection_name,
#             query_vector=query_vector,
#             limit=10,
#             with_payload=True,
#             score_threshold=0.3  # Minimum similarity threshold
#         )
        
#         poses = []
#         for hit in search_result:
#             pose_data = hit.payload
#             poses.append({
#                 "pose_name": pose_data.get("name", ""),
#                 "sanskrit_name": pose_data.get("sanskrit_name", ""),
#                 "expertise_level": pose_data.get("expertise_level", ""),
#                 "pose_type": pose_data.get("pose_type", []),
#                 "photo_url": pose_data.get("photo_url", ""),
#                 "relevance_score": round(hit.score, 3),
#                 "has_photo": pose_data.get("metadata", {}).get("has_photo", False)
#             })
        
#         return poses
        
#     except Exception as e:
#         return [{"error": f"Failed to perform semantic search: {str(e)}"}]


@mcp.resource(
    uri="sequence://template/{style}/{level}",
    description="Get a sequence template for a specific style and level",
    name="Sequence Template"
)
def get_sequence_template(style: str, level: str) -> str:
    """Get a sequence template"""
    
    if style in SEQUENCE_TEMPLATES:
        style_templates = SEQUENCE_TEMPLATES[style]
        if level in style_templates:
            template = style_templates[level]
            return json.dumps(template, indent=2)
    
    return json.dumps({"error": "Template not found"})


# @mcp.resource(
#     uri="poses://type/{pose_type}",
#     description="Get list of poses by type (Standing, Forward Bend, etc.)",
#     name="Poses by Type"
# )
# def get_poses_by_type_resource(pose_type: str) -> str:
#     """Resource to get poses by type"""
    
#     try:
#         client = get_qdrant_client()
#         collection_name = os.getenv("COLLECTION_NAME", "yoga_poses")
        
#         search_result = client.scroll(
#             collection_name=collection_name,
#             scroll_filter={
#                 "must": [
#                     {
#                         "key": "pose_type",
#                         "match": {"any": [pose_type]}
#                     }
#                 ]
#             },
#             limit=15,
#             with_payload=True
#         )
        
#         poses = []
#         for point in search_result[0]:
#             pose_data = point.payload
#             poses.append({
#                 "name": pose_data.get("name", ""),
#                 "sanskrit_name": pose_data.get("sanskrit_name", ""),
#                 "expertise_level": pose_data.get("expertise_level", ""),
#                 "has_photo": pose_data.get("metadata", {}).get("has_photo", False)
#             })
        
#         return json.dumps({
#             "pose_type": pose_type, 
#             "total_poses": len(poses),
#             "poses": poses
#         }, indent=2)
        
#     except Exception as e:
#         return json.dumps({"error": f"Failed to get poses: {str(e)}"})


# @mcp.resource(
#     uri="poses://expertise/{level}",
#     description="Get poses by expertise level (Beginner, Intermediate, Advanced)",
#     name="Poses by Expertise Level"
# )
# def get_poses_by_expertise_resource(level: str) -> str:
#     """Resource to get poses by expertise level"""
    
#     try:
#         client = get_qdrant_client()
#         collection_name = os.getenv("COLLECTION_NAME", "yoga_poses")
        
#         search_result = client.scroll(
#             collection_name=collection_name,
#             scroll_filter={
#                 "must": [
#                     {
#                         "key": "expertise_level",
#                         "match": {"text": level}
#                     }
#                 ]
#             },
#             limit=20,
#             with_payload=True
#         )
        
#         poses = []
#         for point in search_result[0]:
#             pose_data = point.payload
#             poses.append({
#                 "name": pose_data.get("name", ""),
#                 "sanskrit_name": pose_data.get("sanskrit_name", ""),
#                 "pose_type": pose_data.get("pose_type", []),
#                 "photo_url": pose_data.get("photo_url", "")
#             })
        
#         return json.dumps({
#             "expertise_level": level,
#             "total_poses": len(poses), 
#             "poses": poses
#         }, indent=2)
        
#     except Exception as e:
#         return json.dumps({"error": f"Failed to get poses: {str(e)}"})





# Update the sequence templates to use actual pose names from the database
SEQUENCE_TEMPLATES = {
    "hatha": {
        "beginner": {
            "warm_up": ["Easy Pose", "Cat-Cow Pose", "Child's Pose"],
            "standing": ["Mountain Pose", "Tree Pose", "Triangle Pose", "Warrior I"],
            "seated": ["Staff Pose", "Bound Angle Pose", "Seated Forward Fold"],
            "backbends": ["Bridge Pose", "Camel Pose"],
            "cool_down": ["Child's Pose", "Supine Twist", "Corpse Pose"]
        },
        "intermediate": {
            "warm_up": ["Cat-Cow Pose", "Downward-Facing Dog", "Sun Salutation A"],
            "standing": ["Warrior I", "Warrior II", "Triangle Pose", "Extended Side Angle"],
            "seated": ["Boat Pose", "Seated Forward Fold", "Seated Spinal Twist"],
            "backbends": ["Camel Pose", "Wheel Pose", "Fish Pose"],
            "cool_down": ["Pigeon Pose", "Supine Figure 4", "Corpse Pose"]
        }
    },
    "vinyasa": {
        "beginner": {
            "warm_up": ["Easy Pose", "Sun Salutation A"],
            "flow": ["Warrior I", "High Lunge", "Triangle Pose"],
            "peak": ["Crow Pose", "Headstand Preparation"],
            "cool_down": ["Pigeon Pose", "Happy Baby Pose", "Corpse Pose"]
        },
        "intermediate": {
            "warm_up": ["Sun Salutation A", "Sun Salutation B"],
            "flow": ["Warrior III", "Side Plank", "Eagle Pose"],
            "peak": ["Crow Pose", "Forearm Stand", "King Pigeon Pose"],
            "cool_down": ["Double Pigeon", "Supine Twist", "Corpse Pose"]
        }
    },
    "stress_relief": {
        "all_levels": {
            "grounding": ["Child's Pose", "Easy Pose"],
            "gentle": ["Cat-Cow Pose", "Gentle Twist", "Legs-Up-the-Wall Pose"],
            "restorative": ["Supported Forward Fold", "Reclined Bound Angle", "Heart Opener"],
            "relaxation": ["Body Scan", "Yoga Nidra", "Extended Corpse Pose"]
        }
    }
}


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
    """Generate an inspiring class theme"""
    
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


# Helper functions
def calculate_time_allocation(duration_minutes: int, style: str) -> Dict[str, int]:
    """Calculate time allocation for different sequence sections"""
    
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


def select_poses_for_time(poses: List[str], time_minutes: int) -> List[str]:
    """Select appropriate number of poses for given time"""
    
    # Roughly 1-2 minutes per pose depending on style
    target_poses = max(1, min(time_minutes // 1.5, len(poses)))
    return poses[:int(target_poses)]


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
