
# What are Blendshape rules
Below is an example of one of our more complex asset combinations. It consists of 4 mesh modules, with 10 blend shapes between them. The purpose of our blendshape rule system is to allow QC of the interactions between blendshapes of different modules. for example Lengthen, curly, and volume up on crown will each need to be tested against to 7 blendshapes on the 2 other modules. Blendshapes on the same module are assumed to work together. 

## Blendshape sample
- scalp
- crown
	- lengthen
	- curly
	- volume up
- Tail
	- lengthen
	- wavy
	- spread
- Bangs
	- lengthen
	- frizzle
	- spread
	- volume up

## Where are rules stored?
Rules will be stored inside of the style USD for the current style. 

## How are rules created
The system is not responcible for determining these rules. An artist will determin these rules and output them to usd using the QC interface.
## What is done with QC rules
The purpose of the QC rules are to limit blendshape weights during a deterministic run through of all weight combinations. IE if we are firing crown.lengthen blendshape, and it has a QC rule set for tail.lengthen that rule would limit what weights values were allowed. This is not a binary relationship tho. IE a rule relathionship would look something like Crown.lengthen > .8  tail.lengthen >.4.

During the deterministic run through of all blendshape values, all blendshapes should be combined similar to this function. The main difference between the system below and what we need, is that after combinations are created we would also need to parse the blendshape rules to ensure that the max weighting for each combination animation is = to the blendshape combo rule. 

below their are 3 functions of importance
- generate_combinations()
	- This function determines all unique combinations of blendshapes and outputs those combinations
- get_all_valid_param_sets
	- This function as is uses hard uniquitous rules to determin invalid combinations and remove them from the list.
	- In our system these rules will be culled from blendshape blacklists, wich will be generated and listed on module and style usd files, we will have no ubiquitous rules.
- set_up_combinations
	- 

```python
def generate_combinations():
    """
    Generates all unique combinations of shape keys from all meshes in the scene.
    e.g. given a Crown and Bangs asset, returns all of the different unique
    parameter sets which willoutput a viable hairstyle.
    """
    print("[RANDOMIZER] Generating combinations of shape keys.")
    data = {}
    for obj in bpy.data.objects:
        if obj.type == 'MESH':
            if obj.data.shape_keys:
                shape_keys = obj.data.shape_keys.key_blocks

                # Exclude 'Basis' which is the default shape key
                available_keys = [key for key in shape_keys if key.name != 'Basis']

                if not available_keys:
                    continue

                data[obj.name] = get_all_valid_param_sets(obj.name, available_keys)

    # Extract categories and their asset lists
    meshes = data.keys()
    asset_lists = [data[mesh] for mesh in meshes]

    # Generate all possible combinations
    combinations = list(product(*asset_lists))
    list_combinations = []
    for combo in combinations:
        list_combo = []
        for entry in combo:
            for key in entry:
                list_combo.append(key)
        if list_combo not in list_combinations:
            list_combinations.append(list_combo)
```

The goal of get valid params is correct, but our implementation will pull invalid combos from module and style usd files. 
```python
def get_all_valid_param_sets(mesh_name, shape_keys):
    """
    Gathers all valid parameter sets from the shape keys of a mesh. A valid set is defined as
    a combination of shape keys that contains unique categories of parameters without conflicting values.
    e.g. ["length_increase", "bang_length_increase"] is valid, but ["length_increase", "length_decrease"] is not.
    """
    print(f"[RANDOMIZER] Getting all valid parameter sets from shape keys: {shape_keys}.")
    valid_sets = []

    for r in range(1, len(shape_keys)+1):
        for combo in combinations(shape_keys, r):
            combo_str = [k.name for k in combo]
            #checker
            has_fix_shape = False
            for key_name in combo_str:
                if "fix_" in key_name:
                    has_fix_shape = True
                    break
            if has_fix_shape:
                continue

            if ("texture_wave" in combo_str and
                    ("bangs" in mesh_name.lower()
                     or "hair_0006" in mesh_name.lower()
                     or "hair_0133" in mesh_name.lower()
                     or "tail_customGenie_0237" in mesh_name
                     or "tail_hair_0035" in mesh_name
                     or "tail_hair_0152" in mesh_name)):
                continue
            if "thickness_increase" in combo_str and "strands_customGienie_0152" in mesh_name:
                continue
            if ("length_increase" in combo_str and
                    ("tail_customGenie_0229" in mesh_name
                     or "tail_hair_0021" in mesh_name
                     or "tail_hair_0035" in mesh_name
                     or "tail_hair_0153" in mesh_name
                     or "tail_hair_0147" in mesh_name)):
                continue

            if not ("length_increase" in combo_str and "length_decrease" in combo_str) \
                and not ("bang_length_increase" in combo_str and "bang_length_decrease" in combo_str) \
                and not ("volume_in" in combo_str and "volume_out" in combo_str) \
                and not ("volume_increase" in combo_str and "volume_decrease" in combo_str) \
                and not ("strand_thickness_increase" in combo_str and "strand_thickness_decrease" in combo_str):
                    valid_sets.append(combo)
    return valid_sets
```


