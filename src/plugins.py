import logging
from pathlib import Path
from fastmcp import FastMCP
from fastmcp.server import create_proxy
from .config import ConfigManager, PluginSpec

class PluginManager:
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        self.base_repo_dir = config_manager.project_root / "repositories"
        self.logger = logging.getLogger("mcp_father.plugins")

    def mount_plugins(self, mcp: FastMCP):
        """Mounts enabled plugins as MCP servers."""
        enabled_plugins = self.config_manager.get_enabled_plugins()
        
        for name, spec in enabled_plugins:
            plugin_dir = self._base_repo_plugins_path(name)
            command = spec.mcp.command
            args = spec.mcp.args
            self.logger.debug(
                "Mounting plugin name=%s namespace=%s cwd=%s command=%s args=%s",
                name,
                spec.namespace,
                plugin_dir,
                command,
                args,
            )
            if not plugin_dir.exists():
                self.logger.warning(
                    "Plugin directory does not exist; skipping name=%s namespace=%s cwd=%s command=%s args=%s",
                    name,
                    spec.namespace,
                    plugin_dir,
                    command,
                    args,
                )
                continue
            
            try:
                self._register_plugin_as_tool(mcp, name, spec, plugin_dir)
            except Exception:
                self.logger.exception(
                    "Failed to mount plugin name=%s namespace=%s cwd=%s command=%s args=%s",
                    name,
                    spec.namespace,
                    plugin_dir,
                    command,
                    args,
                )

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
        self.logger.info("Mounted plugin %s as namespace %s", name, spec.namespace)
