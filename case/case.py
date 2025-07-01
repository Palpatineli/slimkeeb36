# %%
from math import sqrt
import build123d as bd
from util import cut
from keycap import keycap
MIN = bd.Align.MIN

tol = {'l': 0.8, 'm': 0.5, 's': 0.2}
h = {
    'top': 0.8, 'switch_edge': 0.9, 'plate': 2.2, 'pcb': 1.6, 
    'bottom': 2.4 + tol['s'], 'key': 10.7, 'sticker': 0,  # 3.85
}
# change h['key'] to 7.6 if you only need flat keycaps

keymap = ((50, 50), (50, 69.05), (50, 88.1), (69.05, 47), (69.05, 66.05), (69.05, 85.1), (88.1, 41), (88.1, 60.05), (88.1, 79.1), (107.15, 47), (107.15, 66.05), (107.15, 85.1), (126.2, 59), (126.2, 78.05), (126.2, 97.1), (30, 126.7), (46.5, 110.2), (69.05, 104.15))
keymap_dir = (180, 180, 180, 0, 0, 0, 0, 0, 180, 0, 0, 180, 90, 90, 90, 300, 150, 180)
keymap_dir_l = (0, 0, 0, 0, 0, 0, 0, 0, 180, 0, 0, 180, 90, 90, 90, 300, 150, 180)
pcb_outline = bd.Polyline(((26.5, 136.7), (30.5, 129.9), (30.5, 42.5), (110.5, 42.5), (116.7, 48.7), (126, 48.7), (126, 107.35), (113.5, 107.35), (113.5, 110.5), (57.7, 110.5), (43.9, 118), (31.5, 139.6), (26.5, 136.7)))
wall_thickness = 1.5
wire = bd.Pos(30.6, 97.3) * bd.Rectangle(8.6, 2, align=MIN)
reset = bd.Pos(102, 108.75) * bd.Circle(1)
reset_left = bd.Pos(90, 108.75) * bd.Circle(1)
key = keycap()
keys = bd.Part() + [bd.Pos(x, y, 5.8 + h['plate'] + h['pcb']) * bd.Rot(Z=dir) * key for dir, (x, y) in zip(keymap_dir, keymap)]  # pyright: ignore[reportOperatorIssue, reportCallIssue]
keys_l = bd.mirror(bd.Part() + [bd.Pos(x, y, 5.8 + h['plate'] + h['pcb']) * bd.Rot(Z=dir) * key for dir, (x, y) in zip(keymap_dir_l, keymap)], bd.Plane.XZ)  # pyright: ignore[reportOperatorIssue, reportCallIssue]
# %% mcu
mcu = bd.Pos(0, -4.5 / 2, -2.2 / 2) * bd.Wedge(14, 2.2, 21, -3, 0, 17, 25.5, rotation=(-90, 180, 180))
mcu += bd.Pos(Y=1.7, Z=1.1) * bd.Box(14, 17.6, 2.2)
usb_profile = bd.Plane.XZ * (bd.SlotOverall(8.95, 3.2) + bd.Pos(Y=-0.8) * bd.Rectangle(8.95, 1.6))
usb = bd.Pos(0, 14.5 ,1.6) * bd.extrude(usb_profile, 12) 
mcu_neg = bd.offset(mcu, 0.2) + bd.offset(usb, 0.3)
mcu_neg = bd.Pos(96, 100, 0) * mcu_neg
mcu_neg_left = mcu_neg + bd.Pos(Z=h['pcb']) * bd.extrude(reset_left, 20)
mcu_neg += bd.Pos(Z=h['pcb']) * bd.extrude(reset, 20)
# %%
outline = bd.offset(bd.make_face(pcb_outline), 0.25) + bd.offset([bd.Pos(x, y) * bd.Rot(Z=r) * bd.Rectangle(19.05, 19.05) for r, (x, y) in zip(keymap_dir, keymap)], -wall_thickness)
outline += bd.Pos(27.5, 38.975) * bd.Rectangle(77.5, 70, align=MIN)
outline += bd.Pos(112.1, 44.5) * bd.Rectangle(22.125, 63.1, align=MIN)
thumb_1st = (30, 126.7)
thumb_1st_up = (30 - sqrt(3) / 2 * 8.05, 126.7 - 8.05 / 2)
thumb_1st_down = (30 + sqrt(3) / 2 * 9.55, 126.7 + 9.55 / 2)
extend = 10.75
pt_1 = (thumb_1st[0] - sqrt(3) / 2 * 8.05 - extend / 2, thumb_1st[1] - 8.05 / 2 + extend * sqrt(3) / 2)
pt_2 = (thumb_1st[0] + sqrt(3) / 2 * 9.55 - extend / 2, thumb_1st[1] + 9.55 / 2 + extend * sqrt(3) / 2)
r_up = (27.5 - thumb_1st_up[0]) / (1 - sqrt(3) / 2)
r_down = (thumb_1st_down[1] - 112.175) * 2
outline += bd.make_face(bd.RadiusArc(thumb_1st_up, (27.5, thumb_1st_up[1] - r_up / 2), r_up)
                        + bd.Polyline(((27.5, thumb_1st_up[1] - r_up / 2),
                                       (thumb_1st_down[0] + r_down * sqrt(3) / 2, thumb_1st_up[1] - r_up / 2),
                                       (thumb_1st_down[0] + r_down * sqrt(3) / 2, 110)))
                        + bd.RadiusArc((thumb_1st_down[0] + r_down * sqrt(3) / 2, 110), thumb_1st_down, r_down)
                        + bd.Polyline(thumb_1st_down, pt_2, pt_1, thumb_1st_up))

