import json
from pathlib import Path
from typing import Dict, Optional
import yaml
from pydantic import BaseModel, Field

class MCPCommand(BaseModel):
    command: str
    args: list[str]

class PluginSpec(BaseModel):
    url: str
    branch: str = "main"
    namespace: str
    mcp: MCPCommand

class RepositoryConfig(BaseModel):
    repositories: Dict[str, PluginSpec]

class PluginSettings(BaseModel):
    enabled: bool = False
    locked_commit: Optional[str] = None

class GlobalSettings(BaseModel):
    plugins: Dict[str, PluginSettings] = Field(default_factory=dict)

class ConfigManager:
    def __init__(self, project_root: Path, settings_dir: Path):
        self.project_root = project_root
        self.settings_dir = settings_dir
        self.list_yml_path = project_root / "repositories" / "list.yml"
        self.settings_json_path = settings_dir / "settings.json"
        self.repositories: RepositoryConfig = RepositoryConfig(repositories={})
        self.settings: GlobalSettings = GlobalSettings()

    def init_configs(self):
        """Initialize default configs if they don't exist."""
        self.settings_dir.mkdir(parents=True, exist_ok=True)
        self.list_yml_path.parent.mkdir(parents=True, exist_ok=True)
        
        if not self.list_yml_path.exists():
            default_list = {
                "repositories": {
                    "example-plugin": {
                        "url": "https://github.com/example/example-mcp.git",
                        "branch": "main",
                        "namespace": "example",
                        "mcp": {
                            "command": "uv",
                            "args": ["run", "python", "-m", "example_mcp"]
                        }
                    }
                }
            }
            with open(self.list_yml_path, "w", encoding="utf-8") as f:
                yaml.safe_dump(default_list, f, sort_keys=False)

        if not self.settings_json_path.exists():
            with open(self.settings_json_path, "w", encoding="utf-8") as f:
                json.dump({"plugins": {}}, f, indent=2)

    def load_repositories(self):
        if self.list_yml_path.exists():
            with open(self.list_yml_path, "r", encoding="utf-8-sig") as f:
                data = yaml.safe_load(f) or {}
                self.repositories = RepositoryConfig.model_validate(
                    {"repositories": data.get("repositories") or {}}
                )
        return self.repositories

    def load_settings(self):
        if self.settings_json_path.exists():
            with open(self.settings_json_path, "r", encoding="utf-8-sig") as f:
                data = json.load(f)
                self.settings = GlobalSettings.model_validate(data)
        return self.settings

    def save_settings(self):
        self.settings_dir.mkdir(parents=True, exist_ok=True)
        with open(self.settings_json_path, "w", encoding="utf-8") as f:
            json.dump(self.settings.model_dump(), f, indent=2)

    def update_plugin_status(self, name: str, enabled: bool):
        if name not in self.settings.plugins:
            self.settings.plugins[name] = PluginSettings()
        self.settings.plugins[name].enabled = enabled
        self.save_settings()

    def set_plugin_commit(self, name: str, commit: Optional[str]):
        if name not in self.settings.plugins:
            self.settings.plugins[name] = PluginSettings()
        self.settings.plugins[name].locked_commit = commit
        self.save_settings()

    def get_plugin_status(self, name: str) -> bool:
        return self.settings.plugins.get(name, PluginSettings()).enabled

    def get_plugin_commit(self, name: str) -> Optional[str]:
        if name in self.settings.plugins:
            return self.settings.plugins[name].locked_commit
        return None

    def get_all_plugins_info(self):
        """Returns a list of all plugins with their status."""
        info = []
        for name, spec in self.repositories.repositories.items():
            enabled = self.get_plugin_status(name)
            info.append({
                "name": name,
                "namespace": spec.namespace,
                "enabled": enabled,
                "url": spec.url
            })
        return info

    def get_enabled_plugins(self):
        """Returns list of plugins that are enabled."""
        enabled_plugins = []
        for name, spec in self.repositories.repositories.items():
            if self.get_plugin_status(name):
                enabled_plugins.append((name, spec))
        return enabled_plugins
