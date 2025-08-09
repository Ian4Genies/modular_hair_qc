# Step 2 — USD Utility System (Work Log)

Track granular tasks for Step 2 from `task_list.md`. Follow prim paths in `docs/USD_paths.md` and technical patterns in `docs/USD_reference.md`. Viewport loading must be minimal (proxy-based).

## Scope
- Group utils: whitelist reading, discovery
- Module utils: blendshapes listing, alpha blacklist reading
- Style utils: module references, cross-module exclusions, weight constraints
- Stage helpers: open/create/save, get-or-define prim
- Viewport ops: proxy creation, load/unload prim, set USD blendshape weights

## Checklist
- [x] Canonical prim paths (`StandardPrimPaths`) for Group/Module/Style
- [x] Stage helpers (`USDStageManager`) + simple mtime cache
- [x] Group utils (`USDGroupUtils.list_groups`, `read_module_whitelist`, `read_alpha_whitelist`)
- [x] Module utils (`USDModuleUtils.list_blendshape_names`, `read_alpha_blacklist`)
- [x] Style utils (read module refs; read/write exclusions; read/write constraints)
- [x] Viewport minimal-load ops (proxy-based)
- [x] BlendshapeRules serialization (AnimationRules block) — read/write
- [x] Logging integration for utils
- [x] Smoke test / debug command in UI
- [ ] UI data refresh wiring (modules/styles population beyond basic listing)

## Notes
- Readers are resilient to missing prims/attrs and return empty structures.
- `Sdf.AssetPath` values normalized to strings where applicable.
- Writers create container prims when absent and set relationships/attributes idempotently.

## Follow-ups
- Implement additional UI wiring: load module/style data and state into editors; show exclusions/constraints.
- Add asset path resolver helpers if needed for validation workflows.
