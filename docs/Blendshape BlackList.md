The blendshape blacklist are collections of blendshapes that should not be animated together, and thus should not be included together when combinations are generated. These blacklists are stored at two levels 
- inside of the module usd for each module
	- this includes blendshapes that were designed to work independently and do not interact well, example volumeIn <-> volumeOut, increase_lenght <-> decrease length. 
- inside of the style usd for each style
	- This is for bad blendshape interactions between modules, crown.volumeUp <-> bangs.volumeUP would be blacklisted if thier interaction is so bad it cannot be salvaged with a blendshape rule

as with blendshape rules, it is not on the system to determine these bad interactions. It is for an artist to decide, implement, and log in usd data uding the QC UI in maya.