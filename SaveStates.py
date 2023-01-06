#add on info stored in dictionary
bl_info = {
    "name": "Save States",
    "blender": (2, 80, 0),
    "category": "Files",
}

import bpy
import os
from pathlib import Path
from shutil import rmtree

# ---Counter---------------------------------------------------------
count = 0 
    
# -------------------------------------------------------------------
#   Operators
# -------------------------------------------------------------------

# When "save state" button is clicked, a new state is stored in folder "Save States"
# and the list is updated
class SAVESTATES_OT_addState(bpy.types.Operator):
    """Creates a new save"""
    bl_label = "Create quick save"
    bl_idname = "savestates.addstate" #translates to C-name SAVESTATES_OT_addState
    
    @classmethod
    def poll(cls, context):
        return len(context.scene.save) <= 9 #check if there are 10 saves stored
    
    def execute(self, context):
        global count
        #get filename without .blend
        filename = bpy.path.basename(bpy.context.blend_data.filepath).removesuffix(".blend") 
    
        foldername = "Save States" #folder where states are stored
        blendDir = os.path.dirname(bpy.data.filepath) #get current blend directory    
        path = os.path.join(blendDir, foldername) #define new file path
        
        #os.path.join(os.path.dirname(bpy.data.filepath), "Save States")
        if(os.path.isdir(path) == False):
            os.mkdir(path) #create new folder
            
        scene = bpy.context.scene #reference current scene
        save = scene.save #reference current save
        index = scene.save_index #reference current save index
        
        #--- create filename and path
        saveName = filename + str(count) + ".blend"
        savePath = os.path.join(path, saveName) #add new blend name
        
        #--- add current save to UIList
        item = save.add()
        item.name = saveName
        item.path = savePath
        
        
        count += 1 #increment index      
        bpy.ops.wm.save_as_mainfile(filepath=savePath,copy=True) #save current state as new blend
        return {'FINISHED'}
    
#Removes a save in the list
class SAVESTATES_OT_deleteState(bpy.types.Operator):
    """Delete a selected save"""
    bl_label = "Delete save"
    bl_idname = "savestates.deletestate" #translates to C-name BUTTON_OT_save
    
    #check if there's anything to delete in the list
    @classmethod
    def poll(cls, context):
        return context.scene.save
    
    def execute(self, context):
        global count
        scene = bpy.context.scene #reference current scene
        saveList = scene.save #reference current save
        index = scene.save_index
        save = saveList[index]
        
        foldername = "Save States" #name of folder containing saves
        blendDir = os.path.dirname(bpy.data.filepath) #get current blend directory
        path = os.path.join(blendDir, foldername) #define file path
        
        #delete file
        path = os.path.join(path, save.name)
        
        #add an error checker for this one
        if Path(path).is_file():
            Path(path).unlink() #delete file
        saveList.remove(index) #remove from list
        index = min(max(0, index - 1), len(saveList) - 1)
        return {'FINISHED'}
    
#Clears all saves in the list
class SAVESTATES_OT_clearAll(bpy.types.Operator):
    """WARNING: This will clear all saves"""
    bl_label = "Clear all saves"
    bl_idname = "savestates.clearall" #translates to C-name BUTTON_OT_save
    
    #check if there's anything to delete in the list
    @classmethod
    def poll(cls, context):
        return context.scene.save
    
    def execute(self, context):
        global count
        scene = bpy.context.scene #reference current scene
        save = scene.save #reference current save
        foldername = "Save States" #name of folder containing saves
        blendDir = os.path.dirname(bpy.data.filepath) #get current blend directory
        path = os.path.join(blendDir, foldername) #define file path
        
        #delete all saves in folder
        for path in Path(path).glob("**/*"):
            if path.is_file():
                path.unlink()
            #elif path.is_dir():    #for files
                #rmtree(path)
        
        save.clear()
        count = 0
        bpy.context.scene.save_index = 0
        return {'FINISHED'}

# -------------------------------------------------------------------
#   Drawing
# -------------------------------------------------------------------

#Draws save states panel in tools section
class SAVESTATES_PT_panel(bpy.types.Panel):
    bl_label = "Save States"
    bl_idname = "SAVESTATES_PT_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Save States'
    
    def draw(self, context):
        layout = self.layout
        scene = bpy.context.scene
        
        #row = layout.row() #Label: Save File
        #row.label(text= "Save File")
        
        row = layout.row() 
        row.operator("savestates.addstate") #call save operator
        
        row = layout.row()
        row.label(text= "Saves")
        
        row = layout.row()
        row.template_list("SAVESTATES_UL_itemList", "Save_List", scene, "save", scene, "save_index") #UI List
        
        row = layout.row()
        row.operator("savestates.deletestate") #call clear operator
        row = layout.row()
        row.operator("savestates.clearall") #call clear operator
                    
#Implements UI List
class SAVESTATES_UL_itemList(bpy.types.UIList):
    
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        
        #custom icon
        custom_icon = 'OBJECT_DATAMODE'
        
        #make sure code supports all 3 layout types
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.label(text=item.name)
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon = custom_icon)
            
# -------------------------------------------------------------------
#   Collections
# -------------------------------------------------------------------

class SAVESTATES_objectCollection(bpy.types.PropertyGroup):
    """Group of properties representing a save in the list"""
    
    name : bpy.props.StringProperty(
            name = "Name",
            description = "Name for item",
            default = "Untitled")
            
    path : bpy.props.StringProperty(
            name = "Path",
            description = "File Path for item",
            default = "Empty") #change empty later

# -------------------------------------------------------------------
#   Register & Unregister
# -------------------------------------------------------------------

def register():
    bpy.utils.register_class(SAVESTATES_objectCollection)
    bpy.utils.register_class(SAVESTATES_PT_panel)
    bpy.utils.register_class(SAVESTATES_OT_addState)
    bpy.utils.register_class(SAVESTATES_OT_clearAll)
    bpy.utils.register_class(SAVESTATES_OT_deleteState)
    bpy.utils.register_class(SAVESTATES_UL_itemList)
    bpy.types.Scene.save = bpy.props.CollectionProperty(type = SAVESTATES_objectCollection)
    bpy.types.Scene.save_index = bpy.props.IntProperty(name = "Index for save", default = 0)

def unregister():
    del bpy.types.Scene.save
    del bpy.types.Scene.save_index
    
    bpy.utils.unregister_class(SAVESTATES_objectCollection)
    bpy.utils.unregister_class(SAVESTATES_OT_addState)
    bpy.utils.unregister_class(SAVESTATES_OT_clearAll)
    bpy.utils.unregister_class(SAVESTATES_OT_deleteState)
    bpy.utils.unregister_class(SAVESTATES_PT_panel)
    bpy.utils.unregister_class(SAVESTATES_UL_itemList)
    

if __name__ == "__main__":
    register()
