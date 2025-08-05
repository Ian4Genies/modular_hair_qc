This should be constructed as one coherent menu. There will be instances where multiple versions of the same portion of the menu will be shown. Check labeling for clarity.

The general flow of the menu will be
- Group selection
- Module/style tab
	- which allows the bottom portion of the menu to swap between the module tab and style tab.
	- Module menu
		- allows for the creation and editing of modules
		- Allows for adding of module blendshapes
		- Allows for the editing of module blendshape internal exclusions
	- Style menu
		- Allows for the generating of style combination lists
		- Allows for the editing of blendshape combinatoric max weight rules
		- pupulates the timeline with the blenshape combinatorics of the active style
		- 


# Group Section
This is the top most section of the UI and defines which group USD Data should be loaded from/Added to. In the below modules menu, the modules should all be loaded from/added to to from the group selected here. In the below style menu all styles should be loaded from/added to this groups module combination.

## Features
- a list of all groups inside of the directory. From this list groups can be selected, added, and their names can be changed.
- Underneath the group list is a expandable section that allows alpha white list curation. 
	- Note: all alphas available should be white listed by default 
- Group Selected will populate other menus (module/style) with that groups data.

## Mockup
>Start
Title: Select group
______________________________________________________________________
Note: This section, and all other mockup tables in this UI Mocup doc, should be a scrolling list, also scalable independently in Y within the window.
Note: This section shows all of the group usd files currently available in the directory


| group name |     |       |
| ---------- | --- | ----- |
| long       |     |       |
| short      |     |       |
| braided    |     |       |
| medium     |     |       |
| spiked     |     |       |
|            |     | {Add} |

______________________________________________________________________
:LiArrowDownSquare: Alpha Whitelist

______________________________________________________________________
Note: This section contains the expandable menu contents under "Alpha Whitelist"
Note: 🟩 denotes a checked box for a whitelisted alpha while :LiSquare: denotes an unchecked box for a blacklisted alpha. The add button adds a new section under which a new texture path string can be added.
Note: when a Group is made for the first time all of available alphas should be white listed. 

| whitelisted | texture path                         |       |
| ----------- | ------------------------------------ | ----- |
| 🟩          | scalp/apha/fade/lineUp.png           |       |
| 🟩          | scalp/apha/fade/midFade.png          |       |
| 🟩          | scalp/apha/hairline/balding.png<br>  |       |
| :LiSquare:  | scalp/apha/hairline/bell.png<br>     |       |
| 🟩          | scalp/apha/sideburn/outward.png<br>  |       |
| 🟩          | scalp/apha/sideburn/pointMid.png<br> |       |
|             |                                      | {Add} |
______________________________________________________________________

:LiArrowDown: Module/Style section under here.
______________________________________________________________________
>End

# Module Style Tab

underneath the Group menu is a simple tab system that lets the user swap betweena module menu and a style menu. The group menu above should remain visible at all times, allowing the user to swap between groups while in the module style tab. By default the module menu should be the active tab when the menu is first loaded. 
## Mockup

>Start
______________________________________________________________________
/ Module /  Style /
______________________________________________________________________
>End

# Module Menu

## Staging and usd data
When  a group is selected, the process of lazy loading its modules should begin. When a module is selected in this menu, it should be shown in the scene.  Changes made to the module in the module edit menu should be first updated in the scene/stage, then when the save button is pressed, the staged edits should be pushed to disk. New modules will need to be added to disk immediately as a default module usd. then this module should be added to the stage so edits can be staged and pushed out in the same process described above. 
## Mockup

### Module menu with no selection
>Start
______________________________________________________________________
/ ==Module== /  Style /
______________________________________________________________________
Title: Module Selection
______________________________________________________________________
Note: currently the one scalp.usd module is used for every style

