#!/usr/bin/env python3
"""
Enhanced Yoga Curriculum Generator with Mistral AI Integration

This module generates structured yoga class curricula using both Qdrant database
for pose selection and Mistral AI for enhanced teaching insights and cues.
"""

import os
import json
import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path

# PDF generation imports
try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib.colors import HexColor, black, darkblue, darkgreen, darkred
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.platypus import PageBreak, Image
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
    from jinja2 import Template
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

# Mistral AI imports
try:
    from mistralai.client import MistralClient
    MISTRAL_AVAILABLE = True
except ImportError:
    MISTRAL_AVAILABLE = False


class EnhancedYogaCurriculumGenerator:
    """Enhanced curriculum generator with Mistral AI integration."""
    
    def __init__(self):
        """Initialize the enhanced curriculum generator."""
        self.mistral_client = None
        self.mistral_model = "mistral-small"  # Using small model for cost efficiency
        
        # Initialize Mistral client if API key is available
        mistral_api_key = os.getenv("MISTRAL_API_KEY")
        if MISTRAL_AVAILABLE and mistral_api_key:
            self.mistral_client = MistralClient(api_key=mistral_api_key)
        
        self.class_structures = {
            "beginner": {
                "warm_up_duration": 5,
                "standing_duration": 10,
                "seated_floor_duration": 10,
                "relaxation_duration": 5,
                "preferred_types": ["Standing", "Seated", "Supine"],
                "avoid_types": ["Balancing", "Advanced"],
                "max_poses_per_section": 4,
                "teaching_style": "slow and detailed with lots of explanation"
            },
            "intermediate": {
                "warm_up_duration": 5,
                "standing_duration": 12,
                "seated_floor_duration": 10,
                "balancing_duration": 5,
                "relaxation_duration": 3,
                "preferred_types": ["Standing", "Seated", "Balancing", "Back Bend"],
                "avoid_types": [],
                "max_poses_per_section": 5,
                "teaching_style": "moderate pace with refinement cues"
            },
            "advanced": {
                "warm_up_duration": 3,
                "standing_duration": 15,
                "seated_floor_duration": 8,
                "balancing_duration": 6,
                "inversions_duration": 5,
                "relaxation_duration": 3,
                "preferred_types": ["Standing", "Balancing", "Back Bend", "Forward Bend"],
                "avoid_types": [],
                "max_poses_per_section": 6,
                "teaching_style": "dynamic flow with advanced variations"
            }
        }
    
    async def create_enhanced_class_plan(
        self,
        level: str,
        duration_minutes: int,
        focus_theme: Optional[str] = None,
        poses_data: List[Dict[str, Any]] = None,
        use_mistral_enhancement: bool = True
    ) -> Dict[str, Any]:
        """
        Create an enhanced yoga class plan with Mistral AI insights.
        
        Args:
            level: Class level (beginner, intermediate, advanced)
            duration_minutes: Total class duration in minutes
            focus_theme: Optional theme like "balance", "flexibility", "strength"
            poses_data: List of available poses from Qdrant search
            use_mistral_enhancement: Whether to use Mistral AI for enhancement
            
        Returns:
            Dictionary containing the complete enhanced class plan
        """
        if level.lower() not in self.class_structures:
            raise ValueError(f"Unsupported level: {level}. Use beginner, intermediate, or advanced.")
        
        structure = self.class_structures[level.lower()]
        
        # Scale durations based on total time
        scale_factor = duration_minutes / 30  # Base structure is for 30 minutes
        
        # Create basic class sections
        sections = self._create_class_sections(structure, scale_factor, focus_theme)
        
        # Select poses for each section
        if poses_data:
            sections = self._assign_poses_to_sections(sections, poses_data, level)
        
        # Create base class plan
        class_plan = {
            "metadata": {
                "title": f"{level.title()} Yoga Class",
                "duration": duration_minutes,
                "level": level.title(),
                "focus_theme": focus_theme or "General Practice",
                "created_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "total_poses": sum(len(section.get("poses", [])) for section in sections.values()),
                "enhanced_with_mistral": use_mistral_enhancement and self.mistral_client is not None
            },
            "sections": sections,
            "notes": self._generate_teaching_notes(level, focus_theme),
            "safety_guidelines": self._get_safety_guidelines(level)
        }
        
        # Enhance with Mistral AI if available and requested
        if use_mistral_enhancement and self.mistral_client:
            try:
                enhanced_plan = await self._enhance_with_mistral(class_plan, level, focus_theme)
                return enhanced_plan
            except Exception as e:
                print(f"⚠️ Mistral enhancement failed: {e}")
                # Return base plan if Mistral enhancement fails
                class_plan["metadata"]["mistral_enhancement_error"] = str(e)
        
        return class_plan
    
    async def _enhance_with_mistral(
        self, 
        class_plan: Dict[str, Any], 
        level: str, 
        focus_theme: Optional[str]
    ) -> Dict[str, Any]:
        """Enhance the class plan using Mistral AI."""
        
        # Prepare context for Mistral
        pose_list = []
        for section in class_plan["sections"].values():
            for pose in section.get("poses", []):
                pose_list.append(f"{pose['name']} ({pose.get('sanskrit_name', 'N/A')})")
        
        structure_info = []
        for section_name, section in class_plan["sections"].items():
            structure_info.append(f"{section['name']}: {section['duration']} minutes")
        
        # Create Mistral prompt
        prompt = f"""
As an experienced yoga instructor, please enhance this {level} yoga class curriculum with detailed teaching cues and insights.

Class Details:
- Level: {level.title()}
- Duration: {class_plan['metadata']['duration']} minutes
- Theme: {focus_theme or 'General Practice'}
- Structure: {', '.join(structure_info)}
- Poses included: {', '.join(pose_list[:10])}{"..." if len(pose_list) > 10 else ""}

Please provide:
1. Enhanced teaching cues for each section (specific verbal instructions)
2. Advanced teaching insights for this level and theme
3. Modifications and props suggestions
4. Breathing cues and philosophy integration
5. Common mistakes to watch for and corrections

Format your response as JSON with these keys:
- "enhanced_teaching_cues": object with section names as keys
- "advanced_insights": array of insight strings
- "modifications_and_props": array of modification suggestions
- "breathing_philosophy": object with "breathing_cues" and "philosophy_notes"
- "common_mistakes": array of mistake and correction pairs

Keep responses practical and actionable for yoga teachers.
"""

        try:
            # Call Mistral API
            messages = [{"role": "user", "content": prompt}]
            response = await asyncio.to_thread(
                self.mistral_client.chat,
                model=self.mistral_model,
                messages=messages,
                temperature=0.7,
                max_tokens=2000
            )
            
            # Parse Mistral response
            mistral_content = response.choices[0].message.content
            
            # Try to parse as JSON, fallback to text processing
            try:
                mistral_enhancements = json.loads(mistral_content)
            except json.JSONDecodeError:
                # If not valid JSON, create structured response from text
                mistral_enhancements = self._parse_mistral_text_response(mistral_content)
            
            # Integrate Mistral enhancements into class plan
            enhanced_plan = self._integrate_mistral_enhancements(class_plan, mistral_enhancements)
            
            return enhanced_plan
            
        except Exception as e:
            raise Exception(f"Mistral API error: {str(e)}")
    
    def _parse_mistral_text_response(self, content: str) -> Dict[str, Any]:
        """Parse Mistral response if it's not JSON format."""
        return {
            "enhanced_teaching_cues": {
                "general": [content[:500] + "..."] if len(content) > 500 else [content]
            },
            "advanced_insights": ["Enhanced with Mistral AI insights"],
            "modifications_and_props": ["Use props as needed for comfort and safety"],
            "breathing_philosophy": {
                "breathing_cues": "Focus on steady, deep breathing throughout practice",
                "philosophy_notes": "Cultivate mindfulness and presence"
            },
            "common_mistakes": ["Listen to your body and avoid forcing poses"]
        }
    
    def _integrate_mistral_enhancements(
        self, 
        class_plan: Dict[str, Any], 
        enhancements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Integrate Mistral enhancements into the class plan."""
        
        # Add enhanced teaching cues to sections
        enhanced_cues = enhancements.get("enhanced_teaching_cues", {})
        for section_name, section in class_plan["sections"].items():
            if section_name in enhanced_cues:
                section["enhanced_cues"] = enhanced_cues[section_name]
            elif "general" in enhanced_cues:
                section["enhanced_cues"] = enhanced_cues["general"]
        
        # Add Mistral insights to class plan
        class_plan["mistral_enhancements"] = {
            "advanced_insights": enhancements.get("advanced_insights", []),
            "modifications_and_props": enhancements.get("modifications_and_props", []),
            "breathing_philosophy": enhancements.get("breathing_philosophy", {}),
            "common_mistakes": enhancements.get("common_mistakes", [])
        }
        
        # Mark as enhanced
        class_plan["metadata"]["enhanced_with_mistral"] = True
        
        return class_plan
    
    def _create_class_sections(
        self, 
        structure: Dict[str, Any], 
        scale_factor: float,
        focus_theme: Optional[str]
    ) -> Dict[str, Dict[str, Any]]:
        """Create the basic structure of class sections."""
        sections = {}
        
        # Warm-up section
        sections["warm_up"] = {
            "name": "Warm-up & Centering",
            "duration": max(2, int(structure["warm_up_duration"] * scale_factor)),
            "purpose": "Prepare the body and mind for practice",
            "poses": [],
            "instructions": [
                "Begin in a comfortable seated position",
                "Take 5-10 deep breaths to center yourself",
                "Gentle neck and shoulder rolls",
                "Cat-cow movements to warm the spine"
            ]
        }
        
        # Standing section
        sections["standing"] = {
            "name": "Standing Poses",
            "duration": max(5, int(structure["standing_duration"] * scale_factor)),
            "purpose": "Build strength, stability, and heat in the body",
            "poses": [],
            "instructions": [
                "Focus on grounding through feet",
                "Engage core muscles",
                "Breathe deeply throughout poses"
            ]
        }
        
        # Seated/Floor section
        sections["seated_floor"] = {
            "name": "Seated & Floor Poses",
            "duration": max(5, int(structure["seated_floor_duration"] * scale_factor)),
            "purpose": "Deepen flexibility and introspection",
            "poses": [],
            "instructions": [
                "Sit tall with spine elongated",
                "Use props as needed for comfort",
                "Focus on gentle, mindful movements"
            ]
        }
        
        # Balancing (if applicable)
        if "balancing_duration" in structure:
            sections["balancing"] = {
                "name": "Balance & Focus",
                "duration": max(2, int(structure["balancing_duration"] * scale_factor)),
                "purpose": "Develop concentration and stability",
                "poses": [],
                "instructions": [
                    "Find a focal point (drishti)",
                    "Engage core for stability",
                    "Use wall or props for support if needed"
                ]
            }
        
        # Relaxation
        sections["relaxation"] = {
            "name": "Relaxation & Savasana",
            "duration": max(3, int(structure["relaxation_duration"] * scale_factor)),
            "purpose": "Integration and deep rest",
            "poses": [],
            "instructions": [
                "Lie comfortably on your back",
                "Allow the body to completely relax",
                "Focus on the breath or guided meditation",
                "Rest for 3-5 minutes minimum"
            ]
        }
        
        return sections
    
    def _assign_poses_to_sections(
        self,
        sections: Dict[str, Dict[str, Any]],
        poses_data: List[Dict[str, Any]],
        level: str
    ) -> Dict[str, Dict[str, Any]]:
        """Assign appropriate poses to each section."""
        # Filter poses by level
        level_poses = [
            pose for pose in poses_data 
            if pose.get('pose', {}).get('expertise_level', '').lower() == level.lower()
        ]
        
        # Categorize poses by type
        pose_categories = {
            'standing': [],
            'seated': [],
            'balancing': [],
            'supine': [],
            'prone': [],
            'backbend': [],
            'forward_bend': []
        }
        
        for pose_data in level_poses:
            pose = pose_data.get('pose', {})
            pose_types = pose.get('pose_type', [])
            
            for pose_type in pose_types:
                if 'Standing' in pose_type:
                    pose_categories['standing'].append(pose)
                elif 'Seated' in pose_type:
                    pose_categories['seated'].append(pose)
                elif 'Balancing' in pose_type:
                    pose_categories['balancing'].append(pose)
                elif 'Supine' in pose_type:
                    pose_categories['supine'].append(pose)
                elif 'Prone' in pose_type:
                    pose_categories['prone'].append(pose)
                elif 'Back Bend' in pose_type:
                    pose_categories['backbend'].append(pose)
                elif 'Forward Bend' in pose_type:
                    pose_categories['forward_bend'].append(pose)
        
        # Assign poses to sections
        if 'standing' in sections:
            sections['standing']['poses'] = pose_categories['standing'][:4]
        
        if 'seated_floor' in sections:
            seated_poses = pose_categories['seated'][:2]
            supine_poses = pose_categories['supine'][:2]
            sections['seated_floor']['poses'] = seated_poses + supine_poses
        
        if 'balancing' in sections:
            sections['balancing']['poses'] = pose_categories['balancing'][:3]
        
        return sections
    
    def _generate_teaching_notes(self, level: str, focus_theme: Optional[str]) -> List[str]:
        """Generate teaching notes and cues for the class."""
        base_notes = [
            "Remind students to listen to their bodies",
            "Offer modifications for all poses",
            "Encourage steady, deep breathing",
            "Create a welcoming, non-judgmental atmosphere"
        ]
        
        level_specific_notes = {
            "beginner": [
                "Explain basic alignment principles clearly",
                "Demonstrate poses before students attempt them",
                "Emphasize that yoga is not competitive",
                "Check in frequently with students",
                "Use props generously to support students"
            ],
            "intermediate": [
                "Offer both easier and more challenging variations",
                "Focus on refining alignment and breath awareness",
                "Introduce some longer holds for strength building",
                "Encourage mindful transitions between poses",
                "Begin introducing philosophical concepts"
            ],
            "advanced": [
                "Assume basic knowledge but still cue important details",
                "Offer advanced variations and deeper expressions",
                "Focus on subtle body awareness and energy",
                "Include philosophical elements and meditation",
                "Challenge students while maintaining safety"
            ]
        }
        
        return base_notes + level_specific_notes.get(level.lower(), [])
    
    def _get_safety_guidelines(self, level: str) -> List[str]:
        """Get safety guidelines for the class."""
        base_guidelines = [
            "Always warm up before deeper poses",
            "Move slowly and mindfully",
            "Stop if you feel pain (not just discomfort)",
            "Use props to support your practice",
            "Inform instructor of any injuries or limitations",
            "Stay hydrated throughout practice"
        ]
        
        level_specific = {
            "beginner": [
                "Never force your body into a pose",
                "It's okay to rest in child's pose anytime",
                "Focus on breath over perfect alignment initially"
            ],
            "intermediate": [
                "Respect your limits even as you explore them",
                "Use the breath as a guide for intensity",
                "Back off if you feel strain in joints"
            ],
            "advanced": [
                "Maintain ego awareness in challenging poses",
                "Honor your body's wisdom over external expectations",
                "Practice ahimsa (non-violence) toward yourself"
            ]
        }
        
        return base_guidelines + level_specific.get(level.lower(), [])
    
    def generate_enhanced_pdf(self, class_plan: Dict[str, Any], output_path: str) -> str:
        """
        Generate an enhanced PDF from the class plan with Mistral insights.
        
        Args:
            class_plan: The enhanced class plan dictionary
            output_path: Path where PDF should be saved
            
        Returns:
            Path to the generated PDF file
        """
        if not PDF_AVAILABLE:
            raise ImportError("PDF generation requires reportlab and Pillow packages")
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Create PDF document
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        # Get styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=20,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=darkblue
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            spaceBefore=20,
            textColor=darkgreen
        )
        
        mistral_style = ParagraphStyle(
            'MistralEnhanced',
            parent=styles['Normal'],
            fontSize=10,
            textColor=darkred,
            leftIndent=20,
            spaceAfter=6
        )
        
        # Build PDF content
        story = []
        
        # Title page
        metadata = class_plan['metadata']
        story.append(Paragraph(metadata['title'], title_style))
        
        # Enhanced by Mistral badge
        if metadata.get('enhanced_with_mistral'):
            story.append(Paragraph("✨ Enhanced with Mistral AI Insights", mistral_style))
        
        story.append(Spacer(1, 20))
        
        # Class information table
        class_info = [
            ['Duration:', f"{metadata['duration']} minutes"],
            ['Level:', metadata['level']],
            ['Focus:', metadata['focus_theme']],
            ['Total Poses:', str(metadata['total_poses'])],
            ['Created:', metadata['created_date']],
            ['AI Enhanced:', 'Yes' if metadata.get('enhanced_with_mistral') else 'No']
        ]
        
        info_table = Table(class_info, colWidths=[2*inch, 3*inch])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), HexColor('#f0f0f0')),
            ('TEXTCOLOR', (0, 0), (-1, -1), black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, black)
        ]))
        
        story.append(info_table)
        story.append(Spacer(1, 30))
        
        # Class sections
        story.append(Paragraph("Class Structure", heading_style))
        
        for section_key, section in class_plan['sections'].items():
            # Section header
            section_title = f"{section['name']} ({section['duration']} minutes)"
            story.append(Paragraph(section_title, styles['Heading3']))
            
            # Purpose
            story.append(Paragraph(f"<b>Purpose:</b> {section['purpose']}", styles['Normal']))
            story.append(Spacer(1, 10))
            
            # Poses
            if section.get('poses'):
                story.append(Paragraph("<b>Poses:</b>", styles['Normal']))
                for pose in section['poses']:
                    pose_info = f"• {pose['name']} ({pose.get('sanskrit_name', 'N/A')})"
                    story.append(Paragraph(pose_info, styles['Normal']))
                story.append(Spacer(1, 10))
            
            # Basic instructions
            if section.get('instructions'):
                story.append(Paragraph("<b>Teaching Cues:</b>", styles['Normal']))
                for instruction in section['instructions']:
                    story.append(Paragraph(f"• {instruction}", styles['Normal']))
            
            # Enhanced cues from Mistral
            if section.get('enhanced_cues'):
                story.append(Paragraph("<b>✨ Enhanced Teaching Insights:</b>", styles['Normal']))
                enhanced_cues = section['enhanced_cues']
                if isinstance(enhanced_cues, list):
                    for cue in enhanced_cues:
                        story.append(Paragraph(f"• {cue}", mistral_style))
                elif isinstance(enhanced_cues, str):
                    story.append(Paragraph(enhanced_cues, mistral_style))
            
            story.append(Spacer(1, 20))
        
        # Mistral enhancements section
        if class_plan.get('mistral_enhancements'):
            story.append(PageBreak())
            story.append(Paragraph("✨ Mistral AI Enhanced Insights", heading_style))
            
            enhancements = class_plan['mistral_enhancements']
            
            # Advanced insights
            if enhancements.get('advanced_insights'):
                story.append(Paragraph("<b>Advanced Teaching Insights:</b>", styles['Normal']))
                for insight in enhancements['advanced_insights']:
                    story.append(Paragraph(f"• {insight}", mistral_style))
                story.append(Spacer(1, 15))
            
            # Modifications and props
            if enhancements.get('modifications_and_props'):
                story.append(Paragraph("<b>Modifications & Props:</b>", styles['Normal']))
                for mod in enhancements['modifications_and_props']:
                    story.append(Paragraph(f"• {mod}", mistral_style))
                story.append(Spacer(1, 15))
            
            # Breathing and philosophy
            if enhancements.get('breathing_philosophy'):
                bp = enhancements['breathing_philosophy']
                if bp.get('breathing_cues'):
                    story.append(Paragraph("<b>Breathing Guidance:</b>", styles['Normal']))
                    story.append(Paragraph(bp['breathing_cues'], mistral_style))
                    story.append(Spacer(1, 10))
                
                if bp.get('philosophy_notes'):
                    story.append(Paragraph("<b>Yoga Philosophy Integration:</b>", styles['Normal']))
                    story.append(Paragraph(bp['philosophy_notes'], mistral_style))
                    story.append(Spacer(1, 15))
            
            # Common mistakes
            if enhancements.get('common_mistakes'):
                story.append(Paragraph("<b>Common Mistakes to Watch For:</b>", styles['Normal']))
                for mistake in enhancements['common_mistakes']:
                    story.append(Paragraph(f"• {mistake}", mistral_style))
        
        # Teaching notes
        story.append(PageBreak())
        story.append(Paragraph("Teaching Notes", heading_style))
        for note in class_plan['notes']:
            story.append(Paragraph(f"• {note}", styles['Normal']))
        
        story.append(Spacer(1, 20))
        
        # Safety guidelines
        story.append(Paragraph("Safety Guidelines", heading_style))
        for guideline in class_plan['safety_guidelines']:
            story.append(Paragraph(f"• {guideline}", styles['Normal']))
        
        # Build PDF
        doc.build(story)
        
        return output_path


if __name__ == "__main__":
    async def demo():
        generator = EnhancedYogaCurriculumGenerator()
        
        class_plan = await generator.create_enhanced_class_plan(
            level="beginner",
            duration_minutes=30,
            focus_theme="Gentle Introduction to Yoga",
            use_mistral_enhancement=True
        )
        
        print(json.dumps(class_plan, indent=2))
    
    asyncio.run(demo())
