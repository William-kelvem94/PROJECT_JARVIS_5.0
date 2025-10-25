"""
API Dependencies - Authentication, database sessions, etc.
"""
from typing import Optional, Generator
from fastapi import Depends, HTTPException, status, WebSocket
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import security_manager
from app.core.redis_client import RedisCache
from app.core.exceptions import AuthenticationException
from app.models.user import User
from sqlalchemy import select

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Get current authenticated user
    
    Args:
        credentials: HTTP Bearer token
        db: Database session
    
    Returns:
        Current user
    
    Raises:
        HTTPException: If authentication fails
    """
    try:
        # Decode JWT token
        payload = security_manager.decode_token(credentials.credentials)
        user_id: str = payload.get("sub")
        
        if user_id is None:
            raise AuthenticationException("Invalid authentication credentials")
        
        # Get user from database
        result = await db.execute(select(User).filter(User.id == user_id))
        user = result.scalar_one_or_none()
        
        if user is None:
            raise AuthenticationException("User not found")
        
        if not user.is_active:
            raise AuthenticationException("User is inactive")
        
        return user
        
    except AuthenticationException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get current active user
    
    Args:
        current_user: Current user
    
    Returns:
        Current active user
    
    Raises:
        HTTPException: If user is inactive
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user


async def get_current_superuser(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get current superuser
    
    Args:
        current_user: Current user
    
    Returns:
        Current superuser
    
    Raises:
        HTTPException: If user is not a superuser
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough privileges"
        )
    return current_user


def get_redis_cache() -> RedisCache:
    """
    Get Redis cache instance
    
    Returns:
        Redis cache
    """
    return RedisCache()


async def verify_websocket_token(websocket: WebSocket) -> Optional[User]:
    """
    Verify WebSocket authentication token
    
    Args:
        websocket: WebSocket connection
    
    Returns:
        Authenticated user or None
    """
    try:
        # Get token from query params or headers
        token = websocket.query_params.get("token")
        
        if not token:
            return None
        
        # Decode token
        payload = security_manager.decode_token(token)
        user_id: str = payload.get("sub")
        
        if not user_id:
            return None
        
        # In a real implementation, you would query the database here
        # For now, we'll create a mock user object
        # TODO: Query database for user
        
        return None
        
    except Exception:
        return None

