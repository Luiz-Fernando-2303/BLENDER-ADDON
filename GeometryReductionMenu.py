bl_info = {
    "name": "",
    "author": "",
    "version": (1, 0),
    "blender": (4, 3, 1),
    "location": "View3D > Sidebar > Redução",
    "description": "",
    "category": "Object",
}
import bpy

# Navis: Setorização do modelo (chunks), Dados de analise por chunks(Tamanho de categorias quantidades, complexidade), 
# Tamnaho, Quantidade, Categoria, Descrição 

# ---------- FUNÇÕES DE REDUÇÃO ----------
def clearUselessVertices(obj):
    bpy.ops.object.mode_set(mode='OBJECT')

    mesh = obj.data
    vertices = mesh.vertices
    edges = mesh.edges

    connections = {v.index: 0 for v in vertices}
    for edge in edges:
        a, b = edge.vertices
        connections[a] += 1
        connections[b] += 1

    disconnected_indices = [i for i, c in connections.items() if c == 0]

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.object.mode_set(mode='OBJECT')

    for idx in disconnected_indices:
        mesh.vertices[idx].select = True

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.delete(type='VERT')
    bpy.ops.object.mode_set(mode='OBJECT')

    return mesh

def apply_convex_hull(context):
    obj = context.object
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    context.view_layer.objects.active = obj
    bpy.ops.object.duplicate()
    duplicated = context.active_object
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.convex_hull(delete_unused=True)
    bpy.ops.object.mode_set(mode='OBJECT')

    obj.hide_viewport = True

    return duplicated

def apply_decimate(context, ratio):
    bpy.ops.object.mode_set(mode='OBJECT')
    obj = context.object
    mod = obj.modifiers.new(name="Decimate", type='DECIMATE')
    mod.ratio = ratio
    bpy.ops.object.modifier_apply(modifier=mod.name)
    return clearUselessVertices(obj)

def apply_voxel(context, voxel_size):
    obj = context.object
    mod = obj.modifiers.new(name="VoxelRemesh", type='REMESH')
    mod.mode = 'VOXEL'
    mod.voxel_size = voxel_size
    mod.use_remove_disconnected = False
    bpy.ops.object.modifier_apply(modifier=mod.name)
    return obj

# ---------- FUNÇÕES DE ORGANIZAÇÃO ----------
def renameByStructure():
    pass

def removeEmptyMeshes():
    pass

def reduceOvercomplexObjects():
    pass

# ---------- PAINEL ----------
class OBJECT_PT_BruteReductionPanel(bpy.types.Panel):
    bl_label = "Otimização de Geometria"
    bl_idname = "OBJECT_PT_brute_reduction"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Redução'

    @classmethod
    def poll(cls, context):
        return context.object and context.object.type == 'MESH'

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        row = layout.row()
        row.label(text="Função:")

        row = layout.row(align=True)
        for key, label in [("CONVEX", "Convex"), ("DECIMATE", "Decimate"), ("VOXEL", "Voxel")]:
            op = row.operator("wm.set_reduction_func", text=label, depress=(scene.reducao_func == key))
            op.value = key

        if scene.reducao_func == "DECIMATE":
            row = layout.row()
            row.prop(scene, "reducao_ratio")

        elif scene.reducao_func == "VOXEL":
            row = layout.row()
            row.prop(scene, "reducao_voxel_size")

        row = layout.row()
        row.operator("wm.call_panel_action", text="Aplicar", icon='CHECKMARK')

# ---------- OPERADORES ----------
class WM_OT_SetReductionFunc(bpy.types.Operator):
    bl_idname = "wm.set_reduction_func"
    bl_label = "Seta função de redução"

    value: bpy.props.StringProperty(name="Function")
    
    def execute(self, context):
        context.scene.reducao_func = self.value
        return {'FINISHED'}

class WM_OT_CallPanelAction(bpy.types.Operator):
    bl_idname = "wm.call_panel_action"
    bl_label = "Executar Redução"

    def execute(self, context):
        scene = context.scene
        func = scene.reducao_func
        params = {}

        if func == "DECIMATE":
            params["ratio"] = scene.reducao_ratio
            apply_decimate(context, scene.reducao_ratio)
        elif func == "VOXEL":
            params["voxel_size"] = scene.reducao_voxel_size
            apply_voxel(context, scene.reducao_voxel_size)
        elif func == "CONVEX":
            apply_convex_hull(context)

        resultado = {
            "function": func,
            "parameters": params
        }

        print(">>> Execução:", resultado)
        return {'FINISHED'}

# ---------- REGISTRO ----------
def register():
    try:
        bpy.types.Scene.reducao_func = bpy.props.StringProperty(default="CONVEX")
        bpy.types.Scene.reducao_ratio = bpy.props.FloatProperty(name="Fator de Redução", default=0.5, min=0.0, max=1.0)
        bpy.types.Scene.reducao_voxel_size = bpy.props.FloatProperty(name="Tamanho do Voxel", default=0.1, min=0.001)

        bpy.utils.register_class(OBJECT_PT_BruteReductionPanel)
        bpy.utils.register_class(WM_OT_SetReductionFunc)
        bpy.utils.register_class(WM_OT_CallPanelAction)
    except:
        pass

def unregister():
    try:
        bpy.utils.unregister_class(OBJECT_PT_BruteReductionPanel)
        bpy.utils.unregister_class(WM_OT_SetReductionFunc)
        bpy.utils.unregister_class(WM_OT_CallPanelAction)

        del bpy.types.Scene.reducao_func
        del bpy.types.Scene.reducao_ratio
        del bpy.types.Scene.reducao_voxel_size
    except:
        pass

if __name__ == "__main__":
    register()