| selection  | type  | name        |       |
| :--------- | ----- | ----------- | ----- |
| :LiSquare: | scalp | scalp       |       |
| :LiSquare: | crown | simple      |       |
| :LiSquare: | crown | braided     |       |
| :LiSquare: | crown | fancy       |       |
| :LiSquare: | tail  | braided     |       |
| :LiSquare: | tail  | pony        |       |
| :LiSquare: | tail  | beaded      |       |
| :LiSquare: | bang  | straightCut |       |
| :LiSquare: | bang  | messy       |       |
| :LiSquare: | bang  | parted      |       |
|            |       |             | {Add} |
______________________________________________________________________
:LiArrowDownSquare: Edit Module
______________________________________________________________________
Note: the expandable Edit Module menu toggle button is greyed out and closed when no module is selected

>End

### Module menu with existing module selected 
>Start
______________________________________________________________________
/ ==Module== /  Style /
______________________________________________________________________
Title: Module Selection
______________________________________________________________________
Note: currently the one scalp.usd module is used for every style

| selection  | type  | name        |       |
| :--------- | ----- | ----------- | ----- |
| :LiSquare: | scalp | scalp       |       |
| ==🟩==         | ==crown== | ==simple==      |       |
| :LiSquare: | crown | braided     |       |
| :LiSquare: | crown | fancy       |       |
| :LiSquare: | tail  | braided     |       |
| :LiSquare: | tail  | pony        |       |
| :LiSquare: | tail  | beaded      |       |
| :LiSquare: | bang  | straightCut |       |
| :LiSquare: | bang  | messy       |       |
| :LiSquare: | bang  | parted      |       |
|            |       |             | {Add} |
______________________________________________________________________
:LiArrowDownSquare: Edit Module
______________________________________________________________________
NOTE: Drop Edit Module section can now be expanded, and it contents are show below
Name: "simple" 
Type: Crown (this should be an enum dropdown of all module types)
______________________________________________________________________
Base Mesh: Loaded {Replace}
______________________________________________________________________
Blendshapes
______________________________________________________________________
Note: this section allows the user to add, remove, rename, view, and exclude blendshape data from the module. 

Note: Exclusions - Selecting a module allows the user to view and change what other blendshape are excluded from use alongside the selected blendshape, internal to the module. For example in this section volumeIn is selected, show that volumeOut is excluded. If volumeOut was selected it would show that volumeIn was excluded.  this can be updated by the user using the checkboxes. 
Note: {remove}. This will allow the user to remove the a blendshape and all of its dependent exclusion data from the module.

Note: name - This allows the blendshape in the USD to be renamed. 
Note: Blendshape Weight: this section simply controls the weight of the corresponding blendshape for view in scene. all blendshapes in this menu should be actively attached to the module as blendshapes controllable here. 

Note: {Add} this button would add the selected mesh object in scene to the active module as a new blendshape. if the selected object is not a mesh, or invalid as a blenshape, return an error and do not create a new blendshape on the usd. By default the name of the mesh will be set as the new blendshape name. If another module is selected it should be deselected and the new created blendshape should be the new selection

| selection  | name         | Blendshape Weight                                 | excluded   |          |
| ---------- | ------------ | ------------------------------------------------- | ---------- | -------- |
| :LiSquare: | curly        | < ----------------------------\|------------>     | :LiSquare: | {remove} |
| :LiSquare: | hairline     | < ----------------\|------------------------>     | :LiSquare: | {remove} |
| ==🟩==     | ==volumeIn== | ==< ----\|------------------------------------>== | :LiSquare: | {remove} |
| :LiSquare: | volumeOut    | < ----------------------------\|------------>     | 🟧         | {remove} |
| :LiSquare: | lengthen     | < ----------------\|------------------------>     | :LiSquare: | {remove} |
|            |              |                                                   |            | {Add}    |
______________________________________________________________________
{Save Module}
Note: {Save} - save any staged updates to their corresponding USD files.

>End

# Style Menu

## Initialization
The first time the style menu is opened for a new group, the group should have already been set up with modules, but style combinations between the modules in the active group will not have been generated. The first button at the top of this menu {Generate} will generate this combinations, along with paths to where they should be in the directory and save then save this list to the group usd (NOTE: this is not yet included in our existing USD scoping). This list of possible combinations is NOT the same as the list of active style usd files on disk, and the two will need to be reconciled against eachother. For example, there will often be more possible combinations than exist on disk. In this case next to the {Generate} button will be an {Add Missing} button wich wil add to the usd directory all styles that are possible and listed on the group.usd, but not currently added as style.usd. Inversely if modules have been removed from directory, some styles may no longer be possible. These need to be flagged in the style list, and can be removed in bulk using the {cull invalid} button. On each style in the list there will also be buttons that allow possible styles, or invalid styles to be individually added/removed. see mockup below. 

