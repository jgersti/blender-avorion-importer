import itertools
import math
from collections.abc import Sequence, Iterator
from typing import overload


import bpy
import bpy.types
import numpy as np
import numpy.typing as npt


try:
    import xml.etree.cElementTree as ElementTree
except ImportError:
    import xml.etree.ElementTree as ElementTree

from pathlib import Path

from bpy.types import Armature, Collection, Context, Object, Mesh
from mathutils import Matrix, Vector

from .avorion_utils.parser import Ship, Turret, Block
from .avorion_utils.geometry import Geometry
from .avorion_utils.categories import get_shape, get_category, get_material

def hex2rgba(color: str) -> tuple[float, float, float, float]:
    # thing about a more elegant was to pass this arround
    return tuple((np.roll(np.frombuffer(bytearray.fromhex(color), np.uint8, 4), -1) / 255).tolist())


def generate_mesh(
    geometry: Geometry,
    name: str,
    origin: Vector | None,
    colors: npt.ArrayLike | tuple[float, float, float, float],
    secondary_colors: npt.ArrayLike | tuple[float, float, float, float],
) -> Object:
    mesh = bpy.data.meshes.new(name)

    mesh.vertices.add(len(geometry.vertices))
    mesh.loops.add(int(np.sum(geometry.offsets)))
    mesh.polygons.add(len(geometry.offsets))

    mesh.vertices.foreach_set("co", np.asarray(geometry.vertices).reshape(-1))
    mesh.polygons.foreach_set("loop_total", geometry.offsets)
    mesh.polygons.foreach_set("loop_start", np.cumsum(geometry.offsets)-geometry.offsets)
    mesh.polygons.foreach_set("vertices", geometry.faces)

    if isinstance(colors, tuple):
        colors = np.asarray([colors] * len(geometry.offsets))

    attr = mesh.color_attributes.get("Color") or mesh.color_attributes.new("Color", "BYTE_COLOR", "CORNER")
    attr.data.foreach_set("color_srgb", np.repeat(colors, geometry.offsets, axis=0).reshape(-1))

    if isinstance(secondary_colors, tuple):
        secondary_colors = np.asarray([secondary_colors] * len(geometry.offsets), np.int8)
    attr = mesh.color_attributes.get("Secondary Color") or mesh.color_attributes.new("Secondary Color", "BYTE_COLOR", "CORNER")
    attr.data.foreach_set("color_srgb", np.repeat(secondary_colors, geometry.offsets, axis=0).reshape(-1))

    mesh.color_attributes.default_color_name = "Color"
    mesh.color_attributes.active_color_name = "Color"

    mesh.shade_flat()
    mesh.update()

    obj = bpy.data.objects.new(mesh.name, mesh)

    if origin is not None:
        obj.matrix_world = Matrix.Translation(origin)

    return obj

def generate_objects(
    blocks: Sequence[Block],
    name: str = "",
    origin: Vector | None = None,
    seperate_blocks: bool = False
) -> Iterator[Object]:
    if seperate_blocks:
        yield from (generate_mesh(Geometry.from_block(block), f"{name}.block{block.index}", origin, hex2rgba(block.color), hex2rgba(block.secondary_color)) for block in blocks)
    else:
        geometry, num_faces = Geometry.concatenate(Geometry.from_block(block) for block in blocks)
        colors = [*itertools.chain.from_iterable([hex2rgba(block.color)] * faces for block, faces in zip(blocks, num_faces))]
        secondary_colors = [*itertools.chain.from_iterable([hex2rgba(block.secondary_color)] * faces for block, faces in zip(blocks, num_faces))]

        yield generate_mesh(geometry, name, origin, colors, secondary_colors) # check if this is a problem ...


