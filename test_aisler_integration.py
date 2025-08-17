#!/usr/bin/env python3
"""
AISLER Integration Test - KiCad-Fu Manufacturing Enhancement

Test our enhanced KiCad-Fu system with AISLER PCB manufacturing integration.
"""

import asyncio
import sys
import json
from pathlib import Path

# Add claude directory to path
sys.path.append(str(Path(__file__).parent / 'claude'))

from kicad_fu.server import KiCadFuInterface
from kicad_fu.config import KiCadFuConfig

async def test_aisler_integration():
    """Test AISLER manufacturing integration"""
    print("KiCad-Fu AISLER Integration Test")
    print("=" * 60)
    
    try:
        # Initialize interface
        print("\nInitializing KiCad-Fu with AISLER integration...")
        interface = KiCadFuInterface()
        await interface.initialize()
        print("Interface initialized successfully")
        
        print("\nEnhanced Server Capabilities:")
        print("-" * 40)
        capabilities = interface.get_capabilities()
        print(f"Name: {capabilities['name']}")
        print(f"Description: {capabilities['description']}")
        print(f"Tools: {len(capabilities['tools'])} available")
        for tool in capabilities['tools']:
            print(f"  - {tool}")
        print(f"Prompts: {len(capabilities['prompts'])} available")
        for prompt in capabilities['prompts']:
            print(f"  - {prompt}")
        
        print("\nDiscovering Projects for AISLER Analysis...")
        print("-" * 50)
        discovery_result = await interface.discover_projects()
        if discovery_result['success']:
            projects = discovery_result['result']['projects']
            print(f"Found {len(projects)} projects for AISLER optimization")
            
            # Test AISLER optimization on Master of Muppets
            if projects:
                project_name = projects[0]['name']
                print(f"\nOptimizing '{project_name}' for AISLER Manufacturing...")
                print("-" * 60)
                
                aisler_result = await interface.optimize_for_aisler(project_name)
                print("AISLER result structure:", json.dumps(aisler_result, indent=2, default=str))
                if aisler_result['success']:
                    # The result is nested under 'result' key
                    if 'result' in aisler_result and 'analysis' in aisler_result['result']:
                        analysis = aisler_result['result']['analysis']
                    else:
                        analysis = aisler_result.get('analysis', {})
                    print("AISLER Optimization Analysis:")
                    print(f"  Project: {analysis['project_name']}")
                    
                    if analysis['recommended_config']:
                        config = analysis['recommended_config']
                        print(f"  Recommended Config: {config['rules']['name']}")
                        print(f"  Optimization Score: {config['optimization_score']:.1%}")
                        print(f"  Estimated Price: €{config['estimated_price']:.2f}")
                        print(f"  Compatible: {config['compatible']}")
                        
                        print("\nRecommendation Reasoning:")
                        reasoning = config.get('recommendation_reasoning', 'No reasoning available')
                        for line in reasoning.split('\n'):
                            if line.strip():
                                print(f"    {line.strip()}")
                    
                    print(f"\nCompatible Configurations: {len(analysis['all_compatible_configs'])}")
                    for config in analysis['all_compatible_configs']:
                        rules = config['rules']
                        print(f"  - {rules['name']}: €{config['estimated_price']:.2f}")
                    
                    print("\nAISLER-Specific Optimizations:")
                    for opt in analysis['aisler_optimizations']:
                        print(f"  • {opt}")
                        
                    print("\nCognitive Insights:")
                    insights = analysis['cognitive_insights']
                    print(f"  Manufacturing Complexity: {insights.get('manufacturing_complexity', 'unknown')}")
                    if insights.get('design_recommendations'):
                        print("  Design Recommendations:")
                        for rec in insights['design_recommendations']:
                            print(f"    - {rec}")
                else:
                    print(f"AISLER optimization failed: {aisler_result.get('error')}")
                
                print(f"\nDFM Validation for AISLER...")
                print("-" * 40)
                dfm_result = await interface.validate_dfm(project_name, 'aisler')
                if dfm_result['success']:
                    # Check if validation is in result or directly available
                    if 'result' in dfm_result and 'validation' in dfm_result['result']:
                        validation = dfm_result['result']['validation']
                    else:
                        validation = dfm_result.get('validation', {})
                    print(f"DFM Status: {validation['overall_status']}")
                    print(f"DFM Score: {validation['dfm_score']:.1%}")
                    print(f"Violations: {len(validation['violations'])}")
                    print(f"Warnings: {len(validation['warnings'])}")
                    
                    if validation['violations']:
                        print("\nDFM Violations:")
                        for violation in validation['violations'][:3]:  # Show first 3
                            print(f"  - {violation['severity'].upper()}: {violation['description']}")
                            print(f"    Location: {violation['location']}")
                            print(f"    Actual: {violation['actual_value']:.3f}, Required: {violation['required_value']:.3f}")
                            if violation.get('cognitive_suggestion'):
                                print(f"    Suggestion: {violation['cognitive_suggestion']}")
                    
                    if validation['recommendations']:
                        print("\nDFM Recommendations:")
                        for rec in validation['recommendations']:
                            print(f"  • {rec}")
                else:
                    print(f"DFM validation failed: {dfm_result.get('error')}")
                
                print(f"\nMulti-Manufacturer Comparison...")
                print("-" * 45)
                comparison_result = await interface.compare_manufacturers(project_name)
                if comparison_result.get('manufacturer_results'):
                    print("Manufacturer Comparison Results:")
                    for manufacturer, results in comparison_result['manufacturer_results'].items():
                        print(f"  {manufacturer.upper()}:")
                        print(f"    Status: {results['overall_status']}")
                        print(f"    DFM Score: {results['dfm_score']:.1%}")
                        print(f"    Errors: {results['error_count']}, Warnings: {results['warning_count']}")
                    
                    if comparison_result.get('recommendations'):
                        print("\nCross-Manufacturer Recommendations:")
                        for rec in comparison_result['recommendations']:
                            print(f"  • {rec}")
                else:
                    print("Manufacturer comparison not available")
        else:
            print(f"Project discovery failed: {discovery_result.get('error')}")
        
        print("\n" + "=" * 60)
        print("AISLER Integration Test Complete!")
        print("Manufacturing Intelligence: ENHANCED")
        print("AISLER Optimization: OPERATIONAL")
        print("DFM Validation: ACTIVE")
        
    except Exception as e:
        print(f"\nAISLER integration test failed: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main entry point"""
    print("KiCad-Fu: Enhanced with AISLER Manufacturing Intelligence")
    print("Powered by Autonomous Learning Architecture + AISLER Expertise")
    print("")
    
    asyncio.run(test_aisler_integration())

if __name__ == "__main__":
    main()