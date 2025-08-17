#!/usr/bin/env python3
"""
Code Ingestor v1.0 - Automated Code Analysis and Memory Refresh
Analyzes code changes and updates cognitive understanding automatically
"""

import os
import json
import time
import subprocess
import hashlib
from pathlib import Path
from typing import Dict, List, Set, Any, Optional, Tuple
from dataclasses import dataclass
import ast
import re

@dataclass
class CodeEntity:
    """Represents a code entity (class, function, variable, etc.)"""
    name: str
    type: str  # class, function, variable, constant, template, etc.
    file_path: str
    line_start: int
    line_end: int
    signature: str
    dependencies: Set[str]
    complexity_score: int
    last_modified: float

@dataclass
class CodeChange:
    """Represents a detected code change"""
    file_path: str
    change_type: str  # added, modified, deleted, moved
    entity_name: str
    old_signature: Optional[str]
    new_signature: Optional[str]
    impact_score: float
    timestamp: float

class CodeIngestor:
    """Automated code analysis and cognitive update system"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.code_index: Dict[str, CodeEntity] = {}
        self.file_hashes: Dict[str, str] = {}
        self.last_scan_time: float = 0
        self.supported_extensions = {'.cpp', '.h', '.hpp', '.c', '.py', '.js', '.ts'}
        
        # Load existing index
        self.index_file = self.project_root / "claude" / "code_index.json"
        self._load_index()
    
    def scan_codebase(self, force_rescan: bool = False) -> List[CodeChange]:
        """Scan entire codebase and detect changes"""
        print("🔍 Scanning codebase for changes...")
        
        changes = []
        current_time = time.time()
        
        # Find all code files
        code_files = []
        for ext in self.supported_extensions:
            code_files.extend(self.project_root.rglob(f"*{ext}"))
        
        for file_path in code_files:
            if self._should_skip_file(file_path):
                continue
                
            rel_path = str(file_path.relative_to(self.project_root))
            
            # Check if file changed
            current_hash = self._get_file_hash(file_path)
            old_hash = self.file_hashes.get(rel_path)
            
            if force_rescan or current_hash != old_hash:
                file_changes = self._analyze_file(file_path, rel_path)
                changes.extend(file_changes)
                self.file_hashes[rel_path] = current_hash
        
        self.last_scan_time = current_time
        self._save_index()
        
        print(f"📊 Scan complete: {len(changes)} changes detected in {len(code_files)} files")
        return changes
    
    def _analyze_file(self, file_path: Path, rel_path: str) -> List[CodeChange]:
        """Analyze a single file for code entities and changes"""
        changes = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"⚠️ Error reading {rel_path}: {e}")
            return changes
        
        if file_path.suffix == '.py':
            changes.extend(self._analyze_python_file(content, rel_path))
        elif file_path.suffix in {'.cpp', '.h', '.hpp', '.c'}:
            changes.extend(self._analyze_cpp_file(content, rel_path))
        
        return changes
    
    def _analyze_python_file(self, content: str, rel_path: str) -> List[CodeChange]:
        """Analyze Python file using AST"""
        changes = []
        
        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            print(f"⚠️ Syntax error in {rel_path}: {e}")
            return changes
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                entity = self._create_entity_from_ast_class(node, rel_path)
                changes.extend(self._track_entity_change(entity))
            
            elif isinstance(node, ast.FunctionDef):
                entity = self._create_entity_from_ast_function(node, rel_path)
                changes.extend(self._track_entity_change(entity))
            
            elif isinstance(node, ast.Assign):
                # Track important variables/constants
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id.isupper():
                        entity = self._create_entity_from_ast_assign(node, target, rel_path)
                        changes.extend(self._track_entity_change(entity))
        
        return changes
    
    def _analyze_cpp_file(self, content: str, rel_path: str) -> List[CodeChange]:
        """Analyze C++ file using regex patterns"""
        changes = []
        lines = content.split('\n')
        
        # Class definitions
        class_pattern = re.compile(r'^\s*(?:template\s*<[^>]*>\s*)?class\s+(\w+)')
        # Function definitions  
        func_pattern = re.compile(r'^\s*(?:template\s*<[^>]*>\s*)?(?:[\w:]+\s+)*(\w+)\s*\([^)]*\)\s*(?:const)?\s*\{?')
        # Constants
        const_pattern = re.compile(r'^\s*(?:static\s+)?const(?:expr)?\s+[\w:]+\s+(\w+)')
        
        for i, line in enumerate(lines):
            # Classes
            class_match = class_pattern.match(line)
            if class_match:
                entity = CodeEntity(
                    name=class_match.group(1),
                    type='class',
                    file_path=rel_path,
                    line_start=i + 1,
                    line_end=self._find_cpp_block_end(lines, i),
                    signature=line.strip(),
                    dependencies=self._extract_cpp_dependencies(line),
                    complexity_score=self._estimate_complexity(lines[i:]),
                    last_modified=time.time()
                )
                changes.extend(self._track_entity_change(entity))
            
            # Functions
            func_match = func_pattern.match(line)
            if func_match and not class_match:  # Don't double-count class constructors
                entity = CodeEntity(
                    name=func_match.group(1),
                    type='function',
                    file_path=rel_path,
                    line_start=i + 1,
                    line_end=self._find_cpp_block_end(lines, i),
                    signature=line.strip(),
                    dependencies=self._extract_cpp_dependencies(line),
                    complexity_score=self._estimate_complexity(lines[i:]),
                    last_modified=time.time()
                )
                changes.extend(self._track_entity_change(entity))
            
            # Constants
            const_match = const_pattern.match(line)
            if const_match:
                entity = CodeEntity(
                    name=const_match.group(1),
                    type='constant',
                    file_path=rel_path,
                    line_start=i + 1,
                    line_end=i + 1,
                    signature=line.strip(),
                    dependencies=set(),
                    complexity_score=1,
                    last_modified=time.time()
                )
                changes.extend(self._track_entity_change(entity))
        
        return changes
    
    def get_code_summary(self) -> Dict[str, Any]:
        """Generate summary of codebase understanding"""
        entity_types = {}
        complexity_total = 0
        
        for entity in self.code_index.values():
            entity_types[entity.type] = entity_types.get(entity.type, 0) + 1
            complexity_total += entity.complexity_score
        
        return {
            "total_entities": len(self.code_index),
            "entity_breakdown": entity_types,
            "total_complexity": complexity_total,
            "avg_complexity": complexity_total / max(1, len(self.code_index)),
            "files_tracked": len(set(e.file_path for e in self.code_index.values())),
            "last_scan": self.last_scan_time
        }
    
    def find_related_entities(self, entity_name: str) -> List[CodeEntity]:
        """Find entities related to the given entity"""
        related = []
        
        for entity in self.code_index.values():
            if (entity_name in entity.dependencies or
                entity_name.lower() in entity.signature.lower()):
                related.append(entity)
        
        return related
    
    def get_critical_paths(self) -> List[List[str]]:
        """Identify critical code paths based on dependencies"""
        # Build dependency graph
        deps = {}
        for entity in self.code_index.values():
            deps[entity.name] = list(entity.dependencies)
        
        # Find highly connected components
        critical_entities = sorted(
            self.code_index.values(),
            key=lambda x: len(x.dependencies) + len(self.find_related_entities(x.name)),
            reverse=True
        )[:10]
        
        return [[e.name for e in critical_entities]]
    
    def refresh_cognitive_memory(self):
        """Update cognitive systems with latest code understanding"""
        summary = self.get_code_summary()
        
        # Update cognitive core with code insights
        from cognitive_ops import CognitiveCore
        cc = CognitiveCore()
        
        cc.u("idx.sw.entities", f"{summary['total_entities']}_total")
        cc.u("idx.sw.complexity", f"{summary['avg_complexity']:.1f}_avg")
        cc.u("idx.sw.files", f"{summary['files_tracked']}_tracked")
        cc.save()
        
        print(f"🧠 Updated cognitive memory with {summary['total_entities']} code entities")
    
    def _create_entity_from_ast_class(self, node: ast.ClassDef, file_path: str) -> CodeEntity:
        """Create entity from AST class node"""
        return CodeEntity(
            name=node.name,
            type='class',
            file_path=file_path,
            line_start=node.lineno,
            line_end=getattr(node, 'end_lineno', node.lineno),
            signature=f"class {node.name}({', '.join(b.id for b in node.bases if isinstance(b, ast.Name))})",
            dependencies=self._extract_ast_dependencies(node),
            complexity_score=len(node.body),
            last_modified=time.time()
        )
    
    def _create_entity_from_ast_function(self, node: ast.FunctionDef, file_path: str) -> CodeEntity:
        """Create entity from AST function node"""
        args = [arg.arg for arg in node.args.args]
        return CodeEntity(
            name=node.name,
            type='function',
            file_path=file_path,
            line_start=node.lineno,
            line_end=getattr(node, 'end_lineno', node.lineno),
            signature=f"def {node.name}({', '.join(args)})",
            dependencies=self._extract_ast_dependencies(node),
            complexity_score=len([n for n in ast.walk(node) if isinstance(n, (ast.If, ast.For, ast.While))]),
            last_modified=time.time()
        )
    
    def _create_entity_from_ast_assign(self, node: ast.Assign, target: ast.Name, file_path: str) -> CodeEntity:
        """Create entity from AST assignment node"""
        return CodeEntity(
            name=target.id,
            type='constant',
            file_path=file_path,
            line_start=node.lineno,
            line_end=node.lineno,
            signature=f"{target.id} = ...",
            dependencies=set(),
            complexity_score=1,
            last_modified=time.time()
        )
    
    def _track_entity_change(self, entity: CodeEntity) -> List[CodeChange]:
        """Track changes to a code entity"""
        changes = []
        entity_key = f"{entity.file_path}:{entity.name}"
        
        if entity_key in self.code_index:
            old_entity = self.code_index[entity_key]
            if old_entity.signature != entity.signature:
                changes.append(CodeChange(
                    file_path=entity.file_path,
                    change_type='modified',
                    entity_name=entity.name,
                    old_signature=old_entity.signature,
                    new_signature=entity.signature,
                    impact_score=self._calculate_impact_score(old_entity, entity),
                    timestamp=time.time()
                ))
        else:
            changes.append(CodeChange(
                file_path=entity.file_path,
                change_type='added',
                entity_name=entity.name,
                old_signature=None,
                new_signature=entity.signature,
                impact_score=entity.complexity_score,
                timestamp=time.time()
            ))
        
        self.code_index[entity_key] = entity
        return changes
    
    def _should_skip_file(self, file_path: Path) -> bool:
        """Check if file should be skipped during analysis"""
        skip_dirs = {'node_modules', '.git', '__pycache__', 'build', '.pio'}
        return any(part in skip_dirs for part in file_path.parts)
    
    def _get_file_hash(self, file_path: Path) -> str:
        """Get hash of file content"""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except:
            return ""
    
    def _extract_ast_dependencies(self, node) -> Set[str]:
        """Extract dependencies from AST node"""
        deps = set()
        for child in ast.walk(node):
            if isinstance(child, ast.Name):
                deps.add(child.id)
        return deps
    
    def _extract_cpp_dependencies(self, line: str) -> Set[str]:
        """Extract dependencies from C++ line"""
        deps = set()
        # Look for class names, function calls, etc.
        words = re.findall(r'\b[A-Za-z_][A-Za-z0-9_]*\b', line)
        for word in words:
            if word not in {'const', 'static', 'class', 'struct', 'template'}:
                deps.add(word)
        return deps
    
    def _find_cpp_block_end(self, lines: List[str], start: int) -> int:
        """Find end of C++ block starting at start line"""
        brace_count = 0
        for i in range(start, len(lines)):
            brace_count += lines[i].count('{') - lines[i].count('}')
            if brace_count == 0 and '{' in lines[i]:
                return i + 1
        return start + 1
    
    def _estimate_complexity(self, lines: List[str]) -> int:
        """Estimate complexity score from lines of code"""
        complexity = 1
        for line in lines[:50]:  # Look at first 50 lines
            if any(keyword in line for keyword in ['if', 'for', 'while', 'switch', 'case']):
                complexity += 1
        return complexity
    
    def _calculate_impact_score(self, old_entity: CodeEntity, new_entity: CodeEntity) -> float:
        """Calculate impact score of entity change"""
        score = 0.0
        
        # Signature change impact
        if old_entity.signature != new_entity.signature:
            score += 2.0
        
        # Complexity change impact
        complexity_change = abs(new_entity.complexity_score - old_entity.complexity_score)
        score += complexity_change * 0.5
        
        # Dependency change impact
        deps_added = len(new_entity.dependencies - old_entity.dependencies)
        deps_removed = len(old_entity.dependencies - new_entity.dependencies)
        score += (deps_added + deps_removed) * 0.3
        
        return score
    
    def _load_index(self):
        """Load existing code index"""
        if self.index_file.exists():
            try:
                with open(self.index_file, 'r') as f:
                    data = json.load(f)
                    
                # Reconstruct entities
                for key, entity_data in data.get('entities', {}).items():
                    entity = CodeEntity(**entity_data)
                    entity.dependencies = set(entity.dependencies)
                    self.code_index[key] = entity
                
                self.file_hashes = data.get('file_hashes', {})
                self.last_scan_time = data.get('last_scan_time', 0)
                
                print(f"📁 Loaded code index: {len(self.code_index)} entities")
            except Exception as e:
                print(f"⚠️ Error loading code index: {e}")
    
    def _save_index(self):
        """Save code index to file"""
        self.index_file.parent.mkdir(exist_ok=True)
        
        # Convert entities to serializable format
        entities_data = {}
        for key, entity in self.code_index.items():
            entity_dict = entity.__dict__.copy()
            entity_dict['dependencies'] = list(entity.dependencies)
            entities_data[key] = entity_dict
        
        data = {
            'entities': entities_data,
            'file_hashes': self.file_hashes,
            'last_scan_time': self.last_scan_time
        }
        
        with open(self.index_file, 'w') as f:
            json.dump(data, f, indent=2)

# CLI interface
if __name__ == "__main__":
    import sys
    
    ingestor = CodeIngestor()
    
    if len(sys.argv) < 2:
        summary = ingestor.get_code_summary()
        print("🔍 Code Ingestor Summary:")
        print(f"   Entities: {summary['total_entities']}")
        print(f"   Files: {summary['files_tracked']}")
        print(f"   Avg Complexity: {summary['avg_complexity']:.1f}")
        print(f"   Types: {summary['entity_breakdown']}")
        print("\nCommands:")
        print("  scan             - Scan codebase for changes")
        print("  refresh          - Update cognitive memory")
        print("  find <entity>    - Find related entities")
        print("  critical         - Show critical paths")
        sys.exit(0)
    
    cmd = sys.argv[1]
    
    if cmd == 'scan':
        changes = ingestor.scan_codebase(force_rescan='--force' in sys.argv)
        for change in changes:
            print(f"📝 {change.change_type}: {change.entity_name} in {change.file_path}")
    
    elif cmd == 'refresh':
        ingestor.refresh_cognitive_memory()
    
    elif cmd == 'find' and len(sys.argv) > 2:
        entity_name = sys.argv[2]
        related = ingestor.find_related_entities(entity_name)
        for entity in related:
            print(f"🔗 {entity.name} ({entity.type}) in {entity.file_path}")
    
    elif cmd == 'critical':
        paths = ingestor.get_critical_paths()
        for i, path in enumerate(paths):
            print(f"🎯 Critical Path {i+1}: {' -> '.join(path)}")
    
    else:
        print(f"Unknown command: {cmd}")