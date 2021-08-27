from __future__ import annotations

import numpy as np
import bpy

try:
    import xml.etree.cElementTree as ElementTree
except:
    import xml.etree.ElementTree as ElementTree

from pathlib import Path

from mathutils import Matrix, Vector
from bpy_extras.io_utils import axis_conversion
from bpy_extras.wm_utils.progress_report import ProgressReport

from .avorion_utils.parser import Ship, Turret, Block
from .avorion_utils.shapes import generate_geometry
from .avorion_utils.categories import get_shape, get_category, get_material

def load(context,
        filepath: str,
        *,
        recenter_to_origin: bool = False,
        seperate_blocks: bool = True,
        global_matrix: Matrix = None
    ):

    wm = context.window_manager

    filename = Path(filepath).stem
    print(filename)

    with ProgressReport(wm) as progress:
        progress.enter_substeps(1, f"Importing Avorion XML {filepath}...")

        global_matrix = global_matrix or Matrix()

        progress.enter_substeps(3, f"Parsing Avorion XML file...")
        xml = ElementTree.parse(filepath)
        root = xml.getroot()

        design = None

        tag = root.tag
        if tag == "ship_design" or tag == "plan":
            design = Ship.from_xml(root)
        elif tag == "turret_design":
            design = Turret.from_xml(root)
        else:
            raise IOError(f"Invalid file format.")
        progress.step("Done.")

        progress.enter_substeps(5, f"Building Geomtry...")

        collections = []
        objects = []

        num_vertices = None
        num_faces = None
        num_blocks = None

        if design is Turret:
            raise NotImplementedError("Import of Turrets is not yet implemented.")
        else:
            ###
            # - Assume seperate_blocks = True for now
            # - Ignore Turrets

            for block in design.blocks:
                mesh = bpy.data.meshes.new(f"{filename}.{get_shape(block.type)}.{block.index}")

                vertices, faces, offsets = generate_geometry(block)

                mesh.vertices.add(len(vertices))
                mesh.loops.add(np.sum(offsets))
                mesh.polygons.add(len(offsets))

                mesh.vertices.foreach_set("co", vertices.reshape(-1))
                mesh.polygons.foreach_set("loop_total", offsets)
                mesh.polygons.foreach_set("loop_start", np.cumsum(offsets)-offsets)
                mesh.polygons.foreach_set("vertices", faces)

                mesh.update(calc_edges=True)

                object = bpy.data.objects.new(mesh.name, mesh)
                object.matrix_world = global_matrix
                objects.append(object)

            view_layer = context.view_layer
            collection = view_layer.active_layer_collection.collection

            for o in objects:
                collection.objects.link(o)
                o.select_set(True)

            view_layer.update()


        progress.leave_substeps("Done.")
        progress.leave_substeps(f"Finished importing: {filepath}")

    return {'FINISHED'}