def create_turret_armature(context: Context, collection: Collection, design: Turret, name: str = "turret"):
    _armature = bpy.data.armatures.new(f"{name}_armature")
    armature = bpy.data.objects.new(_armature.name, _armature)

    collection.objects.link(armature)
    armature.select_set(True)
    context.view_layer.objects.active = armature

    bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
    bpy.ops.object.mode_set(mode='EDIT', toggle=False)

    edit_bones = _armature.edit_bones
    bones = (f"{armature.name}_base", f"{armature.name}_rotation",
             f"{armature.name}_elevation", f"{armature.name}_target")

    base = edit_bones.new(bones[0])
    base.head = design.base.origin
    base.tail = design.base.origin + np.array([0, 0.1, 0]) * design.size

    rotation = edit_bones.new(bones[1])
    rotation.head = design.body.origin
    rotation.tail = design.body.origin + np.array([0, 0, -0.1]) * design.size

    elevation = edit_bones.new(bones[2])
    elevation.head = design.barrel.origin
    elevation.tail = design.barrel.origin + np.array([0, 0, 0.1]) * design.size

    target = edit_bones.new(bones[3])
    avg_muzzle = np.sum(design.muzzles) / len(design.muzzles)
    target.head = avg_muzzle + np.array([0, 0, 10]) * design.size
    target.tail = avg_muzzle + np.array([0, 0, 11]) * design.size

    rotation.use_connect = elevation.use_connect = target.use_connect = False
    rotation.parent = base
    elevation.parent = rotation
    target.parent = base

    bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

    assert armature.pose is not None

    pose_bones = armature.pose.bones
    rotation = pose_bones.get(bones[1])
    assert rotation is not None
    elevation = pose_bones.get(bones[2])
    assert elevation is not None
    target = pose_bones.get(bones[3])
    assert target is not None

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



def load(
    context: bpy.types.Context,
    filepath: str,
    *,
    recenter_to_origin: bool = False,
    seperate_blocks: bool = True,
    global_matrix: Matrix | None = None
):
    name = Path(filepath).stem
    wm = context.window_manager
    vl = context.view_layer

    assert vl
    assert vl.active_layer_collection
    assert context.scene

    for o in context.scene.objects:
        o.select_set(False)

    ac = vl.active_layer_collection.collection

    global_matrix = global_matrix or Matrix()

    xml = ElementTree.parse(filepath)
    root = xml.getroot()

    if root.tag not in ("ship_design","turret_design", "plan"):
        raise IOError("Invalid file format.")

    if root.tag == "turret_design":
        design = Turret.from_xml(root, name)


        collection = bpy.data.collections.new(design.name)
        ac.children.link(collection)

        if seperate_blocks:
            if design.coaxial:
                for o in generate_objects(design.base.blocks, design.name, Vector(design.base.origin.tolist()), seperate_blocks):
                    collection.objects.link(o)
                    o.matrix_world = global_matrix @ o.matrix_world
                    o.select_set(True)
            else:
                for part in (design.base, design.body, design.barrel):
                    part_collection = bpy.data.collections.new(f"{design.name}.{part.part}")
                    collection.children.link(part_collection)
                    for o in generate_objects(part.blocks, f"{design.name}.{part.part}", Vector(part.origin.tolist()), seperate_blocks):
                        part_collection.objects.link(o)
                        o.matrix_world = global_matrix @ o.matrix_world
                        o.select_set(True)

            # do not rig for now
        else:
            if design.coaxial:
                objects = [*generate_objects(design.base.blocks, design.name, Vector(design.base.origin.tolist()), seperate_blocks)]
            else:
                objects = []
                # implement iter ?!?
                for part in (design.base, design.body, design.barrel):
                    objects.extend(generate_objects(part.blocks, f"{design.name}.{part.part}", Vector(part.origin.tolist()), seperate_blocks))

            for o in objects:
                collection.objects.link(o)
                # o.matrix_world = global_matrix @ o.matrix_world
                # o.select_set(True)

            if not design.coaxial:
                armature, bones = create_turret_armature(context, collection, design, name)

                # link rig to mesh
                for o, b in zip(objects, bones):
                    o.parent = armature
                    o.parent_type = 'BONE'
                    o.parent_bone = b

                armature.matrix_world = global_matrix # ?!?

            for o in objects:
                o.matrix_world = global_matrix @ o.matrix_world
                o.select_set(True)
    else:
        design = Ship.from_xml(root, name)

        obj = bpy.data.objects.new(design.name, None)
        for o in generate_objects(design.blocks, f"{design.name}.hull", None, seperate_blocks):
           ac.objects.link(o)
           o.parent = obj

        ac.objects.link(obj)
        obj.matrix_world = global_matrix @ obj.matrix_world
        obj.select_set(True)
    vl.update()

    return {'FINISHED'}
