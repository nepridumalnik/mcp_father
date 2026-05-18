from pathlib import Path
from fastmcp import FastMCP
from fastmcp.server import create_proxy
from .config import ConfigManager, PluginSpec

class PluginManager:
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        self.base_repo_dir = config_manager.project_root / "repositories"

    def mount_plugins(self, mcp: FastMCP):
        """Mounts enabled plugins as MCP servers."""
        enabled_plugins = self.config_manager.get_enabled_plugins()
        
        for name, spec in enabled_plugins:
            plugin_dir = self._base_repo_plugins_path(name)
            if not plugin_dir.exists():
                print(f"Warning: Plugin directory for {name} does not exist. Skipping.")
                continue

            # We attempt to register the plugin's command as a tool or use FastMCP's capability
            # If FastMCP supports mounting, we'd use it here. 
            # Since we don't know the exact version's API for proxying, 
            # we will try to implement a simple wrapper that executes the plugin's command.
            
            self._register_plugin_as_tool(mcp, name, spec, plugin_dir)

    def _base_repo_plugins_path(self, name: str) -> Path:
        return self.config_manager.project_root / "repositories" / name

    def _register_plugin_as_tool(self, mcp: FastMCP, name: str, spec: PluginSpec, plugin_dir: Path):
        """Mount a child MCP server through FastMCP's proxy support."""
        config = {
            "mcpServers": {
                name: {
                    "command": spec.mcp.command,
                    "args": spec.mcp.args,
                    "cwd": str(plugin_dir),
                }
            }
        }
        proxy = create_proxy(config, name=name)
        mcp.mount(proxy, namespace=spec.namespace)
        print(f"Mounted plugin: {name} as namespace '{spec.namespace}'")
