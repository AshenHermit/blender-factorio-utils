# Factorio Utils v0.8

A small addon for *Blender* that simplifies the creation of graphics for the game *Factorio*.

<div style="height:128px;"><img height="128" src="pages/pics/factorio_utils.gif"/></div>

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

<div><img height="128" src="pages/pics/screnshot.jpg"/></div>

just screenshot

* **3D View side panel**
    <div><img height="128" src="pages/pics/side_panel.jpg"/></div>

  * **Setup Scene** - Executes all scene setup operators that can be found in the **Object** tab:  
  (rows under "Setup Scene"): <div><img height="128" src="pages/pics/3dview_object_menu.jpg"/></div>

  * **Options**
    * **Main object** - The object whose animations are being rendered.
    * **Directions count** - The number of directions in which the object will be rendered.
    * **Render HR versions** - Render high resolution versions, whose size is **HR scale** times larger.

  * **Export**
    * **Output file** - Path to the folder and name of the future spritesheet.
    * **Render object animations** - render all object animations into spritesheets, as if they individually rendered here, with this button  
    (In the **NLA Editor** side bar):
      <div><img height="128" src="pages/pics/animation_side_panel.jpg"/></div>  
    
    Render examples:

    <p float="left">
    <img src="pages/pics/cycles_1_direction_render.jpg" title="cycles, 1 direction" height="128">
    <img src="pages/pics/eevee_4_directions_render.jpg" title="eevee, 4 directions" height="128">
    </p>

* **Text Editor > Text menu**
  <div><img height="128" src="pages/pics/text_editor_menu.jpg"/></div>
  Here you can generate extremply simple animation data for some entity registration lua code.  
  What it looks like:
  <div><img height="128" src="pages/pics/animation_data_code.jpg"/></div>
  
**checking in game**
<div><img height="128" src="pages/pics/in_game.gif"/></div>

## Ideas
* Maybe should be added the ablility to define *boxes* properties like *"collision_box"*, *"selection_box"*, *"drawing_box"*, by changing sizes of some planes. That would be cool.