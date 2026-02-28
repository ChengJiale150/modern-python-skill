# Modern Python Skill CLI

[![Python Version](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/release/python-3120/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Checked with mypy](https://img.shields.io/badge/checked_with-mypy-blue.svg)](http://mypy-lang.org/)
[![Coverage: 99%](https://img.shields.io/badge/coverage-99%25-brightgreen.svg)](https://github.com/ChengJiale150/modern-python-skill)

A CLI tool designed to manage and synchronize modern Python development best practices and "skills" (templates, guidelines, and configurations) across multiple projects.

## 🚀 Features

- **Centralized Skill Management**: Keep your development standards and best practices in one central location (`~/.modern-python-skill`).
- **Project Synchronization**: Easily apply and update skills to different local projects with a single command.
- **Remote Updates**: Stay up-to-date by pulling the latest skills from a remote git repository or a mirror.
- **Modern Tech Stack**: Built with `uv` for dependency management, `typer` for CLI, `rich` for terminal UI, and `ruff` for code quality.

## 📦 Installation

This tool is best used with [uv](https://github.com/astral-sh/uv).

```bash
# Install as a global tool (recommended)
uv tool install git+https://github.com/ChengJiale150/modern-python-skill.git

# Or clone and install locally
git clone https://github.com/ChengJiale150/modern-python-skill.git
cd modern-python-skill
uv sync
```

## 🛠️ Usage

### 1. Initialize the Tool
Before using the tool for the first time, you need to initialize it. This creates the configuration directory and copies default skills.

```bash
modern-python-skill init
```

### 2. Manage Projects
Add a project directory to be managed by the tool. This will copy the skill files to `<path>/modern-python-skill`.

```bash
modern-python-skill add <project-name> <project-path>
```

To stop managing a project:

```bash
modern-python-skill remove <project-name>
```

### 3. Sync Skills
When your local skills (in `~/.modern-python-skill/skill`) are updated, you can synchronize them to a specific project:

```bash
modern-python-skill sync <project-name>
```

### 4. Update Remote Skills
Pull the latest skills from the source repository to your local skill directory:

```bash
# Pull from the default source
modern-python-skill update

# Pull from a custom mirror
modern-python-skill update --mirror https://github.com/your-org/custom-skills.git
```

## 🧑‍💻 Development

The project uses a standard `src` layout and `uv` for environment management.

### Setup
```bash
make install
```

### Quality Checks
Run all formatting, linting, type checking, and tests:
```bash
make check
```

Available commands in `Makefile`:
- `make format`: Format code with Ruff.
- `make lint`: Lint code with Ruff.
- `make type-check`: Type check with Mypy.
- `make test`: Run tests with Pytest.
- `make clean`: Remove temporary files and caches.

## 📄 License

This project is licensed under the [MIT License](file:///home/chengjiale/code/modern-python-skill/LICENCE).