again the idea of what set_up_combinations is doing is correct, but instead of having hard coded limitations on max key value, this combinations will be stored and referenced from style usd files.  also this animation data will not be set on a frame by frame basis but set up as described in the QC Timeine Design Doc

```python
def set_up_combinations(start_frame = 10, frame_step = 10, randomize = False):
    """
    Sets up the scene with all possible combination of shape keys (parameters).
    Every frame_step frames represents a unique combination of shape keys across all meshes in the scene.
    @start_frame: The frame to start the animation from.
    @frame_step: The step size for each frame increment.
    @randomize: If True, shuffles the parameter combinations for more variance between close frames.
    """
    remove_empty_groups()
    modules = get_all_modules()
    pre_adjustments(modules)
    combinations = generate_combinations()

    if start_frame != 0:
        for obj in bpy.data.objects:
            if obj.type == 'MESH' and obj.data.shape_keys:
                for key in obj.data.shape_keys.key_blocks:
                    if "fix" not in key.name:
                        key.value = 0.0
                        key.keyframe_insert(data_path="value", frame=0)

    current_frame = start_frame
    i = 0
    if randomize:
        random.shuffle(combinations)
    crown = modules["crown"]
    for combo in combinations:
        # Reset all shape keys to 0
        for obj in bpy.data.objects:
            if obj.type == 'MESH' and obj.data.shape_keys:
                for key in obj.data.shape_keys.key_blocks:
                    if "fix" not in key.name:
                        key.value = 0.0
                        key.keyframe_insert(data_path="value", frame=current_frame)

        # Apply the current combination
        for key in combo:
            key.value = 1.0
            if crown:
                if ("crown_customGenie_0080_jadonSancho" in crown.name
                        or "crown_customGenie_0087_willSmith" in crown.name
                        or "crown_hair_0101_braidedManBun" in crown.name
                        or "crown_customGenie_0157_tiesto" in crown.name):
                    key.value = 0.5
                if key.name == "volume_in":
                    if "crown_customGenie_0141_khalid" in crown.name:
                        key.value = 0.4
                    elif "crown_customGenie_0182_shortWhipsy" in crown.name:
                        key.value = 0.5
                    elif "crown_hair_0103_sideSwept" in crown.name:
                        key.value = 0.8
                elif key.name == "volume_out":
                    if ("crown_customGenie_0220_jvke" in crown.name
                        or "crown_hair_0196_wavyBluntBang" in crown.name
                        or "crown_customGenie_0110_joelCorry" in crown.name
                        or "crown_hair_0136_aura" in crown.name):
                        key.value = 0.5
                elif key.name == "strand_thickness_increase":
                    if "crown_customGenie_0044_24KGoldn" in crown.name:
                        key.value = 0.5
                elif key.name == "strand_thickness_decrease":
                    if ("crown_customGenie_0081_amandaNunes" in crown.name
                            or "crown_customGenie_0044_24KGoldn" in crown.name):
                        key.value = 0.5
                elif key.name == "length_increase":
                    if ("crown_customGenie_0118_brett" in crown.name
                        or "crown_customGenie_0110_joelCorry" in crown.name):
                        key.value = 0.6
                    if "crown_customGenie_0121_litKillah" in crown.name:
                        key.value = 0.8

            key.keyframe_insert(data_path="value", frame=current_frame)

        # Post adjustments for the current frame
        post_adjustments(modules, current_frame)
        current_frame += frame_step
        i += 1

    print(f"[RANDOMIZER] Finished setting up scene with {len(combinations)} combinations.")
    bpy.context.scene.frame_end = current_frame
```