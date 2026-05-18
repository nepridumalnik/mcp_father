import logging
import subprocess
from pathlib import Path
from .config import ConfigManager, PluginSpec

class RepositoryManager:
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        self.base_repo_dir = config_manager.project_root / "repositories"
        self.logger = logging.getLogger("mcp_father.repositories")

    def sync_plugin(self, name: str, spec: PluginSpec):
        """Sync a specific plugin repository."""
        self.base_repo_dir.mkdir(parents=True, exist_ok=True)
        target_dir = self.base_repo_dir / name
        url = spec.url
        branch = spec.branch

        if not target_dir.exists():
            self.logger.info("Cloning %s from %s", name, url)
            self._run_git(["clone", "-b", branch, url, str(target_dir)], cwd=self.base_repo_dir)
        else:
            self.logger.info("Updating %s", name)
            self._run_git(["fetch", "origin"], cwd=target_dir)
            self._run_git(["checkout", branch], cwd=target_dir)
            self._run_git(["pull", "origin", branch], cwd=target_dir)

        # Handle locked commit
        commit = self.config_manager.get_plugin_commit(name)
        if commit:
            self.logger.info("Checking out locked commit %s for %s", commit, name)
            self._run_git(["checkout", commit], cwd=target_dir)

    def sync_all(self):
        """Sync all enabled plugins."""
        enabled_plugins = self.config_manager.get_enabled_plugins()
        for name, spec in enabled_plugins:
            try:
                self.sync_plugin(name, spec)
            except Exception:
                self.logger.exception("Failed to sync plugin %s", name)

    def _run_git(self, args: list[str], cwd: Path | None = None, timeout: int = 120):
        command = ["git"] + args
        self.logger.debug("Running command: %s cwd=%s timeout=%s", command, cwd, timeout)
        try:
            result = subprocess.run(
                command,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
        except subprocess.TimeoutExpired as e:
            raise RuntimeError(
                "Git command timed out: "
                f"command={command}, cwd={cwd}, timeout={timeout}, "
                f"stdout={e.stdout}, stderr={e.stderr}"
            ) from e
        if result.returncode != 0:
            raise RuntimeError(
                "Git error: "
                f"command={command}, cwd={cwd}, returncode={result.returncode}, "
                f"stdout={result.stdout}, stderr={result.stderr}"
            )
        return result.stdout
