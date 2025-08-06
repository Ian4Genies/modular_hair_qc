# Questions for Hair QC System Design

## System Architecture & Data Flow

Q: The documentation mentions both "Group USD files" and "group USD data" - are these the same thing? How does the Group USD file relate to the individual module USD files it references?

A: Group usd data and group usd files are basically the same thing, though i think files referes to a plurality of usd group files (long.usd, short.usd for example), and group usd data sounds like it refers to the data inside of a group usd file. Group usd files include a list of modules that are a part of that group, those modules are later used to generate style combinatorics.

Q: In the USD directory structure, I see both `Group/short.usd` and `Group/long.usd` files, but the UI mockup shows groups like "braided", "medium", "spiked". Are these just examples, or is there a mismatch between the expected group types and the USD structure?

A: These are example of group names that could exist in the future. No group name should be hard coded into the system, this represents a possible list of usd groups that would be procedurally loaded into the menu

Q: The blendshape rules document shows Python code for generating combinations, but the USD system uses native USD animation. Should the Maya tool generate USD animation data directly, or should it use a hybrid approach?

A: The python code in the blendshape rules document is from a different system, and the only thing that should be gathered from it is generally how combinatorics, validation, and possibly how weight maxiumums could be added into the timline. In general I want the timeline to both be represented in teh maya viewport timeline and the style usd. I am open to different ways for how that relationship can be managed

## Module System & File Organization

Q: The scalp module is described as "required for all styles" and there's only one `scalp.usd` file shown. Does this mean there's only ever one scalp module, or should there be multiple scalp variations like `short_scalp.usd`, `long_scalp.usd`?

A: Currently there is only one scalp.usd and there is no expectation that will change. If it does change later we will refactor, but that does not need to be accounted for in this design/tool

Q: Module naming conventions show `<group>_<module>_<name>.usd` but the directory examples show files like `Long_crown_simple.usd`. Should the group name be capitalized or lowercase? Should it match exactly with the Group USD filename?

A: These can be lower case, that is a typo, these should match exactly

Q: When a new module is created in Maya, should it immediately create a USD file on disk, or should changes be staged in memory until explicitly saved?

A: I think it should be staged, but I am fairly novice with usd. I am open to suggestions on best practices here. My design shows the modules being staged then explicitly saved but again I am open to opetions you think would be better, like operating directly from the usd if that is better

## Texture & Material System

Q: The two-level alpha texture system (Group whitelist + Module blacklist) seems complex. Can you clarify: if a crown module blacklists a scalp alpha texture, does that affect ALL styles using that crown, or just specific crown-scalp combinations?

A: 

Q: Alpha textures are stored in the scalp module directory (`module/scalp/alpha/`), but other modules can blacklist them. Should non-scalp modules also have their own alpha directories, or do all alpha textures live under scalp?

A: Currently only scalp includes alpha, we do not need to account for other modules having alphas at this stage in develpoment

Q: The USD reference mentions "basic shader parameters only" and that texture connections will be "procedurally assigned in Blender". Does this mean the Maya tool won't handle material assignments at all, or just won't store them in USD?

A: currently the maya tool does not handle material assignments, we will build this out in another iteration of the tool. Honestly the material section can probably be ignored/removed in the usd for now. 

## Blendshape Rules & QC System

Q: The blendshape rules document shows complex hardcoded constraints in Python. How should these translate to the USD constraint system? Should the Maya tool generate USD constraint data, or maintain a separate rules database?

A: If you look in the usd_summary and other usd documents you will see sections and paramaters for storing these rules. There will be no hard coded python rules like in that example. THe maya tool explicitly generates these rules, as seen in the UI Mockup

Q: Internal module exclusions (like `volumeIn` <-> `volumeOut`) are stored in Module USD, but cross-module exclusions are in Style USD. What happens if the same exclusion rule applies to multiple styles? Is there duplication, or a shared reference system?

A: I am not sure on this, I was hoping that within a group, all external (between more than 1 modules) exclusions and rules could be saved to their respective styles, but loaded into one big group pool at runtime that could be referenced against and automatically added to all styles? I could be severly off on this design, and maybe the rules should be saved at the group level? I am not sure what is better and more efficent, but YES it is very important that when a rule is generated on one style, it is enforced on other applicable styles that include the same modules, IE if crown_A and tail_B have a rule, then that rule should be applied when the style is crown_A tail_B bang_C or crown_A tail_B bang_D etc.

