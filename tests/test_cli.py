import shutil
from pathlib import Path
from unittest.mock import MagicMock

import git
import pytest
from typer.testing import CliRunner

from modern_python_skill.cli import app, load_config, save_config

runner = CliRunner()


@pytest.fixture
def mock_env(tmp_path, monkeypatch):
    config_dir = tmp_path / ".modern-python-skill"
    config_file = config_dir / "config.yaml"
    skill_dir = config_dir / "skill"

    monkeypatch.setattr("modern_python_skill.cli.CONFIG_DIR", config_dir)
    monkeypatch.setattr("modern_python_skill.cli.CONFIG_FILE", config_file)
    monkeypatch.setattr("modern_python_skill.cli.SKILL_DIR", skill_dir)

    return {
        "config_dir": config_dir,
        "config_file": config_file,
        "skill_dir": skill_dir,
        "tmp_path": tmp_path,
    }


# --- Basic Config Tests ---


def test_load_config_error(mock_env, monkeypatch):
    # Create a malformed yaml
    mock_env["config_dir"].mkdir(parents=True, exist_ok=True)
    mock_env["config_file"].write_text("invalid: yaml: :")

    config = load_config()
    assert (
        config["source_url"] == "https://github.com/ChengJiale150/modern-python-skill"
    )
    assert config["projects"] == {}


def test_save_config_creates_dir(mock_env):
    test_config = {"source_url": "test", "projects": {}}
    save_config(test_config)
    assert mock_env["config_dir"].exists()
    assert mock_env["config_file"].exists()


# --- Init Command Tests ---


def test_init_already_exists(mock_env):
    mock_env["config_dir"].mkdir(parents=True, exist_ok=True)
    mock_env["config_file"].write_text("source_url: existing")

    result = runner.invoke(app, ["init"])
    assert result.exit_code == 0
    assert "Config already exists" in result.stdout


def test_init_copy_failure(mock_env, monkeypatch):
    # Mock importlib to fail
    monkeypatch.setattr(
        "importlib.resources.files", MagicMock(side_effect=Exception("Resource error"))
    )

    # Also mock the fallback path to not exist
    # In cli.py: src_skill_path = Path(__file__).parent / "skill"
    # We need to mock Path.exists to return False for the specific fallback path
    import pathlib

    original_exists = pathlib.Path.exists

    def mock_exists(self):
        if "modern_python_skill/skill" in str(self):
            return False
        return original_exists(self)

    monkeypatch.setattr(pathlib.Path, "exists", mock_exists)

    result = runner.invoke(app, ["init"])
    assert result.exit_code == 1
    assert "Error copying skills" in result.stdout


def test_init_fallback_with_existing_skill_dir(mock_env, monkeypatch):
    # Mock importlib to fail
    monkeypatch.setattr(
        "importlib.resources.files", MagicMock(side_effect=Exception("Resource error"))
    )

    # Mock the fallback path to exist
    import pathlib

    original_exists = pathlib.Path.exists

    def mock_exists(self):
        if "modern_python_skill/skill" in str(self):
            return True
        return original_exists(self)

    monkeypatch.setattr(pathlib.Path, "exists", mock_exists)

    # Create SKILL_DIR to trigger line 94
    mock_env["skill_dir"].mkdir(parents=True)

    # Mock shutil.copytree to avoid actual copy
    monkeypatch.setattr(shutil, "copytree", MagicMock())
    monkeypatch.setattr(shutil, "rmtree", MagicMock())

    result = runner.invoke(app, ["init"])
    assert result.exit_code == 0
    assert "(fallback)" in result.stdout
    assert shutil.rmtree.called


# --- Add Command Tests ---


def test_add_success(mock_env):
    # Setup skill dir
    mock_env["skill_dir"].mkdir(parents=True, exist_ok=True)
    (mock_env["skill_dir"] / "skill_file.txt").write_text("content")

    target_path = mock_env["tmp_path"] / "target_project"

    result = runner.invoke(app, ["add", "my-project", str(target_path)])
    assert result.exit_code == 0
    assert (target_path / "modern-python-skill" / "skill_file.txt").exists()

    config = load_config()
    assert config["projects"]["my-project"] == str(target_path)


def test_add_copy_error(mock_env, monkeypatch):
    mock_env["skill_dir"].mkdir(parents=True, exist_ok=True)

    # Force copytree to fail
    monkeypatch.setattr(
        shutil, "copytree", MagicMock(side_effect=OSError("Copy failed"))
    )

    result = runner.invoke(app, ["add", "fail-project", "/tmp/anywhere"])
    assert result.exit_code == 1
    assert "Error copying skills to target" in result.stdout


