"""
Performance Enhancements - Advanced Caching, Monitoring, and Optimization
Implementing cutting-edge performance features for enterprise-grade reliability
"""

import asyncio
import time
import json
import redis
import psutil
import logging
import os
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict, deque
import hashlib
import pickle
from functools import wraps

logger = logging.getLogger(__name__)

class AdvancedCacheManager:
    """Advanced caching system with multi-level caching and intelligent invalidation"""
    
    def __init__(self):
        self.redis_client = None
        self.memory_cache = {}
        self.cache_stats = defaultdict(int)
        self.cache_policies = {
            "user_data": {"ttl": 3600, "strategy": "lru"},
            "workflow_data": {"ttl": 1800, "strategy": "lfu"},
            "integration_data": {"ttl": 7200, "strategy": "ttl"},
            "ai_responses": {"ttl": 86400, "strategy": "lru"},
            "static_data": {"ttl": 604800, "strategy": "ttl"}
        }
        
        try:
            self.redis_client = redis.Redis(
                host=os.getenv("REDIS_HOST", "localhost"),
                port=int(os.getenv("REDIS_PORT", 6379)),
                db=0,
                decode_responses=True
            )
            self.redis_client.ping()
            logger.info("Redis cache initialized successfully")
        except Exception as e:
            logger.warning(f"Redis not available, using memory cache only: {e}")
    
    def _generate_cache_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate consistent cache key"""
        key_data = f"{prefix}:{':'.join(str(arg) for arg in args)}"
        if kwargs:
            sorted_kwargs = sorted(kwargs.items())
            key_data += f":{':'.join(f'{k}={v}' for k, v in sorted_kwargs)}"
        return hashlib.md5(key_data.encode()).hexdigest()[:16]
    
    async def get(self, key: str, category: str = "default") -> Optional[Any]:
        """Get item from cache with fallback"""
        self.cache_stats[f"{category}_requests"] += 1
        
        try:
            # Try Redis first
            if self.redis_client:
                result = await asyncio.to_thread(self.redis_client.get, key)
                if result:
                    self.cache_stats[f"{category}_redis_hits"] += 1
                    return json.loads(result)
            
            # Fall back to memory cache
            if key in self.memory_cache:
                item = self.memory_cache[key]
                if item["expires"] > time.time():
                    self.cache_stats[f"{category}_memory_hits"] += 1
                    return item["data"]
                else:
                    del self.memory_cache[key]
            
            self.cache_stats[f"{category}_misses"] += 1
            return None
            
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None
    
    async def set(self, key: str, value: Any, category: str = "default", 
                 ttl: Optional[int] = None) -> bool:
        """Set item in cache with automatic TTL"""
        try:
            policy = self.cache_policies.get(category, {"ttl": 3600})
            ttl = ttl or policy["ttl"]
            
            # Store in Redis
            if self.redis_client:
                await asyncio.to_thread(
                    self.redis_client.setex, 
                    key, 
                    ttl, 
                    json.dumps(value, default=str)
                )
            
            # Store in memory cache
            self.memory_cache[key] = {
                "data": value,
                "expires": time.time() + ttl,
                "created": time.time()
            }
            
            # Cleanup old memory cache entries
            if len(self.memory_cache) > 10000:
                await self._cleanup_memory_cache()
            
            self.cache_stats[f"{category}_sets"] += 1
            return True
            
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False
    
    async def invalidate(self, pattern: str = None, category: str = None):
        """Invalidate cache entries"""
        try:
            if pattern and self.redis_client:
                keys = await asyncio.to_thread(self.redis_client.keys, pattern)
                if keys:
                    await asyncio.to_thread(self.redis_client.delete, *keys)
            
            # Clear memory cache
            if category:
                keys_to_remove = [k for k in self.memory_cache.keys() if category in k]
                for key in keys_to_remove:
                    del self.memory_cache[key]
            
        except Exception as e:
            logger.error(f"Cache invalidation error: {e}")
    
    async def _cleanup_memory_cache(self):
        """Clean up expired entries from memory cache"""
        current_time = time.time()
        expired_keys = [
            key for key, item in self.memory_cache.items()
            if item["expires"] < current_time
        ]
        for key in expired_keys:
            del self.memory_cache[key]

class PerformanceMonitor:
    """Real-time performance monitoring and alerting system"""
    
    def __init__(self):
        self.metrics = defaultdict(deque)
        self.alerts = []
        self.thresholds = {
            "cpu_usage": 80,
            "memory_usage": 85,
            "response_time": 5000,  # ms
            "error_rate": 5,  # percentage
            "active_connections": 1000
        }
        self.monitoring_active = True
        
    async def start_monitoring(self):
        """Start background monitoring tasks"""
        asyncio.create_task(self._monitor_system_metrics())
        asyncio.create_task(self._monitor_application_metrics())
        logger.info("Performance monitoring started")
    
    async def _monitor_system_metrics(self):
        """Monitor system-level metrics"""
        while self.monitoring_active:
            try:
                # CPU usage
                cpu_percent = psutil.cpu_percent(interval=1)
                self._record_metric("cpu_usage", cpu_percent)
                
                # Memory usage
                memory = psutil.virtual_memory()
                memory_percent = memory.percent
                self._record_metric("memory_usage", memory_percent)
                
                # Disk usage
                disk = psutil.disk_usage('/')
                disk_percent = (disk.used / disk.total) * 100
                self._record_metric("disk_usage", disk_percent)
                
                # Network I/O
                net_io = psutil.net_io_counters()
                self._record_metric("network_bytes_sent", net_io.bytes_sent)
                self._record_metric("network_bytes_recv", net_io.bytes_recv)
                
                # Check thresholds
                await self._check_thresholds()
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"System monitoring error: {e}")
                await asyncio.sleep(60)
    
    async def _monitor_application_metrics(self):
        """Monitor application-specific metrics"""
        while self.monitoring_active:
            try:
                # Database connections
                # Note: This would be implemented with actual DB connection pool
                self._record_metric("db_connections", 10)  # Placeholder
                
                # Cache hit rates
                cache_stats = cache_manager.cache_stats
                if cache_stats:
                    total_requests = sum(v for k, v in cache_stats.items() if k.endswith('_requests'))
                    total_hits = sum(v for k, v in cache_stats.items() if k.endswith('_hits'))
                    hit_rate = (total_hits / total_requests * 100) if total_requests > 0 else 0
                    self._record_metric("cache_hit_rate", hit_rate)
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Application monitoring error: {e}")
                await asyncio.sleep(60)
    
    def _record_metric(self, metric_name: str, value: float):
        """Record a metric value with timestamp"""
        timestamp = datetime.utcnow()
        self.metrics[metric_name].append((timestamp, value))
        
        # Keep only last 1000 data points
        if len(self.metrics[metric_name]) > 1000:
            self.metrics[metric_name].popleft()
    
    async def _check_thresholds(self):
        """Check if any metrics exceed thresholds"""
        current_time = datetime.utcnow()
        
        for metric, threshold in self.thresholds.items():
            if metric in self.metrics and self.metrics[metric]:
                latest_value = self.metrics[metric][-1][1]
                
                if latest_value > threshold:
                    alert = {
                        "metric": metric,
                        "value": latest_value,
                        "threshold": threshold,
                        "timestamp": current_time,
                        "severity": "high" if latest_value > threshold * 1.2 else "medium"
                    }
                    
                    # Avoid duplicate alerts within 5 minutes
                    recent_alerts = [
                        a for a in self.alerts 
                        if a["metric"] == metric and 
                        (current_time - a["timestamp"]).seconds < 300
                    ]
                    
                    if not recent_alerts:
                        self.alerts.append(alert)
                        logger.warning(f"Performance alert: {metric} = {latest_value} > {threshold}")
    
    def get_metrics(self, metric_name: str = None, 
                   hours_back: int = 24) -> Dict[str, Any]:
        """Get metrics data for dashboard"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours_back)
        
        if metric_name:
            metrics = {metric_name: self.metrics.get(metric_name, deque())}
        else:
            metrics = dict(self.metrics)
        
        result = {}
        for name, data in metrics.items():
            filtered_data = [
                (ts, value) for ts, value in data 
                if ts > cutoff_time
            ]
            
            if filtered_data:
                values = [value for _, value in filtered_data]
                result[name] = {
                    "current": values[-1],
                    "average": sum(values) / len(values),
                    "min": min(values),
                    "max": max(values),
                    "data_points": len(values),
                    "trend": "increasing" if len(values) > 1 and values[-1] > values[0] else "stable"
                }
        
        return result
    
    def get_alerts(self, severity: str = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent alerts"""
        alerts = self.alerts[-limit:] if not severity else [
            alert for alert in self.alerts[-limit:] 
            if alert["severity"] == severity
        ]
        
        return sorted(alerts, key=lambda x: x["timestamp"], reverse=True)

class RealTimeCollaboration:
    """Real-time collaboration features for workflow editing"""
    
    def __init__(self):
        self.active_sessions = {}  # workflow_id -> {user_id -> session_data}
        self.collaboration_events = deque(maxlen=1000)
        
    async def join_session(self, workflow_id: str, user_id: str, 
                          user_name: str) -> Dict[str, Any]:
        """Join a collaborative editing session"""
        if workflow_id not in self.active_sessions:
            self.active_sessions[workflow_id] = {}
        
        session_data = {
            "user_id": user_id,
            "user_name": user_name,
            "joined_at": datetime.utcnow(),
            "last_activity": datetime.utcnow(),
            "cursor_position": None,
            "selected_nodes": []
        }
        
        self.active_sessions[workflow_id][user_id] = session_data
        
        # Broadcast join event
        event = {
            "type": "user_joined",
            "workflow_id": workflow_id,
            "user_id": user_id,
            "user_name": user_name,
            "timestamp": datetime.utcnow()
        }
        self.collaboration_events.append(event)
        
        return {
            "session_id": f"{workflow_id}:{user_id}",
            "active_users": list(self.active_sessions[workflow_id].values()),
            "event": event
        }
    
    async def leave_session(self, workflow_id: str, user_id: str):
        """Leave a collaborative editing session"""
        if (workflow_id in self.active_sessions and 
            user_id in self.active_sessions[workflow_id]):
            
            user_data = self.active_sessions[workflow_id][user_id]
            del self.active_sessions[workflow_id][user_id]
            
            # Clean up empty sessions
            if not self.active_sessions[workflow_id]:
                del self.active_sessions[workflow_id]
            
            # Broadcast leave event
            event = {
                "type": "user_left",
                "workflow_id": workflow_id,
                "user_id": user_id,
                "user_name": user_data["user_name"],
                "timestamp": datetime.utcnow()
            }
            self.collaboration_events.append(event)
            
            return event
    
    async def update_cursor(self, workflow_id: str, user_id: str, 
                           cursor_position: Dict[str, Any]):
        """Update user's cursor position"""
        if (workflow_id in self.active_sessions and 
            user_id in self.active_sessions[workflow_id]):
            
            self.active_sessions[workflow_id][user_id]["cursor_position"] = cursor_position
            self.active_sessions[workflow_id][user_id]["last_activity"] = datetime.utcnow()
            
            return {
                "type": "cursor_update",
                "workflow_id": workflow_id,
                "user_id": user_id,
                "cursor_position": cursor_position
            }
    
    async def broadcast_change(self, workflow_id: str, user_id: str, 
                             change_data: Dict[str, Any]):
        """Broadcast workflow changes to other users"""
        if workflow_id in self.active_sessions:
            event = {
                "type": "workflow_change",
                "workflow_id": workflow_id,
                "user_id": user_id,
                "change_data": change_data,
                "timestamp": datetime.utcnow()
            }
            
            self.collaboration_events.append(event)
            return event
    
    def get_active_sessions(self, workflow_id: str = None) -> Dict[str, Any]:
        """Get active collaboration sessions"""
        if workflow_id:
            return {
                workflow_id: self.active_sessions.get(workflow_id, {})
            }
        return dict(self.active_sessions)
    
    def get_recent_events(self, workflow_id: str = None, 
                         limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent collaboration events"""
        events = list(self.collaboration_events)[-limit:]
        
        if workflow_id:
            events = [e for e in events if e.get("workflow_id") == workflow_id]
        
        return sorted(events, key=lambda x: x["timestamp"], reverse=True)

def performance_cache(category: str = "default", ttl: int = None):
    """Decorator for caching function results"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = cache_manager._generate_cache_key(
                f"func:{func.__name__}", *args, **kwargs
            )
            
            # Try to get from cache
            cached_result = await cache_manager.get(cache_key, category)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            await cache_manager.set(cache_key, result, category, ttl)
            
            return result
        return wrapper
    return decorator

# Initialize global instances
cache_manager = AdvancedCacheManager()
performance_monitor = PerformanceMonitor()
collaboration_manager = RealTimeCollaboration()

# Start monitoring when module is imported
asyncio.create_task(performance_monitor.start_monitoring())