## Mockup
>Start
______________________________________________________________________
/ Module /  ==Style== /
______________________________________________________________________
Title: Style Selection
______________________________________________________________________
{Generate} {Add Valid} {Cull Invalid}

| :LiSquare: | Status     | crown          | tail        | bang        |          |
| ---------- | ---------- | -------------- | ----------- | ----------- | -------- |
| :LiSquare: | active     | simple<br>     | braided     | straightCut |          |
| ==🟩==     | ==active== | ==simple<br>== | ==braided== | ==messy==   |          |
| :LiSquare: | active     | simple<br>     | braided     | parted      |          |
| :LiSquare: | active     | simple<br>     | pony        | straightCut |          |
| :LiSquare: | active     | simple<br>     | pony        | messy       |          |
| :LiSquare: | active     | simple<br>     | pony        | parted      |          |
| :LiSquare: | active     | simple<br>     | beaded      | straightCut |          |
| :LiSquare: | active     | simple<br>     | beaded      | messy       |          |
| :LiSquare: | active     | simple<br>     | beaded      | parted      |          |
|            | valid      | braided<br>    | braided     | straightCut | {add}    |
|            | valid      | braided        | braided     | messy       | {add}    |
|            | valid      | braided        | braided     | parted      | {add}    |
|            | valid      | braided        | pony        | straightCut | {add}    |
|            | valid      | braided        | pony        | messy       | {add}    |
|            | valid      | braided        | pony        | parted      | {add}    |
|            | valid      | braided        | beaded      | straightCut | {add}    |
|            | valid      | braided        | beaded      | messy       | {add}    |
|            | valid      | braided        | beaded      | parted      | {add}    |
|            | invalid    | fancy<br>      | braided     | straightCut | {remove} |
|            | invalid    | fancy          | braided     | messy       | {remove} |
|            | invalid    | fancy          | braided     | parted      | {remove} |
|            | invalid    | fancy          | pony        | straightCut | {remove} |
|            | invalid    | fancy          | pony        | messy       | {remove} |
|            | invalid    | fancy          | pony        | parted      | {remove} |
|            | invalid    | fancy          | beaded      | straightCut | {remove} |
|            | invalid    | fancy          | beaded      | messy       | {remove} |
|            | invalid    | fancy          | beaded      | parted      | {remove} |
Note: when a style is selected it should become visible in the viewport, and its animation timeline should be loaded. (if another style was previously selected that animation key data should be dumped from the scene, unless you find that overly inefficient, maybe lazy loading provides better ways to associate and disassociate animation data)

Note: in the style menu above, the fancy crown no longer exists in the usd dir. So the status is set to invalid, the option button is set to {remove}. this will remove the individual items from the group.usd (in this case long.usd) valid style combo list, the usd style file wich references missing modules will be removed from the directory, and this list will be reloaded. {cull Invalid} does the same thing but across all of the invalid styles at once. the list should reflow to reflect any changes

Note: in the style menu above, the braided crown module has just been added, and the {generate} button has been pressed, wich has added all newly valid styles to the list. These style usd files do not currently exist on disk. So they are marked as valid, and the context button next to each item that is valid says {Add}. This add button will generate a style.usd for that valid combo. The {Add Valid Button} will batch add all current valid items. The list should reflow to reflect any changes

Note: in the style menu above, the long_simple_braided_messy.usd style is selected. The expandable Edit Style menu below will be populated with the data from this style, and will edit this style.
______________________________________________________________________
:LiArrowDownSquare: Edit Style
______________________________________________________________________
Note: Editing style is a complex multilayered system. You will find example for how style combinatorics are created and added to the timeline as keyframes in [[Blendshape Rules]]. The mockup below demonstrates one frame of data in that combinatoric timeline that should demonstrate all of the features.

