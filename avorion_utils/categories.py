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
    "Cube": (
        0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 22, 23, 24, 25, 50,
        51, 52, 53, 54, 55, 56, 57, 58, 60, 61, 62, 63, 64, 65, 121, 122, 150, 170, 180, 190, 210,
        220, 230, 240, 250, 260, 270, 280, 290, 300, 310, 500, 510, 520, 530, 540, 550, 560, 600,
        650, 700),
    "Edge": (21, 23, 25, 100, 104, 114, 123, 151, 171, 181, 185, 191, 211, 221, 231, 241, 251, 261,
             271, 281, 291, 301, 311, 511, 521, 531, 541, 551, 601, 651, 701),
    "Corner 1": (101, 105, 115, 124, 152, 172, 182, 186, 192, 212, 222, 232, 242, 252, 262, 272,
                 282, 292, 302, 312, 512, 522, 532, 542, 552, 562, 702),
    "Corner 2": (102, 106, 116, 125, 153, 173, 183, 187, 193, 213, 223, 233, 243, 253, 263, 273,
                 283, 293, 303, 313, 513, 523, 533, 543, 553, 563, 703),
    "Corner 3": (103, 107, 117, 126, 154, 174, 184, 188, 194, 214, 224, 234, 244, 254, 264, 274,
                 284, 294, 304, 314, 514, 524, 534, 544, 554, 564, 704),
    "Twisted Corner 1": (108, 110, 118, 128, 155, 175, 195, 197, 199, 215, 225, 235, 245, 255, 265,
                         275, 285, 295, 305, 315, 515, 525, 535, 545, 555, 565, 705),
    "Twisted Corner 2": (109, 111, 119, 129, 156, 176, 196, 198, 200, 216, 226, 236, 246, 256, 266,
                         276, 286, 296, 306, 316, 516, 526, 536, 546, 556, 566, 706),
    "Flat Corner": (112, 113, 120, 127, 157, 177, 201, 202, 203, 217, 227, 237, 247, 257, 267, 277,
                    287, 297, 307, 317, 517, 527, 537, 547, 557, 567, 707),
}


CATEGORIES = {
    "Smart Hull": (0, 1, 2, 100, 101, 102, 103, 108, 109, 112),
    "Armor": (8, 104, 105, 106, 107, 110, 111, 113),
    "Crew": (6, 114, 115, 116, 117, 118, 119, 120),
    "Hull": (121, 122, 123, 124, 125, 126, 127, 128, 129),
    "Glow": (150, 151, 152, 153, 154, 155, 156, 157),
    "Glass": (170, 171, 172, 173, 174, 175, 176, 177),
    "Reflector": (180, 181, 182, 184, 195, 196, 201),
    "Stone": (4, 185, 186, 187, 188, 197, 198, 202),
    "Hologram": (190, 191, 192, 193, 194, 199, 200, 203),
    "Hull Alternate A": (210, 211, 212, 213, 214, 215, 216, 217),
    "Hull Alternate B": (220, 221, 222, 223, 224, 225, 226, 227),
    "Armor Digital Camo": (230, 231, 232, 233, 234, 235, 236, 237),
    "Hull Vivid": (240, 241, 242, 243, 244, 245, 246, 247),
    "Hull White Stripes A": (250, 251, 252, 253, 254, 255, 256, 257),
    "Hull White Stripes B": (260, 261, 262, 263, 264, 265, 266, 267),
    "Hull White Stripes C": (270, 271, 272, 273, 274, 275, 276, 277),
    "Hull Dark Stripes A": (280, 281, 282, 283, 284, 285, 286, 287),
    "Hull Dark Stripes B": (290, 291, 292, 293, 294, 295, 296, 297),
    "Hull Dark Stripes C": (300, 301, 302, 303, 304, 305, 306, 307),
    "Scaffold": (310, 311, 312, 313, 314, 315, 316, 317),
    "Rich Stone": (510, 511, 512, 513, 514, 515, 516, 517),
    "Super Rich Stone": (520, 521, 522, 523, 524, 525, 526, 527),
    "Rift Stone": (530, 531, 532, 533, 534, 535, 536, 537),
    "Rich Rift Stone": (540, 541, 542, 543, 544, 545, 546, 547),
    "Super Rich Rift Stone": (550, 551, 552, 553, 554, 555, 556, 557),
    "Glow Stone" : (560, 561, 562, 563, 564, 565, 566, 567),
    "Wreckage": (700, 701, 702, 703, 704, 705, 706, 707),
    # Rot. Lock,  +Edge, Torp. Launcher, Frontal+, Turret Base, +Edge, ...
    "Hardpoints": (12, 18, 22, 20, 21, 22, 23, 24, 25),
    # Engine, Thruster, Dir. Thruster, Gyro, Inert. Dampener
    "Propulsion": (3, 7, 13, 14, 15),
    # Shield, Energy Cont., Generator, Int. Field, Comp. Core, Hyperspace Core,
    "Systems": (50, 51, 52, 53, 54, 55),
    # Cargo, Framework, Hangar, Dock, Flight Recorder, Assembly, Torp. Storage, Transporter,
    #   Academy, Cloning Pods, Solar Panel, Light, Portal, Name, +Edge, Logo, +Edge
    "The Rest": (5, 9, 10, 11, 16, 17, 19, 56, 57, 58, 60, 61, 62, 63, 64, 65, 500, 600, 601, 650, 651),
}


def get_shape(index: int) -> str:
    try:
        return next((key for key, indices in SHAPES.items() if index in indices), "Cube")
    except Exception as e:
        raise ValueError(f"invalid type index '{index}'.") from e


def get_category(index: int) -> str:
    try:
        return next((key for key, indices in CATEGORIES.items() if index in indices))
    except Exception as e:
        raise ValueError(f"invalid type index '{index}'.") from e


def get_material(index: int) -> Material:
    try:
        return next((m for m in MATERIALS if index == m.index))
    except Exception as e:
        raise ValueError(f"invalid material index '{index}'.") from e
