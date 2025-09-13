#!/usr/bin/env python3
"""
Yoga Curriculum FastMCP Server

This FastMCP server helps yoga teachers create customized course curricula
using Qdrant vector database for pose search and Mistral AI for enhancement.
"""

import asyncio
import os
import sys
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

# Import FastMCP
from fastmcp import FastMCP
from pydantic import Field
from src.mcpservers.enhanced_yoga_curriculum_generator import EnhancedYogaCurriculumGenerator

# Import Qdrant dependencies  
try:
    from qdrant_client import QdrantClient
    from qdrant_client import models
    from sentence_transformers import SentenceTransformer
    QDRANT_AVAILABLE = True
except ImportError:
    print("Warning: Qdrant dependencies not available. Please install them.")
    QDRANT_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastMCP app
mcp = FastMCP("yoga-curriculum")

# Global components
qdrant_client = None
embedding_model = None
enhanced_generator = None
initialized = False

# Configuration
config = {
    "qdrant_url": os.getenv("QDRANT_URL", ""),
    "qdrant_api_key": os.getenv("QDRANT_API_KEY", ""),
    "mistral_api_key": os.getenv("MISTRAL_API_KEY", ""),
    "embedding_model": os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2"),
    "collection_name": os.getenv("COLLECTION_NAME", "yoga_poses")
}

async def initialize_components():
    """Initialize Qdrant client, embedding model, and enhanced generator."""
    global qdrant_client, embedding_model, enhanced_generator, initialized
    
    if initialized:
        return True
    
    try:
        if not QDRANT_AVAILABLE:
            print("⚠️ Qdrant dependencies not available. Install qdrant-client and sentence-transformers")
            return False
        
        # Initialize Qdrant client if credentials available
        if config["qdrant_url"] and config["qdrant_api_key"]:
            qdrant_client = QdrantClient(
                url=config["qdrant_url"],
                api_key=config["qdrant_api_key"]
            )
            print("✅ Qdrant client initialized")
            
            # Initialize embedding model
            embedding_model = SentenceTransformer(config["embedding_model"])
            print("✅ Embedding model loaded")
        else:
            print("⚠️ Qdrant credentials not provided - running in demo mode")
        
        # Initialize enhanced curriculum generator
        enhanced_generator = EnhancedYogaCurriculumGenerator()
        print("✅ Enhanced curriculum generator initialized")
        
        if config["mistral_api_key"]:
            print("✅ Mistral AI integration available")
        else:
            print("⚠️ Mistral API key not provided - running without AI enhancement")
        
        initialized = True
        return True
        
    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        return False

