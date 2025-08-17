#!/usr/bin/env python3
"""
PCB Analysis Suite v1.0 - Comprehensive PCB layout analysis
Master of Muppets specialized analysis tools
"""

import json
import math
from typing import Dict, List, Tuple, Any
from pathlib import Path
from kicad_pcb_parser import KiCadPCBParser, ComponentPlacement
from pcb_placement_optimizer import PCBPlacementOptimizer

class PCBAnalysisSuite:
    """Complete analysis suite for PCB layout evaluation"""
    
    def __init__(self, pcb_file_path: str):
        self.pcb_file = Path(pcb_file_path)
        self.parser = KiCadPCBParser(pcb_file_path)
        self.optimizer = PCBPlacementOptimizer(self.parser)
        
    def analyze_signal_integrity(self) -> Dict[str, Any]:
        """Analyze signal integrity aspects"""
        
        analysis = {
            'i2c_analysis': self._analyze_i2c_routing(),
            'analog_paths': self._analyze_analog_paths(),
            'power_distribution': self._analyze_power_distribution(),
            'critical_distances': self._analyze_critical_distances()
        }
        
        return analysis
    
    def _analyze_i2c_routing(self) -> Dict[str, Any]:
        """Analyze I2C bus routing quality"""
        
        # Find microcontroller and DACs
        groups = self.parser.get_component_groups()
        microcontroller = groups['microcontroller'][0] if groups['microcontroller'] else None
        dacs = groups['dac']
        
        if not microcontroller or not dacs:
            return {'status': 'incomplete', 'issues': ['Missing microcontroller or DACs']}
        
        i2c_analysis = {
            'bus_length': 0.0,
            'max_distance': 0.0,
            'stub_lengths': [],
            'topology': 'unknown',
            'issues': []
        }
        
        # Calculate distances from microcontroller to each DAC
        dac_distances = []
        for dac in dacs:
            distance = microcontroller.distance_to(dac)
            dac_distances.append(distance)
            i2c_analysis['stub_lengths'].append({
                'component': dac.reference,
                'distance': distance
            })
        
        i2c_analysis['max_distance'] = max(dac_distances) if dac_distances else 0.0
        i2c_analysis['bus_length'] = sum(dac_distances)
        
        # Check for issues
        if i2c_analysis['max_distance'] > 50.0:
            i2c_analysis['issues'].append(f"Long I2C trace: {i2c_analysis['max_distance']:.1f}mm > 50mm recommended")
        
        if len(set(int(d/10)*10 for d in dac_distances)) > 1:
            i2c_analysis['issues'].append("Unequal I2C stub lengths may cause timing issues")
        
        return i2c_analysis
    
    def _analyze_analog_paths(self) -> Dict[str, Any]:
        """Analyze analog signal path quality"""
        
        groups = self.parser.get_component_groups()
        dacs = groups['dac']
        opamps = groups['opamp']
        jacks = groups['jack']
        
        analog_analysis = {
            'dac_to_opamp_distances': [],
            'opamp_to_jack_distances': [],
            'signal_path_lengths': [],
            'crosstalk_risks': [],
            'issues': []
        }
        
        # Analyze DAC to OpAmp connections (estimated based on proximity)
        for dac in dacs:
            nearby_opamps = []
            for opamp in opamps:
                distance = dac.distance_to(opamp)
                if distance < 30.0:  # Assume connection if within 30mm
                    nearby_opamps.append((opamp, distance))
                    analog_analysis['dac_to_opamp_distances'].append({
                        'from': dac.reference,
                        'to': opamp.reference,
                        'distance': distance
                    })
        
        # Analyze OpAmp to Jack connections
        for opamp in opamps:
            nearby_jacks = []
            for jack in jacks:
                distance = opamp.distance_to(jack)
                if distance < 50.0:  # Assume connection if within 50mm
                    nearby_jacks.append((jack, distance))
                    analog_analysis['opamp_to_jack_distances'].append({
                        'from': opamp.reference,
                        'to': jack.reference,
                        'distance': distance
                    })
        
        # Check for potential crosstalk (components too close)
        for i, opamp1 in enumerate(opamps):
            for opamp2 in opamps[i+1:]:
                distance = opamp1.distance_to(opamp2)
                if distance < 5.0:
                    analog_analysis['crosstalk_risks'].append({
                        'component1': opamp1.reference,
                        'component2': opamp2.reference,
                        'distance': distance,
                        'risk_level': 'high' if distance < 3.0 else 'medium'
                    })
        
        return analog_analysis
    
    def _analyze_power_distribution(self) -> Dict[str, Any]:
        """Analyze power distribution network"""
        
        groups = self.parser.get_component_groups()
        
        power_analysis = {
            'power_zones': self._identify_power_zones(),
            'decoupling_coverage': self._analyze_decoupling(),
            'power_path_lengths': [],
            'issues': []
        }
        
        return power_analysis
    
    def _identify_power_zones(self) -> List[Dict[str, Any]]:
        """Identify distinct power distribution zones"""
        
        groups = self.parser.get_component_groups()
        zones = []
        
        # Digital zone (around microcontroller)
        if groups['microcontroller']:
            mc = groups['microcontroller'][0]
            zones.append({
                'name': 'Digital Power Zone',
                'center': (mc.x, mc.y),
                'components': ['microcontroller', 'digital_caps'],
                'voltage': '3.3V'
            })
        
        # Analog zones (around DACs and OpAmps)
        for i, dac in enumerate(groups['dac']):
            zones.append({
                'name': f'Analog Zone {i+1}',
                'center': (dac.x, dac.y),
                'components': ['dac', 'opamp', 'analog_caps'],
                'voltage': '±12V, +5V'
            })
        
        return zones
    
    def _analyze_decoupling(self) -> Dict[str, Any]:
        """Analyze decoupling capacitor placement"""
        
        groups = self.parser.get_component_groups()
        capacitors = groups['capacitor']
        active_components = groups['microcontroller'] + groups['dac'] + groups['opamp']
        
        decoupling_analysis = {
            'coverage': [],
            'uncovered_components': [],
            'issues': []
        }
        
        for comp in active_components:
            nearby_caps = []
            for cap in capacitors:
                distance = comp.distance_to(cap)
                if distance < 5.0:  # Within 5mm considered "decoupling"
                    nearby_caps.append((cap.reference, distance))
            
            if nearby_caps:
                decoupling_analysis['coverage'].append({
                    'component': comp.reference,
                    'decoupling_caps': nearby_caps
                })
            else:
                decoupling_analysis['uncovered_components'].append(comp.reference)
        
        if decoupling_analysis['uncovered_components']:
            decoupling_analysis['issues'].append(
                f"Components without nearby decoupling: {', '.join(decoupling_analysis['uncovered_components'])}"
            )
        
        return decoupling_analysis
    
    def _analyze_critical_distances(self) -> Dict[str, Any]:
        """Analyze critical distance requirements"""
        
        groups = self.parser.get_component_groups()
        
        critical_analysis = {
            'jack_spacing': self._check_jack_spacing(groups['jack']),
            'thermal_spacing': self._check_thermal_spacing(),
            'interference_risks': self._check_interference_risks()
        }
        
        return critical_analysis
    
    def _check_jack_spacing(self, jacks: List[ComponentPlacement]) -> Dict[str, Any]:
        """Check jack spacing requirements"""
        
        spacing_analysis = {
            'spacings': [],
            'violations': [],
            'alignment_check': {}
        }
        
        # Sort jacks by position (assuming vertical alignment)
        jacks_sorted = sorted(jacks, key=lambda j: j.y)
        
        # Check spacing between adjacent jacks
        for i in range(len(jacks_sorted) - 1):
            j1, j2 = jacks_sorted[i], jacks_sorted[i + 1]
            spacing = j1.distance_to(j2)
            spacing_analysis['spacings'].append({
                'jack1': j1.reference,
                'jack2': j2.reference,
                'spacing': spacing
            })
            
            if spacing < 19.05:  # Minimum 19.05mm spacing
                spacing_analysis['violations'].append({
                    'jack1': j1.reference,
                    'jack2': j2.reference,
                    'actual_spacing': spacing,
                    'required_spacing': 19.05,
                    'violation': 19.05 - spacing
                })
        
        # Check alignment
        x_coords = [j.x for j in jacks]
        y_coords = [j.y for j in jacks]
        
        spacing_analysis['alignment_check'] = {
            'x_variation': max(x_coords) - min(x_coords) if x_coords else 0,
            'y_variation': max(y_coords) - min(y_coords) if y_coords else 0,
            'aligned': (max(x_coords) - min(x_coords)) < 2.0 or (max(y_coords) - min(y_coords)) < 2.0
        }
        
        return spacing_analysis
    
    def _check_thermal_spacing(self) -> Dict[str, Any]:
        """Check thermal management spacing"""
        
        groups = self.parser.get_component_groups()
        
        # Components that generate heat
        heat_sources = []
        heat_sources.extend(groups['microcontroller'])  # Teensy can get warm
        heat_sources.extend(groups['opamp'])  # OpAmps generate some heat
        
        thermal_analysis = {
            'heat_sources': [h.reference for h in heat_sources],
            'thermal_risks': [],
            'cooling_recommendations': []
        }
        
        # Check for components too close to heat sources
        sensitive_components = groups['dac']  # DACs are temperature sensitive
        
        for heat_source in heat_sources:
            for sensitive in sensitive_components:
                distance = heat_source.distance_to(sensitive)
                if distance < 10.0:
                    thermal_analysis['thermal_risks'].append({
                        'heat_source': heat_source.reference,
                        'sensitive_component': sensitive.reference,
                        'distance': distance,
                        'recommendation': 'Increase spacing or add thermal barrier'
                    })
        
        return thermal_analysis
    
    def _check_interference_risks(self) -> List[Dict[str, Any]]:
        """Check for electromagnetic interference risks"""
        
        groups = self.parser.get_component_groups()
        risks = []
        
        # Digital switching near analog components
        digital_components = groups['microcontroller']
        analog_components = groups['dac'] + groups['opamp']
        
        for digital in digital_components:
            for analog in analog_components:
                distance = digital.distance_to(analog)
                if distance < 15.0:
                    risks.append({
                        'type': 'digital_analog_interference',
                        'digital_component': digital.reference,
                        'analog_component': analog.reference,
                        'distance': distance,
                        'risk_level': 'high' if distance < 10.0 else 'medium',
                        'mitigation': 'Add ground plane separation or increase distance'
                    })
        
        return risks
    
    def generate_comprehensive_report(self) -> str:
        """Generate a comprehensive analysis report"""
        
        # Run all analyses
        component_analysis = self.parser.analyze_placement_quality()
        signal_analysis = self.analyze_signal_integrity()
        placement_score = self.optimizer.calculate_placement_score(self.parser.components)
        
        report = f"""# Master of Muppets PCB Analysis Report

## Executive Summary
- **Placement Score**: {placement_score:.3f}/1.0
- **Total Components**: {len(self.parser.components)}
- **Critical Issues**: {len(component_analysis.get('placement_issues', []))}

## Component Distribution
"""
        
        groups = self.parser.get_component_groups()
        for group_name, components in groups.items():
            if components:
                report += f"- **{group_name.title()}**: {len(components)} components\n"
        
        report += "\n## Signal Integrity Analysis\n"
        
        # I2C Analysis
        i2c = signal_analysis['i2c_analysis']
        if i2c.get('status') != 'incomplete':
            report += f"### I2C Bus Analysis\n"
            report += f"- Max distance to DAC: {i2c['max_distance']:.1f}mm\n"
            report += f"- Total bus length: {i2c['bus_length']:.1f}mm\n"
            
            if i2c['issues']:
                report += "- **Issues**:\n"
                for issue in i2c['issues']:
                    report += f"  - {issue}\n"
        
        # Analog Paths
        analog = signal_analysis['analog_paths']
        if analog['crosstalk_risks']:
            report += f"\n### Crosstalk Risks\n"
            for risk in analog['crosstalk_risks']:
                report += f"- {risk['component1']} <-> {risk['component2']}: {risk['distance']:.1f}mm ({risk['risk_level']} risk)\n"
        
        # Critical Distances
        critical = signal_analysis['critical_distances']
        jack_spacing = critical['jack_spacing']
        
        if jack_spacing['violations']:
            report += f"\n### Jack Spacing Violations\n"
            for violation in jack_spacing['violations']:
                report += f"- {violation['jack1']} <-> {violation['jack2']}: {violation['actual_spacing']:.1f}mm < {violation['required_spacing']}mm\n"
        
        # Recommendations
        suggestions = self.parser.suggest_placement_improvements()
        if suggestions:
            report += f"\n## Optimization Recommendations\n"
            for suggestion in suggestions:
                report += f"- {suggestion}\n"
        
        return report
    
    def export_analysis_data(self, output_file: str):
        """Export complete analysis data to JSON"""
        
        analysis_data = {
            'board_info': self.parser.board_info.__dict__ if self.parser.board_info else {},
            'component_analysis': self.parser.analyze_placement_quality(),
            'signal_integrity': self.analyze_signal_integrity(),
            'placement_score': self.optimizer.calculate_placement_score(self.parser.components),
            'component_groups': {k: [comp.__dict__ for comp in v] 
                               for k, v in self.parser.get_component_groups().items()},
            'optimization_suggestions': self.parser.suggest_placement_improvements()
        }
        
        with open(output_file, 'w') as f:
            json.dump(analysis_data, f, indent=2)
        
        print(f"[ANALYSIS] Complete analysis exported to {output_file}")

# CLI interface
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python pcb_analysis_suite.py <pcb_file>")
        sys.exit(1)
    
    pcb_file = sys.argv[1]
    suite = PCBAnalysisSuite(pcb_file)
    
    # Generate comprehensive report
    report = suite.generate_comprehensive_report()
    print(report)
    
    # Export detailed analysis
    base_name = Path(pcb_file).stem
    suite.export_analysis_data(f"{base_name}_complete_analysis.json")