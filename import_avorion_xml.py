from __future__ import annotations

import numpy as np
import bpy

try:
    import xml.etree.cElementTree as ElementTree
except:
    import xml.etree.ElementTree as ElementTree

from pathlib import Path

from mathutils import Matrix, Vector
from bpy_extras.wm_utils.progress_report import ProgressReport

from .avorion_utils.parser import Ship, Turret, Block
from .avorion_utils.geometry import generate_geometry
from .avorion_utils.categories import get_shape, get_category, get_material


def create_mesh(objects, vertices, faces, offsets, dataname):
    mesh = bpy.data.meshes.new(dataname)

    mesh.vertices.add(len(vertices))
    mesh.loops.add(np.sum(offsets))
    mesh.polygons.add(len(offsets))

    mesh.vertices.foreach_set("co", np.asarray(vertices).reshape(-1))
    mesh.polygons.foreach_set("loop_total", offsets)
    mesh.polygons.foreach_set("loop_start", np.cumsum(offsets)-offsets)
    mesh.polygons.foreach_set("vertices", faces)

    mesh.update(calc_edges=True)

    object = bpy.data.objects.new(mesh.name, mesh)
    objects.append(object)

def load(context,
        filepath: str,
        *,
        recenter_to_origin: bool = False,
        seperate_blocks: bool = True,
        global_matrix: Matrix = None
    ):
    filename = Path(filepath).stem
    wm = context.window_manager
    vl = context.view_layer
    ac = vl.active_layer_collection.collection

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

        # num_vertices = 0
        # num_faces = 0
        # num_blocks = 0

        collections = []
        objects = []

        if design is Turret:
            raise NotImplementedError("Import of Turrets is not yet implemented.")
        else:
            ###
            # - Ignore Turrets

            num_vertices = 0
            num_faces = 0
            num_blocks = 0

            vertices = []
            faces = []
            offsets = []

            for block in design.blocks:
                _vertices, _faces, _offsets = generate_geometry(block)

                if seperate_blocks:
                    create_mesh(objects, _vertices, _faces, _offsets, f"{filename}.{block.index}")
                else:
                    vertices.extend(_vertices)
                    faces.extend(_faces + num_vertices)
                    offsets.extend(_offsets)

                num_vertices += len(_vertices)
                num_faces += len(_offsets)
                num_blocks += 1

            if seperate_blocks:
                collection = bpy.data.collections.new(filename)
                collections.append(collection)
            else:
                create_mesh(objects, vertices, faces, offsets, filename)
                collection = ac

            #???

            for c in collections:
                ac.children.link(c)

            for o in objects:
                o.matrix_world = global_matrix
                collection.objects.link(o)
                o.select_set(True)

        vl.update()

        progress.leave_substeps("Done.")
        progress.leave_substeps(f"Finished importing: {filepath}")

    return {'FINISHED'}