async def search_yoga_poses(
    query: str, 
    limit: int = 10,
    expertise_filter: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Search for yoga poses using Qdrant."""
    if not qdrant_client or not embedding_model:
        # Return demo poses if Qdrant not available
        return get_demo_poses(expertise_filter or "beginner")
    
    try:
        # Generate query embedding
        query_embedding = embedding_model.encode([query])
        query_vector = query_embedding[0].tolist()
        
        # Build filter conditions
        must_conditions = []
        if expertise_filter:
            must_conditions.append(
                models.FieldCondition(
                    key="expertise_level",
                    match=models.MatchValue(value=expertise_filter)
                )
            )
        
        query_filter = models.Filter(must=must_conditions) if must_conditions else None
        
        # Perform search
        search_results = qdrant_client.query_points(
            collection_name=config["collection_name"],
            query=query_vector,
            query_filter=query_filter,
            limit=limit,
            with_payload=True
        )
        
        # Format results
        results = []
        for result in search_results.points:
            results.append({
                'id': result.id,
                'score': result.score,
                'pose': result.payload
            })
        
        return results
        
    except Exception as e:
        print(f"Error searching poses: {e}")
        return get_demo_poses(expertise_filter or "beginner")

def get_demo_poses(level: str) -> List[Dict[str, Any]]:
    """Get demo poses for testing without Qdrant."""
    demo_poses = [
        {"pose": {"name": "Mountain Pose", "sanskrit_name": "Tadasana", "expertise_level": level.title(), "pose_type": ["Standing"]}},
        {"pose": {"name": "Tree Pose", "sanskrit_name": "Vrikshasana", "expertise_level": level.title(), "pose_type": ["Standing", "Balancing"]}},
        {"pose": {"name": "Warrior I Pose", "sanskrit_name": "Virabhadrasana A", "expertise_level": level.title(), "pose_type": ["Standing"]}},
        {"pose": {"name": "Warrior II Pose", "sanskrit_name": "Virabhadrasana B", "expertise_level": level.title(), "pose_type": ["Standing"]}},
        {"pose": {"name": "Chair Pose", "sanskrit_name": "Utkatasana", "expertise_level": level.title(), "pose_type": ["Standing", "Balancing"]}},
        {"pose": {"name": "Easy Pose", "sanskrit_name": "Sukhasana", "expertise_level": level.title(), "pose_type": ["Seated"]}},
        {"pose": {"name": "Child's Pose", "sanskrit_name": "Balasana", "expertise_level": level.title(), "pose_type": ["Supine"]}},
        {"pose": {"name": "Corpse Pose", "sanskrit_name": "Savasana", "expertise_level": level.title(), "pose_type": ["Supine"]}}
    ]
    return demo_poses

@mcp.tool(
    title="Create Yoga Class Curriculum",
    description="Create a comprehensive yoga class curriculum with structured poses, timing, teacher cues, and optional PDF export. Enhanced with Mistral AI insights for professional teaching guidance.",
)
async def create_yoga_curriculum(
    level: str = Field(description="Class difficulty level: beginner, intermediate, or advanced"),
    duration_minutes: int = Field(description="Total class duration in minutes (15-120)", ge=15, le=120),
    focus_theme: str = Field(description="Optional theme for the class (e.g., 'strength building', 'flexibility', 'stress relief')", default="General Practice"),
    use_mistral_enhancement: bool = Field(description="Whether to use Mistral AI for enhanced teaching insights", default=True),
    generate_pdf: bool = Field(description="Whether to generate a PDF file of the curriculum", default=True)
) -> str:
    """
    Create a yoga class curriculum with poses, timing, and teaching cues.
    
    Sample input: level="beginner", duration_minutes=30, focus_theme="stress relief"
    Output: Complete curriculum with PDF file containing poses, sequences, and teacher cues.
    """
    
    # Initialize components if needed
    if not initialized:
        await initialize_components()
    
    if not enhanced_generator:
        return "❌ Enhanced curriculum generator not available. Please check installation."
    
    try:
        # Search for appropriate poses
        pose_query = f"{level} yoga poses {focus_theme}"
        poses_data = await search_yoga_poses(
            query=pose_query,
            limit=20,
            expertise_filter=level.title() if level.lower() in ["beginner", "intermediate", "advanced"] else None
        )
        
        # Create enhanced curriculum
        class_plan = await enhanced_generator.create_enhanced_class_plan(
            level=level,
            duration_minutes=duration_minutes,
            focus_theme=focus_theme,
            poses_data=poses_data,
            use_mistral_enhancement=use_mistral_enhancement and bool(config["mistral_api_key"])
        )
        
        # Generate PDF if requested
        pdf_path = None
        if generate_pdf:
            output_dir = Path("yoga_curricula")
            output_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_title = "".join(c for c in class_plan['metadata']['title'] if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_title = safe_title.replace(' ', '_')
            mistral_suffix = "_AI_Enhanced" if class_plan["metadata"].get("enhanced_with_mistral") else ""
            pdf_filename = f"{safe_title}_{timestamp}{mistral_suffix}.pdf"
            pdf_path = output_dir / pdf_filename
            
            try:
                generated_path = enhanced_generator.generate_enhanced_pdf(class_plan, str(pdf_path))
                pdf_path = generated_path
            except Exception as e:
                print(f"PDF generation failed: {e}")
                pdf_path = None
        
        # Format response
        metadata = class_plan["metadata"]
        response_parts = [
            f"🧘 **{metadata['title']}**",
            f"⏱️  Duration: {metadata['duration']} minutes",
            f"📊 Level: {metadata['level']}",
            f"🎯 Focus: {metadata['focus_theme']}",
            f"🔢 Total Poses: {metadata['total_poses']}"
        ]
        
        # Add AI enhancement status
        if metadata.get("enhanced_with_mistral"):
            response_parts.append("✨ **Enhanced with Mistral AI insights**")
        else:
            response_parts.append("📝 Standard curriculum")
        
        response_parts.append("\n📋 **Class Structure:**")
        
        # Add section details
        for section_key, section in class_plan["sections"].items():
            response_parts.append(f"\n**{section['name']}** ({section['duration']} min)")
            response_parts.append(f"   Purpose: {section['purpose']}")
            
            if section.get('poses'):
                response_parts.append(f"   Poses ({len(section['poses'])}):")
                for pose in section['poses'][:3]:  # Show first 3 poses
                    response_parts.append(f"   • {pose['name']} ({pose.get('sanskrit_name', 'N/A')})")
                if len(section['poses']) > 3:
                    response_parts.append(f"   • ... and {len(section['poses']) - 3} more")
            
            # Show enhanced cues if available
            if section.get('enhanced_cues'):
                response_parts.append("   ✨ AI Enhanced Teaching Cues:")
                enhanced_cues = section['enhanced_cues']
                if isinstance(enhanced_cues, list):
                    for cue in enhanced_cues[:2]:  # Show first 2 enhanced cues
                        response_parts.append(f"   • {cue}")
                elif isinstance(enhanced_cues, str):
                    response_parts.append(f"   • {enhanced_cues[:150]}...")
        
        # Show Mistral enhancements summary
        if class_plan.get("mistral_enhancements"):
            enhancements = class_plan["mistral_enhancements"]
            response_parts.append("\n✨ **Mistral AI Enhancements Include:**")
            
            if enhancements.get("advanced_insights"):
                response_parts.append(f"• {len(enhancements['advanced_insights'])} advanced teaching insights")
            
            if enhancements.get("modifications_and_props"):
                response_parts.append(f"• {len(enhancements['modifications_and_props'])} modification suggestions")
            
            if enhancements.get("breathing_philosophy"):
                response_parts.append("• Breathing guidance and philosophy integration")
            
            if enhancements.get("common_mistakes"):
                response_parts.append(f"• {len(enhancements['common_mistakes'])} common mistake corrections")
        
        # PDF information
        if pdf_path and Path(pdf_path).exists():
            file_size = Path(pdf_path).stat().st_size
            response_parts.append(f"\n📄 **PDF Generated:** {Path(pdf_path).name}")
            response_parts.append(f"   File size: {file_size:,} bytes")
            response_parts.append(f"   Location: {pdf_path}")
            response_parts.append("   Complete curriculum with poses, detailed teaching cues, and safety guidelines")
        
        return "\n".join(response_parts)
        
    except Exception as e:
        return f"❌ Error creating curriculum: {str(e)}"

@mcp.tool(
    title="Search Yoga Poses",
    description="Search for yoga poses using natural language queries with expertise level filtering.",
)
async def search_poses(
    query: str = Field(description="Natural language query (e.g., 'standing balance pose', 'beginner backbend')"),
    limit: int = Field(description="Maximum number of results to return", default=5, ge=1, le=20),
    expertise_level: str = Field(description="Filter by expertise level", default="", enum=["", "Beginner", "Intermediate", "Advanced"])
) -> str:
    """Search for yoga poses using semantic similarity."""
    
    # Initialize components if needed
    if not initialized:
        await initialize_components()
    
    try:
        # Perform search
        results = await search_yoga_poses(
            query=query,
            limit=limit,
            expertise_filter=expertise_level if expertise_level else None
        )
        
        if not results:
            return f"🔍 No yoga poses found for query: '{query}'"
        
        # Format results
        response_parts = [f"🧘 Found {len(results)} yoga poses for '{query}':\n"]
        
        for i, result in enumerate(results, 1):
            pose = result['pose']
            score = result.get('score', 0.0)
            
            response_parts.append(f"{i}. **{pose['name']}** ({pose.get('sanskrit_name', 'N/A')})")
            response_parts.append(f"   📊 Expertise: {pose['expertise_level']}")
            response_parts.append(f"   🏷️  Types: {', '.join(pose['pose_type'])}")
            
            if score > 0:
                response_parts.append(f"   🎯 Similarity Score: {score:.3f}")
            
            if pose.get('searchable_text'):
                desc = pose['searchable_text'][:100] + "..." if len(pose['searchable_text']) > 100 else pose['searchable_text']
                response_parts.append(f"   📄 Description: {desc}")
            
            response_parts.append("")  # Empty line between poses
        
        return "\n".join(response_parts)
        
    except Exception as e:
        return f"❌ Error searching poses: {str(e)}"

@mcp.resource(
    uri="curriculum://{level}/{duration}",
    description="Get a yoga curriculum template",
    name="Curriculum Template",
)
def get_curriculum_template(
    level: str,
    duration: str,
) -> str:
    """Get a basic curriculum template for the specified level and duration."""
    
    duration_int = int(duration) if duration.isdigit() else 30
    
    templates = {
        "beginner": {
            "focus": "Gentle introduction to yoga fundamentals",
            "key_poses": ["Mountain Pose", "Tree Pose", "Child's Pose"],
            "teaching_emphasis": "Clear instruction and safety"
        },
        "intermediate": {
            "focus": "Building strength and refining alignment",
            "key_poses": ["Warrior sequences", "Balance poses", "Backbends"],
            "teaching_emphasis": "Breath awareness and variations"
        },
        "advanced": {
            "focus": "Deep practice and challenging poses",
            "key_poses": ["Advanced balances", "Inversions", "Complex flows"],
            "teaching_emphasis": "Subtle alignment and philosophy"
        }
    }
    
    template = templates.get(level.lower(), templates["beginner"])
    
    return json.dumps({
        "level": level.title(),
        "duration_minutes": duration_int,
        "focus_theme": template["focus"],
        "suggested_poses": template["key_poses"],
        "teaching_emphasis": template["teaching_emphasis"],
        "structure": {
            "warm_up": f"{max(3, duration_int // 10)} minutes",
            "main_practice": f"{duration_int * 0.7:.0f} minutes",
            "relaxation": f"{max(3, duration_int // 6)} minutes"
        }
    }, indent=2)

@mcp.prompt("generate_teaching_cues")
def generate_teaching_cues_prompt(
    pose_name: str = Field(description="The name of the yoga pose"),
    level: str = Field(description="Student level: beginner, intermediate, or advanced", default="beginner"),
    focus: str = Field(description="What to focus on (alignment, breath, modifications)", default="alignment"),
) -> str:
    """Generate a prompt for creating detailed teaching cues for a yoga pose."""
    
    level_adjustments = {
        "beginner": "Use simple, clear language. Focus on basic safety and foundational alignment.",
        "intermediate": "Include refinement cues and breath awareness. Offer variations.",
        "advanced": "Provide subtle alignment details and advanced modifications. Include philosophical aspects."
    }
    
    focus_guidance = {
        "alignment": "Focus on precise body positioning and anatomical details",
        "breath": "Emphasize breathing patterns and breath-body connection", 
        "modifications": "Provide options for different body types and limitations",
        "philosophy": "Include yogic philosophy and mindfulness aspects"
    }
    
    return f"""As an experienced yoga instructor, create detailed teaching cues for {pose_name}.

Student Level: {level.title()}
Primary Focus: {focus.title()}

Guidelines:
- {level_adjustments.get(level, level_adjustments['beginner'])}
- {focus_guidance.get(focus, focus_guidance['alignment'])}
- Include setup, key actions, and common mistakes to avoid
- Provide clear, actionable instructions that students can follow
- Consider safety and accessibility

Please provide comprehensive teaching cues that would help a {level} student safely and effectively practice {pose_name}."""

# Initialize server on startup
async def startup():
    """Initialize components when server starts."""
    print("🧘 Starting Yoga Curriculum Generator MCP Server...")
    success = await initialize_components()
    if success:
        print("✅ Server initialized successfully")
    else:
        print("⚠️ Server started with limited functionality")

async def run_server():
    """Initialize and run the FastMCP server."""
    await startup()
    await mcp.run_async()

if __name__ == "__main__":
    print("🧘 Yoga Curriculum Generator MCP Server")
    print("=" * 50)
    print("Features:")
    print("• Create comprehensive yoga curricula")
    print("• Search yoga poses with semantic matching")
    print("• Mistral AI enhanced teaching insights")
    print("• Professional PDF export")
    print("• Qdrant vector database integration")
    print("=" * 50)
    
    import asyncio
    asyncio.run(run_server())