def test_add_no_skill_dir(mock_env):
    # Ensure SKILL_DIR does not exist
    result = runner.invoke(app, ["add", "no-skill", "/tmp/path"])
    assert result.exit_code == 1
    assert "run 'init' first" in result.stdout


# --- Remove Command Tests ---


def test_remove_success(mock_env):
    save_config({"projects": {"p1": "path1"}})
    result = runner.invoke(app, ["remove", "p1"])
    assert result.exit_code == 0
    assert "Removed project 'p1'" in result.stdout
    config = load_config()
    assert "p1" not in config["projects"]


def test_remove_not_found(mock_env):
    result = runner.invoke(app, ["remove", "non-existent"])
    assert result.exit_code == 0
    assert "Project 'non-existent' not found" in result.stdout


# --- Update Command Tests ---


def test_update_success(mock_env, monkeypatch):
    # Mock git.Repo.clone_from
    def mock_clone(_url, to_path):
        p = Path(to_path)
        skill_path = p / "skill"
        skill_path.mkdir(parents=True)
        (skill_path / "new_skill.txt").write_text("new content")
        return MagicMock()

    monkeypatch.setattr(git.Repo, "clone_from", mock_clone)

    result = runner.invoke(app, ["update"])
    assert result.exit_code == 0
    assert (mock_env["skill_dir"] / "new_skill.txt").exists()
    assert "Updated skills from" in result.stdout


def test_update_clone_fail(mock_env, monkeypatch):
    monkeypatch.setattr(
        git.Repo,
        "clone_from",
        MagicMock(side_effect=git.GitCommandError("clone", "failed")),
    )

    result = runner.invoke(app, ["update"])
    assert result.exit_code == 1
    assert "Error cloning repository" in result.stdout


def test_update_missing_skill_dir(mock_env, monkeypatch):
    def mock_clone_no_skill(_url, _to_path):
        # Create a temp dir without 'skill' folder
        return MagicMock()

    monkeypatch.setattr(git.Repo, "clone_from", mock_clone_no_skill)

    result = runner.invoke(app, ["update"])
    assert result.exit_code == 1
    assert "Error: Could not find 'skill' directory" in result.stdout


# --- Sync Command Tests ---


def test_sync_success(mock_env):
    # Setup config
    target_path = mock_env["tmp_path"] / "sync_target"
    save_config({"projects": {"sync-project": str(target_path)}})

    # Setup local skills
    mock_env["skill_dir"].mkdir(parents=True, exist_ok=True)
    (mock_env["skill_dir"] / "skill.md").write_text("local")

    result = runner.invoke(app, ["sync", "sync-project"])
    assert result.exit_code == 0
    assert (target_path / "modern-python-skill" / "skill.md").exists()


def test_sync_project_not_found(mock_env):
    result = runner.invoke(app, ["sync", "missing"])
    assert result.exit_code == 1
    assert "Error: Project 'missing' not found" in result.stdout


def test_sync_no_local_skills(mock_env):
    save_config({"projects": {"project": "/tmp"}})
    # skill_dir does not exist

    result = runner.invoke(app, ["sync", "project"])
    assert result.exit_code == 1
    assert "Error: ~/.modern-python-skill/skill does not exist" in result.stdout


def test_sync_copy_error(mock_env, monkeypatch):
    target_path = mock_env["tmp_path"] / "sync_target"
    save_config({"projects": {"project": str(target_path)}})
    mock_env["skill_dir"].mkdir(parents=True, exist_ok=True)

    monkeypatch.setattr(
        shutil, "copytree", MagicMock(side_effect=Exception("Sync failed"))
    )

    result = runner.invoke(app, ["sync", "project"])
    assert result.exit_code == 1
    assert "Error syncing skills" in result.stdout


def test_init_copy_fallback_success(mock_env, monkeypatch):
    # Mock importlib to fail
    monkeypatch.setattr(
        "importlib.resources.files", MagicMock(side_effect=Exception("Resource error"))
    )

    # Mock the fallback path to exist
    import pathlib

    original_exists = pathlib.Path.exists

    def mock_exists(self):
        if "modern_python_skill/skill" in str(self):
            return True
        return original_exists(self)

    monkeypatch.setattr(pathlib.Path, "exists", mock_exists)

    # Mock shutil.copytree to avoid actual copy
    monkeypatch.setattr(shutil, "copytree", MagicMock())

    result = runner.invoke(app, ["init"])
    assert result.exit_code == 0
    assert "Copied skills to" in result.stdout
    assert "(fallback)" in result.stdout


