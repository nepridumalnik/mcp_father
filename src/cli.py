import argparse
import logging
import sys
from pathlib import Path

from .config import ConfigManager
from .repositories import RepositoryManager
from .plugins import PluginManager
from .app import MCPFatherApp
from .logging_config import setup_logging

class MCPFatherCLI:
    @staticmethod
    def _project_root() -> Path:
        return Path(__file__).resolve().parents[1]

    def __init__(self):
        project_root = self._project_root()
        settings_dir = Path.home() / ".mcp_father"
        self.config_manager = ConfigManager(project_root, settings_dir)
        self.repo_manager = RepositoryManager(self.config_manager)
        self.plugin_manager = PluginManager(self.config_manager)
        self.logger = logging.getLogger("mcp_father")

    def execute(self):
        parser = argparse.ArgumentParser(prog="mcp-father", description="MCP Father Hub CLI")
        parser.add_argument("--debug", "-d", action="store_true", help="Enable debug logging")
        debug_parent = argparse.ArgumentParser(add_help=False)
        debug_parent.add_argument("--debug", "-d", action="store_true", help=argparse.SUPPRESS)
        subparsers = parser.add_subparsers(dest="command", help="Commands")

        # run command
        subparsers.add_parser("run", parents=[debug_parent], help="Start the MCP hub")

        # list command
        subparsers.add_parser("list", parents=[debug_parent], help="List all plugins")

        # enable command
        enable_parser = subparsers.add_parser("enable", parents=[debug_parent], help="Enable a plugin")
        enable_parser.add_argument("name", help="Plugin name")

        # disable command
        disable_parser = subparsers.add_parser("disable", parents=[debug_parent], help="Disable a plugin")
        disable_parser.add_argument("name", help="Plugin name")

        # sync command
        sync_parser = subparsers.add_parser("sync", parents=[debug_parent], help="Sync plugins")
        sync_parser.add_argument("name", nargs="?", help="Specific plugin name to sync (optional)")

        # lock command
        lock_parser = subparsers.add_parser("lock", parents=[debug_parent], help="Lock a plugin to a specific commit")
        lock_parser.add_argument("name", help="Plugin name")
        lock_parser.add_argument("commit", help="Commit hash or branch")

        # unlock command
        unlock_parser = subparsers.add_parser("unlock", parents=[debug_parent], help="Unlock a plugin")
        unlock_parser.add_argument("name", help="Plugin name")

        # init command
        subparsers.add_parser("init", parents=[debug_parent], help="Initialize configuration")

        raw_debug = any(arg in ("--debug", "-d") for arg in sys.argv[1:])
        args = parser.parse_args()
        args.debug = args.debug or raw_debug
        self.logger = setup_logging(args.debug)
        self.logger.debug("CLI arguments parsed: %s", args)

        if args.command == "run":
            self._initialize_config()
            app = MCPFatherApp(project_root=self._project_root())
            app.run()
        elif args.command == "list":
            self.list_plugins()
        elif args.command == "enable":
            self._initialize_config()
            self._require_plugin(args.name)
            self.config_manager.update_plugin_status(args.name, True)
            print(f"Plugin '{args.name}' enabled.")
        elif args.command == "disable":
            self._initialize_config()
            self._require_plugin(args.name)
            self.config_manager.update_plugin_status(args.name, False)
            print(f"Plugin '{args.name}' disabled.")
        elif args.command == "sync":
            self._initialize_config()
            if args.name:
                repos = self.config_manager.load_repositories().repositories
                if args.name in repos:
                    self.repo_manager.sync_plugin(args.name, repos[args.name])
                else:
                    print(f"Plugin '{args.name}' not found in list.yml")
            else:
                self.repo_manager.sync_all()
        elif args.command == "lock":
            self._initialize_config()
            self._require_plugin(args.name)
            self.config_manager.set_plugin_commit(args.name, args.commit)
            print(f"Plugin '{args.name}' locked to {args.commit}")
        elif args.command == "unlock":
            self._initialize_config()
            self._require_plugin(args.name)
            self.config_manager.set_plugin_commit(args.name, None)
            print(f"Plugin '{args.name}' unlocked.")
        elif args.command == "init":
            self.config_manager.init_configs()
            print("Configuration initialized.")
        else:
            parser.print_help()

    def list_plugins(self):
        self.config_manager.load_repositories()
        self.config_manager.load_settings()
        repos = self.config_manager.load_repositories().repositories
        if not repos:
            print("No plugins configured.")
            return
        for name, spec in repos.items():
            enabled = self.config_manager.get_plugin_status(name)
            status = "ENABLED" if enabled else "DISABLED"
            print(f"[{status}] {name} ({spec.namespace}) - {spec.url}")

    def _require_plugin(self, name: str):
        repos = self.config_manager.load_repositories().repositories
        if name not in repos:
            raise ValueError(f"Plugin '{name}' not found in repositories/list.yml")
        return repos[name]

    def _initialize_config(self):
        self.config_manager.init_configs()
        self.config_manager.load_repositories()
        self.config_manager.load_settings()

if __name__ == "__main__":
    cli = MCPFatherCLI()
    cli.execute()
