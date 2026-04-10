import pytest
from fastapi import Depends
from app.api.dependencies import require_auth
from app.core.auth import verify_api_key


def test_require_auth_dependency():
    """Test that require_auth is properly configured"""
    assert require_auth is not None
    # Check that it's a Depends object by verifying its attributes
    assert hasattr(require_auth, "dependency")
    assert require_auth.dependency == verify_api_key
