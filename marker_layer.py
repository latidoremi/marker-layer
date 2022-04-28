# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

bl_info = {
    "name": "Marker Layer",
    "author": "Latidoremi",
    "version": (1, 0),
    "blender": (3, 1, 0),
    "location": "Dopesheet Editor/Timeline Editor > N-Panel",
    "description": "manage markers with layers",
    "category": "Animation",
}


import bpy

def update_count(scene):
    layer = scene.marker_layer[scene.marker_layer_active]
    count = len(layer.markers)
    layer.count = str(count)

def markers_to_layer(scene, use_clear=False, use_select=False):
    markers = scene.marker_layer[scene.marker_layer_active].markers
    if use_clear:
        markers.clear()
    for t_mk in scene.timeline_markers:
        if use_select:
            if not t_mk.select:
                continue
        mk = markers.add()
        mk.name = t_mk.name
        mk.frame = t_mk.frame
        mk.camera = t_mk.camera
    update_count(scene)

def layer_to_markers(scene, use_clear=False):
    if use_clear:
        scene.timeline_markers.clear()
    
    markers = scene.marker_layer[scene.marker_layer_active].markers
    for mk in markers:
        t_mk = scene.timeline_markers.new(mk.name, frame = mk.frame)
        t_mk.camera = mk.camera


class MARKERLAYER_OT_add_scene_layer(bpy.types.Operator):
    bl_idname = 'marker_layer.add_scene_layer'
    bl_label = 'Add'
    bl_options = {'UNDO'}
    
    def execute(self, context):
        scene = context.scene
        count = len(scene.marker_layer)
        ml = scene.marker_layer.add()
        ml.name = f'layer_{count}'
        scene.marker_layer_active = count
        return {'FINISHED'}

class MARKERLAYER_OT_remove_scene_layer(bpy.types.Operator):
    bl_idname = 'marker_layer.remove_scene_layer'
    bl_label = 'Remove'
    bl_options = {'UNDO'}
    
    def execute(self, context):
        scene = context.scene
        index = scene.marker_layer_active
        scene.marker_layer.remove(index)
        if index!=0:
            scene.marker_layer_active = index-1
        return {'FINISHED'}


class MARKERLAYER_OT_move_scene_layer(bpy.types.Operator):
    bl_idname = 'marker_layer.move_scene_layer'
    bl_label = 'Move'
    bl_options = {'UNDO'}
    
    direction: bpy.props.BoolProperty(name = 'move_direction') #True:UP; False:DOWN
    
    def execute(self, context):
        scene = context.scene
        index = scene.marker_layer_active
        max_index = len(scene.marker_layer)-1
        
        if self.direction: #UP
            if index ==0:
                return {'FINISHED'}
            else:
                neightbor = index-1
        else: #DOWN
            if index==max_index:
                return {'FINISHED'}
            else:
                neightbor = index+1
        
        scene.marker_layer.move(neightbor, index)
        scene.marker_layer_active = neightbor
        return {'FINISHED'}

class MARKERLAYER_OT_assign_scene_markers(bpy.types.Operator):
    '''assign scene markers to active marker layer'''
    bl_idname = 'marker_layer.assign_scene_markers'
    bl_label = 'Assign'
    bl_options = {'UNDO'}
    
    items=[
        ('assign_all','Assign All','',0),
        ('assign_selected','Assign Selected','',1),
        ('append_all','Append All','',2),
        ('append_selected','Append Selected','',3),
    ]
    op: bpy.props.EnumProperty(items=items, name='op')
    
    @classmethod
    def poll(cls, context):
        return (True if context.scene.marker_layer else False)
    
    def execute(self, context):
        scene = context.scene
        
        if self.op == 'assign_all':
            markers_to_layer(scene, use_clear=True, use_select=False)
        elif self.op == 'assign_selected':
            markers_to_layer(scene, use_clear=True, use_select=True)
        elif self.op == 'append_all':
            markers_to_layer(scene, use_clear=False, use_select=False)
        elif self.op == 'append_selected':
            markers_to_layer(scene, use_clear=False, use_select=True)
    
        return {'FINISHED'}

