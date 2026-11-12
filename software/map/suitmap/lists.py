"""The lists behind the numbers (porjadok/SOFTWARE.md, *CI-BTP*): the place list as Baťa's
SOFTWARE has it; the IMUs' places on the bones and the joint list, a first draft from Bogatyr's
CONSTRUCTION (*The IMUs*), to be tuned on the recordings.

A joint's value is the turn of its child bone in its parent bone's frame; `axes` the joint
table's (1 flexion, 2 abduction, 3 rotation, 4 swing forward, 5 swing out, 6 twist); the range
each axis's low and high ends in degrees, a first guess with room to spare, to be set by the
recordings and in 2° steps in the table.
"""
from __future__ import annotations

from dataclasses import dataclass

# --- the place list: line → places ------------------------------------------------------------

PLACES = {
    1: "left shoulder", 2: "left upper arm", 3: "left forearm", 4: "left hand",
    5: "right shoulder", 6: "right upper arm", 7: "right forearm", 8: "right hand",
    9: "left hip", 10: "left thigh", 11: "left calf", 12: "left foot",
    13: "right hip", 14: "right thigh", 15: "right calf", 16: "right foot",
    17: "head", 18: "chest and abdomen", 19: "neck and upper back", 20: "lower back",
    21: "Nataša", 22: "Míša",
}
LINE_PLACES = {1: [1, 2, 3, 4], 2: [5, 6, 7, 8], 3: [9, 10, 11, 12], 4: [13, 14, 15, 16],
               5: [17], 6: [18], 7: [19, 20], 8: [21, 22]}
HAND_FOOT = {1: 4, 2: 8, 3: 12, 4: 16}          # the glove's or the sock's place on a line


def place_of_line(place: int) -> int:
    return next(line for line, ps in LINE_PLACES.items() if place in ps)


# --- the IMUs' places: a unit's IMU k sits on this bone ----------------------------------------
# In each place, the IMUs in the order of Bogatyr's table, the order of the unit's table.

def _side(side: str, items: list[str]) -> list[str]:
    return [f"{side} {i}" for i in items]


IMU_PLACES: dict[int, list[str]] = {}
for side, base in (("left", 0), ("right", 4)):
    IMU_PLACES[1 + base] = _side(side, ["scapula", "scapula", "clavicle"])   # acromion, spine
    IMU_PLACES[2 + base] = _side(side, ["humerus"] * 4)
    IMU_PLACES[3 + base] = _side(side, ["ulna", "radius"])
    hand = ["index proximal", "index middle", "index distal", "thumb metacarpal",
            "middle proximal", "middle middle", "middle distal", "hand",
            "ring proximal", "ring middle", "ring distal", "hand",
            "little proximal", "little middle", "little distal", "hand",
            "thumb metacarpal", "thumb proximal", "thumb distal", "hand",
            "hand", "hand", "hand", "hand"]
    IMU_PLACES[4 + base] = _side(side, hand)
for side, base in (("left", 8), ("right", 12)):
    IMU_PLACES[1 + base] = ["pelvis"]                # the iliac crest: the pelvis' second look
    IMU_PLACES[2 + base] = _side(side, ["femur"] * 4)
    IMU_PLACES[3 + base] = _side(side, ["tibia", "tibia"])
    IMU_PLACES[4 + base] = _side(side, ["calcaneus", "midfoot", "forefoot", "hallux",
                                        "forefoot", "toes", "toes", "calcaneus"])
IMU_PLACES[17] = ["skull"] * 4
IMU_PLACES[18] = ["sternum"]
IMU_PLACES[19] = ["C2", "C5", "upper thorax", "upper thorax"]               # C2, C5, T2, T6
IMU_PLACES[20] = ["lower thorax", "lumbar", "pelvis"]                        # T12–L1, L3, S1


# --- the joint list ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Joint:
    number: int
    name: str
    parent: str
    child: str
    axes: tuple[int, ...]
    ranges: tuple[tuple[int, int], ...]      # degrees, an axis's low and high
    swing: bool = False                      # the shoulder and the hip: swing and twist


def _joints() -> list[Joint]:
    j: list[Joint] = []

    def add(name, parent, child, axes, ranges, swing=False):
        j.append(Joint(len(j) + 1, name, parent, child, axes, ranges, swing))

    add("head on neck", "C2", "skull", (1, 2, 3), ((-60, 60), (-50, 50), (-90, 90)))
    add("neck", "upper thorax", "C2", (1, 2, 3), ((-60, 60), (-50, 50), (-90, 90)))
    add("thoracic spine", "lower thorax", "upper thorax", (1, 2, 3), ((-40, 60), (-40, 40),
                                                                          (-50, 50)))
    add("lumbar spine", "pelvis", "lower thorax", (1, 2, 3), ((-40, 80), (-40, 40), (-40, 40)))
    for side in ("left", "right"):
        s = side + " "
        add(s + "scapula on thorax", "upper thorax", s + "scapula", (1, 2, 3),
            ((-40, 40), (-40, 40), (-40, 40)))
        add(s + "clavicle on sternum", "sternum", s + "clavicle", (1, 2), ((-40, 40), (-40, 40)))
        add(s + "shoulder", s + "scapula", s + "humerus", (4, 5, 6),
            ((-150, 150), (-150, 150), (-90, 90)), swing=True)
        add(s + "elbow", s + "humerus", s + "ulna", (1,), ((-10, 160),))
        add(s + "forearm", s + "ulna", s + "radius", (3,), ((-100, 100),))
        add(s + "wrist", s + "radius", s + "hand", (1, 2), ((-90, 90), (-40, 40)))
        add(s + "thumb CMC", s + "hand", s + "thumb metacarpal", (1, 2), ((-30, 60), (-20, 80)))
        add(s + "thumb MCP", s + "thumb metacarpal", s + "thumb proximal", (1,), ((-20, 80),))
        add(s + "thumb IP", s + "thumb proximal", s + "thumb distal", (1,), ((-30, 100),))
        for finger in ("index", "middle", "ring", "little"):
            f = s + finger + " "
            add(f + "MCP", s + "hand", f + "proximal", (1, 2), ((-40, 100), (-30, 30)))
            add(f + "PIP", f + "proximal", f + "middle", (1,), ((-10, 120),))
            add(f + "DIP", f + "middle", f + "distal", (1,), ((-20, 100),))
        add(s + "hip", "pelvis", s + "femur", (4, 5, 6), ((-150, 150), (-150, 150), (-90, 90)),
            swing=True)
        add(s + "knee", s + "femur", s + "tibia", (1, 3), ((-10, 160), (-40, 40)))
        add(s + "ankle", s + "tibia", s + "calcaneus", (1, 2), ((-60, 40), (-40, 40)))
        add(s + "midfoot", s + "calcaneus", s + "forefoot", (1, 2), ((-30, 30), (-30, 30)))
        add(s + "big toe", s + "forefoot", s + "hallux", (1,), ((-40, 90),))
    return j


JOINTS = _joints()


def joint_values() -> list[tuple[int, int, int, int]]:
    """The joint table's entries, one a value in the snapshot's order: the joint, the axis, the
    range's ends in 2° (meta packets 3 and 4)."""
    out = []
    for jt in JOINTS:
        for axis, (lo, hi) in zip(jt.axes, jt.ranges):
            out.append((jt.number, axis, lo // 2, hi // 2))
    return out
