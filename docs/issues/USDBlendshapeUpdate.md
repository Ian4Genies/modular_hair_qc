To see and **interactively preview blendshapes on a USD proxy** in **Maya**, you’ll need to follow a few steps, as **USD blendshape animation doesn't display by default** on proxy shapes. Maya’s native USD plugin (via `maya-usd`) supports blendshapes (via `UsdSkel`) but requires some setup to expose the weights for interactive editing.

---

## ✅ GOAL

You want to change the blendshape weights of a USD file loaded as a **proxy shape** in Maya and see the results update in the **viewport**.

---

## ✅ PREREQUISITES

1. ✅ You're using **mayaUSD plugin** (shipped with Maya 2022+).
2. ✅ Your USD has properly authored **blendShapes and UsdSkel animation schema** (e.g., `UsdSkelAnimation` with `blendShapeWeights` and `blendShapes` on `UsdSkelBindingAPI`).
3. ✅ You’re using a **Proxy shape**, not an imported/converted mesh.

---

## 🧩 WHAT DOESN’T WORK AUTOMATICALLY

* **Blendshapes in a USD file won’t auto-populate as editable attrs** on the Maya proxy shape.
* You can’t key or interactively move sliders in the Attribute Editor unless they’re explicitly **exposed to Maya**.

---

## ✅ SOLUTION OPTIONS

### 🔹 Option 1: Author BlendShape Weights in USD, Edit via Maya Attribute Editor

#### Step 1: Confirm BlendShapes Exist in USD

Open the **USD Layer Editor** or `usdview` and confirm that:

* Your mesh is **bound to a skeleton** using `UsdSkelBindingAPI`.
* The `UsdSkelAnimation` contains:

  * `blendShapes` array
  * `blendShapeWeights` time-sampled data

#### Step 2: Create Maya Attributes to Drive BlendShape Weights

The proxy shape doesn’t expose blendshape weights by default, but you can:

* Add **custom attributes** to the proxy node (or any Maya control node).
* Connect those attributes to the appropriate USD **blendShapeWeights** via the **USD Attribute Editor** or `usdAttrQuery`.

> This requires **authoring** USD blendshape weights using either a `usdEdit` session or scripting.

#### Scripted Example:

If your blendshape is on path:

```
/Root/MyMesh.blendShapeWeights
```

You can connect a Maya attribute to drive it via:

```python
import maya.cmds as cmds
from pxr import Usd, UsdGeom, Sdf, UsdSkel

# Create an attr
cmds.addAttr('usdProxyShape1', longName='smileWeight', attributeType='double', min=0, max=1, defaultValue=0.0, keyable=True)

# You would then need to hook this to the actual USD attribute programmatically.
# This part requires using the USD Stage API and writing the value into the stage
```

But Maya doesn't natively reflect the change unless the proxy shape is configured to live update. That brings us to:

---

### 🔹 Option 2: Use a **Stage Cache and Update the Weights Live** (Recommended for preview/debug)

You can get the USD stage from the proxy shape and live-edit the `blendShapeWeights`.

```python
from pxr import Usd, UsdSkel, UsdGeom, Sdf
import mayaUsd.lib as mayaUsdLib

# Get stage
stage = mayaUsdLib.GetPrim(mayaUsdLib.ufe.PathToPrim('/usdProxy1'))
blend_anim_prim = stage.GetPrimAtPath('/Root/MyBlendAnim')

# Access animation
blend_anim = UsdSkel.Animation(blend_anim_prim)
blend_attr = blend_anim.GetBlendShapeWeightsAttr()

# Set blendshape 0 to 1.0
blend_attr.Set([1.0, 0.0, 0.0])  # assuming 3 blendshapes
```

> You should then see the shape change in the viewport **if the USD stage and bindings are valid**.

---

### 🔹 Option 3: Reimport as Maya Mesh with Deformers

If you need full Maya-native editing, use:

* `USD Import (not proxy)` with `blendShapes` enabled.
* This creates actual **Maya meshes with blendShape deformers**, editable directly in Maya.

---

## ✅ Tips

* Ensure `blendShapeWeights` are **time-sampled or editable**, not static.
* If you're debugging why blendshapes don't appear, run `usdcat` on your file to inspect the `UsdSkel` structure.
* The **Hydra Viewport** in Maya may not reflect live updates unless the stage is **muted/unmuted** or the time is scrubbed.

---

## 🧠 Final Notes

USD in Maya **does not currently support automatic creation of sliders** for blendshape weights in the proxy shape. You must:

* Use scripting to change weights on the `UsdSkelAnimation`
* OR create Maya custom attrs to control those weights
* OR import the mesh as editable geometry

Let me know if you want a working code example for live-driving a blendshape from Maya to USD proxy.
