# Follow-up Questions & Technical Clarifications

## Responses to Your Answers & New Questions

### System Architecture & Data Flow

**Your Answer on Group USD Data**: Clear - Group USD files contain module lists for generating style combinations.

**New Q**: When you mention "style combinatorics" - do you mean all possible combinations of modules within a group (e.g., if a group has 3 crowns, 2 tails, 3 bangs = 18 possible styles), or do you mean the blendshape combinations within a single style?

A: Style Combinatorics = module combinations that come to gether to make a style, so your example of 18 styles is correct
Look Combinatorics, in the style animation timeline = all of the blendshape combinations in a style

### Module System & File Organization

**Your Answer on Scalp Module**: Understood - single scalp.usd for now.

**Your Answer on Staging vs Direct USD**: You're open to suggestions on best practices.

**My Recommendation**: For USD best practices, I'd suggest a hybrid approach:
- Load USD data into Maya's USD stage for viewing/editing
- Stage changes in memory (Maya's USD proxy system)  
- Explicit save operations write back to USD files
- This gives you the benefits of USD's change tracking while maintaining control over when files are written

**New Q**: Does this approach sound reasonable for your workflow needs?

A: yes this sounds good. 

### Texture & Material System

**Your Answer on Alpha Textures**: Only scalp has alphas currently.

**Your Answer on Materials**: Maya tool won't handle materials for now - can ignore/remove material sections.

**New Q**: Should I remove all material-related USD paths and code from the system design, or keep the structure but not implement the Maya UI for it (for future expansion)?

A: Lets remove the material related usd paths for now, We will implement in future but it will likley be very different from what we have now

**UNANSWERED from original**: The crown blacklist question - if a crown module blacklists a scalp alpha texture, does that affect ALL styles using that crown, or just specific crown-scalp combinations?

A: Right now there is only one scalp, lets say it affects all styles using that crown. That answer may change some day if more scalps are introduced, but that is unlikely. 

### Blendshape Rules & QC System

**Your Answer on Rules Storage**: Rules are stored in USD as shown in documentation, Maya tool generates them via UI.

**Your Answer on Cross-Module Rules**: You want rules to apply across all applicable styles, but unsure if they should be stored at group level vs style level.

**My Recommendation**: Based on your requirement that rules apply universally, I suggest:
- Store cross-module rules at the **Group level** in Group USD files
- Style USD files reference/inherit these group-level rules
- When a rule is created in one style, it's automatically saved to the group and applied to all applicable styles
- This eliminates duplication and ensures consistency

**New Q**: Does this group-level rule storage approach align with your vision?

A: Yes do it this way!

**Your Answer on Blacklists vs Exclusions**: Same concept, different names.

**New Q**: Should I standardize the terminology throughout the system? I suggest using "exclusions" everywhere for consistency.

A: Yes

### Animation & Timeline System

**Your Answer on Timeline Storage**: Permanently stored in Style USD, can be regenerated as rules update.

**Your Answer on Large Combinations**: Use the elegant combination handling from the Python code snippets.

**Your Answer on Rule Changes**: Manual regeneration for now, with visual highlighting of affected timeline regions if possible.

**New Q**: For the timeline visualization in Maya - should this use Maya's native timeline/animation system, or a custom UI widget? The native timeline might be limiting for showing thousands of combinations.

A: Lets use the native timeline. I am hoping that limiting each combination to 10 frames will help limit complexity. Remember we are only ever viewing the blendshape combinatorics of a single style.

**New Q**: When displaying "regions that would be eliminated" - should this be a color-coding system on the timeline, or a separate list/table showing affected frame ranges?

A: Color coding on the timeline would be optimal

### UI & Workflow Questions

**Your Answer on USD Management**: Open to suggestions, wants rapid QC workflow.

**My Recommendation**: For rapid QC workflow:
- Use USD stages for in-memory operations
- Batch save operations to minimize disk I/O
- Cache validation results but refresh when USD files change
- Use Maya's USD proxy system for fast geometry switching

**Your Answer on Lazy Loading**: Load only modules within a specific group, need fast display/hide.

**New Q**: Should module geometry be loaded as Maya references, USD references, or imported geometry? Each has different performance characteristics for show/hide operations.

A: I assume usd references would be fastest? I do not know the characteristics of each

**Your Answer on Style Validity**: Valid = in group combinations but not on disk, Invalid = references missing modules.

**New Q**: Should the tool also validate that all blendshapes referenced in Style USD files actually exist in their Module USD files? This could catch another class of "invalid" styles.

A: Actually yes, good catch.

### Technical Implementation

**Your Answer on USD APIs**: Open to custom abstraction layer for custom data types, wants easy extensibility.

**My Recommendation**: Create a hybrid system:
- Direct USD Python APIs for standard USD operations (geometry, animation, references)
- Custom utility classes for your specific data types (BlendshapeRules, CrossModuleExclusions, etc.)
- Pattern like: `style_utils.load_blendshape_rules(usd_stage)` and `style_utils.save_blendshape_rules(rules_data, usd_stage)`

**New Q**: Should these utility classes be designed as Maya plugins, or pure Python modules that can work outside Maya?

A: I honestly think that will vary on a case by case bases, I dont particulary care as long as the tool works as intended

**Your Answer on Maya Integration**: Shelf tool is sufficient.

**Your Answer on Code Organization**: Utilities in util folder for now.

### Data Validation & Error Handling

**Your Answer on Broken References**: Show errors in UI with options to remove bad data.

**New Q**: For the "remove bad data" option - should this remove the reference from the USD file, or mark it as disabled/inactive while preserving the reference for potential future repair?

A: This would be removing invalid usd and usd references in othere files, once the user presses a button to remove the invalid data I do not need any more references to it. 

**Your Answer on Invalid Combinations**: The QC tool's purpose is to let users determine and save invalid combinations.

**Clarification Needed**: This seems to contradict the exclusion/blacklist system. Are you saying:
- Users should be able to create any combination initially
- Then use the QC process to mark combinations as invalid/excluded
- The exclusion rules prevent those combinations in future timeline generation?

A: yes this is correct for both exclusions and constraints

**Your Answer on External Changes**: Want automatic pickup but not UI bloat, asking if stage updates would be sufficient.

**My Recommendation**: 
- Check for external file changes when switching groups/styles (natural refresh points)
- Add a manual "Refresh" button for immediate updates
- Show a subtle indicator when external changes are detected

**New Q**: Should the tool warn users if they have unsaved changes when external modifications are detected?

A: I think so. 

## New Technical Questions

### Performance & Scalability

**New Q**: Approximately how many modules do you expect in a typical group? And how many blendshapes per module? This will help optimize the combination generation algorithms.

A: each module will have ~3-4 blendshapes, and each group will have a completely variable number of modules (but likely no more than 20), but each style will only ever have 4 modules. 

**New Q**: For the timeline with thousands of combinations - should there be a maximum frame limit, or should it use a different time representation (like combination indices rather than frame numbers)?

A: I think a maximum frame limit would help keep the tool from braking if there are 2 many combinations. Lets default to 2000 frames and make sure that if we go over the UI clearly lets us know this. if timeline overload is to common we can refactor later, but atleast this limit will keep the tool from crashing. 

### File Management

**New Q**: Should the tool create backup copies of USD files before making changes, or rely on external version control?

A: Lets rely on external version control for now

**New Q**: When creating new groups/modules/styles, should there be naming validation rules (e.g., no spaces, special characters, etc.)?

A: Lets make sure no spaces, or characters that would break the file are included.

### UI/UX Details

**New Q**: For the scrollable lists in the UI mockup - should these support multi-selection for batch operations (e.g., selecting multiple styles to delete)?

A: NO, we never want multi selection, on this lists, we should modify one asset at a time.

**New Q**: Should there be keyboard shortcuts for common operations (like switching between module/style tabs, or regenerating timelines)?

A: I think that would be amazing. Can we create a hotkey menu at the top?

### Integration Points

**New Q**: Will this tool need to integrate with any existing pipeline tools, or should it be completely standalone?

A: For now standalone.

**New Q**: Should the tool support importing existing Maya scenes/geometry into the USD system, or will all assets be created externally and imported as USD files?

A: The module UI section currently has a description for how base mesh and blendshapes are added to the modules. Curretnly texture are added to the directory by hand and this is ok. 