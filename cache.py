"""
HTTP Cache Implementation
Supports in-memory and file-based caching with TTL
"""

import time
import os
import json
import hashlib
from pathlib import Path

class Cache:
    def __init__(self, ttl=300, max_size=100, cache_dir=None):
        """
        Initialize cache
        
        Args:
            ttl: Time to live in seconds (default: 5 minutes)
            max_size: Maximum number of cached items
            cache_dir: Directory for file-based cache (None for memory-only)
        """
        self.ttl = ttl
        self.max_size = max_size
        self.cache_dir = cache_dir
        
        # In-memory cache
        self.memory_cache = {}
        self.access_times = {}
        
        # File-based cache setup
        if cache_dir:
            self.cache_path = Path(cache_dir)
            self.cache_path.mkdir(exist_ok=True)
            self.index_file = self.cache_path / 'cache_index.json'
            self._load_index()
        else:
            self.cache_path = None
            self.index_file = None
            self.file_index = {}
    
    def _load_index(self):
        """Load cache index from file"""
        try:
            if self.index_file.exists():
                with open(self.index_file, 'r') as f:
                    self.file_index = json.load(f)
            else:
                self.file_index = {}
        except Exception:
            self.file_index = {}
    
    def _save_index(self):
        """Save cache index to file"""
        if not self.cache_path:
            return
        
        try:
            with open(self.index_file, 'w') as f:
                json.dump(self.file_index, f)
        except Exception:
            pass
    
    def _get_cache_key(self, url):
        """Generate cache key from URL"""
        return hashlib.md5(url.encode('utf-8')).hexdigest()
    
    def _is_expired(self, timestamp):
        """Check if cache entry is expired"""
        return time.time() - timestamp > self.ttl
    
    def _cleanup_memory(self):
        """Remove expired entries from memory cache"""
        current_time = time.time()
        expired_keys = []
        
        for key, (data, timestamp) in self.memory_cache.items():
            if current_time - timestamp > self.ttl:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.memory_cache[key]
            if key in self.access_times:
                del self.access_times[key]
    
    def _cleanup_files(self):
        """Remove expired entries from file cache"""
        if not self.cache_path:
            return
        
        current_time = time.time()
        expired_keys = []
        
        for key, entry in self.file_index.items():
            if current_time - entry['timestamp'] > self.ttl:
                expired_keys.append(key)
        
        for key in expired_keys:
            # Remove file
            cache_file = self.cache_path / f"{key}.cache"
            try:
                cache_file.unlink()
            except FileNotFoundError:
                pass
            
            # Remove from index
            del self.file_index[key]
        
        if expired_keys:
            self._save_index()
    
    def _evict_lru(self):
        """Evict least recently used items if cache is full"""
        # Memory cache LRU eviction
        if len(self.memory_cache) >= self.max_size:
            # Sort by access time and remove oldest
            sorted_keys = sorted(self.access_times.items(), key=lambda x: x[1])
            num_to_remove = len(self.memory_cache) - self.max_size + 1
            
            for key, _ in sorted_keys[:num_to_remove]:
                if key in self.memory_cache:
                    del self.memory_cache[key]
                del self.access_times[key]
        
        # File cache LRU eviction
        if self.cache_path and len(self.file_index) >= self.max_size:
            sorted_entries = sorted(
                self.file_index.items(), 
                key=lambda x: x[1]['access_time']
            )
            num_to_remove = len(self.file_index) - self.max_size + 1
            
            for key, _ in sorted_entries[:num_to_remove]:
                cache_file = self.cache_path / f"{key}.cache"
                try:
                    cache_file.unlink()
                except FileNotFoundError:
                    pass
                del self.file_index[key]
            
            self._save_index()
    
    def get(self, url):
        """Get cached response for URL"""
        cache_key = self._get_cache_key(url)
        current_time = time.time()
        
        # Cleanup expired entries
        self._cleanup_memory()
        if self.cache_path:
            self._cleanup_files()
        
        # Check memory cache first
        if cache_key in self.memory_cache:
            data, timestamp = self.memory_cache[cache_key]
            if not self._is_expired(timestamp):
                self.access_times[cache_key] = current_time
                return data
            else:
                del self.memory_cache[cache_key]
                if cache_key in self.access_times:
                    del self.access_times[cache_key]
        
        # Check file cache
        if self.cache_path and cache_key in self.file_index:
            entry = self.file_index[cache_key]
            if not self._is_expired(entry['timestamp']):
                cache_file = self.cache_path / f"{cache_key}.cache"
                try:
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        data = f.read()
                    
                    # Update access time
                    entry['access_time'] = current_time
                    self._save_index()
                    
                    return data
                except Exception:
                    # File corrupted or missing, remove from index
                    del self.file_index[cache_key]
                    self._save_index()
        
        return None
    
    def set(self, url, data):
        """Cache response for URL"""
        if not data:
            return
        
        cache_key = self._get_cache_key(url)
        current_time = time.time()
        
        # Evict old entries if needed
        self._evict_lru()
        
        # Store in memory cache
        self.memory_cache[cache_key] = (data, current_time)
        self.access_times[cache_key] = current_time
        
        # Store in file cache if enabled
        if self.cache_path:
            try:
                cache_file = self.cache_path / f"{cache_key}.cache"
                with open(cache_file, 'w', encoding='utf-8') as f:
                    f.write(data)
                
                self.file_index[cache_key] = {
                    'url': url,
                    'timestamp': current_time,
                    'access_time': current_time
                }
                self._save_index()
            except Exception:
                pass
    
    def clear(self):
        """Clear all cached data"""
        # Clear memory cache
        self.memory_cache.clear()
        self.access_times.clear()
        
        # Clear file cache
        if self.cache_path:
            try:
                # Remove all cache files
                for cache_file in self.cache_path.glob("*.cache"):
                    cache_file.unlink()
                
                # Clear index
                self.file_index.clear()
                self._save_index()
            except Exception:
                pass
    
    def stats(self):
        """Get cache statistics"""
        memory_count = len(self.memory_cache)
        file_count = len(self.file_index) if self.cache_path else 0
        
        return {
            'memory_entries': memory_count,
            'file_entries': file_count,
            'total_entries': memory_count + file_count,
            'ttl': self.ttl,
            'max_size': self.max_size,
            'cache_dir': str(self.cache_path) if self.cache_path else None
        }