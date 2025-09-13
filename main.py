"""
Yoga Teacher Sequencing MCP Server

OVERVIEW:
This MCP server helps yoga teachers create effective class sequences by combining:
1. Built-in sequencing templates for different yoga styles
2. Qdrant vector database integration for pose discovery
3. Semantic search for finding poses based on natural language queries

PROCESS STEPS:
1. Create basic sequences using predefined templates
2. Search for specific poses using semantic queries
3. Generate inspiring class themes and intentions
4. Access pose details and variations from the database

The server focuses purely on helping yoga teachers plan and sequence their classes effectively.
"""

from mcp.server.fastmcp import FastMCP
from pydantic import Field
import os
import json
from typing import List, Dict, Optional
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
import mcp.types as types

# Initialize FastMCP server
mcp = FastMCP("Yoga Teacher Sequencing Server", port=3000, stateless_http=True, debug=True)

# Initialize embedding model for semantic search
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

# Initialize Qdrant client
def get_qdrant_client():
    """Initialize Qdrant client with environment variables.
    
    Returns:
        QdrantClient: Configured client for vector database operations
    """
    qdrant_url = os.getenv("QDRANT_URL")
    qdrant_api_key = os.getenv("QDRANT_API_KEY")
    
    if not qdrant_url:
        raise ValueError("QDRANT_URL environment variable not set")
    
    return QdrantClient(
        url=qdrant_url,
        api_key=qdrant_api_key,
        timeout=30
    )


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
    """Create a customized yoga sequence using predefined templates.

    Args:
        duration_minutes: Class duration in minutes (5-90)
        level: Student level: beginner, intermediate, or advanced
        style: Yoga style: hatha, vinyasa, or stress_relief
        focus: Class focus area for targeted sequencing
    """
    
    if duration_minutes < 5 or duration_minutes > 90:
        return {"error": "Duration must be between 5 and 90 minutes"}
    
    if style not in SEQUENCE_TEMPLATES:
        return {"error": f"Style must be one of: {list(SEQUENCE_TEMPLATES.keys())}"}
    
    style_template = SEQUENCE_TEMPLATES[style]
    
    if style == "stress_relief":
        level = "all_levels"
    
    if level not in style_template:
        available_levels = list(style_template.keys())
        return {"error": f"Level '{level}' not available for {style}. Available: {available_levels}"}
    
    template = style_template[level]
    
    time_allocation = calculate_time_allocation(duration_minutes, style)
    
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
    title="Search Poses Semantically",
    description="Find yoga poses using natural language descriptions with semantic similarity"
)
def search_poses_semantically(
    query: str = Field(description="Natural language search query (e.g., 'poses for tight hips', 'calming poses for stress')")
) -> List[Dict]:
    """Search poses using semantic similarity from Qdrant vector database.

    Args:
        query: Natural language search query describing desired poses or benefits
    """
    
    try:
        client = get_qdrant_client()
        collection_name = os.getenv("COLLECTION_NAME", "yoga_poses")
        
        # Convert query to embedding vector
        query_vector = embedding_model.encode(query).tolist()
        
        # Perform semantic search using vector similarity
        search_result = client.search(
            collection_name=collection_name,
            query_vector=query_vector,
            limit=10,
            with_payload=True,
            score_threshold=0.3  # Minimum similarity threshold
        )
        
        poses = []
        for hit in search_result:
            pose_data = hit.payload
            poses.append({
                "pose_name": pose_data.get("name", ""),
                "sanskrit_name": pose_data.get("sanskrit_name", ""),
                "expertise_level": pose_data.get("expertise_level", ""),
                "pose_type": pose_data.get("pose_type", []),
                "photo_url": pose_data.get("photo_url", ""),
                "relevance_score": round(hit.score, 3),
                "has_photo": pose_data.get("metadata", {}).get("has_photo", False)
            })
        
        return poses
        
    except Exception as e:
        return [{"error": f"Failed to perform semantic search: {str(e)}"}]


