#!/usr/bin/env python3
"""
KiCad-Fu Main Entry Point - Cognitive KiCad Interface

Launch the cognitive-enhanced KiCad MCP server with autonomous learning.
"""

import asyncio
import argparse
import json
from pathlib import Path

from .server import KiCadFuServer, KiCadFuInterface
from .config import KiCadFuConfig

async def test_kicad_fu():
    """Test KiCad-Fu functionality"""
    print("🥋 KiCad-Fu Test Suite Starting...")
    
    # Initialize interface
    interface = KiCadFuInterface()
    await interface.initialize()
    
    print("\n📊 Server Capabilities:")
    capabilities = interface.get_capabilities()
    print(json.dumps(capabilities, indent=2))
    
    print("\n🔍 Discovering Projects...")
    discovery_result = await interface.discover_projects()
    print(json.dumps(discovery_result, indent=2))
    
    print("\n📋 Getting Projects List...")
    projects_result = await interface.get_projects_list()
    print(json.dumps(projects_result, indent=2))
    
    print("\n🎯 Master of Muppets Status...")
    mom_status = await interface.get_master_of_muppets_status()
    print(json.dumps(mom_status, indent=2))
    
    print("\n🧠 Cognitive Insights...")
    insights = await interface.get_cognitive_insights()
    print(json.dumps(insights, indent=2))
    
    # Test opening Master of Muppets if found
    if mom_status.get('data', {}).get('status') == 'found':
        print("\n🚀 Testing Master of Muppets Project Opening...")
        open_result = await interface.open_project('MasterOfMuppets')
        print(json.dumps(open_result, indent=2))
    
    print("\n✅ KiCad-Fu Test Suite Complete!")

async def run_server():
    """Run the KiCad-Fu MCP server"""
    config = KiCadFuConfig.from_environment()
    server = KiCadFuServer(config)
    
    print("🥋 KiCad-Fu: The Art of Intelligent KiCad Interaction")
    print(f"Configuration: {config}")
    print("\nStarting cognitive-enhanced MCP server...")
    
    await server.run_server()

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='KiCad-Fu: Cognitive KiCad Interface')
    parser.add_argument('--test', action='store_true', help='Run test suite')
    parser.add_argument('--server', action='store_true', help='Run MCP server')
    parser.add_argument('--config', help='Configuration file path')
    
    args = parser.parse_args()
    
    if args.test:
        asyncio.run(test_kicad_fu())
    elif args.server:
        asyncio.run(run_server())
    else:
        # Default: run test suite
        asyncio.run(test_kicad_fu())

if __name__ == "__main__":
    main()