outerline = bd.offset(outline, wall_thickness)
edge_l, edge_u, _ = outerline.bounding_box().min
edge_r, edge_b, _ = outerline.bounding_box().max
# %% battery
battery_shell = bd.Plane.XZ * (bd.Rectangle(7.3, 6.55 * sqrt(2) + 0.25, align=MIN) + bd.Pos(X=7.3, Y=0.25) * (bd.Circle(6.55) + bd.Rot(Z=45) * bd.Rectangle(6.55, 6.55, align=MIN)))
battery_shell = bd.Pos(26, 37.475, -h['bottom'] + 6.25) * bd.extrude(battery_shell, - 63)
battery_profile = bd.Plane.XZ * (bd.Pos(5.8, 5.8) * (bd.Circle(5.8) + bd.Rot(Z=45) * bd.Rectangle(5.8, 5.8, align=MIN)))
battery = bd.Pos(27.5, 39, -h['bottom'] + 0.4) * bd.extrude(battery_profile, -59)
# %% top
switch_profile = [bd.Pos(x, y) * bd.Rot(Z=r) * bd.Rectangle(14, 14) for (x, y), r in zip(keymap, keymap_dir)]  # type: ignore
top = bd.Pos(Z=h['pcb']) * bd.extrude(outerline - switch_profile,  h['plate'])
# top += bd.Pos(Z=h['pcb']) * mcu_pos - bd.Pos(Z=h['pcb']) * bd.extrude(switch_profile,  h['plate'])
top += battery_shell
top += bd.extrude(outerline - outline, h['pcb'])
top -= bd.Pos(Z=h['pcb']) * bd.extrude(bd.Sketch() + [bd.Pos(x, y) * bd.Rot(Z=r) * (bd.Rectangle(14.8, 7.2) + bd.Rectangle(7.2, 14.8)) for (x, y), r in zip(keymap, keymap_dir)], 0.6)
top -= battery + bd.extrude(outline, h['pcb']) + bd.extrude(outerline, -20)
top = cut(top, bd.extrude(outerline, 20), 0)[0]
# %% bottom
def get_hotswap():
    hotswap = bd.Polyline([(0, -3.4), (-4.8, -3.4), (-4.8, 1.2), (-2.5, 1.2), (0, 3.4)])
    hotswap += bd.mirror(bd.mirror(hotswap, bd.Plane.XZ), bd.Plane.YZ)
    hotswap = bd.offset(bd.make_face(bd.Plane.XY * hotswap), tol['m'] + 0.2)  # type: ignore
    hotswap = bd.extrude(hotswap, -2 - tol['s']).clean()  # type: ignore
    hotswap += bd.Location([-6.1, -1.1, -1.0 - tol['s'] / 2]) * bd.Box(2.8, 2.8, 2 + tol['s']) + bd.Location([6.1, 1.1, -1.0 - tol['s'] / 2]) * bd.Box(2.8, 2.8, 2 + tol['s'])
    hotswap = bd.Location([2.5, -4.9, 0]) * hotswap
    hotswap_height = 3 - h['pcb'] + tol['m']
    hotswap += bd.Location([0, 0, -hotswap_height / 2]) * bd.Cylinder(2.5 + tol['s'], hotswap_height)
    return bd.mirror(hotswap, bd.Plane.YZ)

