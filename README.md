# Factorio Utils v0.6

A small addon for *Blender* that simplifies the creation of graphics for the game *Factorio*.

<div style="height:128px;"><img src="pages/pics/factorio_utils.gif"/></div>

## Features
* Quick scene setup:
  * Shadow catcher.
  * Game tiles grid.
  * Camera and lighting setup.
* Rendering animations (nla tracks) into spritesheets, in different directions.
* Generation of block of lua code with entity animation data.

## Installation
* Download repo as zip and install it into blender
* **OR** clone repo into `~/AppData/Blender Foundation/Blender/version/scripts/addons/`
* Activate it in preferences

## Controls places

<div style="height:128px;"><img src="pages/pics/screnshot.jpg"/></div>

just screenshot

* **3D View side panel**
    <div style="height:128px;"><img src="pages/pics/side_panel.jpg"/></div>

  * **Setup Scene** - Executes all scene setup operators that can be found in the **Object** tab:  
  (rows under "Setup Scene"): <div style="height:128px;"><img src="pages/pics/3dview_object_menu.jpg"/></div>

  * **Options**
    * **Main object** - The object whose animations are being rendered.
    * **Directions count** - The number of directions in which the object will be rendered.
    * **Render HR versions** - Render high resolution versions, whose size is **HR scale** times larger.

  * **Export**
    * **Output file** - Path to the folder and name of the future spritesheet.
    * **Render object animations** - render all object animations into spritesheets, as if they individually rendered here, with this button  
    (In the **NLA Editor** side bar):
      <div style="height:128px;"><img src="pages/pics/animation_side_panel.jpg"/></div>  
    
    Render examples:
    <div style="display: flex;">
    <figure>
    <img src="pages/pics/cycles_1_direction_render.jpg" alt="cycles, 1 direction" style="height:128px;">
    <figcaption align = "center"><b>cycles, 1 direction</b></figcaption>
    </figure>
    <figure>
    <img src="pages/pics/eevee_4_directions_render.jpg" alt="eevee, 4 directions" style="height:128px;">
    <figcaption align = "center"><b>eevee, 4 directions</b></figcaption>
    </figure>
    </div>

* **Text Editor > Text menu**
  <div style="height:128px;"><img src="pages/pics/text_editor_menu.jpg"/></div>
  Here you can generate extremply simple animation data for some entity registration lua code.  
  What it looks like:
  <div style="height:128px;"><img src="pages/pics/animation_data_code.jpg"/></div>
  
**checking in game**
<div style="height:128px;"><img src="pages/pics/in_game.gif"/></div>

## Ideas
* Maybe should be added the ablility to define *boxes* properties like *"collision_box"*, *"selection_box"*, *"drawing_box"*, by changing sizes of some planes. That would be cool.
* The ablility to stop rendering spritesheet.
