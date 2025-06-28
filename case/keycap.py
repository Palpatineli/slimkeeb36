# %%
__all__ = ("keycap", )
from functools import cache
import build123d as bd

key = {'l': 18, 'w': 17, 'h': 3.4}
shroud = {'height': 0.5, 'thick': 1}
foot = {'w': 1.19, 'h': 2.99, 'z': 2.99}
curvature, dip = 27, 2
chamfer = 2
# %%
@cache
def keycap(homing: bool = False) -> bd.Part:
    stem_profile = bd.fillet((bd.Rectangle(1.17, 4.1) + bd.Rectangle(4.1, 1.17)).vertices().sort_by(bd.Axis.X)[2:-2].sort_by(bd.Axis.Y)[2: -2], 0.3)
    stem = bd.extrude(bd.Circle(2.65) - stem_profile, -3.8)
    head = bd.Pos(Z=-1) * bd.extrude(bd.fillet(bd.Rectangle(18.5, 18.5).vertices(), 2), 3) - bd.Pos(Z=-1.5) * bd.fillet(bd.Box(16, 16, 3).edges().filter_by(bd.Axis.Z), 0.75)
    head = bd.chamfer(head.edges().group_by(bd.Axis.Z)[-1], 1.2)
    if homing:
        head_norm = head - bd.Pos(Z=40.45) * bd.Sphere(40)
        return head_norm + stem
    else:
        head_home = head - (bd.Pos(Z=40.45) * bd.Sphere(40) - bd.Pos(Y=-9) * bd.Box(20, 2, 20))
        return head_home + stem

def sandbar():
    bar = bd.Pos(Z=-3) * bd.Box(14, 7, 6) + bd.Pos(Z=-31) * bd.Cylinder(10, 50)
    foot_sketch = bd.chamfer(bd.Box(1.19, 2.995, 3.9).edges().group_by(bd.Axis.Z)[-1], 0.4).clean()
    foot_height = key['h'] + foot['z'] / 2
    feet = bd.Pos(X=-2.85, Z=foot_height) * foot_sketch + bd.Pos(X=2.85, Z=foot_height) * foot_sketch
    bar -= bd.mirror(bd.Pos(Z=-2.9) * bd.offset(feet.clean(), 0.2), bd.Plane.XY)
    return bar.clean()

# %%
if __name__ == "__main__":
    _ = bd.export_stl(keycap(), 'output/keycap.stl')
    _ = bd.export_stl(keycap(homing=True), 'output/keycap_homing.stl')
    _ = bd.export_stl(sandbar(), 'output/sand_bar.stl')
# %%
