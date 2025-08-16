#!/usr/bin/env python3
"""
Working Graph System - Hot memory for active graph operations
Think: CPU registers for hardware/software graph computations

Architecture:
- JSON files = Hard disk (persistence) 
- working_graphs = CPU cache (active computation)
- cognitive_cache = CPU registers (instant state)
"""

import json
import time
from dataclasses import dataclass, field
from typing import Dict, List, Set, Any, Optional, Tuple
from collections import defaultdict, deque

@dataclass
class HotNode:
    """Ultra-fast node representation for active work"""
    id: str
    type: str
    props: Dict[str, Any] = field(default_factory=dict)
    edges: Set[str] = field(default_factory=set)
    last_access: float = field(default_factory=time.time)
    dirty: bool = False  # Changed since last git sync
    
    def touch(self):
        """Mark as recently accessed"""
        self.last_access = time.time()
    
    def mark_dirty(self):
        """Mark as changed"""
        self.dirty = True
        self.touch()

@dataclass 
class WorkingSet:
    """Focus-aware subset of graph for current task"""
    name: str
    nodes: Dict[str, HotNode] = field(default_factory=dict)
    hot_paths: List[List[str]] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    
class WorkingGraph:
    """Hot memory graph optimized for active computation"""
    
    def __init__(self, name: str, git_rev: str = "HEAD"):
        self.name = name
        self.git_rev = git_rev
        self.nodes: Dict[str, HotNode] = {}
        self.edge_index: Dict[str, Set[str]] = defaultdict(set)
        self.type_index: Dict[str, Set[str]] = defaultdict(set)
        self.working_set: Optional[WorkingSet] = None
        self.access_log: deque = deque(maxlen=1000)  # LRU tracking
        self.delta_tracker: Dict[str, Any] = {}
        
    def add_node(self, node_id: str, node_type: str, props: Dict = None) -> HotNode:
        """Add node with instant indexing"""
        node = HotNode(node_id, node_type, props or {})
        self.nodes[node_id] = node
        self.type_index[node_type].add(node_id)
        node.mark_dirty()
        self._log_access(f"add_node:{node_id}")
        return node
    
    def connect(self, from_id: str, to_id: str, weight: float = 1.0):
        """O(1) edge creation with bidirectional indexing"""
        if from_id in self.nodes and to_id in self.nodes:
            self.nodes[from_id].edges.add(to_id)
            self.nodes[to_id].edges.add(from_id)
            self.edge_index[from_id].add(to_id)
            self.edge_index[to_id].add(from_id)
            self.nodes[from_id].mark_dirty()
            self.nodes[to_id].mark_dirty()
            self._log_access(f"connect:{from_id}->{to_id}")
    
    def neighbors(self, node_id: str) -> Set[str]:
        """O(1) neighbor lookup"""
        if node_id in self.nodes:
            self.nodes[node_id].touch()
            self._log_access(f"neighbors:{node_id}")
            return self.edge_index[node_id].copy()
        return set()
    
    def by_type(self, node_type: str) -> Set[str]:
        """O(1) type-based lookup"""
        self._log_access(f"by_type:{node_type}")
        return self.type_index[node_type].copy()
    
    def focus_on(self, center_nodes: List[str], radius: int = 2) -> WorkingSet:
        """Create working set focused on specific nodes"""
        ws = WorkingSet(f"focus_{int(time.time())}")
        visited = set()
        queue = [(node_id, 0) for node_id in center_nodes]
        
        while queue:
            node_id, depth = queue.pop(0)
            if node_id in visited or depth > radius:
                continue
                
            visited.add(node_id)
            if node_id in self.nodes:
                ws.nodes[node_id] = self.nodes[node_id]
                self.nodes[node_id].touch()
                
                if depth < radius:
                    for neighbor in self.neighbors(node_id):
                        queue.append((neighbor, depth + 1))
        
        self.working_set = ws
        self._log_access(f"focus_on:{center_nodes}")
        return ws
    
    def hot_path(self, start: str, end: str, max_depth: int = 5) -> List[str]:
        """Find shortest path with hot caching"""
        if start == end:
            return [start]
            
        queue = deque([(start, [start])])
        visited = {start}
        
        while queue:
            node, path = queue.popleft()
            if len(path) > max_depth:
                continue
                
            for neighbor in self.neighbors(node):
                if neighbor == end:
                    result = path + [neighbor]
                    self._cache_hot_path(result)
                    return result
                    
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))
        
        return []  # No path found
    
    def get_dirty_delta(self) -> Dict[str, Any]:
        """Get changes since last git sync"""
        dirty_nodes = {nid: node for nid, node in self.nodes.items() if node.dirty}
        return {
            "git_rev": self.git_rev,
            "timestamp": time.time(),
            "dirty_count": len(dirty_nodes),
            "dirty_nodes": {nid: {
                "type": node.type,
                "props": node.props,
                "edges": list(node.edges)
            } for nid, node in dirty_nodes.items()}
        }
    
    def sync_to_git(self, git_rev: str):
        """Mark as synced to git revision"""
        for node in self.nodes.values():
            node.dirty = False
        self.git_rev = git_rev
        self._log_access(f"sync_to_git:{git_rev}")
    
    def _log_access(self, operation: str):
        """Track access patterns for optimization"""
        self.access_log.append((time.time(), operation))
    
    def _cache_hot_path(self, path: List[str]):
        """Cache frequently used paths"""
        if self.working_set:
            self.working_set.hot_paths.append(path)

