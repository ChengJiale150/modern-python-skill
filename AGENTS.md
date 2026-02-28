## Dependencies
- Using `uv` for dependency management, use `uv run` to run commands in the virtual environment.
- NEVER directly modify `pyproject.toml`, Add dependencies using `uv add <package-name>`, Sync Envirment using `uv sync`.

## Devlopment
- MUST Use `make check` to run checking before finish a feature or fix a bug.