Q: The document mentions "blendshape blacklists" at both module and style levels. How does this differ from "blendshape exclusions"? Are these the same concept with different names?

A: same concept different names

## Animation & Timeline System

Q: The style editing UI shows a complex timeline system with combinatorics. Should this timeline data be generated fresh each time a style is loaded, or permanently stored in the Style USD file?

A: Permantly stored in style USD file, then referenced in to the scene. It needs to be able to be regenerated in the timeline as rules for that style update, and then saved back out to the style usd.

Q: The animation system mentions "deterministic run through of all weight combinations". How should the Maya tool handle styles with many blendshapes that could generate thousands of combinations? Should there be limits or optimization strategies?

A: Yes, That is the main reason I included the code snippets in Blendshape Rules. I think the combinations is handled elegantly there and does a good job of minimizing bloat.

Q: When blendshape rules change (like max weight constraints), should the Maya tool automatically regenerate all affected animation timelines, or should this be a manual operation?

A: Some tday I would like this to be automatic, but for the time being I need a manual version fo this tool for testing. If it was possible to highlight regions of the timeline that would be eliminated based on current rules, if the timeilne were regenerated that would help a lot. 

## UI & Workflow Questions

Q: The UI mockup shows the ability to add/remove groups, modules, and styles. Should the Maya tool handle USD file creation/deletion directly, or should it work with a separate USD management system?

A: I honestly do not know the answer to this questions. The purpose of this tool is to update the USD files on disk. I am ok if that happens in real time, but I assume changes made in scene would be made on the stage then need to be pushed to the usd directory on disk? I am mostly rellying on you to make sure the USD implementation is correct and what best suits this project, wich is a QC tool that should rapidly parse through objects as fast as the QC'er can go.

Q: The lazy loading concept is mentioned for performance. Should the Maya tool load full USD scenes into Maya, or work with USD data without importing geometry until specifically requested?

A: I Think considering the very large quantity of usd data that will eventually be linked into this system it would not make sense to load everything at once. I think the broadest set of geometry that should ever be imported is the modules under a specific group, wich should be somewhat limited in scope always, and will need to be quickly displayed/hidden very often. 

Q: The UI shows both "valid" and "invalid" styles in the style selection menu. How should the Maya tool determine validity? Should it validate USD references in real-time, or cache validation results?

A: Valid styles constitute combinatorics that are currently listed in at the group level. The {generate} button looks at all modules assocaited with the group, and generates valid module combinatorics. This list is then compared to what is actively on disk. If styles are listed in valid combinations, but not on disk, that style is listed as valid, and the {add} button would ad its .usd file to the directory. If a style is composed of one or more modules that no longer exist on disk, that style is invalid. 

## Technical Implementation

Q: The system uses both USD native schemas and custom data structures. Should the Maya tool use USD Python APIs directly, or would you prefer a custom abstraction layer for USD operations?

A: I do not know. I don't think the usd functionality described here is too custom? but some of the data I exepect to store in the USD is as you say not native to usd, and being used more like a json file attached to the usd. So for those custom data types, a custom util save load setup that coudl be used every time each type of custom data was stored would make sense. something like style.load.blendshapeRules save.blendshapeRules, somethign like taht, Again I am rellying on you to make the blendshape side of this work correctly and efficiently. I think making things easy top manually extend and add features to wil be a huge plus. 

Q: For the "main script that launches this menu in maya" - should this be a Maya shelf tool, a menu item, or both? Are there any specific Maya integration requirements?

A:  a maya shelf tool would be more than sufficient.

Q: The documentation mentions "reusable utility scripts". Should these be organized as a Python package, or as individual Maya modules? Do you have preferences for code organization?

A: I think for now jsut iclude utilties nicely organized under a util folder and later on we can talk about splitting them out if needed.

## Data Validation & Error Handling

Q: When USD references are broken (like missing module files), how should the Maya tool handle this? Should it show errors in the UI, attempt repairs, or prevent loading?

A: show errors in the UI, with options to remove that bad data.

Q: The system allows for complex blendshape combinations that might be invalid. Should the Maya tool prevent invalid combinations from being created, or allow them with warnings?

A: The point of the QC tool and rules is to allow a user to determin invalid blendshape combinations and save them to the usd directory

Q: If a user modifies USD files outside of the Maya tool, how should the tool detect and handle these external changes?

A: That is a great question. I would love for these and other changes to be picked up automaticaly but I dont want to over bloat the UI. I think there are multiple moments when the stage is being updated during the use of this tool correct? would that be sufficient to pickup external changes? 