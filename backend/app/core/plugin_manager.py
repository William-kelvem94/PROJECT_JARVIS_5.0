"""
Advanced Plugin Management System with Hot-Reload
"""
import importlib
import importlib.util
import inspect
import os
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Any, Optional, Type
import asyncio
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import logging

from app.core.config import settings
from app.core.exceptions import PluginException
from app.core.logger import LoggerMixin

logger = logging.getLogger(__name__)


class PluginBase(ABC, LoggerMixin):
    """
    Base class for all plugins
    """
    
    # Plugin metadata
    name: str = "base_plugin"
    version: str = "1.0.0"
    description: str = "Base plugin"
    author: str = "Jarvis Team"
    enabled: bool = True
    
    def __init__(self):
        self.initialized = False
        self._config: Dict[str, Any] = {}
    
    @abstractmethod
    async def initialize(self) -> bool:
        """
        Initialize the plugin
        
        Returns:
            Success status
        """
        pass
    
    @abstractmethod
    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process data through the plugin
        
        Args:
            data: Input data
        
        Returns:
            Processed data
        """
        pass
    
    @abstractmethod
    async def shutdown(self):
        """
        Cleanup and shutdown the plugin
        """
        pass
    
    def configure(self, config: Dict[str, Any]):
        """
        Configure the plugin
        
        Args:
            config: Configuration dictionary
        """
        self._config = config
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value
        
        Args:
            key: Configuration key
            default: Default value
        
        Returns:
            Configuration value
        """
        return self._config.get(key, default)
    
    def get_info(self) -> Dict[str, Any]:
        """
        Get plugin information
        
        Returns:
            Plugin metadata
        """
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "author": self.author,
            "enabled": self.enabled,
            "initialized": self.initialized
        }


class PluginFileHandler(FileSystemEventHandler):
    """
    File system event handler for plugin hot-reload
    """
    
    def __init__(self, plugin_manager: 'PluginManager'):
        self.plugin_manager = plugin_manager
        self.debounce_timer: Optional[asyncio.Task] = None
    
    def on_modified(self, event):
        if event.is_directory or not event.src_path.endswith('.py'):
            return
        
        logger.info(f"Plugin file modified: {event.src_path}")
        
        # Create task in a thread-safe way
        try:
            loop = asyncio.get_event_loop()
            if self.debounce_timer:
                self.debounce_timer.cancel()
            self.debounce_timer = loop.create_task(
                self._debounced_reload(event.src_path)
            )
        except RuntimeError:
            # No event loop in current thread
            pass
    
    async def _debounced_reload(self, file_path: str):
        await asyncio.sleep(1)  # Wait for file writes to complete
        await self.plugin_manager.reload_plugin_from_file(file_path)


