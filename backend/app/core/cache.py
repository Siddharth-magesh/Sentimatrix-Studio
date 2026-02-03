"""Caching utilities for API responses."""

import hashlib
import json
import time
from dataclasses import dataclass, field
from functools import wraps
from typing import Any, Callable, Optional

from fastapi import Request, Response


@dataclass
class CacheEntry:
    """Cache entry with value and metadata."""

    value: Any
    created_at: float
    expires_at: float
    hits: int = 0


class InMemoryCache:
    """Simple in-memory cache with TTL support."""

    def __init__(self, default_ttl: int = 300, max_size: int = 1000):
        self.default_ttl = default_ttl
        self.max_size = max_size
        self._cache: dict[str, CacheEntry] = {}

    def _generate_key(self, *args, **kwargs) -> str:
        """Generate a cache key from arguments."""
        key_data = json.dumps({"args": args, "kwargs": kwargs}, sort_keys=True, default=str)
        return hashlib.md5(key_data.encode()).hexdigest()

    def _cleanup_expired(self) -> None:
        """Remove expired entries."""
        now = time.time()
        expired = [k for k, v in self._cache.items() if v.expires_at < now]
        for key in expired:
            del self._cache[key]

    def _evict_if_needed(self) -> None:
        """Evict least recently used entries if cache is full."""
        if len(self._cache) >= self.max_size:
            # Remove oldest 10% of entries
            entries = sorted(self._cache.items(), key=lambda x: x[1].created_at)
            to_remove = len(entries) // 10 or 1
            for key, _ in entries[:to_remove]:
                del self._cache[key]

    def get(self, key: str) -> Any | None:
        """Get value from cache."""
        self._cleanup_expired()

        entry = self._cache.get(key)
        if entry is None:
            return None

        if entry.expires_at < time.time():
            del self._cache[key]
            return None

        entry.hits += 1
        return entry.value

    def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        """Set value in cache."""
        self._evict_if_needed()

        ttl = ttl or self.default_ttl
        now = time.time()

        self._cache[key] = CacheEntry(
            value=value,
            created_at=now,
            expires_at=now + ttl,
        )

    def delete(self, key: str) -> bool:
        """Delete entry from cache."""
        if key in self._cache:
            del self._cache[key]
            return True
        return False

    def clear(self) -> None:
        """Clear all cache entries."""
        self._cache.clear()

    def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate all keys matching a pattern."""
        import fnmatch

        keys_to_delete = [k for k in self._cache.keys() if fnmatch.fnmatch(k, pattern)]
        for key in keys_to_delete:
            del self._cache[key]
        return len(keys_to_delete)

    def stats(self) -> dict:
        """Get cache statistics."""
        self._cleanup_expired()
        total_hits = sum(e.hits for e in self._cache.values())
        return {
            "size": len(self._cache),
            "max_size": self.max_size,
            "total_hits": total_hits,
            "default_ttl": self.default_ttl,
        }


# Global cache instance
_cache: InMemoryCache | None = None


def get_cache() -> InMemoryCache:
    """Get or create the global cache instance."""
    global _cache
    if _cache is None:
        _cache = InMemoryCache()
    return _cache


def cache_response(
    ttl: int = 300,
    key_builder: Callable[[Request], str] | None = None,
    vary_by_user: bool = True,
):
    """
    Decorator to cache API responses.

    Args:
        ttl: Time to live in seconds
        key_builder: Custom function to build cache key
        vary_by_user: Include user ID in cache key

    Usage:
        @router.get("/expensive")
        @cache_response(ttl=600)
        async def expensive_endpoint():
            ...
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Find request in args/kwargs
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            if not request:
                request = kwargs.get("request")

            if not request:
                return await func(*args, **kwargs)

            # Build cache key
            if key_builder:
                cache_key = key_builder(request)
            else:
                cache_key = f"{request.method}:{request.url.path}"
                if request.query_params:
                    cache_key += f"?{request.query_params}"

            # Add user ID if varying by user
            if vary_by_user:
                user_id = getattr(request.state, "user_id", "anonymous")
                cache_key = f"{user_id}:{cache_key}"

            # Check cache
            cache = get_cache()
            cached = cache.get(cache_key)
            if cached is not None:
                return cached

            # Execute function
            result = await func(*args, **kwargs)

            # Cache result
            cache.set(cache_key, result, ttl)

            return result

        return wrapper

    return decorator


def invalidate_cache(*patterns: str):
    """
    Decorator to invalidate cache after a function call.

    Args:
        patterns: Cache key patterns to invalidate

    Usage:
        @router.post("/items")
        @invalidate_cache("GET:/items*")
        async def create_item():
            ...
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            result = await func(*args, **kwargs)

            cache = get_cache()
            for pattern in patterns:
                cache.invalidate_pattern(pattern)

            return result

        return wrapper

    return decorator


class CacheKeyBuilder:
    """Helper class to build consistent cache keys."""

    @staticmethod
    def for_user(user_id: str, resource: str, resource_id: str | None = None) -> str:
        """Build cache key for user-specific resource."""
        if resource_id:
            return f"user:{user_id}:{resource}:{resource_id}"
        return f"user:{user_id}:{resource}"

    @staticmethod
    def for_project(project_id: str, resource: str) -> str:
        """Build cache key for project resource."""
        return f"project:{project_id}:{resource}"

    @staticmethod
    def for_list(
        resource: str,
        user_id: str | None = None,
        page: int = 1,
        filters: dict | None = None,
    ) -> str:
        """Build cache key for list endpoint."""
        parts = [resource]
        if user_id:
            parts.append(f"user:{user_id}")
        parts.append(f"page:{page}")
        if filters:
            filter_str = json.dumps(filters, sort_keys=True)
            parts.append(f"filters:{hashlib.md5(filter_str.encode()).hexdigest()[:8]}")
        return ":".join(parts)


# Cache tags for easier invalidation
class CacheTags:
    """Predefined cache tags for different resources."""

    PROJECTS = "projects:*"
    TARGETS = "targets:*"
    RESULTS = "results:*"
    SCHEDULES = "schedules:*"
    WEBHOOKS = "webhooks:*"
    DASHBOARD = "dashboard:*"

    @staticmethod
    def for_user(user_id: str) -> str:
        return f"user:{user_id}:*"

    @staticmethod
    def for_project(project_id: str) -> str:
        return f"project:{project_id}:*"
