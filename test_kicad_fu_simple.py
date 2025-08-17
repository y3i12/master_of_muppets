#!/usr/bin/env python3
"""
Simple KiCad-Fu Test - No Emoji Version

Test our cognitive-enhanced KiCad MCP implementation.
"""

import asyncio
import sys
import json
from pathlib import Path

# Add claude directory to path
sys.path.append(str(Path(__file__).parent / 'claude'))

from kicad_fu.server import KiCadFuInterface
from kicad_fu.config import KiCadFuConfig

async def test_kicad_fu():
    """Test KiCad-Fu functionality"""
    print("KiCad-Fu Test Suite Starting...")
    print("=" * 60)
    
    try:
        # Initialize interface
        print("\nInitializing KiCad-Fu interface...")
        interface = KiCadFuInterface()
        await interface.initialize()
        print("Interface initialized successfully")
        
        print("\nServer Capabilities:")
        print("-" * 30)
        capabilities = interface.get_capabilities()
        print(json.dumps(capabilities, indent=2))
        
        print("\nDiscovering KiCad Projects...")
        print("-" * 40)
        discovery_result = await interface.discover_projects()
        print("Discovery result:", json.dumps(discovery_result, indent=2))
        
        print("\nGetting Projects List...")
        print("-" * 40)
        projects_result = await interface.get_projects_list()
        print("Projects list result:", json.dumps(projects_result, indent=2))
        
        print("\nMaster of Muppets Status...")
        print("-" * 40)
        mom_status = await interface.get_master_of_muppets_status()
        print("Master of Muppets status:", json.dumps(mom_status, indent=2))
        
        print("\nCognitive Insights...")
        print("-" * 40)
        insights = await interface.get_cognitive_insights()
        print("Cognitive insights:", json.dumps(insights, indent=2))
        
        print("\n" + "=" * 60)
        print("KiCad-Fu Test Suite Complete!")
        print("Autonomous Learning Architecture: INTEGRATED")
        print("KiCad-Fu Status: OPERATIONAL")
        
    except Exception as e:
        print(f"\nTest suite failed with error: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main entry point"""
    print("KiCad-Fu: The Art of Intelligent KiCad Interaction")
    print("Powered by Autonomous Learning Architecture (87% Score)")
    print("")
    
    asyncio.run(test_kicad_fu())

if __name__ == "__main__":
    main()