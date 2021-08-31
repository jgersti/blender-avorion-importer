from __future__ import annotations

import numpy as np
from dataclasses import dataclass, field

try:
    from xml.etree.cElementTree import Element
except:
    from xml.etree.ElementTree import Element


@dataclass(frozen=True)
class Block:
    index:          int
    lower:          np.ndarray
    upper:          np.ndarray
    orientation:    np.ndarray
    type:           int
    material:       int
    color:          str
    parent:         int = -1

    @classmethod
    def from_xml(cls, item_xml: Element) -> Block:
        if item_xml.tag == "item":
            block_xml = item_xml.find("block")
            if block_xml != None:
                attr = block_xml.attrib

                lower = np.array([attr["lx"], attr["ly"], attr["lz"]], dtype=np.float64)
                upper = np.array([attr["ux"], attr["uy"], attr["uz"]], dtype=np.float64)
                orientation = np.array([attr["look"], attr["up"]], dtype=np.int64)

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
    size:           float
    coaxial:        bool = False
    parent:         int = -1
    color:          int = -1
    base_origin:    np.ndarray = field(default_factory=lambda: np.zeros(3), repr=False)
    base:           list[Block] = field(default_factory=list, repr=False)
    body_origin:    np.ndarray = field(default_factory=lambda: np.zeros(3), repr=False)
    body:           list[Block] = field(default_factory=list, repr=False)
    barrel_origin:  np.ndarray = field(default_factory=lambda: np.zeros(3), repr=False)
    barrel:         list[Block] = field(default_factory=list, repr=False)
    muzzles:        list[np.ndarray] = field(default_factory=list, repr=False)

    @classmethod
    def from_xml(cls, turret_xml: Element) -> Turret:
        if turret_xml.tag != "turret_design" and turret_xml.tag != "turretDesign":
            raise ValueError("Invalid turret element.")

        coaxial = turret_xml.get("coaxial") == "true"

        muzzles = [np.array([m.get("x"), m.get("y"), m.get("z")], dtype=np.float64)
                   for m in turret_xml.iterfind("muzzlePosition")]

        if coaxial:
            raise NotImplementedError("Coaxial turrets are not yet implemented.")
        else:
            base_xml = turret_xml.find("base")
            base_origin = np.array([base_xml.get("px"),
                                    base_xml.get("py"),
                                    base_xml.get("pz")],
                                   dtype=np.float64)
            base = [Block.from_xml(b) for b in base_xml.iterfind("*/item")]

            body_xml = turret_xml.find("body")
            body_origin = np.array([body_xml.get("px"),
                                    body_xml.get("py"),
                                    body_xml.get("pz")],
                                   dtype=np.float64)
            body = [Block.from_xml(b) for b in body_xml.iterfind("*/item")]

            barrel_xml = turret_xml.find("barrel")
            barrel_origin = np.array([barrel_xml.get("px"),
                                      barrel_xml.get("py"),
                                      barrel_xml.get("pz")],
                                     dtype=np.float64)
            barrel = [Block.from_xml(b) for b in barrel_xml.iterfind("*/item")]

            return Turret(
                size            = float(turret_xml.get("size")),
                coaxial         = coaxial,
                color           = int(turret_xml.get("shot_color")),
                parent          = int(turret_xml.get("blockIndex", -1)),
                muzzles         = muzzles,
                base_origin     = base_origin,
                base            = base,
                body_origin     = body_origin,
                body            = body,
                barrel_origin   = barrel_origin,
                barrel          = barrel)

    def get_part(self, part: str) -> tuple[list[Block], np.np.adarray]:
        if part.casefold() == "base":
            return self.base, self.base_origin
        elif part.casefold() == "body":
            return self.body, self.body_origin
        elif part.casefold() == "barrel":
            return self.barrel, self.barrel_origin
        else:
            raise ValueError(f"Invalid input argument '{part}'.")


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
