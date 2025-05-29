from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Self, Literal

import numpy as np
import numpy.typing as npt

try:
    from xml.etree.cElementTree import Element
except ImportError:
    from xml.etree.ElementTree import Element


__all__ = ["Block", "Ship", "Turret"]


def _parse_coordinate(elem: Element) -> npt.NDArray[np.float64]:
    return np.array([elem.get("px"), elem.get("py"), elem.get("pz")], dtype=np.float64)

@dataclass(frozen=True, slots=True)
class Block:
    index: int
    lower: npt.NDArray[np.float64]
    upper: npt.NDArray[np.float64]
    orientation: npt.NDArray[np.int64]
    type: int
    material: int
    color: str
    secondary_color: str
    parent: int = -1

    @classmethod
    def from_xml(cls, item_xml: Element) -> Self:
        if item_xml.tag != "item":
            raise ValueError("Invalid <item> tag.")

        if (block_xml := item_xml.find("block")) is not None:
            attr = block_xml.attrib

            lower = np.array([attr["lx"], attr["ly"], attr["lz"]], dtype=np.float64)
            upper = np.array([attr["ux"], attr["uy"], attr["uz"]], dtype=np.float64)
            orientation = np.array([attr["look"], attr["up"]], dtype=np.int64)

            return cls(
                index=int(item_xml.get("index", "")),
                parent=int(item_xml.get("parent", "")),
                lower=lower,
                upper=upper,
                orientation=orientation,
                type=int(attr["index"]),
                material=int(attr["material"]),
                color=attr["color"],
                secondary_color=attr.get("secondaryColor", "00000000"),
            )
        else:
            raise ValueError("<item> does not contain <block> tag.")

    @property
    def bounds(self) -> tuple[npt.NDArray[np.float64], npt.NDArray[np.float64]]:
        return self.lower, self.upper


@dataclass(frozen=True, slots=True)
class TurretPart:
    part: Literal["barrel", "base", "body"] = "base"
    origin: npt.NDArray[np.float64] = field(default_factory=lambda: np.zeros(3), repr=False)
    blocks: Sequence[Block] = field(default_factory=list, repr=False)

    @classmethod
    def from_xml(cls, part_xml: Element) -> Self:
        assert part_xml.tag in ("barrel", "base", "body")

        return cls(
            part=part_xml.tag,
            origin=_parse_coordinate(part_xml),
            blocks=[Block.from_xml(b) for b in part_xml.iterfind("*/item")],
        )


@dataclass(frozen=True, slots=True)
class Turret:
    name: str
    size: float
    coaxial: bool = False
    parent: int = -1
    color: int = -1
    base: TurretPart = field(default_factory=TurretPart)
    body: TurretPart = field(default_factory=TurretPart)
    barrel: TurretPart = field(default_factory=TurretPart)
    muzzles: Sequence[npt.NDArray[np.float64]] = field(default_factory=list, repr=False)

    @classmethod
    def from_xml(cls, turret_xml: Element, name: str = "") -> Self:
        if turret_xml.tag != "turret_design" and turret_xml.tag != "turretDesign":
            raise ValueError("Invalid turret element.")

        base_xml = turret_xml.find("base")
        assert base_xml is not None
        body_xml = turret_xml.find("body")
        assert body_xml is not None
        barrel_xml = turret_xml.find("barrel")
        assert barrel_xml is not None

        return cls(
            name=name,
            size=float(turret_xml.get("size", "")),
            coaxial=turret_xml.get("coaxial") == "true",
            color=int(turret_xml.get("shot_color", "")),
            parent=int(turret_xml.get("blockIndex", -1)),
            muzzles=[
                np.asarray([m.get("x"), m.get("y"), m.get("z")], dtype=np.float64)
                for m in turret_xml.iterfind("muzzlePosition")
            ],
            base=TurretPart.from_xml(base_xml),
            body=TurretPart.from_xml(body_xml),
            barrel=TurretPart.from_xml(barrel_xml),
        )

@dataclass(frozen=True, slots=True)
class Ship:
    name: str
    blocks: Sequence[Block] = field(default_factory=list, repr=False)
    turrets: Sequence[Turret] = field(default_factory=list, repr=False)

    @classmethod
    def from_xml(cls, ship_xml: Element, name: str = "") -> Self:
        match ship_xml.tag:
            case "ship_design":
                tag = "plan/item"
            case "plan":
                tag = "item"
            case _:
                raise ValueError(f"Invalid XML tag: {ship_xml.tag}")

        return cls(
            name=name,
            blocks=[Block.from_xml(item) for item in ship_xml.iterfind(tag)],
            turrets=[Turret.from_xml(turret) for turret in ship_xml.iterfind("turretDesign")],
        )
