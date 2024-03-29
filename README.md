# Count Dart

Automatic dart scoring system.

Still under development...

## Setup Dev Environment

### VS Code in container (recommended)

1. Clone the project
2. Open the project in VS Code `File --> Open Folder`

#### Open Backend
3. Run devcontainer (backend)
   1. press `F1`
   2. Select `Dev Containers: Reopen in container`
   3. Select `Dev Container: Count Dart Backend Container`
4. Select python interpreter
   1. press `F1`
   2. select `Python: Select Interpreter`
   3. Interpreter path is `/opt/venvs/countdart/bin/python3`
5. Install editable `pip install -e .`
6. Install pre-commit hooks: `pre-commit install`

#### Open Frontend
After opening the backend dev container:
1. Open `File -> New Window` in vs code
2. Run devcontainer (frontend)
   1. press `F1`
   2. Select `Dev Containers: Reopen in container`
   3. Select `Dev Container: Count Dart Frontend Container`


## Contributing

If you want to add, remove or change dependencies, make your edits inside `pyproject.toml`.

Run following make target to update requirement files under `requirements/`:

```
make pip-compile
```
