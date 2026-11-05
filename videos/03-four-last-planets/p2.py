from lib import *
from planets import *
from nature import cottage
from timeline import NAME_HOLD

SHOTS = {'p2a': 5.75, 'p2b': 4.0, 'p2c': 3.5, 'p2d': 4.0}
NIGHT = (0.02, 0.03, 0.07)
S = 1.4                       # escala das casas
ROW = 12.0                    # distância da rua até a fileira de casas
HERO_Y = 28.0                 # a casa do jogador, na fileira da esquerda

def night_sky():
    world_space((0.004, 0.006, 0.02), 0.6, 0.5)

def warm_windows():
    for m in bpy.data.materials:
        if m.name.split('.')[0] == 'gl':
            p = m.node_tree.nodes['Principled BSDF']
            p.inputs['Base Color'].default_value = (0.9, 0.55, 0.25, 1)
            p.inputs['Emission Color'].default_value = (1.0, 0.72, 0.36, 1)
            p.inputs['Emission Strength'].default_value = 3.0

def house_proto():
    h = cottage((0, 0, 0), 0.0, 1.0, (0.78, 0.74, 0.66), (0.30, 0.10, 0.08))
    warm_windows()
    kids = list(h.children)
    hide(kids)
    return kids

def lamp(x, y):
    pole = box('pole', (0.12, 0.12, 4.6), (x, y, 2.3), simple('pole', (0.03, 0.03, 0.035), 0.6))
    bulb = ico('bulb', 0.28, (x, y, 4.7), emission('bulb', (1.0, 0.75, 0.40), 22.0), 2)
    return pole, bulb

def street(hero=False, lights=3):
    s = reset(18)
    night_sky()
    sun(0.5, (0.3, 0.4, 0.8), (0.55, 0.65, 1.0), 4.0)
    box('lawn', (6000, 6000, 1), (0, 0, -0.5), simple('lawn', (0.015, 0.035, 0.025), 0.95))
    box('road', (7.0, 6000, 0.04), (0, 0, 0.0), simple('road', (0.02, 0.02, 0.026), 0.55))
    kids = house_proto()
    for i in range(22):
        y = i * 9.0 - 36
        for side in (-1, 1):
            if hero and side == -1 and abs(y - HERO_Y) < 1:
                continue
            clone(kids, (side * ROW, y, 0), math.pi / 2 if side < 0 else -math.pi / 2, S)
    for i in range(10):
        lamp(-4.2 if i % 2 else 4.2, i * 18 - 36)
    return s

def hero_house():
    h = cottage((-ROW, HERO_Y, 0), math.pi / 2, S, (0.78, 0.74, 0.66), (0.30, 0.10, 0.08))
    door = [c for c in h.children if c.name.split('.')[0] == 'd'][0]
    warm_windows()
    return h, door

def mailbox(x, y):
    box('mpost', (0.08, 0.08, 1.0), (x, y, 0.5), simple('mpost', (0.08, 0.06, 0.05), 0.8))
    box('mbox', (0.5, 0.26, 0.28), (x, y, 1.12), simple('mbox', (0.10, 0.10, 0.12), 0.5))
    cu = bpy.data.curves.new('you', 'FONT'); cu.body = 'YOU'; cu.size = 0.17; cu.extrude = 0.004
    cu.align_x = 'CENTER'; cu.align_y = 'CENTER'
    o = bpy.data.objects.new('you', cu); link(o)
    o.data.materials.append(emission('you', (1.0, 0.95, 0.85), 6.0))
    o.rotation_euler = (math.pi / 2, 0, math.pi / 2)
    o.location = (x + 0.27, y, 1.12)

