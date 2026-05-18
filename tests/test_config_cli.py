import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from src.config import ConfigManager


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
    def test_main_file_list_command_runs(self):
        project_root = Path(__file__).resolve().parents[1]

        result = subprocess.run(
            [sys.executable, "__main__.py", "list"],
            cwd=project_root,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("No plugins configured.", result.stdout)


if __name__ == "__main__":
    unittest.main()
