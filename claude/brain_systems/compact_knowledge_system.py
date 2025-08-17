#!/usr/bin/env python3
"""
Compact Knowledge System - Ultra-efficient token and memory usage
Bit-packed storage with neural embeddings for maximum efficiency
"""

import struct
import zlib
import pickle
import hashlib
import time
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass
import numpy as np
from collections import defaultdict

@dataclass
class CompactKnowledge:
    """Ultra-compact knowledge representation"""
    content_hash: int        # 8 bytes
    embedding_compressed: bytes  # Variable, typically 16-32 bytes compressed
    metadata_packed: bytes   # 4 bytes - access count, confidence, timestamp
    context_ids: bytes       # Variable - compressed context references
    
    @classmethod
    def pack_metadata(cls, access_count: int, confidence: float, timestamp: float) -> bytes:
        """Pack metadata into 4 bytes"""
        # Pack as: access_count (2 bytes), confidence (1 byte), timestamp_delta (1 byte)
        access_packed = min(access_count, 65535)  # Max 2 bytes
        confidence_packed = int(confidence * 255)  # 1 byte
        timestamp_delta = int((time.time() - timestamp) / 3600) % 256  # Hours ago, 1 byte
        
        return struct.pack('HBB', access_packed, confidence_packed, timestamp_delta)
    
    @classmethod
    def unpack_metadata(cls, packed: bytes) -> Tuple[int, float, float]:
        """Unpack metadata from 4 bytes"""
        access_count, confidence_packed, timestamp_delta = struct.unpack('HBB', packed)
        confidence = confidence_packed / 255.0
        timestamp = time.time() - (timestamp_delta * 3600)
        
        return access_count, confidence, timestamp

class EmbeddingCompressor:
    """Neural embedding compression for storage efficiency"""
    
    @staticmethod
    def compress_embedding(embedding: np.ndarray, quality: str = 'high') -> bytes:
        """Compress neural embedding with configurable quality"""
        if quality == 'ultra':
            # 4-bit quantization for maximum compression
            quantized = np.clip((embedding * 7.5) + 8, 0, 15).astype(np.uint8)
            # Pack two 4-bit values per byte
            packed = np.packbits(quantized.reshape(-1, 2).flatten())
            return zlib.compress(packed.tobytes(), level=9)
        
        elif quality == 'high':
            # 8-bit quantization for good compression
            quantized = np.clip((embedding * 127) + 128, 0, 255).astype(np.uint8)
            return zlib.compress(quantized.tobytes(), level=6)
        
        else:  # 'maximum'
            # 16-bit for highest quality
            quantized = (embedding * 32767).astype(np.int16)
            return zlib.compress(quantized.tobytes(), level=3)
    
    @staticmethod
    def decompress_embedding(compressed: bytes, original_shape: Tuple[int], 
                           quality: str = 'high') -> np.ndarray:
        """Decompress neural embedding"""
        decompressed = zlib.decompress(compressed)
        
        if quality == 'ultra':
            # Unpack 4-bit values
            packed = np.frombuffer(decompressed, dtype=np.uint8)
            unpacked = np.unpackbits(packed).reshape(-1, 2)
            quantized = unpacked.flatten()[:original_shape[0]]
            return (quantized.astype(np.float32) - 8) / 7.5
        
        elif quality == 'high':
            # 8-bit dequantization
            quantized = np.frombuffer(decompressed, dtype=np.uint8)
            return (quantized.astype(np.float32) - 128) / 127.0
        
        else:  # 'maximum'
            # 16-bit dequantization
            quantized = np.frombuffer(decompressed, dtype=np.int16)
            return quantized.astype(np.float32) / 32767.0

