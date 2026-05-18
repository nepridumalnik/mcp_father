import subprocess
from pathlib import Path
from .config import ConfigManager, PluginSpec

class RepositoryManager:
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        self.base_repo_dir = config_manager.project_root / "repositories"
        self.base_repo_dir.mkdir(parents=True, exist_ok=True)

    def sync_plugin(self, name: str, spec: PluginSpec):
        """Sync a specific plugin repository."""
        target_dir = self.base_repo_dir / name
        url = spec.url
        branch = spec.branch

        if not target_dir.exists():
            print(f"Cloning {name} from {url}...")
            self._run_git(["clone", "-b", branch, url, str(target_dir)], cwd=self.base_repo_dir)
        else:
            print(f"Updating {name}...")
            self._run_git(["fetch", "origin"], cwd=target_dir)
            self._run_git(["checkout", branch], cwd=target_dir)
            self._run_git(["pull", "origin", branch], cwd=target_dir)

        # Handle locked commit
        commit = self.config_manager.get_plugin_commit(name)
        if commit:
            print(f"Checking out locked commit {commit} for {name}...")
            self._run_git(["checkout", commit], cwd=target_dir)

    def sync_all(self):
        """Sync all enabled plugins."""
        enabled_plugins = self.config_manager.get_enabled_plugins()
        for name, spec in enabled_plugins:
            try:
                self.sync_plugin(name, spec)
            except Exception as e:
                print(f"Failed to sync {name}: {e}")

    def _run_git(self, args: list[str], cwd: Path | None = None):
        result = subprocess.run(["git"] + args, cwd=cwd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"Git error: {result.stderr}")
        return result.stdout
