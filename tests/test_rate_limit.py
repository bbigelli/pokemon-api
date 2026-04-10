from app.core.rate_limit import limiter
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.core.config import settings


def test_rate_limit_configured():
    """Test rate limiter is configured"""
    assert limiter is not None
    assert isinstance(limiter, Limiter)


def test_rate_limit_key_func():
    """Test rate limit key function is configured"""
    assert limiter._key_func == get_remote_address


def test_rate_limit_default_limits_exists():
    """Test default limits exist"""
    assert hasattr(limiter, "_default_limits")
    assert limiter._default_limits is not None
    assert len(limiter._default_limits) > 0


def test_rate_limit_from_settings():
    """Test rate limit is loaded from settings"""
    assert settings.RATE_LIMIT == "100/minute"
    assert settings.RATE_LIMIT is not None


def test_limiter_has_limit_method():
    """Test limiter has limit method"""
    assert hasattr(limiter, "limit")
    assert callable(limiter.limit)


def test_limiter_has_shared_limit_method():
    """Test limiter has shared_limit method"""
    assert hasattr(limiter, "shared_limit")
    assert callable(limiter.shared_limit)
