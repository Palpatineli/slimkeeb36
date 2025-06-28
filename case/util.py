# %%
from typing import Tuple, TypedDict
from math import sqrt, tan, pi
import build123d as bd
MIN = bd.Align.MIN

tolerance_s = 0.1
tolerance_m = 0.3
max_dist = 10

def make_locking(size: float, height: float) -> Tuple[bd.Part, bd.Part]:
    # size, height = 10, 20
    s = bd.Rectangle(size / 2, size / 8) + bd.Rectangle(size / 8, size / 2)
    s = bd.fillet([s.vertices()[idx] for idx in (2, 5, 8, 11)], radius=size / 8)
    inset = bd.extrude(s, height)  # type: ignore
    socket = bd.extrude(bd.offset(s, tolerance_s), height)
    return inset, socket


def cut(part: bd.Part, loc: bd.Part, tol: float = 0.2) -> Tuple[bd.Part, bd.Part]:
    """return the part inside loc, then the part outside"""
    MAX_SIZE = 900
    return part - (bd.Box(MAX_SIZE, MAX_SIZE, MAX_SIZE) - loc), part - (bd.offset(loc, tol) if tol > 0 else loc)


def build_joint(height: float) -> bd.Part:
    beam = 10
    notch = bd.make_face(bd.Polyline((-beam / 6, 0), (-beam / 4, beam / 3), (beam / 4, beam / 3), (beam / 6, 0), (-beam / 6, 0)))  # type: ignore
    return bd.Pos(X=beam/2) * bd.extrude(notch, height)

def hex_screw_hole(nut_side: float) -> bd.Sketch:
    sqrt3 = sqrt(3)
    return bd.make_face(bd.offset(
        bd.Polyline((-nut_side / 2, -nut_side / (2 * sqrt3)), (-nut_side / 2, nut_side / (2 * sqrt3)),
                    (0, nut_side / sqrt3), (nut_side / 2, nut_side / (2 * sqrt3)),
                    (nut_side / 2, -nut_side / (2 * sqrt3)), (0, -nut_side / sqrt3),
                    (-nut_side / 2, -nut_side / (2 * sqrt3))), 0.2))  # type: ignore

def hex_screw_drop(nut_side: float, depth: float) -> bd.Part:
    sqrt3 = sqrt(3)
    return bd.extrude(bd.make_face(bd.offset(
        bd.Polyline((-nut_side / 2, -nut_side / (2 * sqrt3)), (-nut_side / 2, nut_side / sqrt3),
                    (nut_side / 2, nut_side / sqrt3), (nut_side / 2, -nut_side / (2 * sqrt3)), (0, -nut_side / sqrt3),
                    (-nut_side / 2, -nut_side / (2 * sqrt3))), 0.2)), depth + 0.3)  # type: ignore
# %%
def screw_nut_tab(hang: float, thickness: float, screw_length: float, standoff: float, screw_size: float = 4, 
                  is_square: bool = True) -> Tuple[bd.Part, bd.Part]:
    """Create a tab/wing for a screw, centered at the top of the screw hole.
    returns the part and a holeless part for subtraction
    """
    if is_square:
        nut_side = 8 + tolerance_m * 2
        nut_thickness = 2.7 + tolerance_m * 2
        nut_primitive = bd.Pos(Z=-max_dist / 2) * bd.Rot(Z=45) * bd.Box(nut_side + tolerance_m, nut_side + tolerance_m * 3, max_dist)
    else:
        nut_side = 7.9 + tolerance_m * 2
        nut_thickness = 2.8 + tolerance_m * 2
        nut_primitive = bd.Rot(Z=90) * bd.extrude(hex_screw_hole(nut_side), -max_dist)  # type: ignore
    outer_diam = screw_size * 4
    hang = max(hang, outer_diam / 3)
    nut_hole = bd.Pos(Y=tolerance_m, Z=-(screw_length - standoff - nut_thickness / 2)) * nut_primitive
    triangle_height = hang + outer_diam / sqrt(2)
    frame = bd.Pos(Y=triangle_height / 2 - hang) * bd.Triangle(a = triangle_height * 2, B=45, C=45, align=bd.Align.CENTER)
    frame = bd.fillet(frame.vertices()[2], radius=outer_diam / 2)
    pos = bd.extrude(frame, -thickness) + bd.loft([frame, bd.Pos(Z=standoff) * bd.Circle(outer_diam / 4 + screw_size / 4)])
    neg = nut_hole + bd.Pos(Z=standoff - screw_length / 2 - tolerance_m) * bd.Cylinder(screw_size / 2 + tolerance_m, screw_length + tolerance_m * 2)
    return pos, neg


def screw_tab(hang: float, set_back: float, head_size: float = 7.5, head_height: float = 1.4) -> Tuple[bd.Part, bd.Part]:
    skin = 2.5
    screw_size = 4 + tolerance_m * 2
    head_size += tolerance_m * 2
    head_height += tolerance_s
    screw_clearance = 5
    beam_size = 10
    outer_diam = screw_size * 3
    triangle_height = hang + outer_diam / sqrt(2)
    frame = bd.Pos(Y=triangle_height / 2 - hang) * bd.Triangle(a = triangle_height * 2, B=45, C=45, align=bd.Align.CENTER)
    frame = bd.fillet(frame.vertices()[2], radius=outer_diam / 2)
    pos = bd.extrude(frame, -beam_size)  # type: ignore
    pos -= bd.Pos(Y=set_back * 3, Z=-(beam_size + skin + head_height) / 2) * bd.Box(set_back * 8, set_back * 8, beam_size - skin - head_height)
    neg = bd.Pos(Z=(screw_clearance - head_height) / 2) * bd.Cylinder(head_size / 2, head_height + screw_clearance) \
        + bd.Pos(Z=(-head_height - skin / 2)) * bd.Cylinder(screw_size / 2, skin)
    return pos, neg


