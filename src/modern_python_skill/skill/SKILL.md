---
name: "modern-python-best-practices"
description: "Best practices for modern Python projects. USE WHEN building any non-trivial Python project (not simple scripts)."
---

# Modern Python Best Practices

This skill provides guidance and standards for building professional-grade Python projects using modern tools and conventions.

## Core Principles

- **Project Structure**: Use a `src` layout to prevent accidental imports from the project root and ensure the package is correctly installed.
- **Dependency Management**: Use modern tools like `uv`, `poetry`, or `pdm`. Always use a `pyproject.toml` for project configuration.
- **Type Safety**: Leverage `mypy` or `pyright` for static type checking. Use Python's type hinting system extensively.
- **Code Quality**:
  - **Linting & Formatting**: Use `ruff` for extremely fast linting and formatting.
  - **Consistency**: Follow PEP 8 and use tools to enforce it automatically.
- **Testing**:
  - Use `pytest` for all testing needs.
  - Aim for high test coverage but focus on meaningful tests.
  - Use `pytest-cov` for coverage reports.
- **Environment Isolation**: Always use virtual environments (`venv`, `conda`, or built-in tool isolation).
- **Git Hooks**: Use `pre-commit` to run checks (linting, type checking, tests) before every commit.
- **Documentation**: Use `mkdocs` or `sphinx` with clear, concise, and up-to-date documentation.

## When to Invoke

- **Initial Project Setup**: When starting a new Python project that is more than a single-file script.
- **Code Review**: When reviewing PRs to ensure modern standards are followed.
- **Tool Selection**: When deciding on what tools to use for linting, testing, or dependency management.
- **Architecture Decisions**: When structuring the package layout or defining module boundaries.

## Checklist for a Serious Project

1. [ ] `pyproject.toml` is present and correctly configured.
2. [ ] `src/` layout is used.
3. [ ] `ruff` is configured for both linting and formatting.
4. [ ] `mypy` is enabled with strict settings.
5. [ ] `pytest` is used with a dedicated `tests/` directory.
6. [ ] `.pre-commit-config.yaml` is set up.
7. [ ] CI/CD pipeline (e.g., GitHub Actions) is configured to run tests and linters.