def build_p2a():
    s = reset(20)
    world_space((0.012, 0.012, 0.016), 1.0)
    sd = (-1.0, -0.5, 0.4)
    sun(3.5, sd, (1, 0.9, 0.8))
    p = planet_cul(1.0); atmosphere(1.0, (1.0, 0.65, 0.35), sd, 1.03, power=4, strength=1.0)
    p.rotation_euler = (0.3, -0.2, 0)
    cam = camera((0, -3.6, 0), (0, 0, 0), 40)
    def update(t, u):
        u = zoom_after(t, NAME_HOLD, SHOTS['p2a'])
        p.rotation_euler.z = 0.06 * t
        d = lerp(3.5, 1.32, ease(u))
        cam.location = (0.2 * (1 - u) - 0.25 * u, -d, 0.15 + 0.1 * u)
        look(cam, (-0.25 * u, 0, 0.1 * u))
    return update

def build_p2b():
    street()
    fog(NIGHT, 6, 140, 0.95)
    for y in (6, 24):
        point((0, y, 4.2), 700, (1.0, 0.75, 0.45), 0.4)
    cam = camera((0, -12, 1.6), (0, 30, 1.8), 26)
    def update(t, u):
        y = -12 + 3.4 * t
        cam.location = (0.02 * math.sin(t * 3.4), y, 1.6 + 0.02 * math.sin(t * 6.8))
        look(cam, (0, y + 40, 1.9))
    return update

def build_p2c():
    street(hero=True)
    hero_house(); mailbox(-4.7, HERO_Y)
    fog(NIGHT, 6, 140, 0.95)
    point((-4.3, HERO_Y - 1.5, 4.3), 900, (1.0, 0.75, 0.45), 0.4)
    cam = camera((0, 18, 1.6), (-8, 40, 1.4), 30)
    def update(t, u):
        y = lerp(19.5, 24.5, u)
        cam.location = (0.02 * math.sin(t * 3.4), y, 1.6 + 0.02 * math.sin(t * 6.8))
        look(cam, vlerp((-5, y + 14, 1.5), (-4.7, HERO_Y, 1.15), ease(u * 1.15)))
    return update

def build_p2d():
    street(hero=True)
    h, door = hero_house(); mailbox(-4.7, HERO_Y)
    fog(NIGHT, 6, 140, 0.95)
    s = bpy.context.scene
    door_world = (-ROW + 1.52 * S, HERO_Y)
    # luz da varanda
    porch = ico('porch', 0.18, (door_world[0] + 0.3, door_world[1] + 0.8, 2.7), emission('porch', (1.0, 0.82, 0.5), 0.0), 2)
    pl = point((door_world[0] + 0.7, door_world[1] + 0.8, 2.5), 0, (1.0, 0.8, 0.5), 0.15)
    glow = box('doorway', (0.02, 0.9 * S, 1.7 * S), (door_world[0] - 0.018, door_world[1], 0.85 * S), emission('doorway', (1.0, 0.6, 0.25), 40.0))
    inner = point((door_world[0] - 1.6, door_world[1], 1.4), 0, (1.0, 0.65, 0.3), 0.6)
    fig = figure((door_world[0] + 0.12, door_world[1], 0), math.pi / 2, 1.1, eyes=False)
    fig.scale = (0.0, 0.0, 0.0)
    cam = camera((-5.8, HERO_Y - 1.8, 1.55), (door_world[0], door_world[1], 1.3), 28)
    emit = porch.data.materials[0].node_tree.nodes['Emission']
    ang = 0.0
    def update(t, u):
        on = ease((t - 0.2) / 0.1)
        emit.inputs['Strength'].default_value = 0.4 + 30.0 * on
        pl.data.energy = 600 * on
        op = ease((t - 2.0) / 1.4)
        a = op * 1.25
        door.location = (-0.45 + 0.45 * math.cos(a), -1.52 + 0.45 * math.sin(a), 0.85)
        door.rotation_euler.z = a
        inner.data.energy = 900 * op
        fz = ease((t - 2.8) / 0.2)
        fig.scale = (1.1 * fz, 1.1 * fz, 1.1 * fz)
        cam.location = (-5.8 - 0.1 * t, HERO_Y - 1.8 + 0.05 * t, 1.55 + 0.012 * math.sin(t * 5))
        look(cam, (door_world[0], door_world[1], 1.4))
    return update