def screw_tab_standoff(hang: float, standoff: float, screw_size: float = 4, head_size: float = 6.5,
                       head_height: float = 2.65) -> Tuple[bd.Part, bd.Part]:
    skin = 2.5
    head_height += tolerance_m
    outer_diam = screw_size * 3
    triangle_height = hang + outer_diam / sqrt(2)
    frame = bd.Pos(Y=triangle_height / 2 - hang) * bd.Triangle(a = triangle_height * 2, B=45, C=45, align=bd.Align.CENTER)
    frame = bd.fillet(frame.vertices()[2], radius=outer_diam / 2)
    frame_height = max(skin, skin + head_height - standoff)
    pos = bd.extrude(frame, -frame_height) + bd.loft([bd.Circle(outer_diam / 2), bd.Pos(Z=standoff) * bd.Circle(outer_diam / 4 + screw_size / 4)])
    neg = bd.Pos(Z=(standoff - frame_height) / 2) * bd.Cylinder(screw_size / 2 + tolerance_m, standoff + frame_height)\
        + bd.Pos(Z=head_height / 2 - frame_height) * bd.Cylinder(head_size / 2 + tolerance_m, head_height)
    return pos, neg


def gen_psu(psu: dict, screw: dict, beam: float, tol: float, skin: float,
            top_beam: bool = True) -> Tuple[bd.Part, bd.Part]:
    # screw, tol, skin = screw['psu'], tol['m'], skin['l']
    screw_skin = 2
    psu_neg = bd.Pos(-tol, -tol) * bd.Box(psu['w'] + tol * 2, psu['h'] + tol * 2, psu['l'] + beam * 2 + tol * 2, align=MIN)
    edge_x, edge_y = psu['edge']
    screw_locs = ((edge_x, edge_y), (edge_x, psu['h'] - edge_y),
                 (psu['w'] - edge_x, edge_y), (psu['w'] - edge_x, psu['h'] - edge_y))
    head = screw['head'][1] + tol
    for x, y in screw_locs:
        psu_neg += bd.Pos(x, y, -screw_skin / 2) * bd.Cylinder(screw['shaft'][0] / 2 + tol * 1.5, screw_skin)
        psu_neg += bd.Pos(x, y, -screw_skin - head / 2) * bd.Cylinder(screw['head'][0] / 2 + tol * 1.5, head)
    frame_size = psu['w'] + (tol + skin) * 2, psu['h'] + (tol + skin) * 2, beam
    frame = bd.Box(frame_size[0] - (0 if top_beam else skin + tol), frame_size[1], frame_size[2], align=MIN)\
        - bd.Pos(beam, beam) * bd.Box(frame_size[0] - beam * 2, frame_size[1] - beam * 2, beam, align=MIN)
    corner = bd.extrude(bd.Pos(Y=1) * bd.Triangle(a=35, B=45, C=45, align=bd.Align.CENTER), head + screw_skin)
    corners = [bd.Pos(x, y) * bd.Rot(Z=rot) * corner for (x, y), rot in zip(screw_locs, (135, 45, -135, -45))]
    frame += bd.Pos(skin, skin) * (bd.Part() + corners)  # type: ignore
    return frame, bd.Pos(skin, skin, head + screw_skin) * psu_neg

class FanConfig(TypedDict):
    w: float
    h: float
    radius: float
    hole_dist: float

class InsertDict(TypedDict):
    od: float
    id: float
    hole: float

def gen_fan(fan: FanConfig, insert: InsertDict, thickness: float, extra_rim: float = 0):
    wedge_dist = (fan['radius'] - tan(pi / 8) * fan['radius']) * (sqrt(2) * fan['w'] / 2 - fan['radius']) / ((sqrt(2) - 1) * fan['radius'])
    wedge = bd.make_face(bd.Polyline(((0, -extra_rim), (wedge_dist, -extra_rim), (wedge_dist, 0), (0, wedge_dist), (0, -extra_rim))))
    hole = bd.Pos(fan['hole_dist'], fan['hole_dist']) * bd.Circle((insert['hole'] + tolerance_s) / 2)
    wedges = wedge + bd.Pos(X=fan['w']) * bd.mirror(wedge, bd.Plane.YZ)
    holes = hole + bd.Pos(X=fan['w']) * bd.mirror(hole, bd.Plane.YZ)
    wedges += bd.Pos(Y=fan['w']) * bd.mirror(wedges, bd.Plane.XZ)
    holes += bd.Pos(Y=fan['w']) * bd.mirror(holes, bd.Plane.XZ)
    return bd.extrude(wedges, thickness), bd.extrude(holes, thickness)




if __name__ == "__main__":
    # pos, neg = screw_nut_tab(4, 4, 10, 7.3, 5)
    # pos, neg = screw_tab(10, 5)
    from config import fan, insert
    pos = gen_fan(fan['140'], insert['m2.5'], 5)
    bd.export_stl(pos, 'output/util_test.stl')
print('done')
# %%