def test_add_overwrite_existing(mock_env):
    mock_env["skill_dir"].mkdir(parents=True, exist_ok=True)
    target_path = mock_env["tmp_path"] / "overwrite_project"
    target_skill_dir = target_path / "modern-python-skill"
    target_skill_dir.mkdir(parents=True)
    (target_skill_dir / "old.txt").write_text("old")

    result = runner.invoke(app, ["add", "overwrite", str(target_path)])
    assert result.exit_code == 0
    assert not (target_skill_dir / "old.txt").exists()


def test_sync_overwrite_existing(mock_env):
    target_path = mock_env["tmp_path"] / "sync_overwrite"
    save_config({"projects": {"p": str(target_path)}})
    mock_env["skill_dir"].mkdir(parents=True, exist_ok=True)

    target_skill_dir = target_path / "modern-python-skill"
    target_skill_dir.mkdir(parents=True)
    (target_skill_dir / "old.txt").write_text("old")

    result = runner.invoke(app, ["sync", "p"])
    assert result.exit_code == 0
    assert not (target_skill_dir / "old.txt").exists()


def test_update_overwrite_existing(mock_env, monkeypatch):
    mock_env["skill_dir"].mkdir(parents=True, exist_ok=True)
    (mock_env["skill_dir"] / "old.txt").write_text("old")

    def mock_clone(_url, to_path):
        p = Path(to_path)
        skill_path = p / "skill"
        skill_path.mkdir(parents=True)
        return MagicMock()

    monkeypatch.setattr(git.Repo, "clone_from", mock_clone)

    result = runner.invoke(app, ["update"])
    assert result.exit_code == 0
    assert not (mock_env["skill_dir"] / "old.txt").exists()


def test_init_source_not_found(mock_env, monkeypatch):
    # Mock importlib to return non-existent path
    monkeypatch.setattr("importlib.resources.files", MagicMock())

    class MockAsFile:
        def __enter__(self):
            return Path("/non/existent")

        def __exit__(self, *args):
            pass

    monkeypatch.setattr("importlib.resources.as_file", lambda _: MockAsFile())

    # Mock fallback to also not exist
    import pathlib

    original_exists = pathlib.Path.exists

    def mock_exists(self):
        if "modern_python_skill/skill" in str(self):
            return False
        return original_exists(self)

    monkeypatch.setattr(pathlib.Path, "exists", mock_exists)

    result = runner.invoke(app, ["init"])
    assert result.exit_code == 1
    assert "Could not locate source skill directory" in result.stdout


def test_add_projects_missing_in_config(mock_env):
    # Save config without 'projects' key
    save_config({"source_url": "test"})
    mock_env["skill_dir"].mkdir(parents=True, exist_ok=True)

    result = runner.invoke(app, ["add", "new", str(mock_env["tmp_path"] / "new")])
    assert result.exit_code == 0
    config = load_config()
    assert "projects" in config
    assert config["projects"]["new"] == str(mock_env["tmp_path"] / "new")


def test_init_removes_existing_skill_dir(mock_env, monkeypatch):
    mock_env["skill_dir"].mkdir(parents=True, exist_ok=True)
    (mock_env["skill_dir"] / "old.txt").write_text("old")

    # Mock source to exist
    mock_src = mock_env["tmp_path"] / "src_skill"
    mock_src.mkdir()

    monkeypatch.setattr("importlib.resources.files", MagicMock())

    # Mock as_file context manager
    class MockAsFile:
        def __enter__(self):
            return mock_src

        def __exit__(self, *args):
            pass

    monkeypatch.setattr("importlib.resources.as_file", lambda _: MockAsFile())

    result = runner.invoke(app, ["init"])
    assert result.exit_code == 0
    assert not (mock_env["skill_dir"] / "old.txt").exists()


def test_remove_projects_key_missing(mock_env):
    save_config({"source_url": "test"})
    result = runner.invoke(app, ["remove", "any"])
    assert result.exit_code == 0
    assert "not found in config" in result.stdout


def test_init_fallback_inner_exception(mock_env, monkeypatch):
    # Mock importlib to fail
    monkeypatch.setattr(
        "importlib.resources.files", MagicMock(side_effect=Exception("Outer error"))
    )

    # Mock fallback to fail during copytree
    import pathlib

    original_exists = pathlib.Path.exists

    def mock_exists(self):
        if "modern_python_skill/skill" in str(self):
            return True
        return original_exists(self)

    monkeypatch.setattr(pathlib.Path, "exists", mock_exists)

    monkeypatch.setattr(
        shutil, "copytree", MagicMock(side_effect=Exception("Inner error"))
    )

    result = runner.invoke(app, ["init"])
    assert result.exit_code == 1
