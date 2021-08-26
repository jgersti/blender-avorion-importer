from __future__ import annotations

from dataclasses import dataclass, field
from numpy import ndarray, float64, int64

try:
    from xml.etree.cElementTree import Element
except:
    from xml.etree.ElementTree import Element


@dataclass(frozen=True)
class Block:
    index:          int
    lower:          ndarray
    upper:          ndarray
    orientation:    ndarray
    type:           int
    material:       int
    color:          str
    parent:         int = -1

    @classmethod
    def from_xml(cls, item_xml: Element, offset: ndarray = None) -> Block:
        if item_xml.tag == "item":
            block_xml = item_xml.find("block")
            if block_xml != None:
                attr = block_xml.attrib

                lower = ndarray([attr["lx"], attr["ly"], attr["lz"]], dtype=float64)
                upper = ndarray([attr["ux"], attr["uy"], attr["uz"]], dtype=float64)
                orientation = ndarray(
                    [attr["look"], attr["up"]], dtype=int64)

                if offset is not None:
                    lower += offset
                    upper += offset

                return Block(
                    index       = int(item_xml.get("index")),
                    parent      = int(item_xml.get("parent")),
                    lower       = lower,
                    upper       = upper,
                    orientation = orientation,
                    type        = int(attr["index"]),
                    material    = int(attr["material"]),
                    color       = attr["color"])
            else:
                raise ValueError("<item> does not contain <block> tag.")
        else:
            raise ValueError("Invalid <item> tag.")


@dataclass(frozen=True)
class Turret:
    size:       float
    coaxial:    bool
    parent:     int = -1
    color:      int = -1
    muzzles:    list[ndarray] = field(init=False, default_factory=list, repr=False)
    base:       list[Block] = field(default_factory=list, repr=False)
    body:       list[Block] = field(default_factory=list, repr=False)
    barrel:     list[Block] = field(default_factory=list, repr=False)

    @classmethod
    def from_xml(cls, turret_xml: Element) -> Turret:
        if turret_xml.tag != "turret_design" and turret_xml.tag != "turretDesign":
            raise ValueError("Invalid turret element.")

        coaxial = turret_xml.get("coaxial") == "true"

        if coaxial:
            raise NotImplementedError("Coaxial turrets are not yet implemented.")
        else:
            base_xml = turret_xml.find("base")
            base_offset = ndarray([base_xml.get("px"),
                                   base_xml.get("py"),
                                   base_xml.get("pz")], dtype=float64)
            base = [Block.from_xml(b, base_offset) for b in base_xml.iterfind("*/item")]

            body_xml = turret_xml.find("body")
            body_offset = ndarray([body_xml.get("px"),
                                   body_xml.get("py"),
                                   body_xml.get("pz")], dtype=float64)
            body = [Block.from_xml(b, body_offset) for b in body_xml.iterfind("*/item")]

            barrel_xml = turret_xml.find("barrel")
            barrel_offset = ndarray([barrel_xml.get("px"),
                                     barrel_xml.get("py"),
                                     barrel_xml.get("pz")], dtype=float64)
            barrel = [Block.from_xml(b, barrel_offset) for b in barrel_xml.iterfind("*/item")]

            return Turret(
                size=float(turret_xml.get("size")),
                coaxial=coaxial,
                color=int(turret_xml.get("shot_color")),
                parent=int(turret_xml.get("blockIndex", -1)),
                base=base,
                body=body,
                barrel=barrel)



@dataclass(frozen=True)
class Ship:
    blocks:     list[Block] = field(default_factory=list, repr=False)
    turrets:    list[Turret] = field(default_factory=list, repr=False)

    @classmethod
    def from_xml(cls, ship_xml: Element, name: str = "") -> Ship:
        if ship_xml.tag != "ship_design":
            raise ValueError("No <ship_design> found.")

        blocks = [Block.from_xml(item) for item in ship_xml.iterfind('plan/item')]
        turrets = [Turret.from_xml(turret) for turret in ship_xml.iterfind('turretDesign')]

        return Ship(blocks=blocks, turrets=turrets)
