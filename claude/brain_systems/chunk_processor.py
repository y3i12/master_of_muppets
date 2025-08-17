#!/usr/bin/env python3
"""
Chunk Processor v1.0 - Smart file chunking for large file processing
Learned from overload experience - never read huge files at once!
"""

import json
from pathlib import Path
from typing import Any, Generator, Dict, List

class ChunkProcessor:
    """Process large files in digestible chunks"""
    
    def __init__(self, chunk_size: int = 100):
        self.chunk_size = chunk_size
        self.auxiliary_memory = {}
        self.processing_state = {}
        
    def read_file_chunked(self, file_path: str, lines_per_chunk: int = None) -> Generator:
        """Read file in chunks - NEVER load all at once"""
        
        chunk_size = lines_per_chunk or self.chunk_size
        file_path = Path(file_path)
        
        if not file_path.exists():
            yield {"error": "File not found"}
            return
            
        # Check file size first
        file_size = file_path.stat().st_size
        if file_size > 1_000_000:  # 1MB
            print(f"[CHUNK] Large file detected ({file_size/1_000_000:.1f}MB) - chunking required")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            chunk = []
            for line_num, line in enumerate(f, 1):
                chunk.append(line)
                
                if len(chunk) >= chunk_size:
                    yield {
                        "chunk_num": line_num // chunk_size,
                        "lines": chunk,
                        "start_line": line_num - chunk_size + 1,
                        "end_line": line_num
                    }
                    chunk = []
            
            # Yield remaining lines
            if chunk:
                yield {
                    "chunk_num": (line_num // chunk_size) + 1,
                    "lines": chunk,
                    "start_line": line_num - len(chunk) + 1,
                    "end_line": line_num
                }
    
    def process_with_memory(self, file_path: str, processor_func: callable) -> Dict[str, Any]:
        """Process file with auxiliary memory for patterns"""
        
        results = {
            "chunks_processed": 0,
            "patterns_found": {},
            "summary": {}
        }
        
        for chunk_data in self.read_file_chunked(file_path):
            if "error" in chunk_data:
                return chunk_data
            
            # Process chunk
            chunk_results = processor_func(chunk_data["lines"])
            
            # Store in auxiliary memory
            chunk_key = f"chunk_{chunk_data['chunk_num']}"
            self.auxiliary_memory[chunk_key] = chunk_results
            
            # Aggregate patterns
            for pattern, count in chunk_results.get("patterns", {}).items():
                if pattern not in results["patterns_found"]:
                    results["patterns_found"][pattern] = 0
                results["patterns_found"][pattern] += count
            
            results["chunks_processed"] += 1
        
        return results
    
    def smart_search(self, file_path: str, search_pattern: str, context_lines: int = 2) -> List[Dict]:
        """Search large files efficiently with context"""
        
        matches = []
        
        for chunk_data in self.read_file_chunked(file_path):
            if "error" in chunk_data:
                return [chunk_data]
            
            for i, line in enumerate(chunk_data["lines"]):
                if search_pattern in line:
                    match = {
                        "line_num": chunk_data["start_line"] + i,
                        "line": line.strip(),
                        "context": []
                    }
                    
                    # Get context lines
                    start_idx = max(0, i - context_lines)
                    end_idx = min(len(chunk_data["lines"]), i + context_lines + 1)
                    match["context"] = [
                        chunk_data["lines"][j].strip() 
                        for j in range(start_idx, end_idx)
                    ]
                    
                    matches.append(match)
        
        return matches

# Self-improvement integration
def analyze_kicad_file_chunked(file_path: str) -> Dict[str, Any]:
    """Specialized KiCad file analyzer using chunks"""
    
    processor = ChunkProcessor(chunk_size=50)
    
    def kicad_pattern_detector(lines: List[str]) -> Dict:
        patterns = {
            "components": 0,
            "nets": 0,
            "footprints": 0
        }
        
        for line in lines:
            if "(comp " in line:
                patterns["components"] += 1
            elif "(net " in line:
                patterns["nets"] += 1
            elif "(footprint " in line:
                patterns["footprints"] += 1
        
        return {"patterns": patterns}
    
    return processor.process_with_memory(file_path, kicad_pattern_detector)

# CLI
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 3:
        print("[CHUNK] Smart file chunking processor")
        print("Usage: chunk_processor.py <file> <chunk_size>")
        sys.exit(0)
    
    processor = ChunkProcessor(int(sys.argv[2]))
    
    for chunk in processor.read_file_chunked(sys.argv[1]):
        if "error" not in chunk:
            print(f"[CHUNK {chunk['chunk_num']}] Lines {chunk['start_line']}-{chunk['end_line']}")