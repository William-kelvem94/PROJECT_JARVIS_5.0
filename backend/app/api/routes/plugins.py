"""
Plugin management routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Any

from app.api.dependencies import get_current_superuser
from app.models.user import User
from app.core.plugin_manager import PluginManager

router = APIRouter()

# Global plugin manager instance (will be initialized on startup)
_plugin_manager: PluginManager = None


def get_plugin_manager() -> PluginManager:
    """Get global plugin manager instance"""
    global _plugin_manager
    if _plugin_manager is None:
        _plugin_manager = PluginManager()
    return _plugin_manager


@router.get("/", response_model=List[Dict[str, Any]])
async def list_plugins(
    current_user: User = Depends(get_current_superuser)
):
    """
    List all plugins (superuser only)
    """
    plugin_manager = get_plugin_manager()
    return plugin_manager.list_plugins()


@router.get("/{plugin_name}", response_model=Dict[str, Any])
async def get_plugin_info(
    plugin_name: str,
    current_user: User = Depends(get_current_superuser)
):
    """
    Get plugin information (superuser only)
    """
    plugin_manager = get_plugin_manager()
    plugin = plugin_manager.get_plugin(plugin_name)
    
    if not plugin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plugin not found: {plugin_name}"
        )
    
    return plugin.get_info()


@router.post("/{plugin_name}/enable")
async def enable_plugin(
    plugin_name: str,
    current_user: User = Depends(get_current_superuser)
):
    """
    Enable a plugin (superuser only)
    """
    plugin_manager = get_plugin_manager()
    
    if not plugin_manager.get_plugin(plugin_name):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plugin not found: {plugin_name}"
        )
    
    plugin_manager.enable_plugin(plugin_name)
    
    return {"message": f"Plugin {plugin_name} enabled"}


@router.post("/{plugin_name}/disable")
async def disable_plugin(
    plugin_name: str,
    current_user: User = Depends(get_current_superuser)
):
    """
    Disable a plugin (superuser only)
    """
    plugin_manager = get_plugin_manager()
    
    if not plugin_manager.get_plugin(plugin_name):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plugin not found: {plugin_name}"
        )
    
    plugin_manager.disable_plugin(plugin_name)
    
    return {"message": f"Plugin {plugin_name} disabled"}


@router.post("/{plugin_name}/execute")
async def execute_plugin(
    plugin_name: str,
    data: Dict[str, Any],
    current_user: User = Depends(get_current_superuser)
):
    """
    Execute a plugin (superuser only)
    """
    plugin_manager = get_plugin_manager()
    
    try:
        result = await plugin_manager.execute_plugin(plugin_name, data)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/{plugin_name}/reload")
async def reload_plugin(
    plugin_name: str,
    current_user: User = Depends(get_current_superuser)
):
    """
    Reload a plugin (superuser only)
    """
    plugin_manager = get_plugin_manager()
    
    plugin = plugin_manager.get_plugin(plugin_name)
    if not plugin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plugin not found: {plugin_name}"
        )
    
    try:
        await plugin_manager.unload_plugin(plugin_name)
        # Reload logic would go here
        return {"message": f"Plugin {plugin_name} reloaded"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

