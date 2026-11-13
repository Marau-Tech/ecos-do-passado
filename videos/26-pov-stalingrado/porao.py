"""O porão: a descida pela escada no escuro (t3) e os soldados sentados contra a parede à luz de uma vela (t4)."""
from lib import *
from places import *
import timeline as TL

SHOTS = {'t3': 7.0, 't4': 8.0}
FLOOR = -2.6
ROOM = (-3.0, 3.0, 3.6, 10.0)          # x0, x1, y0, y1


def cellar(lamp=0.0):
    """escada de 8 degraus descendo em +y e uma sala de tijolo; lamp > 0 acende a vela em cima do caixote"""
    world_flat((0, 0, 0), 0.0)
    wall = brick_mat(1)
    floor = noisy('dirt', (0.05, 0.045, 0.04), (0.14, 0.12, 0.1), 3.0)
    for i in range(8):  # degraus
        box('step', (1.4, 0.45, 0.33), (0, 0.1 + i * 0.45, -0.165 - i * 0.325), wall)
    box('stairL', (0.2, 4.2, 3.2), (-0.8, 1.7, -1.0), wall)
    box('stairR', (0.2, 4.2, 3.2), (0.8, 1.7, -1.0), wall)
    street_floor = snow_mat()            # calçada lá em cima, em volta da abertura da escada
    box('landing', (8, 6, 0.2), (0, -3.0, -0.1), street_floor)
    box('sideL', (3.4, 4.0, 0.2), (-2.6, 1.8, -0.1), street_floor)
    box('sideR', (3.4, 4.0, 0.2), (2.6, 1.8, -0.1), street_floor)
    x0, x1, y0, y1 = ROOM
    box('floor', (x1 - x0, y1 - y0, 0.1), ((x0 + x1) / 2, (y0 + y1) / 2, FLOOR - 0.05), floor)
    box('ceil', (x1 - x0, y1 - y0, 0.2), ((x0 + x1) / 2, (y0 + y1) / 2, 0.1), wall)
    box('back', (x1 - x0, 0.2, 2.8), ((x0 + x1) / 2, y1, FLOOR + 1.4), wall)
    box('left', (0.2, y1 - y0, 2.8), (x0, (y0 + y1) / 2, FLOOR + 1.4), wall)
    box('right', (0.2, y1 - y0, 2.8), (x1, (y0 + y1) / 2, FLOOR + 1.4), wall)
    box('front_l', (2.2, 0.2, 2.8), (x0 + 1.1, y0, FLOOR + 1.4), wall)
    box('front_r', (2.2, 0.2, 2.8), (x1 - 1.1, y0, FLOOR + 1.4), wall)
    wood = noisy('crate', (0.12, 0.08, 0.05), (0.24, 0.16, 0.1), 5.0)
    box('crate', (0.7, 0.6, 0.6), (0.3, 8.6, FLOOR), wood)
    box('crate2', (0.6, 0.6, 0.5), (1.1, 9.2, FLOOR), wood)
    rubble(40, (x0 + 0.3, x1 - 0.3), (y0 + 0.5, y1 - 0.3), 21, (0.08, 0.3))
    # luz fria e fraca que entra pela porta lá em cima, atrás de quem desce
    l = bpy.data.lights.new('door', 'AREA'); l.energy = 140; l.size = 1.2; l.color = (0.75, 0.82, 0.95)
    door = bpy.data.objects.new('door', l); link(door); door.location = (0, -0.8, 1.2)
    look(door, (0, 3.5, FLOOR))
    if lamp:
        box('candle', (0.05, 0.05, 0.12), (0.3, 8.6, FLOOR + 0.66), emission('flame', (1.0, 0.6, 0.25), 25.0))
        return point((0.3, 8.6, FLOOR + 0.8), lamp, (1.0, 0.58, 0.28), 0.04)
    return None


def build_t3():
    """Descendo a escada: a luz da porta fica para trás e a sala lá embaixo é quase toda escura."""
    reset(32)
    cellar()
    for i, (x, y, yaw) in enumerate([(-2.4, 7.5, -math.pi / 2), (2.4, 8.2, math.pi / 2)]):
        seated((x, y, FLOOR), yaw, seed=i + 1)
    cam = camera((0, -0.4, EYE), (0, 4, FLOOR + 1), 24)

    def update(t, u):
        e = ease(min(1.0, t / 5.5))
        y = lerp(-0.4, 4.4, e)
        z = lerp(EYE, FLOOR + EYE, e)
        step = math.sin(math.pi * 2.0 * t)
        cam.location = (0.04 * step, y, z + 0.03 * abs(step))
        j = shake(t, 0.03, 1.4, 6.0)
        look(cam, Vector((0, y + 6, z + lerp(-4.5, -1.0, e))) + j * 6, roll=0.015 * step)
        return None
    return update


def build_t4():
    """Parado no meio do porão, a câmera passa devagar pelos homens sentados contra as paredes, à luz de uma vela."""
    reset(32)
    flame = cellar(lamp=45.0)
    spots = [(-2.45, 5.0, -math.pi / 2), (-2.45, 6.4, -math.pi / 2), (-2.45, 8.0, -math.pi / 2),
             (2.45, 5.6, math.pi / 2), (2.45, 7.2, math.pi / 2), (1.6, 9.5, math.pi)]
    for i, (x, y, yaw) in enumerate(spots):
        seated((x, y, FLOOR), yaw, seed=i + 3)
    cam = camera((0, 4.2, FLOOR + 1.55), (-3, 6, FLOOR + 0.6), 24)

    def update(t, u):
        a = lerp(math.radians(-62), math.radians(58), ease(t / SHOTS['t4']))
        p = Vector((0, 4.2, FLOOR + 1.55 + 0.01 * math.sin(2 * math.pi * 0.25 * t)))
        cam.location = p
        j = shake(t, 0.02, 1.2, 8.0)
        look(cam, p + Vector((math.sin(a) * 4, math.cos(a) * 4, -0.9)) + j * 4)
        flame.data.energy = 45.0 * (0.85 + 0.15 * noise.noise(Vector((t * 6.0, 0.5, 0.5))))
        return None
    return update
