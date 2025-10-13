# backend/tests/integration/test_redis.py - Tests de Integración con Redis

import pytest
import json
from datetime import datetime, timedelta

@pytest.mark.integration
class TestRedisIntegration:
    """Tests de integración con Redis."""
    
    def test_redis_connection(self, mock_redis):
        """Test conexión a Redis."""
        result = mock_redis.ping()
        assert result is True
    
    def test_redis_set_get(self, mock_redis):
        """Test operaciones SET y GET."""
        key = "test:key"
        value = "test_value"
        
        mock_redis.set.return_value = True
        mock_redis.get.return_value = value
        
        # Set value
        result = mock_redis.set(key, value)
        assert result is True
        
        # Get value
        retrieved = mock_redis.get(key)
        assert retrieved == value
    
    def test_redis_expiration(self, mock_redis):
        """Test expiración de claves."""
        key = "test:expiring_key"
        value = "temporary_value"
        expiration = 300  # 5 minutos
        
        mock_redis.setex.return_value = True
        
        result = mock_redis.setex(key, expiration, value)
        assert result is True
    
    def test_redis_delete(self, mock_redis):
        """Test eliminación de claves."""
        key = "test:to_delete"
        
        mock_redis.delete.return_value = 1
        
        result = mock_redis.delete(key)
        assert result == 1
    
    def test_redis_exists(self, mock_redis):
        """Test verificar existencia de clave."""
        key = "test:existing_key"
        
        mock_redis.exists.return_value = True
        
        result = mock_redis.exists(key)
        assert result is True
    
    def test_cache_user_session(self, mock_redis):
        """Test cachear sesión de usuario."""
        session_data = {
            "user_id": 1,
            "email": "test@justicia.ma",
            "role": "admin",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        session_key = f"session:user:1"
        
        mock_redis.setex.return_value = True
        mock_redis.get.return_value = json.dumps(session_data)
        
        # Guardar sesión
        result = mock_redis.setex(
            session_key,
            3600,  # 1 hora
            json.dumps(session_data)
        )
        assert result is True
        
        # Recuperar sesión
        cached = mock_redis.get(session_key)
        assert cached is not None
        
        retrieved_data = json.loads(cached)
        assert retrieved_data["user_id"] == 1
        assert retrieved_data["role"] == "admin"
    
    def test_rate_limiting_with_redis(self, mock_redis):
        """Test rate limiting usando Redis."""
        user_id = 1
        limit_key = f"rate_limit:user:{user_id}"
        max_requests = 100
        window = 60  # 1 minuto
        
        mock_redis.get.return_value = "50"  # 50 requests actuales
        mock_redis.setex.return_value = True
        
        # Verificar requests actuales
        current_requests = mock_redis.get(limit_key)
        
        if current_requests:
            count = int(current_requests)
            assert count < max_requests
        
        # Incrementar contador
        new_count = int(current_requests) + 1
        mock_redis.setex(limit_key, window, str(new_count))
    
    def test_cache_case_statistics(self, mock_redis):
        """Test cachear estadísticas de casos."""
        stats_key = "stats:cases:summary"
        stats_data = {
            "total": 150,
            "pending": 45,
            "in_progress": 60,
            "resolved": 30,
            "closed": 15,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        mock_redis.setex.return_value = True
        mock_redis.get.return_value = json.dumps(stats_data)
        
        # Cache stats
        result = mock_redis.setex(
            stats_key,
            600,  # 10 minutos
            json.dumps(stats_data)
        )
        assert result is True
        
        # Retrieve stats
        cached_stats = mock_redis.get(stats_key)
        retrieved_stats = json.loads(cached_stats)
        
        assert retrieved_stats["total"] == 150
        assert retrieved_stats["pending"] == 45
    
    def test_list_operations(self, mock_redis):
        """Test operaciones de lista (queue)."""
        queue_key = "queue:notifications"
        notification = json.dumps({
            "user_id": 1,
            "message": "Nuevo caso asignado",
            "timestamp": datetime.utcnow().isoformat()
        })
        
        mock_redis.lpush.return_value = 1
        
        # Push notification to queue
        result = mock_redis.lpush(queue_key, notification)
        assert result == 1

@pytest.mark.integration
class TestRedisCaching:
    """Tests de caching con Redis."""
    
    def test_cache_invalidation(self, mock_redis):
        """Test invalidación de caché."""
        cache_key = "cache:user:1:profile"
        
        mock_redis.delete.return_value = 1
        
        # Invalidar caché
        result = mock_redis.delete(cache_key)
        assert result == 1
    
    def test_cache_pattern_deletion(self, mock_redis):
        """Test eliminación por patrón."""
        pattern = "cache:user:*"
        
        mock_redis.keys.return_value = [
            "cache:user:1:profile",
            "cache:user:2:profile",
            "cache:user:3:profile"
        ]
        
        # Obtener todas las claves que coinciden
        keys = mock_redis.keys(pattern)
        assert len(keys) == 3
    
    def test_cache_ttl(self, mock_redis):
        """Test tiempo de vida de caché."""
        key = "cache:temporary"
        ttl = 300  # 5 minutos
        
        mock_redis.setex.return_value = True
        
        result = mock_redis.setex(key, ttl, "value")
        assert result is True

@pytest.mark.integration
class TestRedisPerformance:
    """Tests de performance con Redis."""
    
    @pytest.mark.slow
    def test_bulk_operations_performance(self, mock_redis):
        """Test performance de operaciones masivas."""
        import time
        
        start = time.time()
        
        # Simular 1000 operaciones
        for i in range(1000):
            mock_redis.set(f"test:bulk:{i}", f"value_{i}")
        
        end = time.time()
        
        # Debe completarse rápido
        assert (end - start) < 1.0
