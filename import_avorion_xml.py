from __future__ import annotations

import math
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

def hex2rgba(color: str) -> tuple(float):
    return (int(color[2:4], 16)/255, int(color[4:6], 16)/255, int(color[6:8], 16)/255, int(color[0:2], 16)/255)

def create_mesh(objects,
                vertices,
                faces,
                offsets,
                colors=None,
                origin=None,
                dataname="block"
                ):
    mesh = bpy.data.meshes.new(dataname)

    mesh.vertices.add(len(vertices))
    mesh.loops.add(np.sum(offsets))
    mesh.polygons.add(len(offsets))

    mesh.vertices.foreach_set("co", np.asarray(vertices).reshape(-1))
    mesh.polygons.foreach_set("loop_total", offsets)
    mesh.polygons.foreach_set("loop_start", np.cumsum(offsets)-offsets)
    mesh.polygons.foreach_set("vertices", faces)

    if colors is not None:
        print(colors)
        if type(colors) is tuple:
            colors = colors * len(offsets)

        color_layer = mesh.vertex_colors.get("Color") or mesh.vertex_colors.new(name="Color")
        color_layer.data.foreach_set("color", np.repeat(colors, offsets, axis=0).reshape(-1))

    mesh.update(calc_edges=True)

    obj = bpy.data.objects.new(mesh.name, mesh)

    if origin is not None:
        obj.matrix_world = Matrix.Translation(origin)

    objects.append(obj)

def create_turret_armature(context, collection, design, dataname="turret"):
    _armature = bpy.data.armatures.new(f"{dataname}_armature")
    armature = bpy.data.objects.new(_armature.name, _armature)

    collection.objects.link(armature)
    armature.select_set(True)
    context.view_layer.objects.active = armature

    bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
    bpy.ops.object.mode_set(mode='EDIT', toggle=False)

    edit_bones = _armature.edit_bones
    bones = (f"{armature.name}_base", f"{armature.name}_rotation",
             f"{armature.name}_elevation", f"{armature.name}_target")

    size = design.size

    base = edit_bones.new(bones[0])
    base.head = design.base_origin
    base.tail = design.base_origin + np.array([0, 0.1, 0]) * size

    rotation = edit_bones.new(bones[1])
    rotation.head = design.body_origin
    rotation.tail = design.body_origin + np.array([0, 0, -0.1]) * size

    elevation = edit_bones.new(bones[2])
    elevation.head = design.barrel_origin
    elevation.tail = design.barrel_origin + np.array([0, 0, 0.1]) * size

    target = edit_bones.new(bones[3])
    avg_muzzle = np.sum(design.muzzles) / len(design.muzzles)
    target.head = avg_muzzle + np.array([0, 0, 10]) * size
    target.tail = avg_muzzle + np.array([0, 0, 11]) * size

    rotation.use_connect = elevation.use_connect = target.use_connect = False
    rotation.parent = base
    elevation.parent = rotation
    target.parent = base

    bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

    pose_bones = armature.pose.bones
    rotation = pose_bones.get(bones[1])
    elevation = pose_bones.get(bones[2])
    target = pose_bones.get(bones[3])

    c = rotation.constraints.new(type='LOCKED_TRACK')
    c.target = armature
    c.subtarget = target.name
    c.track_axis = 'TRACK_NEGATIVE_Y'
    c.lock_axis = 'LOCK_Z'

    c = elevation.constraints.new(type='LOCKED_TRACK')
    c.target = armature
    c.subtarget = target.name
    c.track_axis = 'TRACK_Y'
    c.lock_axis = 'LOCK_X'

    c = elevation.constraints.new(type='LIMIT_ROTATION')
    c.owner_space = 'LOCAL'
    c.use_limit_x = True
    c.min_x = math.radians(-85)
    c.max_x = math.radians(15)

    c = target.constraints.new(type='COPY_ROTATION')
    c.target = armature
    c.subtarget = rotation.name
    c.owner_space = 'LOCAL'
    c.target_space = 'LOCAL'
    c.use_x, c.use_y, c.use_z = False, False, True
    c.invert_z = True

    c = target.constraints.new(type='COPY_ROTATION')
    c.target = armature
    c.subtarget = elevation.name
    c.owner_space = 'LOCAL'
    c.target_space = 'LOCAL'
    c.use_x, c.use_y, c.use_z = True, False, False

    return armature, bones

