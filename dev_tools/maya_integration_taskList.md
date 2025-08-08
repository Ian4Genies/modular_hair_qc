## Maya Integration Task List (Hot-Reload + Logging)

Goal: Eliminate Maya restarts during development and persist logs for fast diagnosis and sharing.

### Deliverables
- Hot-reload flow (shelf button + menu item): reload modules, close current UI if present, relaunch UI
- Developer menu entries:
  - Open Hair QC Tool
  - Developer ▸ Reload Code
  - Developer ▸ Open Logs Folder
- Centralized logging under the selected USD directory (UI target): `<USD_DIR>/logs/hair_qc_tool/` (stdout/stderr, Qt messages, uncaught exceptions) with rotation
- Remote debug optional helper (debugpy)

### Logs Directory
- Root: inside the UI‑targeted USD directory (configurable via the UI)
  - Path: `<USD_DIR>/logs/hair_qc_tool/`
  - Example (current test setup): `docs/TestDirectory/logs/hair_qc_tool/`
- Rotation: keep last N = 10 (configurable)
- Filename: `#####_Log_YYYYMMDD_HHMMSS.txt` (##### = 5‑digit session id)
- Created automatically when initializing the USD directory (and on first launch if missing)

---

## Tasks

### 1) Developer Menu in `hair_qc_tool/main.py`
- Add a Developer submenu under Hair QC menu with:
  - Developer ▸ Reload Code
  - Developer ▸ Open Logs Folder
- Implement functions:
  - developer_reload_code(): calls reloader, closes/reopens UI
  - developer_open_logs_folder(): open `<USD_DIR>/logs/hair_qc_tool/` in Explorer
- Acceptance: menu installs; actions run without errors; status feedback visible
- Status: DONE (menu updated; `developer_reload_code` and `developer_open_logs_folder` implemented)

### 2) Centralized Reloader Utility
- New file: `hair_qc_tool/utils/reloader.py`
  - reload_hair_qc_modules(): apply dependency-ordered reload (use order from `simple_reload_test.py` / `force_reload_and_test.py`)
  - Return stats (reloaded count, errors)
- Wire shelf and Developer ▸ Reload Code to use this utility.
- Acceptance: code changes in `hair_qc_tool/*` reflect immediately; no Maya restart.
- Status: DONE (`reloader.py` added; Developer ▸ Reload Code uses it)

### 3) Persistent File Logging under `<USD_DIR>/logs/hair_qc_tool/`
- New file: `hair_qc_tool/utils/logging_utils.py`
  - install_file_logging(log_dir, rotate_keep=10): ensure `<USD_DIR>/logs/hair_qc_tool/`; setup root logger (FileHandler + StreamHandler)
  - install_stdout_stderr_tee(): tee sys.stdout/sys.stderr to logger
  - install_qt_message_handler(): route Qt messages to logger
  - install_exception_hook(): log uncaught exceptions with tracebacks
- Integrate into `HairQCTool.launch()` before window creation:
  - Resolve `log_dir = config.usd_directory / 'logs' / 'hair_qc_tool'`
  - Create directory if missing; install logging hooks idempotently
- Acceptance: a log file appears per session at `<USD_DIR>/logs/hair_qc_tool/` with prints, Qt warnings, and tracebacks; Open Logs Folder works
- Status: DONE (`logging_utils.py` added; `install_all_logging` invoked at launch; config init creates logs path)

### 4) Shelf Buttons
- Button A: Open Hair QC (existing)
- Button B: Reload Code + Relaunch UI (use reloader utility)
- Acceptance: both commands work from current shelf
- Status: TODO (document shelf commands; optional helper script)

### 5) Remote Debugging (Optional)
- Developer ▸ Start Debug Server (port 5678)
  - Runs minimal debugpy listen and prints status
- Acceptance: IDE can attach on 5678; breakpoints hit after reloads
- Status: TODO (add optional menu item)

### 6) USD Directory Initialization: ensure logs path exists
- Update initialization routine to create `<USD_DIR>/logs/hair_qc_tool/` along with `Group/`, `module/`, `style/`
- On first launch, if logs path is missing, create it before installing logging
- Acceptance: when using `docs/TestDirectory` or any new directory, the logs folder is present and writable
- Status: DONE (added to `config.initialize_usd_directory`)

### 7) Config and Safety
- Add config flags to disable file logging in production
- Skip reloading modules not yet imported gracefully
- Guard UI close/reopen; handle no-window case
- Acceptance: no crashes on repeated reload; toggles work; easy off-switch
- Status: PARTIAL (reloader skips modules not loaded; logging can be bypassed by not setting USD dir)

---

## References in Repo
- Reload order examples: `simple_reload_test.py`, `force_reload_and_test.py`
- UI/menu entry point: `hair_qc_tool/main.py`
- New utilities: `hair_qc_tool/utils/reloader.py`, `hair_qc_tool/utils/logging_utils.py`

---

## Quick Manual Commands (today)

Open Hair QC
```python
from hair_qc_tool.main import launch_hair_qc_tool
launch_hair_qc_tool()
```

Reload Code + Relaunch UI
```python
from hair_qc_tool.utils.reloader import reload_hair_qc_modules
from hair_qc_tool.main import launch_hair_qc_tool, _hair_qc_tool

res = reload_hair_qc_modules()
print(res.summary)
try:
    if _hair_qc_tool and _hair_qc_tool.main_window:
        _hair_qc_tool.main_window.close()
except Exception:
    pass
launch_hair_qc_tool()
```

---

## Acceptance Test Plan
1) Install Hair QC menu; open tool
2) Modify any file under `hair_qc_tool/`, then use Developer ▸ Reload Code (or shelf button)
3) Verify UI relaunches; changes reflect
4) Confirm a new log under `<USD_DIR>/logs/hair_qc_tool/` (e.g., `docs/TestDirectory/logs/hair_qc_tool/`)
5) Share log file for issues

---

## Rollback
- Comment logging init if needed
- Remove Developer menu via `deleteUI` if undesired