class MARKERLAYER_OT_load(bpy.types.Operator):
    '''load active layer markers to scene'''
    bl_idname = 'marker_layer.load'
    bl_label = 'Load'
    bl_options = {'UNDO'}
    
    items=[
        ('replace','Replace','',0),
        ('append','Append','',1),
    ]
    op: bpy.props.EnumProperty(items=items, name='op')
    
    
    @classmethod
    def poll(cls, context):
        return (True if context.scene.marker_layer else False)
    
    def execute(self, context):
        scene = context.scene
        if self.op == 'replace':
            layer_to_markers(scene, use_clear=True)
        else:
            layer_to_markers(scene, use_clear=False)
        
        return {'FINISHED'}


class MARKERLAYER_UL_scene_markers(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            split = layout.split(factor=0.8)
            split.prop(item,'name', emboss=False ,icon_value = icon)
            split.label(text=item.count)
        
        
class MARKERLAYER_PT_marker_layer_main_panel(bpy.types.Panel):
    bl_label = "Marker Layer"
    bl_idname = "MARKER_PT_marker_layer_main_panel"
    bl_space_type = 'DOPESHEET_EDITOR'
    bl_region_type = 'UI'
    bl_category = 'Marker Layer'
    

    def draw(self, context):
        scene = context.scene
        layout = self.layout
        
        row = layout.row(align=True)
        row.template_list("MARKERLAYER_UL_scene_markers", "", scene, "marker_layer", scene, "marker_layer_active",rows=4)
        
        subcol = row.column(align=True)
        subcol.operator('marker_layer.add_scene_layer', text='', icon = 'ADD')
        subcol.operator('marker_layer.remove_scene_layer', text='', icon = 'REMOVE')
        
        subcol.separator()
        
        subcol.operator('marker_layer.move_scene_layer', text='', icon = 'TRIA_UP').direction = True
        subcol.operator('marker_layer.move_scene_layer', text='', icon = 'TRIA_DOWN').direction = False
        
        row = layout.row(align=True)
        row.operator_menu_enum('marker_layer.assign_scene_markers','op')
        row.operator_menu_enum('marker_layer.load','op')
        

class MARKERLAYER_marker(bpy.types.PropertyGroup):
    name:bpy.props.StringProperty(name='name')
    frame:bpy.props.IntProperty(name='frame', default = 0)
    camera:bpy.props.PointerProperty(name='camera', type=bpy.types.Object)

class MARKERLAYER_scene_marker_layer(bpy.types.PropertyGroup):
    name:bpy.props.StringProperty(name='')
    count:bpy.props.StringProperty(name='',default='0')
    markers:bpy.props.CollectionProperty(name='layer', type = MARKERLAYER_marker)


classes=[
    MARKERLAYER_OT_add_scene_layer,
    MARKERLAYER_OT_remove_scene_layer,
    MARKERLAYER_OT_move_scene_layer,
    
    MARKERLAYER_OT_assign_scene_markers,
    MARKERLAYER_OT_load,
    
    MARKERLAYER_UL_scene_markers,
    
    MARKERLAYER_PT_marker_layer_main_panel,
    MARKERLAYER_marker,
    MARKERLAYER_scene_marker_layer,
]


def register():
    for c in classes:
        bpy.utils.register_class(c)
        
    bpy.types.Scene.marker_layer = bpy.props.CollectionProperty(type=MARKERLAYER_scene_marker_layer)
    bpy.types.Scene.marker_layer_active = bpy.props.IntProperty(name='active layer', default = 0, min = 0)

def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)
        
    del bpy.types.Scene.marker_layer
    del bpy.types.Scene.marker_layer_active


if __name__ == "__main__":
    register()
