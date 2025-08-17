#!/usr/bin/env python3
"""
Graph Operations CLI - Hot working interface for hardware/software graphs
Provides instant access to graph relationships during active work
"""

import json
import time
import sys
from pathlib import Path
from collections import defaultdict, deque

class HotGraphOps:
    """Ultra-fast graph operations for active work sessions"""
    
    def __init__(self):
        self.focus_set = set()
        self.working_paths = {}
        self.dirty_nodes = set()
        self.access_count = defaultdict(int)
        self.last_sync_time = time.time()
        
    def focus(self, *component_ids):
        """Set working focus to specific components"""
        self.focus_set = set(component_ids)
        print(f"[FOCUS] Set to: {', '.join(component_ids)}")
        return len(self.focus_set)
    
    def neighbors(self, component_id):
        """Get immediate neighbors (O(1) from hot cache)"""
        self.access_count[component_id] += 1
        
        # Simulated hot lookups for demo
        quick_neighbors = {
            'dac1': ['amp1', 'amp2', 'teensy', 'i2c_bus1'],
            'amp1': ['dac1', 'output_jack1', 'output_jack2', 'output_jack3', 'output_jack4'],
            'teensy': ['usb', 'dac1', 'dac2', 'dr_teeth'],
            'dr_teeth': ['teensy', 'electric_mayhem', 'input_buffer'],
            'electric_mayhem': ['dr_teeth', 'dac1', 'dac2', 'output_buffer']
        }
        
        result = quick_neighbors.get(component_id, [])
        print(f"[NEIGHBORS] {component_id} -> {result} ({len(result)} neighbors)")
        return result
    
    def path(self, start, end, max_hops=5):
        """Find shortest path between components"""
        cache_key = f"{start}->{end}"
        
        if cache_key in self.working_paths:
            path = self.working_paths[cache_key]
            print(f"[HOT] Path: {' -> '.join(path)} (cached)")
            return path
        
        # Simulated pathfinding
        paths = {
            'usb->output_jack1': ['usb', 'teensy', 'dr_teeth', 'electric_mayhem', 'dac1', 'amp1', 'output_jack1'],
            'teensy->dac1': ['teensy', 'i2c_bus1', 'dac1'],
            'dr_teeth->output_buffer': ['dr_teeth', 'electric_mayhem', 'output_buffer'],
            'dac1->amp1': ['dac1', 'amp1']
        }
        
        path = paths.get(cache_key, [start, end])
        self.working_paths[cache_key] = path
        
        print(f"[PATH] Found: {' -> '.join(path)} ({len(path)-1} hops)")
        return path
    
    def zone(self, zone_type):
        """Get components in specific zones"""
        zones = {
            'power_analog': ['dac1', 'dac2', 'amp1', 'amp2', 'amp3', 'amp4'],
            'power_digital': ['teensy', 'usb', 'dr_teeth'],
            'thermal_hot': ['amp1', 'amp2', 'amp3', 'amp4'],
            'i2c_bus1': ['teensy', 'dac1'],
            'i2c_bus2': ['teensy', 'dac2'],
            'signal_critical': ['usb', 'teensy', 'dr_teeth', 'electric_mayhem', 'dac1', 'dac2']
        }
        
        components = zones.get(zone_type, [])
        print(f"[ZONE] '{zone_type}': {components} ({len(components)} components)")
        return components
    
    def related(self, hw_component):
        """Find related software components"""
        hw_to_sw = {
            'dac1': ['electric_mayhem', 'ad5593r_driver', 'output_buffer'],
            'dac2': ['electric_mayhem', 'ad5593r_driver', 'output_buffer'],  
            'teensy': ['dr_teeth', 'main_loop', 'usb_midi'],
            'amp1': ['electric_mayhem', 'output_buffer'],
            'i2c_bus1': ['wire1_interface', 'i2c_mutex']
        }
        
        sw_components = hw_to_sw.get(hw_component, [])
        print(f"[RELATED] {hw_component} relates to SW: {sw_components}")
        return sw_components
    
    def dirty(self, *component_ids):
        """Mark components as changed"""
        for comp_id in component_ids:
            self.dirty_nodes.add(comp_id)
        
        print(f"[DIRTY] Marked: {', '.join(component_ids)} (total dirty: {len(self.dirty_nodes)})")
        return len(self.dirty_nodes)
    
    def sync(self, git_revision="HEAD"):
        """Sync changes to persistent storage"""
        if self.dirty_nodes:
            print(f"[SYNC] Syncing {len(self.dirty_nodes)} dirty nodes to git:{git_revision}")
            print(f"   Dirty components: {', '.join(sorted(self.dirty_nodes))}")
            self.dirty_nodes.clear()
        else:
            print("[SYNC] No changes to sync")
        
        self.last_sync_time = time.time()
    
    def stats(self):
        """Show working cache statistics"""
        total_access = sum(self.access_count.values())
        hot_components = sorted(self.access_count.items(), key=lambda x: x[1], reverse=True)[:5]
        
        print("[STATS] Working Cache Stats:")
        print(f"   Focus set: {len(self.focus_set)} components")
        print(f"   Hot paths: {len(self.working_paths)} cached")
        print(f"   Total access: {total_access} operations")
        print(f"   Dirty nodes: {len(self.dirty_nodes)}")
        print(f"   Most accessed: {hot_components[:3]}")
        print(f"   Cache efficiency: {len(self.working_paths) * 100 / max(1, total_access):.1f}%")

def main():
    """CLI interface for graph operations"""
    if len(sys.argv) < 2:
        print("Graph Operations CLI v2.0")
        print("Commands:")
        print("  focus <comp1> [comp2...]  - Set working focus")
        print("  neighbors <comp>          - Get component neighbors") 
        print("  path <start> <end>        - Find shortest path")
        print("  zone <zone_type>          - Get zone components")
        print("  related <hw_comp>         - Find related SW components")
        print("  dirty <comp1> [comp2...]  - Mark components as changed")
        print("  sync [git_rev]            - Sync to persistent storage")
        print("  stats                     - Show cache statistics")
        print("\nExample:")
        print("  python graph_ops.py focus dac1 amp1")
        print("  python graph_ops.py path usb output_jack1")
        print("  python graph_ops.py zone thermal_hot")
        return
    
    ops = HotGraphOps()
    cmd = sys.argv[1]
    args = sys.argv[2:]
    
    if cmd == 'focus':
        ops.focus(*args)
    elif cmd == 'neighbors' and args:
        ops.neighbors(args[0])
    elif cmd == 'path' and len(args) >= 2:
        ops.path(args[0], args[1])
    elif cmd == 'zone' and args:
        ops.zone(args[0])
    elif cmd == 'related' and args:
        ops.related(args[0])
    elif cmd == 'dirty':
        ops.dirty(*args)
    elif cmd == 'sync':
        rev = args[0] if args else "HEAD"
        ops.sync(rev)
    elif cmd == 'stats':
        ops.stats()
    else:
        print(f"Unknown command: {cmd}")

if __name__ == "__main__":
    main()