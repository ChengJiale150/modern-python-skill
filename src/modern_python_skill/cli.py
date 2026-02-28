import importlib.resources
import shutil
import tempfile
from pathlib import Path
from typing import Any

import git
import typer
import yaml
from rich.console import Console
from rich.panel import Panel

app = typer.Typer(help="CLI tool for managing modern python skills.")
console = Console()

CONFIG_DIR = Path.home() / ".modern-python-skill"
CONFIG_FILE = CONFIG_DIR / "config.yaml"
SKILL_DIR = CONFIG_DIR / "skill"
DEFAULT_SOURCE_URL = "https://github.com/ChengJiale150/modern-python-skill"


def load_config() -> dict[str, Any]:
    """Load configuration from the config file."""
    if not CONFIG_FILE.exists():
        return {"source_url": DEFAULT_SOURCE_URL, "projects": {}}
    try:
        with CONFIG_FILE.open() as f:
            return yaml.safe_load(f) or {
                "source_url": DEFAULT_SOURCE_URL,
                "projects": {},
            }
    except Exception as e:
        console.print(f"[red]Error loading config:[/red] {e}")
        return {"source_url": DEFAULT_SOURCE_URL, "projects": {}}


def save_config(config: dict[str, Any]) -> None:
    """Save configuration to the config file."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with CONFIG_FILE.open("w") as f:
        yaml.dump(config, f)


@app.command()
def init() -> None:
    """
    Initialize the tool, create ~/.modern-python-skill directory,
    and create config.yaml and skill directory.
    """
    console.print(Panel("Initializing modern-python-skill...", style="bold blue"))

    # Ensure config dir exists
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    # Create config.yaml if not exists
    if not CONFIG_FILE.exists():
        config = {"source_url": DEFAULT_SOURCE_URL, "projects": {}}
        save_config(config)
        console.print(f"[green]Created config at {CONFIG_FILE}[/green]")
    else:
        console.print(f"[yellow]Config already exists at {CONFIG_FILE}[/yellow]")

    # Copy skill directory
    try:
        # Try to locate skill directory within the package
        package_skill_dir = importlib.resources.files("modern_python_skill").joinpath(
            "skill"
        )

        with importlib.resources.as_file(package_skill_dir) as src_skill_path:
            if not src_skill_path.exists():
                # Fallback: try to locate relative to this file if running from source
                src_skill_path = Path(__file__).parent / "skill"

            if not src_skill_path.exists():
                console.print(
                    "[red]Error: Could not locate source skill directory within the package.[/red]"
                )
                raise typer.Exit(code=1)

            if SKILL_DIR.exists():
                shutil.rmtree(SKILL_DIR)

            shutil.copytree(src_skill_path, SKILL_DIR)
            console.print(f"[green]Copied skills to {SKILL_DIR}[/green]")

    except Exception as e:
        console.print(f"[red]Error copying skills:[/red] {e}")
        # If importlib fails, try local fallback directly
        try:
            src_skill_path = Path(__file__).parent / "skill"
            if src_skill_path.exists():
                if SKILL_DIR.exists():
                    shutil.rmtree(SKILL_DIR)
                shutil.copytree(src_skill_path, SKILL_DIR)
                console.print(f"[green]Copied skills to {SKILL_DIR} (fallback)[/green]")
                return
        except Exception:
            pass
        raise typer.Exit(code=1) from e


@app.command()
def add(name: str, path: str) -> None:
    """
    Add a skill directory by copying ~/.modern-python-skill/skill contents
    to <path>/skill/modern-python-skill and recording it in config.yaml.
    """
    target_root = Path(path).resolve()
    target_skill_dir = target_root / "modern-python-skill"

    if not SKILL_DIR.exists():
        console.print(
            "[red]Error: ~/.modern-python-skill/skill does not exist. Please run 'init' first.[/red]"
        )
        raise typer.Exit(code=1)

    # Copy
    if target_skill_dir.exists():
        shutil.rmtree(target_skill_dir)

    # Create parent dir if needed
    target_skill_dir.parent.mkdir(parents=True, exist_ok=True)

    try:
        shutil.copytree(SKILL_DIR, target_skill_dir)
        console.print(f"[green]Copied skills to {target_skill_dir}[/green]")
    except Exception as e:
        console.print(f"[red]Error copying skills to target:[/red] {e}")
        raise typer.Exit(code=1) from e

    # Update config
    config = load_config()
    if "projects" not in config:
        config["projects"] = {}
    config["projects"][name] = str(target_root)
    save_config(config)
    console.print(f"[green]Added project '{name}' with path {target_root}[/green]")


@app.command()
def remove(name: str) -> None:
    """
    Remove the corresponding skill directory entry from config.yaml.
    """
    config = load_config()
    if "projects" in config and name in config["projects"]:
        del config["projects"][name]
        save_config(config)
        console.print(f"[green]Removed project '{name}' from config.[/green]")
    else:
        console.print(f"[yellow]Project '{name}' not found in config.[/yellow]")


@app.command()
def update(
    mirror: str = typer.Option(
        DEFAULT_SOURCE_URL, "--mirror", help="Git mirror URL to pull from"
    ),
) -> None:
    """
    Pull the latest git from mirror URL to a temporary directory,
    and overwrite the local skills.
    """
    # Use mirror parameter as the source URL
    source_url = mirror

    with tempfile.TemporaryDirectory() as temp_dir:
        console.print(f"Cloning {source_url} to temporary directory...")
        try:
            git.Repo.clone_from(source_url, temp_dir)
        except git.GitCommandError as e:
            console.print(f"[red]Error cloning repository:[/red] {e}")
            raise typer.Exit(code=1) from e

        cloned_root = Path(temp_dir)
        possible_paths = [
            cloned_root / "skill",
            cloned_root / "src" / "modern_python_skill" / "skill",
        ]

        found_skill_path = None
        for p in possible_paths:
            if p.exists() and p.is_dir():
                found_skill_path = p
                break

        if not found_skill_path:
            console.print(
                "[red]Error: Could not find 'skill' directory in the repository.[/red]"
            )
            raise typer.Exit(code=1)

        console.print(f"Found skills at {found_skill_path}")

        # Copy to ~/.modern-python-skill/skill
        # Always overwrite for update command as per original mirror logic intent
        if SKILL_DIR.exists():
            shutil.rmtree(SKILL_DIR)
        shutil.copytree(found_skill_path, SKILL_DIR)
        console.print(f"[green]Updated skills from {source_url}.[/green]")


@app.command()
def sync(name: str) -> None:
    """
    Sync the latest local skills to the specified project.
    """
    config = load_config()
    if "projects" not in config or name not in config["projects"]:
        console.print(f"[red]Error: Project '{name}' not found.[/red]")
        raise typer.Exit(code=1)

    target_root = Path(config["projects"][name])
    target_skill_dir = target_root / "skill" / "modern-python-skill"

    if not SKILL_DIR.exists():
        console.print(
            "[red]Error: ~/.modern-python-skill/skill does not exist. Please run 'init' first.[/red]"
        )
        raise typer.Exit(code=1)

    if target_skill_dir.exists():
        shutil.rmtree(target_skill_dir)

    target_skill_dir.parent.mkdir(parents=True, exist_ok=True)
    try:
        shutil.copytree(SKILL_DIR, target_skill_dir)
        console.print(f"[green]Synced skills to {target_skill_dir}[/green]")
    except Exception as e:
        console.print(f"[red]Error syncing skills:[/red] {e}")
        raise typer.Exit(code=1) from e


if __name__ == "__main__":
    app()