hotswap = bd.mirror(get_hotswap(), bd.Plane.XZ)
hotswaps = [bd.Pos(*loc) * bd.Rot(Z=dir) * hotswap for loc, dir in zip(keymap, keymap_dir)]
hotswaps_left = [bd.Pos(*loc) * bd.Rot(Z=dir) * bd.mirror(hotswap, bd.Plane.YZ) for loc, dir in zip(keymap, keymap_dir_l)]
bottom = bd.extrude(outerline, -h['bottom'])
bottom += bd.extrude(bd.offset(outline, -0.2) - bd.offset(bd.make_face(pcb_outline), 0.5), h['pcb'] - 0.2)
bottom -= bd.extrude(wire, -2)  # type: ignore
bottom -= battery
# %% hook
def make_hook(height, length):
    thickness, hook_size, hook_h, hook_tol = 1.5, 0.6, 0.1, 0.15
    hook_sketch = bd.Polyline((0, 0), (0, height), (thickness, height), (thickness + hook_size, height + hook_size),
                              (thickness + hook_size, height + hook_size + hook_h),
                              (thickness, height + hook_size * 2 + hook_h), (thickness, 0), (0, 0))
    hook_sketch_neg = bd.Polyline((0, 0), (0, height), (thickness + hook_size + hook_tol, height),
                                  (thickness + hook_size + hook_tol, height + hook_size - hook_h),
                                  (thickness + hook_tol, height + hook_size * 2 - hook_h),
                                  (thickness + hook_tol, 0), (0, 0))
    hook = bd.Pos(Y=length / 2) * bd.extrude(bd.make_face(bd.Plane.XZ * hook_sketch), length)  # type: ignore
    hook_neg = bd.Pos(Y=length / 2 + 0.3) * bd.extrude(bd.make_face(bd.Plane.XZ * hook_sketch_neg), length + 0.6)  # type: ignore
    return hook, hook_neg

hooks_pos, hooks_neg = [], []

locs = (((26, 50), 0), ((26, 72.5), 0), ((26, 95), 0), ((70, 37.475), 90), ((106, 37.475), 90),
        ((edge_r, 59.5), 180), ((edge_r, 95.25), 180), ((69, 113.7), 270), ((123, 109.1), 270),
        (((pt_1[0] + pt_2[0]) / 2 - 1.5 / 2, (pt_1[1] + pt_2[1]) / 2 + 1.5 * sqrt(3) / 2), 300))

hook, hook_neg = make_hook(-h['bottom'], 15)
for (x, y), r in locs:
    hooks_pos.append(bd.Pos(x, y) * bd.Rot(Z=r) * hook)
    hooks_neg.append(bd.Pos(x, y) * bd.Rot(Z=r) * hook_neg)
