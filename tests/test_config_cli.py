import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock

from src.config import ConfigManager, MCPCommand, PluginSpec, RepositoryConfig
from src.plugins import PluginManager


class ConfigManagerTests(unittest.TestCase):
    def test_empty_repository_file_loads_as_empty_config(self):
        with tempfile.TemporaryDirectory() as project_dir, tempfile.TemporaryDirectory() as settings_dir:
            project_root = Path(project_dir)
            repositories_dir = project_root / "repositories"
            repositories_dir.mkdir()
            (repositories_dir / "list.yml").write_text("repositories:\n", encoding="utf-8")

            config = ConfigManager(project_root, Path(settings_dir))

            repositories = config.load_repositories()

            self.assertEqual(repositories.repositories, {})

    def test_plugin_status_defaults_to_disabled(self):
        with tempfile.TemporaryDirectory() as project_dir, tempfile.TemporaryDirectory() as settings_dir:
            config = ConfigManager(Path(project_dir), Path(settings_dir))

            self.assertFalse(config.get_plugin_status("missing"))


class CLITests(unittest.TestCase):
    def test_main_file_list_without_config_prints_init_hint(self):
        project_root = Path(__file__).resolve().parents[1]

        with tempfile.TemporaryDirectory() as home_dir:
            env = self._env_with_home(home_dir)
            result = subprocess.run(
                [sys.executable, "__main__.py", "list"],
                cwd=project_root,
                env=env,
                capture_output=True,
                text=True,
                timeout=30,
            )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Configuration is not initialized. Run: mcp-father init", result.stdout)

    def test_debug_flag_works_before_and_after_command(self):
        project_root = Path(__file__).resolve().parents[1]

        for args in (["-d", "list"], ["list", "-d"]):
            with self.subTest(args=args), tempfile.TemporaryDirectory() as home_dir:
                env = self._env_with_home(home_dir)
                result = subprocess.run(
                    [sys.executable, "__main__.py", *args],
                    cwd=project_root,
                    env=env,
                    capture_output=True,
                    text=True,
                    timeout=30,
                )

                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn("DEBUG", result.stdout)

    def test_help_does_not_create_home_config(self):
        project_root = Path(__file__).resolve().parents[1]

        with tempfile.TemporaryDirectory() as home_dir:
            env = self._env_with_home(home_dir)
            result = subprocess.run(
                [sys.executable, "__main__.py", "--help"],
                cwd=project_root,
                env=env,
                capture_output=True,
                text=True,
                timeout=30,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertFalse((Path(home_dir) / ".mcp_father").exists())

    @staticmethod
    def _env_with_home(home_dir: str):
        env = dict(os.environ)
        env["HOME"] = home_dir
        env["USERPROFILE"] = home_dir
        return env


class PluginManagerTests(unittest.TestCase):
    def test_mount_continues_after_single_plugin_error(self):
        with tempfile.TemporaryDirectory() as project_dir, tempfile.TemporaryDirectory() as settings_dir:
            project_root = Path(project_dir)
            (project_root / "repositories" / "bad").mkdir(parents=True)
            (project_root / "repositories" / "good").mkdir(parents=True)
            config = ConfigManager(project_root, Path(settings_dir))
            config.repositories = RepositoryConfig(
                repositories={
                    "bad": PluginSpec(
                        url="https://example.invalid/bad.git",
                        namespace="bad_ns",
                        mcp=MCPCommand(command="python", args=["-V"]),
                    ),
                    "good": PluginSpec(
                        url="https://example.invalid/good.git",
                        namespace="good_ns",
                        mcp=MCPCommand(command="python", args=["-V"]),
                    ),
                }
            )
            config.update_plugin_status("bad", True)
            config.update_plugin_status("good", True)
            manager = PluginManager(config)
            calls = []

            def register(mcp, name, spec, plugin_dir):
                calls.append(name)
                if name == "bad":
                    raise RuntimeError("boom")

            manager._register_plugin_as_tool = register

            with self.assertLogs("mcp_father.plugins", level="ERROR"):
                manager.mount_plugins(Mock())

            self.assertEqual(calls, ["bad", "good"])


if __name__ == "__main__":
    unittest.main()
