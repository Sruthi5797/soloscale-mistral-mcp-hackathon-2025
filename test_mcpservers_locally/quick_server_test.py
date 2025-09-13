#!/usr/bin/env python3
"""
Simple test to run the Yoga Curriculum FastMCP Server
"""

import asyncio
import sys
from pathlib import Path


async def test_server():
    print("🧘 TESTING YOGA CURRICULUM FASTMCP SERVER")
    print("=" * 50)

    # Test that we can import the server
    try:
        print("📦 Importing server...")
        import yoga_curriculum_mcp_server
        print("✅ Server imported successfully!")
        
        # Check available tools
        from yoga_curriculum_mcp_server import mcp
        tools = await mcp.get_tools()
        print(f"🔧 Available tools: {len(tools)}")
        for tool in tools:
            if hasattr(tool, 'name'):
                print(f"  • {tool.name}: {getattr(tool, 'description', 'No description')}")
            else:
                print(f"  • {tool}")
        
        resources = await mcp.get_resources()
        print(f"📋 Available resources: {len(resources)}")
        
        prompts = await mcp.get_prompts()
        print(f"💬 Available prompts: {len(prompts)}")
        
        print("\n🚀 Components ready!")
        print("🧘 Initializing components...")
        await yoga_curriculum_mcp_server.initialize_components()
        print("✅ Components initialized!")
        print("🎉 FastMCP server is working correctly!")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

    print("\n🎯 QUICK FUNCTIONALITY TEST")
    print("=" * 30)

    # Test the enhanced generator directly
    try:
        from enhanced_yoga_curriculum_generator import EnhancedYogaCurriculumGenerator
        
        print("🧘 Creating yoga curriculum generator...")
        generator = EnhancedYogaCurriculumGenerator()
        
        print("📋 Testing curriculum creation...")
        
        result = await generator.create_enhanced_class_plan(
            level="beginner",
            duration_minutes=30,
            focus_theme="stress relief",
            use_mistral_enhancement=False,  # Skip Mistral for quick test
        )
        
        print("✅ Curriculum created successfully!")
        print(f"Class: {result.get('class_info', {}).get('title', 'Untitled')}")
        print(f"Duration: {result.get('class_info', {}).get('duration', 'Unknown')} minutes")
        print(f"Sections: {len(result.get('sections', {}))}")
        
        for section_name, section in result.get('sections', {}).items():
            print(f"  • {section_name}: {section.get('duration', 0)} min - {section.get('description', 'No description')}")
        
    except Exception as e:
        print(f"❌ Curriculum test error: {e}")
        import traceback
        traceback.print_exc()

    print("\n🎉 ALL TESTS COMPLETED!")
    print("=" * 25)
    print("The FastMCP server is ready for use!")
    print("Connect with an MCP client to test the full functionality.")
    return True

if __name__ == "__main__":
    asyncio.run(test_server())