# %% shroud
shroud_base = outerline - outline
shroud_inner = bd.offset(outline, 0.6) - outline
shroud_outer = outerline - bd.offset(outline, 0.9)
shroud_boxes = bd.Pos(26, 37.475) * bd.Rectangle(7.3, 63, align=MIN)
shroud_boxes += bd.Pos(119, 43) * bd.Rectangle(17, 3, align=MIN)
shroud_round = bd.Pos(119, 46) * (bd.Box(17, 3, 3, align=MIN) - bd.Pos(8.5, 3, 3) * bd.Rot(Y=90) * bd.Cylinder(3, 17))
shroud_boxes += bd.Pos(95, 108.5) * bd.Rectangle(20.25, 6, align=MIN)
shroud_round += bd.Pos(95, 105.5) * (bd.Box(20.25, 3, 3, align=MIN) - bd.Pos(15.125, 0, 3) * bd.Rot(Y=90) * bd.Cylinder(3, 30.25))
vacuum = (bd.extrude(outerline, h['key'] + h['top'] + h['switch_edge']) - (bd.extrude(shroud_boxes, h['key'] + h['top'] + h['switch_edge'])))
saw_tooth = bd.extrude(bd.Pos(25, 70) * bd.Rectangle(10, 23), h['key'] + h['top'] + h['switch_edge'] + wall_thickness)
shroud = bd.extrude(shroud_base, h['key'] + h['top'] + h['switch_edge'] - wall_thickness / 4) - (vacuum - shroud_round)
shroud_left = bd.Pos(Z=h['key'] + h['top'] + h['switch_edge'] - wall_thickness / 4) * (bd.extrude(shroud_outer, wall_thickness / 2) - vacuum)
shroud_left, bit_left = cut(shroud_left, saw_tooth)
shroud_right = bd.Pos(Z=h['key'] + h['top'] + h['switch_edge'] - wall_thickness / 4) * (bd.extrude(shroud_inner, wall_thickness / 2) - vacuum)
shroud_right, bit_right = cut(shroud_right, saw_tooth)
shroud_left += bit_right
shroud_right += bit_left
shroud_left = bd.Pos(Z=h['pcb'] + h['plate']) * (shroud + shroud_left)
shroud_right = bd.Pos(Z=h['pcb'] + h['plate']) * (shroud + shroud_right)
# %%
top_left_ass = top - mcu_neg_left + hooks_pos + shroud_left
top_ass = top - mcu_neg + hooks_pos + shroud_right
bottom_ass = bottom - mcu_neg - hooks_neg
bd.export_stl(bd.mirror(top_ass, bd.Plane.XZ), 'output/top.stl')
bd.export_stl(bd.mirror(bd.mirror(top_left_ass, bd.Plane.XZ), bd.Plane.YZ), 'output/left-top.stl')
bd.export_stl(bd.mirror(keys, bd.Plane.XZ), 'output/keys.stl')
bd.export_stl(bd.mirror(keys_l, bd.Plane.YZ), 'output/left-keys.stl')
bd.export_stl(bd.mirror(bottom_ass - hotswaps - bd.Pos(Z=h['pcb'] - 0.2) * (bd.Part() + hotswaps), bd.Plane.XZ), 'output/bottom.stl')
bd.export_stl(bd.mirror(bd.mirror(bottom_ass - hotswaps_left - bd.Pos(Z=h['pcb'] - 0.2) * (bd.Part() + hotswaps_left), bd.Plane.XZ), bd.Plane.YZ), 'output/left-bottom.stl')
# bd.export_step(bd.mirror(top_ass, bd.Plane.XZ), 'output/top.step')
# bd.export_step(bd.mirror(bd.mirror(top_left_ass, bd.Plane.XZ), bd.Plane.YZ), 'output/left-top.step')
# bd.export_step(bd.mirror(keys, bd.Plane.XZ), 'output/keys.step')
# bd.export_step(bd.mirror(keys_l, bd.Plane.YZ), 'output/left-keys.step')
# bd.export_step(bd.mirror(bottom_ass - hotswaps - bd.Pos(Z=h['pcb'] - 0.2) * (bd.Part() + hotswaps), bd.Plane.XZ), 'output/bottom.step')
# bd.export_step(bd.mirror(bd.mirror(bottom_ass - hotswaps_left - bd.Pos(Z=h['pcb'] - 0.2) * (bd.Part() + hotswaps_left), bd.Plane.XZ), bd.Plane.YZ), 'output/left-bottom.step')
# %%
