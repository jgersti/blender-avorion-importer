bl_info = {
    "name" : "Avorion XML Format",
    "author" : "Janick Gerstenberger",
    "description": "Import Avorion XML",
    "blender" : (2, 90, 0),
    "version" : (0, 0, 1),
    "location" : "File > Import-Export",
    "warning" : "",
    "category" : "Import-Export"
}

if "bpy" in locals():
    import importlib
    if "import_avorion_xml" in locals():
        importlib.reload(import_avorion_xml)
    if "avorion_utils" in locals():
        importlib.reload(avorion_utils)

import bpy
from bpy.props import BoolProperty, FloatProperty, StringProperty, EnumProperty
from bpy.types import Operator, Panel
from bpy_extras.io_utils import orientation_helper, path_reference_mode, axis_conversion


@orientation_helper(axis_forward='-Z', axis_up='Y')
class ImportAvorionXML(Operator):
    bl_idname = "avorion.import_xml"
    bl_label = "Import Avorion XML"
    bl_options = {'PRESET', 'UNDO'}

    filename_ext = ".xml"
    filter_glob: StringProperty(
        default="*.xml",
        options={'HIDDEN'}
    )

    filepath: StringProperty(
        name="File Path",
        description="Filepath used for importing the file",
        maxlen=1024,
        subtype='FILE_PATH'
    )

    recenter_to_origin: BoolProperty(
        name="Recenter to Origin",
        description="Recenter model median to origin",
        default=False
    )

    seperate_blocks: BoolProperty(
        name="Seperate Blocks",
        description="Seperate Blocks into indiviual Meshes",
        default=True
    )

    def draw(self, context):
        pass

    def execute(self, context):
        from . import import_avorion_xml

        keywords = self.as_keywords(ignore=("axis_forward", "axis_up", "filter_glob"))

        global_matrix = axis_conversion(from_forward=self.axis_forward, from_up=self.axis_up)
        keywords["global_matrix"] = global_matrix



        return import_avorion_xml.load(context, **keywords)

    def invoke(self, context, _event):
        from pathlib import Path
        from . appdirs import user_data_dir

        path = Path(user_data_dir('Avorion', appauthor=False, roaming= True))
        path /= "ships"

        if path.exists() and path.is_dir():
            self.filepath = str(path) + "//"

        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


class XML_PT_import_transform(Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_region_type = 'TOOL_PROPS'
    bl_label = "Transform"
    bl_parent_id = "FILE_PT_operator"

    @classmethod
    def poll(cls, context):
        sfile = context.space_data
        operator = sfile.active_operator

        return operator.bl_idname == "AVORION_OT_import_xml"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        sfile = context.space_data
        operator = sfile.active_operator

        layout.prop(operator, "axis_forward")
        layout.prop(operator, "axis_up")


class XML_PT_import_geometry(Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_region_type = 'TOOL_PROPS'
    bl_label = "Geometry"
    bl_parent_id = "FILE_PT_operator"

    @classmethod
    def poll(cls, context):
        sfile = context.space_data
        operator = sfile.active_operator

        return operator.bl_idname == "AVORION_OT_import_xml"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        sfile = context.space_data
        operator = sfile.active_operator

        layout.prop(operator, "recenter_to_origin")
        layout.prop(operator, "seperate_blocks")


def menu_func_import(self, context):
    self.layout.operator(ImportAvorionXML.bl_idname, text="Avorion (.xml)")

classes = (
    ImportAvorionXML,
    XML_PT_import_transform,
    XML_PT_import_geometry
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)

def unregister():
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)

    for cls in classes:
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