def load(context,
         filepath: str,
         *,
         recenter_to_origin: bool = False,
         seperate_blocks: bool = True,
         global_matrix: Matrix = None
         ):
    name = Path(filepath).stem
    wm = context.window_manager
    vl = context.view_layer

    for o in context.scene.objects:
        o.select_set(False)

    ac = vl.active_layer_collection.collection

    global_matrix = global_matrix or Matrix()

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

    if type(design) is Turret:
        collection = bpy.data.collections.new(name)
        ac.children.link(collection)

        parts = ("base", "body", "barrel") if not design.coaxial else ("base")

        objects = []
        collections = []

        if seperate_blocks:
            counts = []

            for p in parts:
                blocks, origin = design.get_part(p)
                counts.append(len(blocks))
                base = f"{name}_{p}" if not design.coaxial else name

                for b in blocks:
                    create_mesh(objects, *generate_geometry(b), colors=hex2rgba(b.color),
                                origin=origin, dataname=f"{base}_block{b.index}")

                if design.coaxial:
                    collections.append(collection)
                else:
                    coll = bpy.data.collections.new(base)
                    collections.append(coll)

            _end = np.cumsum(counts)
            _start = _end - counts
            for coll, s, e in zip(collections, _start, _end):
                collection.children.link(coll)
                for o in objects[s:e]:
                    coll.objects.link(o)
        else:
            for p in parts:
                base = f"{name}_{p}" if not design.coaxial else name
                num_vertices = 0

                vertices = []
                faces = []
                offsets = []
                colors = []

                blocks, origin = design.get_part(p)
                for b in blocks:
                    _vertices, _faces, _offsets = generate_geometry(b)
                    _faces += num_vertices
                    num_vertices += len(_vertices)

                    vertices.extend(_vertices)
                    faces.extend(_faces)
                    offsets.extend(_offsets)
                    colors.extend([hex2rgba(b.color)] * len(_offsets))
                create_mesh(objects, vertices, faces, offsets, colors=colors, origin=origin, dataname=base)

            for o in objects:
                collection.objects.link(o)

            if not design.coaxial:
                armature, bones = create_turret_armature(context, collection, design, name)

                # link rig to mesh
                for o, b in zip(objects, bones):
                    o.parent = armature
                    o.parent_type = 'BONE'
                    o.parent_bone = b

                armature.matrix_world = global_matrix

        for o in objects:
            o.matrix_world = global_matrix @ o.matrix_world
            o.select_set(True)
    else:
        ###
        # - Ignore Turrets for now
        objects = []

        num_vertices = 0
        num_faces = 0
        num_blocks = 0

        vertices = []
        faces = []
        offsets = []
        colors = []

        for block in design.blocks:
            _vertices, _faces, _offsets = generate_geometry(block)

            if seperate_blocks:
                create_mesh(objects, _vertices, _faces, _offsets, colors=hex2rgba(block.color),
                            dataname=f"{name}_block{block.index}")
            else:
                _faces += num_vertices

                vertices.extend(_vertices)
                faces.extend(_faces)
                offsets.extend(_offsets)
                colors.extend([hex2rgba(block.color)] * len(_offsets))

            num_vertices += len(_vertices)

        if seperate_blocks:
            collection = bpy.data.collections.new(name)
            ac.children.link(collection)
        else:
            create_mesh(objects, vertices, faces, offsets, colors=colors, dataname=name)
            collection = ac

        for o in objects:
            collection.objects.link(o)
            o.matrix_world = global_matrix @ o.matrix_world
            o.select_set(True)

    vl.update()

    return {'FINISHED'}
