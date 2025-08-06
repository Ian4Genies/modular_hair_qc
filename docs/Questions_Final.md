# Final Technical Clarifications

## System Design Confirmation

Based on your answers, I now have a clear understanding of the system. Just a few final technical clarifications to ensure optimal implementation:

### Performance & Technical Details

**New Q**: You mentioned 4 modules per style with ~3-4 blendshapes each = ~12-16 blendshapes total. Using the combination algorithm from the Python code, this could generate ~100-500 combinations per style. At 10 frames per combination, that's 1000-5000 frames. Does this align with your 2000 frame limit expectation?

A: that is amazing, lets limit to 6000 frames then, I do not think that will break maya

**New Q**: For USD references performance - you're correct that USD references are typically fastest. Should I implement geometry loading as:
- USD references that stay as USD proxies in Maya (fastest switching)
- USD references that get imported to Maya geometry (better for blendshape manipulation)

A: lets use imported geo for simplicity for now. If the tool slows down we can refactor to the more complex USD blendshape implementation later!

### UI Implementation Details

**New Q**: For the hotkey menu at the top - should this be:
- A traditional Maya menu bar item with keyboard shortcuts
- A custom widget within the tool window showing available hotkeys
- Both?

A: Both - add a "Hair QC" menu to Maya's main menu bar with keyboard shortcuts for discoverability, plus a compact hotkey reference widget at the top of the tool window for quick reference. This follows Maya's standard approach for professional tools. Lets do a custom wid

**New Q**: For timeline color-coding of "regions that would be eliminated" - should eliminated regions be:
- Grayed out/dimmed (still visible but clearly marked as invalid)
- Red/warning color (clearly marked as problematic)
- Hidden entirely until "Show Invalid" is toggled

A: red warning color

### Module Creation Workflow

**New Q**: In the Module UI section, when a user adds a base mesh from the Maya scene - should the tool:
- Copy the mesh geometry into the Module USD immediately
- Create a reference to the Maya scene file
- Import the mesh and then allow the user to save it to USD when they hit "Save Module"

A: the mesh will be in scene (loaded seperately from the tool) and I think it should be saved to the USD as geometry data

### Cross-Module Rules Implementation

**New Q**: For group-level rule storage - when a user creates a rule in Style A, and it gets saved to the group level, should:
- All other applicable styles automatically regenerate their timelines
- Other styles show a "Rules Updated" indicator and require manual regeneration
- Rules only apply to newly created styles (existing styles keep their current timelines)

A: So I think rules should only need to be caught once, IE if a style A is QC'd then style B is QC'd it would be extremely rare that the second style QC'd would affect the first, because QC issues should have already been caught on the first. I think flagging this in the list would be sufficient, but I think it will  rarely or never happen. It would mean that the QC'er missed something on the first pass.

### File Naming & Validation

**New Q**: For naming validation, should the tool:
- Auto-convert spaces to underscores (user types "long crown simple" → becomes "long_crown_simple")
- Reject names with spaces and show an error
- Both options available to the user

A: auto conversion seems file

## Implementation Approach Confirmation

Based on all your answers, here's my planned implementation approach. Please confirm this aligns with your vision:

### Architecture Summary:
1. **USD System**: Group-level rules, Style-level animation, Module-level assets (no materials for now)
2. **Maya Integration**: Shelf tool, USD stages with explicit save, native timeline with color coding
3. **Performance**: 2000 frame limit, USD references, lazy loading by group 
4. **UI**: Single-selection lists, hotkey menu, manual timeline regeneration with visual indicators
5. **Validation**: Real-time USD reference checking, blendshape existence validation
6. **File Management**: External version control, naming validation, clean removal of invalid data

**Final Q**: Does this summary accurately capture the system you want built?

A: 600 frame limit, otherwise yes. 