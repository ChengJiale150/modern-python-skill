# Contributing Guide

Thank you for your interest in contributing to `modern-python-skill`! This project aims to showcase modern Python best practices.

## Development Setup

1.  **Install `uv`**: This project uses [uv](https://github.com/astral-sh/uv) for dependency management.
2.  **Clone the repository**:
    ```bash
    git clone https://github.com/ChengJiale150/modern-python-skill.git
    cd modern-python-skill
    ```
3.  **Install dependencies**:
    ```bash
    make install
    ```
    This will install dependencies and set up pre-commit hooks.

## Development Workflow

-   **Make changes**: Edit code in `src/` or tests in `tests/`.
-   **Run checks**: Always run `make check` before committing. It runs:
    -   `ruff format`: Formatting
    -   `ruff check`: Linting
    -   `mypy`: Type checking
    -   `pytest`: Tests
-   **Commit changes**: Follow [Conventional Commits](https://www.conventionalcommits.org/) for commit messages.

## Project Structure

-   `src/modern_python_skill/`: Main package source code.
-   `tests/`: Unit and integration tests.
-   `Makefile`: Convenient shortcuts for common tasks.
-   `pyproject.toml`: Project metadata and tool configurations.

## Submitting Changes

1.  Fork the repository.
2.  Create a feature branch.
3.  Implement your changes and tests.
4.  Ensure `make check` passes.
5.  Submit a Pull Request.

Happy coding!