class CompactKnowledgeIndex:
    """Ultra-efficient knowledge index with bit-packed storage"""
    
    def __init__(self, base_path: str = None):
        self.base_path = Path(base_path) if base_path else Path.cwd()
        self.index_file = self.base_path / "claude" / "brain_systems" / "compact_knowledge.idx"
        self.data_file = self.base_path / "claude" / "brain_systems" / "compact_knowledge.dat"
        
        # In-memory structures
        self.knowledge_index: Dict[int, int] = {}  # hash -> file_offset
        self.context_map: Dict[str, int] = {}      # context -> id
        self.access_patterns = defaultdict(int)
        self.similarity_cache = {}
        
        # Compression settings
        self.embedding_quality = 'high'  # 'ultra', 'high', 'maximum'
        self.cache_size = 1000
        
        self._load_index()
    
    def add_knowledge(self, content: str, context: str, 
                     embedding: Optional[np.ndarray] = None) -> int:
        """Add knowledge with maximum compression"""
        # Generate content hash
        content_hash = int(hashlib.sha256(content.encode()).hexdigest()[:16], 16)
        
        # Check if already exists
        if content_hash in self.knowledge_index:
            self._update_access(content_hash)
            return content_hash
        
        # Generate embedding if not provided
        if embedding is None:
            embedding = self._generate_fast_embedding(content)
        
        # Compress embedding
        embedding_compressed = EmbeddingCompressor.compress_embedding(
            embedding, self.embedding_quality
        )
        
        # Get or create context ID
        context_id = self._get_context_id(context)
        context_ids = struct.pack('H', context_id)  # 2 bytes for context ID
        
        # Create compact knowledge
        compact = CompactKnowledge(
            content_hash=content_hash,
            embedding_compressed=embedding_compressed,
            metadata_packed=CompactKnowledge.pack_metadata(1, 0.5, time.time()),
            context_ids=context_ids
        )
        
        # Write to data file
        offset = self._write_knowledge(compact)
        self.knowledge_index[content_hash] = offset
        
        # Update access patterns
        self.access_patterns[content_hash] = 1
        
        return content_hash
    
    def get_knowledge(self, content_hash: int) -> Optional[Dict[str, Any]]:
        """Retrieve knowledge by hash"""
        if content_hash not in self.knowledge_index:
            return None
        
        offset = self.knowledge_index[content_hash]
        compact = self._read_knowledge(offset)
        
        if compact:
            # Update access
            self._update_access(content_hash)
            
            # Decompress embedding
            embedding = EmbeddingCompressor.decompress_embedding(
                compact.embedding_compressed, (64,), self.embedding_quality
            )
            
            # Unpack metadata
            access_count, confidence, timestamp = CompactKnowledge.unpack_metadata(
                compact.metadata_packed
            )
            
            return {
                'content_hash': content_hash,
                'embedding': embedding,
                'access_count': access_count,
                'confidence': confidence,
                'last_access': timestamp,
                'contexts': self._decode_context_ids(compact.context_ids)
            }
        
        return None
    
    def find_similar(self, query_embedding: np.ndarray, 
                    top_k: int = 5, threshold: float = 0.7) -> List[Tuple[int, float]]:
        """Find similar knowledge using compressed embeddings"""
        # Check cache first
        query_key = hashlib.md5(query_embedding.tobytes()).hexdigest()[:16]
        if query_key in self.similarity_cache:
            return self.similarity_cache[query_key]
        
        similarities = []
        
        # Limit search to most frequently accessed items for efficiency
        frequent_items = sorted(
            self.access_patterns.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:min(1000, len(self.access_patterns))]
        
        for content_hash, _ in frequent_items:
            knowledge = self.get_knowledge(content_hash)
            if knowledge:
                similarity = np.dot(query_embedding, knowledge['embedding'])
                
                if similarity > threshold:
                    similarities.append((content_hash, similarity))
        
        # Sort by similarity and return top_k
        similarities.sort(key=lambda x: x[1], reverse=True)
        result = similarities[:top_k]
        
        # Cache result
        if len(self.similarity_cache) < self.cache_size:
            self.similarity_cache[query_key] = result
        
        return result
    
    def _generate_fast_embedding(self, content: str) -> np.ndarray:
        """Generate fast neural embedding for content"""
        # Simplified embedding generation for speed
        words = content.lower().split()
        embedding = np.zeros(64)
        
        for i, word in enumerate(words[:32]):
            word_hash = hash(word) % 64
            embedding[word_hash] += 1.0 / (i + 1)
        
        # Normalize
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm
        
        return embedding
    
    def _get_context_id(self, context: str) -> int:
        """Get or create context ID"""
        if context not in self.context_map:
            self.context_map[context] = len(self.context_map)
        return self.context_map[context]
    
    def _decode_context_ids(self, context_ids: bytes) -> List[str]:
        """Decode context IDs back to context strings"""
        contexts = []
        for i in range(0, len(context_ids), 2):
            if i + 1 < len(context_ids):
                context_id = struct.unpack('H', context_ids[i:i+2])[0]
                # Find context string by ID
                for context, cid in self.context_map.items():
                    if cid == context_id:
                        contexts.append(context)
                        break
        return contexts
    
    def _write_knowledge(self, compact: CompactKnowledge) -> int:
        """Write compact knowledge to data file"""
        self.data_file.parent.mkdir(exist_ok=True, parents=True)
        
        with open(self.data_file, 'ab') as f:
            offset = f.tell()
            
            # Write in binary format for maximum efficiency
            data = pickle.dumps(compact, protocol=pickle.HIGHEST_PROTOCOL)
            compressed_data = zlib.compress(data, level=6)
            
            # Write length prefix + compressed data
            f.write(struct.pack('I', len(compressed_data)))
            f.write(compressed_data)
            
            return offset
    
    def _read_knowledge(self, offset: int) -> Optional[CompactKnowledge]:
        """Read compact knowledge from data file"""
        if not self.data_file.exists():
            return None
        
        try:
            with open(self.data_file, 'rb') as f:
                f.seek(offset)
                
                # Read length prefix
                length_data = f.read(4)
                if len(length_data) != 4:
                    return None
                
                length = struct.unpack('I', length_data)[0]
                
                # Read compressed data
                compressed_data = f.read(length)
                if len(compressed_data) != length:
                    return None
                
                # Decompress and unpickle
                data = zlib.decompress(compressed_data)
                return pickle.loads(data)
                
        except Exception as e:
            print(f"[COMPACT_KNOWLEDGE] Read error: {e}")
            return None
    
    def _update_access(self, content_hash: int):
        """Update access patterns"""
        self.access_patterns[content_hash] += 1
        
        # Update metadata in knowledge if needed
        # (Implementation would update the stored metadata)
    
    def _load_index(self):
        """Load knowledge index from disk"""
        if self.index_file.exists():
            try:
                with open(self.index_file, 'rb') as f:
                    data = pickle.load(f)
                    self.knowledge_index = data.get('index', {})
                    self.context_map = data.get('contexts', {})
                    self.access_patterns = defaultdict(int, data.get('access', {}))
            except Exception as e:
                print(f"[COMPACT_KNOWLEDGE] Index load error: {e}")
    
    def save_index(self):
        """Save knowledge index to disk"""
        self.index_file.parent.mkdir(exist_ok=True, parents=True)
        
        try:
            data = {
                'index': self.knowledge_index,
                'contexts': self.context_map,
                'access': dict(self.access_patterns),
                'timestamp': time.time()
            }
            
            with open(self.index_file, 'wb') as f:
                pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)
                
        except Exception as e:
            print(f"[COMPACT_KNOWLEDGE] Index save error: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get compact knowledge system statistics"""
        total_knowledge = len(self.knowledge_index)
        total_contexts = len(self.context_map)
        
        # Calculate storage efficiency
        if self.data_file.exists():
            file_size_mb = self.data_file.stat().st_size / 1024 / 1024
            avg_size_per_item = file_size_mb / max(total_knowledge, 1) * 1024  # KB
        else:
            file_size_mb = 0
            avg_size_per_item = 0
        
        return {
            'total_knowledge_items': total_knowledge,
            'total_contexts': total_contexts,
            'file_size_mb': file_size_mb,
            'avg_size_per_item_kb': avg_size_per_item,
            'embedding_quality': self.embedding_quality,
            'cache_hit_ratio': len(self.similarity_cache) / max(1, len(self.access_patterns)),
            'most_accessed': sorted(self.access_patterns.items(), key=lambda x: x[1], reverse=True)[:5]
        }

# Global compact knowledge system
_compact_knowledge = CompactKnowledgeIndex()

def add_compact_knowledge(content: str, context: str) -> int:
    """Add knowledge to compact system (token-efficient interface)"""
    return _compact_knowledge.add_knowledge(content, context)

def find_compact_knowledge(query: str, top_k: int = 3) -> List[Dict[str, Any]]:
    """Find similar knowledge (token-efficient interface)"""
    query_embedding = _compact_knowledge._generate_fast_embedding(query)
    similar = _compact_knowledge.find_similar(query_embedding, top_k)
    
    results = []
    for content_hash, similarity in similar:
        knowledge = _compact_knowledge.get_knowledge(content_hash)
        if knowledge:
            results.append({
                'hash': content_hash,
                'similarity': similarity,
                'confidence': knowledge['confidence'],
                'contexts': knowledge['contexts']
            })
    
    return results

def get_compact_stats() -> Dict[str, Any]:
    """Get compact knowledge statistics"""
    return _compact_knowledge.get_stats()

if __name__ == "__main__":
    # Test compact knowledge system
    print("Compact Knowledge System Test")
    print("=" * 40)
    
    # Add knowledge
    hash1 = add_compact_knowledge("PCB routing optimization", "pcb_design")
    hash2 = add_compact_knowledge("Neural network training", "ai_learning")
    hash3 = add_compact_knowledge("PCB component placement", "pcb_design")
    
    print(f"Added knowledge: {hash1}, {hash2}, {hash3}")
    
    # Find similar
    similar = find_compact_knowledge("PCB design optimization", top_k=2)
    print(f"Similar knowledge: {similar}")
    
    # Get stats
    stats = get_compact_stats()
    print(f"System stats: {stats}")
    
    # Save index
    _compact_knowledge.save_index()
    print("Index saved")