Note: The style itself is comprised of modules. The style is used to create "Looks", see terminology.md.  In blendshape rules you will see that for each combination of blendshapes across all of a styles modules, every possible combination is calculated and added to the animation timeline. The menu below tracks data in relation to those combinatorics in the animation timeline. For example, the active column shows what blendshapes are currently actively being combined in the timeline. The blendshape weight column shows the active blendshape weight of each module blendshape, but is also a slider that can be tweaked to test each blendshape individually without changing animation frame (basic functionality of all blendshape sliders).  Where things get tricky is the selection, max, and exclude columns. This is where blendshape rules are created. Selection is limited to blendshapes that are currently active on this frame of the combinatoric timeline.   When a blendshape is selected, the max and exclude sections are populated (as with all of these selection menus, only one list item can be selected at a time).  For example, when volumeIn on the simple crown is selected, max and exclude are populated with volumeIn's relationships to other blendshapes. Simple crown volumeOut is already excluded at the module level so that exclude checkbox is greyed out. There is no reason to set a max weight relationship for VolumeOut because it is fully exclude, so that section is also greyed out, but noted as excluded. The Other blendshapes of this module do not get a check box because they should be excluded at the module level, so changes can not be made here. This would be consistent across any blendshape that is selected, the other blendshapes on the same module would not be excludable here. You will notice their max is still setable, while the max on volume out is not. For blendshapes on other modules, the exclude option is togglable. toggleing eclude on ensures that blendshape is never combined with volumeIn when combinatorics are generated, and visa versa. If bang messy lengthen, was excluded, that would actually make this style invalid and Regenerating timeline would remove it from the timeilne in scene.  No while still selected on crown simple volume in, we can also set blendshape weight maxes for valid blendshape combinations in this look. For example when crown simple volumeIn, Bang messy lengthen, and bang messy spread are all included in a look, their max blendshape weights during combinatorics should be set as show in the table. This value should be editable from the list menu below. 

Note: when a style is created, or when a style is updated, all style rules should be check against eachother. IE if I create a rule or exclusion between tail_braided_lengthen and bang_messy_lengthen, I should also add that rule to any other style that includes, tail_braided, and bang_messy, wich will save the QC'er time. also when a new style is created in any way, including the style selection menu above, it should search through other existing styles for existing relevant rules. 

{Regenerate Timeline}
Note: this button will regenerate the timeline of blendshape animations base on update exclusions and max weights to remove blacklisted or rulled out combinations. 

| active | selection  | type      | Name       | blendshape   | Blendshape Weight            | Max    | exclude    |
| ------ | ---------- | --------- | ---------- | ------------ | ---------------------------- | ------ | ---------- |
| 🟨     | :LiSquare: | crown     | simple     | lengthen     | < ---\|---------------->[.2] | 1      |            |
| 🟨     | :LiSquare: | crown     | simple     | curly        |                              | 1      |            |
| ⚫      | :LiSquare: | crown     | simple     | hairline     |                              | 1      |            |
| 🟨     | ==🟩==     | ==crown== | ==simple== | ==volumeIn== |                              | ==.8== |            |
| ⚫      | ⚫          | crown     | simple     | volumeOut    |                              | X      | ⚫          |
| ⚫      | :LiSquare: | tail      | braided    | lengthen     |                              | 1      | :LiSquare: |
| ⚫      | ⚫          | tail      | braided    | wavy         |                              | 1      | 🟧         |
| ⚫      | ⚫          | tail      | braided    | spread       |                              | 1      | :LiSquare: |
| 🟨     | :LiSquare: | bang      | messy      | lengthen     |                              | .7     | :LiSquare: |
| 🟨     | :LiSquare: | bang      | messy      | frizzle      |                              | 1      | :LiSquare: |
| ⚫      | ⚫          | bang      | messy      | spread       |                              | .9     | :LiSquare: |
{Save Timeline}
Note: the animation timeline will include every blendshape combinatoric for this style as described in the blendshape rules document. The purpose of this tool is to allow for the QC and culling of bad data from that timeline. When the QC'er is complete with QC the animation timeline for this style should be saved to the style.usd. in this case long_simple_braided_messy.usd