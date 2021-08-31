from dataclasses import dataclass


@dataclass(frozen=True)
class Material:
    index: int
    name: str
    color: str


MATERIALS = (
    Material(0, "Iron", "#ffb380"),
    Material(1, "Titanium", "#ffffff"),
    Material(2, "Naonite", "#4dff4d"),
    Material(3, "Trinium", "#4d9aff"),
    Material(4, "Xanion", "#ffff4d"),
    Material(5, "Ogonite", "#ff8133"),
    Material(6, "Avorion", "#ff2626"),
)


SHAPES = {
    "Cube":             (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18,
                         19, 20, 22, 50, 51, 52, 53, 54, 55, 56, 57, 58, 60, 61, 121,
                         122, 150, 170, 180, 190, 510, 520, 600, 650, 700),
    "Edge":             (21, 23, 100, 104, 114, 123, 151, 171, 181, 185, 191, 511, 521,
                         601, 651, 701),
    "Corner 1":         (101, 105, 115, 124, 152, 172, 182, 186, 192, 512, 522, 702),
    "Corner 2":         (102, 106, 116, 125, 153, 173, 183, 187, 193, 513, 523, 703),
    "Corner 3":         (103, 107, 117, 126, 154, 174, 184, 188, 194, 514, 524, 704),
    "Twisted Corner 1": (108, 110, 118, 128, 155, 175, 195, 197, 199, 515, 525, 705),
    "Twisted Corner 2": (109, 111, 119, 129, 156,176, 196, 198, 200, 516, 526, 706),
    "Flat Corner":      (112, 113, 120, 127, 157, 177, 201, 202, 203, 517, 527, 707),
}


CATEGORIES = {
    "Smart Hull":       (1, 2, 100, 101, 102, 103, 108, 109, 112),
    "Hull":             (121, 122, 123, 124, 125, 126, 127, 128, 129),
    "Armor":            (8, 104, 105, 106, 107, 110, 111, 113),
    "Crew":             (6, 114, 115, 116, 117, 118, 119, 120),
    "Glow":             (150, 151, 152, 153, 154, 155, 156, 157),
    "Glass":            (170, 171, 172, 173, 174, 175, 176, 177),
    "Reflector":        (180, 181, 182, 184, 195, 196, 201),
    "Stone":            (4, 185, 186, 187, 188, 197, 198, 202),
    "Hologram":         (190, 191, 192, 193, 194, 199, 200, 203),
    "Rich Stone":       (510, 511, 512, 513, 514, 515, 516, 517),
    "Super Rich Stone": (520, 521, 522, 523, 524, 525, 526, 527),
    "Wreckage":         (700, 701, 702, 703, 704, 705, 706, 707),
    # Rot. Lock,  +Edge, Torp. Launcher, Frontal+, Turret Base, +Edge
    "Hardpoints":       (12, 23, 18, 22, 20, 21),
    # Engine, Thruster, Dir. Thruster, Gyro, Inert. Dampener
    "Propulsion":       (3, 7, 13, 14, 15),
    # Shield, Energy Cont., Generator, Int. Field, Comp. Core, Hyperspace Core,
    "Systems":          (50, 51, 52, 53, 54, 55),
    # Cargo, Framework, Hangar, Dock, Flight Recorder, Assembly, Torp. Storage, Transporter,
    #   Academy, Cloning Pods, Solar Panel, Light, Name, +Edge, Logo, +Edge
    "The Rest":         (5, 9, 10, 11, 16, 17, 19, 56, 57, 58, 60, 61, 600, 601, 650, 651),
}


def get_shape(index: int) -> str:
    try:
        return next((key for key, indices in SHAPES.items() if index in indices))
    except:
        raise ValueError(f"invalid type index '{index}'.")

def get_category(index: int) -> str:
    try:
        return next((key for key, indices in CATEGORIES.items() if index in indices))
    except:
        raise ValueError(f"invalid type index '{index}'.")

def get_material(index: int) -> Material:
    try:
        return next((m for m in MATERIALS if index == m.index))
    except:
        raise ValueError(f"invalid material index '{index}'.")
