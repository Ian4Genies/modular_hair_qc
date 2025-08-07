# Lazy Loading in viewport request
So I think we have had a miscommunication about how I want usd data to be "loaded" into the scene. For modules and styles, and really anything related to pulling from usd data. I do not need that data to be "Imported" in the scene. It does not need to be editable, It just needs to be viewable. If the usd are manually importable that is more than enough. Right now the base mesh imports corectly but it looks like the blendshape meshes are not being saved and are not importable as blendshapes when nattively importing the usd file.

Feature request
- When modules are clicked instead of "importing" we want to actually use proxy shapes.
- the blendshape weight slider in the UI should control the blendshapes weights on the proxy shape.
- Blendshape weight on modules never needs to be saved to the module
- Though we never need to import the usd files through the interface, module usd files should be natively importable, so the base mesh and blendshapes should be set up correctly for this.
- currently the base mesh does import, but I don't think blendshapes are being saved at all, let alone being saved correctly for native loading. 

# Lazy Loading info
With **lazy loading USD in Maya**, particularly using **USD stages via the Maya USD plugin** (like `pxr.UsdStage` or through the `mayaUsdProxyShape`), you *can* display meshes in the viewport **without fully loading them into the Maya DAG**. This is one of the primary advantages of the USD system. Here’s a breakdown of how this works:

---

### ✅ **Display Meshes Without Full Load:**

When using **`mayaUsdProxyShape`**, meshes can be:

* **Displayed in the viewport (Hydra rendering)**.
* **Not present in the Maya scene graph (DAG)**.
* **Only loaded into memory as needed (on selection, edit, etc.)**.

This is possible through **USD's deferred/lazy loading**, combined with **viewport streaming via Hydra**.

---

### 🔧 How to Achieve This:

#### 1. **Use `mayaUsdProxyShape` node**

* When you load a USD file through `mayaUsdProxyShape`, it creates a lightweight representation in Maya.
* The contents of the USD file are rendered via **Hydra** but are *not* actual Maya nodes.

#### 2. **Set the Load Rules**

You can control what is loaded using load rules:

```python
proxyShape = 'stageShape1'  # Your Proxy Shape name
import maya.cmds as cmds
cmds.setAttr(proxyShape + '.loadPayloads', False)
```

Or in Python API with USD:

```python
from pxr import Usd

stage = Usd.Stage.Open('your_file.usd', load=Usd.Stage.LoadNone)
```

> With `LoadNone`, only the structure of the stage is visible. You can still see geometry in the viewport rendered by Hydra, but payloads (actual mesh data) aren't loaded into Maya DAG or memory unless requested.

#### 3. **Viewport Draw**

Hydra (via **Viewport 2.0**) allows previewing these assets:

* Even without loading the payloads.
* Geometry will display as long as it's in the **USD stage structure**.
* You won’t be able to select or modify until payloads are loaded.

---

### 🧠 Summary:

| Feature                    | Status                                        |
| -------------------------- | --------------------------------------------- |
| View geometry in viewport  | ✅ Yes, via Hydra                              |
| Load full Maya nodes (DAG) | ❌ Not until user interaction or explicit load |
| Ideal for                  | Massive USD sets, lookdev, referencing        |

---

### 🔍 Bonus: Load on Demand

You can implement a system where clicking or selecting a prim in the scene triggers loading:

```python
prim = stage.GetPrimAtPath('/Model/Details')
stage.Load(prim.GetPath())
```

Let me know if you're looking to customize this workflow or automate lazy loading per module/prim basis.
