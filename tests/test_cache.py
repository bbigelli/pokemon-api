import pytest
from unittest.mock import Mock, patch, MagicMock
from app.core.cache import CacheService


class TestCacheService:
    """Test suite for CacheService"""

    def test_init_redis_success(self):
        """Test successful Redis connection"""
        with patch("redis.Redis") as mock_redis:
            mock_redis_instance = Mock()
            mock_redis_instance.ping = Mock(return_value=True)
            mock_redis.return_value = mock_redis_instance

            cache = CacheService()
            assert cache.redis_client is not None
            mock_redis_instance.ping.assert_called_once()

    def test_init_redis_failure(self):
        """Test Redis connection failure"""
        with patch("redis.Redis") as mock_redis:
            mock_redis.side_effect = Exception("Connection failed")

            cache = CacheService()
            assert cache.redis_client is None

    def test_get_without_redis(self):
        """Test get when Redis is not available"""
        cache = CacheService()
        cache.redis_client = None

        result = cache.get("test_key")
        assert result is None

    def test_get_success(self):
        """Test successful get from cache"""
        with patch("redis.Redis") as mock_redis:
            mock_redis_instance = Mock()
            mock_redis_instance.get.return_value = '{"data": "test"}'
            mock_redis.return_value = mock_redis_instance

            cache = CacheService()
            result = cache.get("test_key")

            assert result == {"data": "test"}
            mock_redis_instance.get.assert_called_once_with("test_key")

    def test_get_with_exception(self):
        """Test get when Redis raises exception"""
        with patch("redis.Redis") as mock_redis:
            mock_redis_instance = Mock()
            mock_redis_instance.get.side_effect = Exception("Redis error")
            mock_redis.return_value = mock_redis_instance

            cache = CacheService()
            result = cache.get("test_key")

            assert result is None

    def test_set_without_redis(self):
        """Test set when Redis is not available"""
        cache = CacheService()
        cache.redis_client = None

        result = cache.set("test_key", {"data": "test"})
        assert result is False

    def test_set_success(self):
        """Test successful set to cache"""
        with patch("redis.Redis") as mock_redis:
            mock_redis_instance = Mock()
            mock_redis_instance.setex = Mock(return_value=True)
            mock_redis.return_value = mock_redis_instance

            cache = CacheService()
            result = cache.set("test_key", {"data": "test"}, ttl=3600)

            assert result is True
            mock_redis_instance.setex.assert_called_once_with(
                "test_key", 3600, '{"data": "test"}'
            )

    def test_set_with_exception(self):
        """Test set when Redis raises exception"""
        with patch("redis.Redis") as mock_redis:
            mock_redis_instance = Mock()
            mock_redis_instance.setex.side_effect = Exception("Redis error")
            mock_redis.return_value = mock_redis_instance

            cache = CacheService()
            result = cache.set("test_key", {"data": "test"})

            assert result is False

    def test_delete_without_redis(self):
        """Test delete when Redis is not available"""
        cache = CacheService()
        cache.redis_client = None

        result = cache.delete("test_key")
        assert result is False

    def test_delete_success(self):
        """Test successful delete from cache"""
        with patch("redis.Redis") as mock_redis:
            mock_redis_instance = Mock()
            mock_redis_instance.delete = Mock(return_value=1)
            mock_redis.return_value = mock_redis_instance

            cache = CacheService()
            result = cache.delete("test_key")

            assert result is True
            mock_redis_instance.delete.assert_called_once_with("test_key")

    def test_delete_with_exception(self):
        """Test delete when Redis raises exception"""
        with patch("redis.Redis") as mock_redis:
            mock_redis_instance = Mock()
            mock_redis_instance.delete.side_effect = Exception("Redis error")
            mock_redis.return_value = mock_redis_instance

            cache = CacheService()
            result = cache.delete("test_key")

            assert result is False

    def test_clear_without_redis(self):
        """Test clear when Redis is not available"""
        cache = CacheService()
        cache.redis_client = None

        result = cache.clear()
        assert result is False

    def test_clear_success(self):
        """Test successful clear cache"""
        with patch("redis.Redis") as mock_redis:
            mock_redis_instance = Mock()
            mock_redis_instance.flushdb = Mock(return_value=True)
            mock_redis.return_value = mock_redis_instance

            cache = CacheService()
            result = cache.clear()

            assert result is True
            mock_redis_instance.flushdb.assert_called_once()

    def test_clear_with_exception(self):
        """Test clear when Redis raises exception"""
        with patch("redis.Redis") as mock_redis:
            mock_redis_instance = Mock()
            mock_redis_instance.flushdb.side_effect = Exception("Redis error")
            mock_redis.return_value = mock_redis_instance

            cache = CacheService()
            result = cache.clear()

            assert result is False
