import logging
from pathlib import Path
from fastmcp import FastMCP
from .config import ConfigManager
from .tools import register_builtin_tools
from .plugins import PluginManager
from .repositories import RepositoryManager

class MCPFatherApp:
    def __init__(self, project_root: Path | None = None):
        self.project_root = project_root or Path(__file__).resolve().parents[1]
        self.settings_dir = Path.home() / ".mcp_father"
        
        self.config_manager = ConfigManager(self.project_root, self.settings_dir)
        self.plugin_manager = PluginManager(self.config_manager)
        self.repo_manager = RepositoryManager(self.config_manager)
        self.mcp = FastMCP("mcp-father-hub")
        
        self.logger = logging.getLogger("mcp_father")

    def initialize(self):
        self.config_manager.init_configs()
        self.config_manager.load_repositories()
        self.config_manager.load_settings()

    def run(self):
        self.initialize()
        self.logger.info("Initializing MCP Father Hub...")
        
        # Register built-in tools
        register_builtin_tools(self.mcp)
        
        # Mount plugins
        try:
            self.plugin_manager.mount_plugins(self.mcp)
        except Exception as e:
            self.logger.error(f"Failed to mount plugins: {e}")

        print("MCP Father Hub is running. Use an MCP client to connect.")
        self.mcp.run()

def start():
    app = MCPFatherApp()
    app.run()

if __name__ == "__main__":
    start()