@mcp.tool(
    title="Get Pose Details",
    description="Retrieve detailed information about a specific yoga pose"
)
def get_pose_details(
    pose_name: str = Field(description="Name of the yoga pose (e.g., 'Downward Dog', 'Tree Pose')")
) -> Dict:
    """Get detailed information about a yoga pose from Qdrant database.

    Args:
        pose_name: Name of the yoga pose to look up
    """
    
    try:
        client = get_qdrant_client()
        collection_name = os.getenv("COLLECTION_NAME", "yoga_poses")
        
        # Search for the pose in Qdrant using name matching
        search_result = client.scroll(
            collection_name=collection_name,
            scroll_filter={
                "must": [
                    {
                        "key": "name",
                        "match": {"text": pose_name}
                    }
                ]
            },
            limit=1,
            with_payload=True
        )
        
        if not search_result[0]:
            return {"error": f"Pose '{pose_name}' not found in database"}
        
        pose_data = search_result[0][0].payload
        
        return {
            "pose_name": pose_data.get("name", pose_name),
            "sanskrit_name": pose_data.get("sanskrit_name", ""),
            "expertise_level": pose_data.get("expertise_level", ""),
            "pose_type": pose_data.get("pose_type", []),
            "photo_url": pose_data.get("photo_url", ""),
            "metadata": pose_data.get("metadata", {}),
            "id": pose_data.get("id", "")
        }
        
    except Exception as e:
        return {"error": f"Failed to retrieve pose details: {str(e)}"}


@mcp.tool(
    title="Find Poses by Type",
    description="Search yoga poses by category and expertise level"
)
def find_poses_by_type(
    pose_type: str = Field(description="Pose type: Standing, Forward Bend, Backbend, Twist, Inversion, Arm Balance, etc."),
    expertise_level: str = Field(description="Expertise level: Beginner, Intermediate, Advanced", default="all")
) -> List[Dict]:
    """Search for poses by type and expertise level from Qdrant database.

    Args:
        pose_type: Category of poses to find
        expertise_level: Difficulty level filter for poses
    """
    
    try:
        client = get_qdrant_client()
        collection_name = os.getenv("COLLECTION_NAME", "yoga_poses")
        
        # Build filter - pose_type is an array field
        filter_conditions = [
            {
                "key": "pose_type",
                "match": {"any": [pose_type]}
            }
        ]
        
        if expertise_level != "all":
            filter_conditions.append({
                "key": "expertise_level", 
                "match": {"text": expertise_level}
            })
        
        search_result = client.scroll(
            collection_name=collection_name,
            scroll_filter={"must": filter_conditions},
            limit=15,
            with_payload=True
        )
        
        poses = []
        for point in search_result[0]:
            pose_data = point.payload
            poses.append({
                "pose_name": pose_data.get("name", ""),
                "sanskrit_name": pose_data.get("sanskrit_name", ""),
                "expertise_level": pose_data.get("expertise_level", ""),
                "pose_type": pose_data.get("pose_type", []),
                "photo_url": pose_data.get("photo_url", ""),
                "has_photo": pose_data.get("metadata", {}).get("has_photo", False)
            })
        
        return poses
        
    except Exception as e:
        return [{"error": f"Failed to search poses: {str(e)}"}]


# Sequence templates kept as fallback data when Qdrant is not available
# These provide reliable pose sequences for different yoga styles and levels


@mcp.resource(
    uri="sequence://template/{style}/{level}",
    description="Get a sequence template for a specific style and level",
    name="Sequence Template"
)
def get_sequence_template(style: str, level: str) -> str:
    """Get a sequence template for planning classes.

    Args:
        style: Yoga style (hatha, vinyasa, stress_relief)
        level: Student level (beginner, intermediate, advanced)
    """
    
    if style in SEQUENCE_TEMPLATES:
        style_templates = SEQUENCE_TEMPLATES[style]
        if level in style_templates:
            template = style_templates[level]
            return json.dumps(template, indent=2)
    
    return json.dumps({"error": "Template not found"})


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
    """Generate an inspiring class theme with seasonal elements.

    Args:
        style: Yoga style to theme the class around
        duration: Class duration for appropriate pacing
        season: Current season for seasonal theming
        intention: Desired focus or intention for the class
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


def calculate_time_allocation(duration_minutes: int, style: str) -> Dict[str, int]:
    """Calculate time allocation for different sequence sections.

    Args:
        duration_minutes: Total class duration
        style: Yoga style to determine section timing
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


def select_poses_for_time(poses: List[str], time_minutes: int) -> List[str]:
    """Select appropriate number of poses for given time allocation.

    Args:
        poses: List of available poses for the section
        time_minutes: Time allocated for this section
    """
    target_poses = max(1, min(time_minutes // 1.5, len(poses)))
    return poses[:int(target_poses)]


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
