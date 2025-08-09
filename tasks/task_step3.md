# Step 3 — Group Management System (Granular Plan)

Scope: Implement the Group layer end-to-end (data, USD I/O, UI wiring), following USD minimal-load rules and docs in `docs/`. Operate on USD prim paths; avoid importing geometry. Group data is small, so focus on targeted prim edits, not whole-stage loads.

## Objectives
- Discover/select Groups from USD directory
- Create/rename/delete Group USD files safely
- Read/write Module Whitelists per Group
- Read/write Scalp Alpha Whitelist per Group
- Read/write Group-level Cross-Module Exclusions and Weight Constraints (storage only; enforcement is later)
- Wire UI Group section per `docs/UI Mockup.md` with single-selection lists

NOTE: The docs may refer to check box selection, this is outdated, and selection shoul happen when user clicks on list items. There is no need for checkbox column for selection. 

## Data Model & Paths
Update or add to `hair_qc_tool/utils/usd_utils.py`:
- Extend `StandardPrimPaths` with:
  - `GROUP_EXCLUSIONS_ROOT = "/HairGroup/CrossModuleExclusions"`
  - `GROUP_CONSTRAINTS_ROOT = "/HairGroup/BlendshapeConstraints"`
- Keep existing:
  - `GROUP_ROOT`, `GROUP_MODULE_WHITELIST_ROOT`, `GROUP_ALPHA_WHITELIST_ROOT`

Notes:
- All read/write ops should use `USDStageManager.get_or_define_prim()` and precise child paths; do not restructure existing prims.
- For relationships, use absolute prim paths as targets.

## Backend — USD Group Utilities
Add/extend methods in `USDGroupUtils`:

1) Group discovery & stage open
- `list_groups(usd_directory) -> List[str]` (exists)
- `open_group_stage(usd_directory: str, group_name: str)`
  - Build `Group/{group_name}.usd` path, open via `USDStageManager.open_stage()`

2) Group creation/rename/delete
- `create_group(usd_directory: str, group_name: str) -> bool`
  - Validate name (no spaces; auto-convert spaces to underscores). Create new USD with root `"/HairGroup"` and empty `ModuleWhitelist` and `AlphaWhitelist/Scalp` containers; save.
- `rename_group(usd_directory: str, old_name: str, new_name: str) -> bool`
  - File rename; refresh caches.
- `delete_group(usd_directory: str, group_name: str) -> bool`
  - Remove file; no cascading deletions.

3) Module whitelist management
- `read_module_whitelist(stage) -> Dict[str, List[str]]` (exists)
- `write_module_whitelist(stage, data: Dict[str, List[str]]) -> bool`
- Convenience mutators:
  - `add_module_to_whitelist(stage, module_type: str, asset_path: str) -> bool`
  - `remove_module_from_whitelist(stage, module_type: str, asset_path: str) -> bool`

4) Scalp alpha whitelist management
- `read_alpha_whitelist(stage) -> Dict[str, List[str]]` (exists)
- `write_alpha_whitelist(stage, data: Dict[str, List[str]]) -> bool`
- Convenience mutators:
  - `whitelist_alpha(stage, category: str, asset_path: str) -> bool`
  - `blacklist_alpha(stage, category: str, asset_path: str) -> bool`

5) Group-level rule storage (exclusions & constraints)
- Exclusions:
  - `read_group_exclusions(stage) -> List[CrossModuleExclusion]`
  - `write_group_exclusions(stage, exclusions: List[CrossModuleExclusion]) -> bool`
- Constraints:
  - `read_group_constraints(stage) -> List[BlendshapeConstraint]`
  - `write_group_constraints(stage, constraints: List[BlendshapeConstraint]) -> bool`

Implementation mirrors `USDStyleUtils` methods but rooted under `StandardPrimPaths.GROUP_EXCLUSIONS_ROOT` and `GROUP_CONSTRAINTS_ROOT`.

## Validation & Naming Rules
Apply in create/rename flows and UI inputs:
- Auto-convert spaces to underscores; reject illegal filesystem chars `[\\/:*?"<>|]`
- Prefer lowercase for group filenames to match docs examples
- Ensure required containers exist when writing (define if missing)
- Normalize `Sdf.AssetPath` to strings when reading/writing arrays

## UI — Group Section Wiring (`hair_qc_tool/ui/main_window.py`)
Implement per `docs/UI Mockup.md`:

1) Group list panel
- Single-selection list via row click; no multi-select
- Buttons: {Add}, {Rename}, {Delete}
- On select: load group into in-memory state; populate Module/Style tabs from this context

2) Alpha Whitelist expandable section
- Collapsible panel titled "Alpha Whitelist"
- Table with rows: [checked, texture path, actions]
  - Checkbox toggles inclusion (whitelist add/remove)
  - {Add} button to append new row (text input validation)
- On toggle/edit: write through to USD and save

3) Module whitelist editor
- Subsection per module type (Scalp, Crown, Tail, Bang)
- List current assets per type; per-row {Remove}
- {Add} opens file chooser scoped to `module/{type}/` under configured USD directory

4) Save & refresh behavior
- Write-through on edits with debounce, or explicit {Save Group}
- Use `USDStageManager.save_stage()`; refresh UI after writes
- Soft-refresh when switching groups; detect external changes on selection switch

## Minimal-Load & USD Rules Compliance
- Operate only on group USD stages; no geometry imports
- Get/define exact container prims; no renames of existing prims
- Use absolute prim paths for relationships
- Avoid full-stage loads; open only the Group file being edited

## Error Handling & UX
- Inline error banners for:
  - Missing `Group/` directory
  - Invalid asset paths in whitelists
  - Save failures
- {Revert} button to reload from disk if unsaved/dirty
- Subtle indicator if external changes detected on selection switch

## Integration Points
- Group-level rules feed Style timeline generation (later steps). Store-only here.
- Group module whitelist drives Style combinatorics; ensure deterministic ordering in arrays

## Acceptance Criteria
- Selecting a group shows its module whitelist and alpha whitelist
- Add/remove entries updates the USD on disk; UI updates without restart
- Create/rename/delete groups updates `Group/` and UI without restart
- Group-level exclusions/constraints can be authored and persist to disk
- All operations use prim-path targeting; no unintended restructures

## Test Plan
- Use `docs/TestDirectory/Group/` as sandbox; or configurable temp directory
- Cases:
  - Create new group; verify containers exist; read back empty lists
  - Add module assets for each type; read back; remove; idempotency
  - Add/toggle alpha whitelist entries across all categories; normalize asset paths
  - Add exclusions/constraints with valid absolute prim targets; read back equals written
  - Rename group; ensure stage reopens correctly
  - Delete group; ensure removal from list; no crashes on stale selection

## Implementation Notes
- Keep writes idempotent; sort arrays for stable diffs
- Debounce disk writes from UI (e.g., 300–500ms)
- Log all mutations via `logging_utils`
- Extend config if needed for base USD directory (`hair_qc_tool/config.py`)
