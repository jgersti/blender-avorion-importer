from __future__ import annotations

import numpy as np
import bpy

try:
    import xml.etree.cElementTree as ElementTree
except:
    import xml.etree.ElementTree as ElementTree

from mathutils import Matrix, Vector
from bpy_extras.io_utils import axis_conversion
from bpy_extras.wm_utils.progress_report import ProgressReport

from .avorion_utils.parser import Ship, Turret, Block

def load(context,
        filepath: str,
        *,
        recenter_to_origin: bool = False,
        seperate_blocks: bool = True,
        global_matrix: Matrix = None
    ):

    wm = context.window_manager


    with ProgressReport(wm) as progress:
        progress.enter_substeps(1, f"Importing Avorion XML {filepath}...")

        global_matrix = global_matrix or Matrix()

        progress.enter_substeps(3, f"Parsing Avorion XML file...")
        xml = ElementTree.parse(filepath)
        root = xml.getroot()

        design = None

        tag = root.tag
        if tag == "ship_design":
            design = Ship.from_xml(root)
        elif tag == "turret_design":
            design = Turret.from_xml(root)
        else:
            raise IOError("Invalid file format.")
        progress.step("Done.")

        progress.enter_substeps(5, f"Building Geomtry...")





    return {'FINISHED'}