class PluginManager(LoggerMixin):
    """
    Advanced plugin manager with dynamic loading and hot-reload
    """
    
    def __init__(self):
        self.plugins: Dict[str, PluginBase] = {}
        self.plugin_classes: Dict[str, Type[PluginBase]] = {}
        self.plugins_dir = Path(settings.PLUGINS_DIR)
        self.observer: Optional[Observer] = None
        
        self.logger.info(f"Plugin manager initialized. Plugins dir: {self.plugins_dir}")
    
    async def load_all_plugins(self):
        """
        Load all plugins from the plugins directory
        """
        if not self.plugins_dir.exists():
            self.logger.warning(f"Plugins directory not found: {self.plugins_dir}")
            self.plugins_dir.mkdir(parents=True, exist_ok=True)
            return
        
        # Find all Python files in plugins directory
        plugin_files = list(self.plugins_dir.glob("*_plugin.py"))
        
        self.logger.info(f"Found {len(plugin_files)} plugin files")
        
        for plugin_file in plugin_files:
            try:
                await self.load_plugin_from_file(plugin_file)
            except Exception as e:
                self.logger.error(f"Failed to load plugin {plugin_file}: {str(e)}")
        
        # Start hot-reload watcher if enabled
        if settings.ENABLE_PLUGIN_HOT_RELOAD:
            self._start_watcher()
        
        self.logger.info(f"Loaded {len(self.plugins)} plugins successfully")
    
    async def load_plugin_from_file(self, file_path: Path):
        """
        Load a plugin from a file
        
        Args:
            file_path: Path to plugin file
        """
        module_name = file_path.stem
        
        try:
            # Import the module
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            if spec is None or spec.loader is None:
                raise PluginException(
                    f"Cannot load spec for {file_path}",
                    plugin_name=module_name
                )
            
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Find plugin classes
            for name, obj in inspect.getmembers(module):
                if (inspect.isclass(obj) and 
                    issubclass(obj, PluginBase) and 
                    obj != PluginBase):
                    
                    # Instantiate plugin
                    plugin = obj()
                    
                    # Initialize plugin
                    success = await plugin.initialize()
                    
                    if success:
                        plugin.initialized = True
                        self.plugins[plugin.name] = plugin
                        self.plugin_classes[plugin.name] = obj
                        self.logger.info(f"Loaded plugin: {plugin.name} v{plugin.version}")
                    else:
                        self.logger.warning(f"Plugin initialization failed: {plugin.name}")
        
        except Exception as e:
            raise PluginException(
                f"Failed to load plugin from {file_path}",
                plugin_name=module_name,
                details={"error": str(e)}
            )
    
    async def reload_plugin_from_file(self, file_path: str):
        """
        Reload a plugin from file (hot-reload)
        
        Args:
            file_path: Path to plugin file
        """
        try:
            plugin_path = Path(file_path)
            module_name = plugin_path.stem
            
            # Find plugin by module name
            plugin_to_reload = None
            for plugin in self.plugins.values():
                if type(plugin).__module__ == module_name:
                    plugin_to_reload = plugin
                    break
            
            if plugin_to_reload:
                # Unload old plugin
                await self.unload_plugin(plugin_to_reload.name)
                
                # Load new version
                await self.load_plugin_from_file(plugin_path)
                
                self.logger.info(f"Reloaded plugin: {plugin_to_reload.name}")
        
        except Exception as e:
            self.logger.error(f"Failed to reload plugin from {file_path}: {str(e)}")
    
    async def unload_plugin(self, plugin_name: str):
        """
        Unload a plugin
        
        Args:
            plugin_name: Name of the plugin
        """
        if plugin_name in self.plugins:
            plugin = self.plugins[plugin_name]
            await plugin.shutdown()
            del self.plugins[plugin_name]
            self.logger.info(f"Unloaded plugin: {plugin_name}")
    
    async def unload_all_plugins(self):
        """
        Unload all plugins
        """
        for plugin_name in list(self.plugins.keys()):
            await self.unload_plugin(plugin_name)
        
        if self.observer:
            self.observer.stop()
            self.observer.join()
        
        self.logger.info("All plugins unloaded")
    
    def _start_watcher(self):
        """
        Start file system watcher for hot-reload
        """
        self.observer = Observer()
        event_handler = PluginFileHandler(self)
        self.observer.schedule(event_handler, str(self.plugins_dir), recursive=False)
        self.observer.start()
        self.logger.info("Plugin hot-reload watcher started")
    
    async def execute_plugin(
        self,
        plugin_name: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute a specific plugin
        
        Args:
            plugin_name: Name of the plugin
            data: Input data
        
        Returns:
            Plugin output
        
        Raises:
            PluginException: If plugin not found or execution fails
        """
        if plugin_name not in self.plugins:
            raise PluginException(
                f"Plugin not found: {plugin_name}",
                plugin_name=plugin_name
            )
        
        plugin = self.plugins[plugin_name]
        
        if not plugin.enabled:
            raise PluginException(
                f"Plugin is disabled: {plugin_name}",
                plugin_name=plugin_name
            )
        
        try:
            result = await plugin.process(data)
            return result
        except Exception as e:
            raise PluginException(
                f"Plugin execution failed: {plugin_name}",
                plugin_name=plugin_name,
                details={"error": str(e)}
            )
    
    async def execute_all_plugins(
        self,
        data: Dict[str, Any],
        parallel: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Execute all enabled plugins
        
        Args:
            data: Input data
            parallel: Execute in parallel or sequentially
        
        Returns:
            List of plugin outputs
        """
        enabled_plugins = [p for p in self.plugins.values() if p.enabled]
        
        if parallel:
            tasks = [plugin.process(data) for plugin in enabled_plugins]
            results = await asyncio.gather(*tasks, return_exceptions=True)
        else:
            results = []
            for plugin in enabled_plugins:
                try:
                    result = await plugin.process(data)
                    results.append(result)
                except Exception as e:
                    self.logger.error(f"Plugin {plugin.name} failed: {str(e)}")
                    results.append({"error": str(e), "plugin": plugin.name})
        
        return results
    
    def get_plugin(self, plugin_name: str) -> Optional[PluginBase]:
        """
        Get a plugin by name
        
        Args:
            plugin_name: Name of the plugin
        
        Returns:
            Plugin instance or None
        """
        return self.plugins.get(plugin_name)
    
    def list_plugins(self) -> List[Dict[str, Any]]:
        """
        List all plugins and their info
        
        Returns:
            List of plugin information
        """
        return [plugin.get_info() for plugin in self.plugins.values()]
    
    def enable_plugin(self, plugin_name: str):
        """
        Enable a plugin
        
        Args:
            plugin_name: Name of the plugin
        """
        if plugin_name in self.plugins:
            self.plugins[plugin_name].enabled = True
            self.logger.info(f"Enabled plugin: {plugin_name}")
    
    def disable_plugin(self, plugin_name: str):
        """
        Disable a plugin
        
        Args:
            plugin_name: Name of the plugin
        """
        if plugin_name in self.plugins:
            self.plugins[plugin_name].enabled = False
            self.logger.info(f"Disabled plugin: {plugin_name}")