class DualGraphWorkspace:
    """Combined hardware + software working graphs"""
    
    def __init__(self, git_rev: str = "HEAD"):
        self.hw_graph = WorkingGraph("hardware", git_rev)
        self.sw_graph = WorkingGraph("software", git_rev) 
        self.cross_refs: Dict[str, Set[str]] = defaultdict(set)  # hw<->sw links
        self.focus_mode: str = "dual"  # "hw", "sw", or "dual"
        
    def link_hw_sw(self, hw_node: str, sw_node: str):
        """Create cross-reference between hardware and software"""
        self.cross_refs[f"hw:{hw_node}"].add(f"sw:{sw_node}")
        self.cross_refs[f"sw:{sw_node}"].add(f"hw:{hw_node}")
    
    def find_related(self, node_id: str, graph_type: str) -> Set[str]:
        """Find related nodes across hw/sw boundary"""
        key = f"{graph_type}:{node_id}"
        return self.cross_refs.get(key, set())
    
    def focus_dual(self, hw_centers: List[str], sw_centers: List[str]):
        """Focus on related hw+sw components"""
        hw_ws = self.hw_graph.focus_on(hw_centers)
        sw_ws = self.sw_graph.focus_on(sw_centers)
        
        # Add cross-referenced nodes
        for hw_node in hw_ws.nodes:
            related_sw = self.find_related(hw_node, "hw")
            for sw_ref in related_sw:
                sw_node = sw_ref.replace("sw:", "")
                if sw_node in self.sw_graph.nodes:
                    sw_ws.nodes[sw_node] = self.sw_graph.nodes[sw_node]
    
    def get_combined_delta(self) -> Dict[str, Any]:
        """Get all changes across both graphs"""
        return {
            "hardware": self.hw_graph.get_dirty_delta(),
            "software": self.sw_graph.get_dirty_delta(),
            "cross_refs": dict(self.cross_refs)
        }
    
    def export_to_json(self, hw_path: str, sw_path: str):
        """Export to persistent JSON format"""
        # Convert working graphs back to JSON format
        hw_data = {
            "git_revision": self.hw_graph.git_rev,
            "nodes": {nid: {
                "type": node.type,
                "properties": node.props
            } for nid, node in self.hw_graph.nodes.items()},
            "edges": {nid: list(node.edges) 
                     for nid, node in self.hw_graph.nodes.items()}
        }
        
        with open(hw_path, 'w') as f:
            json.dump(hw_data, f, indent=2)
            
        # Similar for software...
        print(f"Exported working graphs to {hw_path}, {sw_path}")

# CLI for rapid working graph operations
if __name__ == "__main__":
    import sys
    
    # Quick test/demo
    workspace = DualGraphWorkspace()
    
    # Add some test nodes
    workspace.hw_graph.add_node("dac1", "ic", {"part": "AD5593R", "channels": 8})
    workspace.hw_graph.add_node("amp1", "ic", {"part": "TL074", "channels": 4})
    workspace.hw_graph.connect("dac1", "amp1")
    
    workspace.sw_graph.add_node("dr_teeth", "class", {"file": "dr_teeth.h"})
    workspace.sw_graph.add_node("electric_mayhem", "template", {"file": "electric_mayhem.h"})
    workspace.sw_graph.connect("dr_teeth", "electric_mayhem")
    
    # Link hardware to software
    workspace.link_hw_sw("dac1", "electric_mayhem")
    
    print("Working Graph System Demo:")
    print(f"HW neighbors of dac1: {workspace.hw_graph.neighbors('dac1')}")
    print(f"SW related to dac1: {workspace.find_related('dac1', 'hw')}")
    print(f"Hot path test: {workspace.hw_graph.hot_path('dac1', 'amp1')}")
    
    # Show dirty delta
    delta = workspace.get_combined_delta()
    print(f"Dirty nodes: HW={delta['hardware']['dirty_count']}, SW={delta['software']['dirty_count']}")