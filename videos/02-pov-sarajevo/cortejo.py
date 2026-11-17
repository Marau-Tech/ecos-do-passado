"""Cortejo automobilistico de Sarajevo, junho de 1914."""
from lib import *
from places import *
import timeline as TL

SHOTS = {'t2': 15.0, 't3': 15.0, 't4': 15.0, 't5': 15.0}


def automobile(y, x=0.0, color=(0.12, 0.10, 0.075)):
    body = simple('car_body', color, 0.48)
    dark = simple('car_tire', (0.025, 0.023, 0.020), 0.95)
    metal = simple('car_metal', (0.24, 0.22, 0.17), 0.32, 0.65)
    brass = simple('car_brass', (0.55, 0.38, 0.13), 0.3, 0.65)
    leather = simple('car_leather', (0.12, 0.055, 0.025), 0.85)
    glass = simple('car_glass', (0.12, 0.17, 0.18), 0.2)

    box('car_chassis', (1.65, 3.5, 0.22), (x, y, 0.72), metal)
    box('car_body_lower', (1.8, 2.5, 0.55), (x, y - 0.15, 1.05), body)
    box('car_hood', (1.55, 1.15, 0.55), (x, y + 1.15, 1.20), body)
    box('car_radiator', (0.75, 0.10, 0.52), (x, y + 1.76, 1.20), metal)
    box('car_dashboard', (1.45, 0.12, 0.55), (x, y + 0.15, 1.43), body)

    for sx in (-0.43, 0.43):
        box('car_seat', (0.62, 0.55, 0.18), (x + sx, y - 0.85, 1.25), leather)
        box('car_seat_back', (0.62, 0.16, 0.62), (x + sx, y - 1.05, 1.55), leather)

    for wx in (-0.98, 0.98):
        for wy in (-1.15, 1.15):
            wheel = sphere('car_wheel', 0.38, (x + wx, y + wy, 0.48), dark, 32, 16)
            wheel.scale = (0.32, 1.0, 1.0)
            hub = sphere('car_hub', 0.12, (x + wx * 1.02, y + wy, 0.48), brass, 24, 12)
            hub.scale = (0.5, 1.0, 1.0)

    for hx in (-0.58, 0.58):
        box('headlamp_support', (0.09, 0.20, 0.12), (x + hx, y + 1.65, 1.48), metal)
        sphere('headlamp', 0.17, (x + hx, y + 1.76, 1.55), brass, 24, 12)

    box('windscreen_glass', (1.25, 0.045, 0.48), (x, y + 0.35, 1.88), glass)
    for sx in (-0.65, 0.65):
        box('windscreen_frame', (0.055, 0.08, 0.55), (x + sx, y + 0.35, 1.88), metal)


def crowd_line(y, count=12, x=6.0):
    for i in range(count):
        yy = y + i * 2.1
        for side in (-1, 1):
            figure((side * x, yy, 0), yaw=math.pi if side < 0 else 0,
                   s=0.85, color=(0.045, 0.035, 0.027))


def base_cortejo():
    reset(24)
    summer_light()
    city_street(125, width=12, seed=3)
    crowd_line(12, 16)
    automobile(30, 0.0, (0.12, 0.10, 0.075))
    automobile(38, 0.0, (0.16, 0.13, 0.09))
    automobile(46, 0.0, (0.10, 0.09, 0.075))
    cam = camera((0.0, 8.0, EYE), (0.0, 25.0, 1.5), 35)
    return cam


def build_t2():
    cam = base_cortejo()
    me = pov_body(cam)
    def update(t, u):
        walk_pov(cam, t, (0.0, 8.0, EYE), speed=0.18, pitch=-2.0, seed=8.0)
        pov_pose(me, cam, t, speed=0.18)
        return None
    return update


def build_t3():
    cam = base_cortejo()
    me = pov_body(cam)
    def update(t, u):
        walk_pov(cam, t, (0.0, 10.0, EYE), speed=0.32, pitch=-2.0, seed=9.0)
        pov_pose(me, cam, t, speed=0.32)
        return None
    return update


def build_t4():
    cam = base_cortejo()
    thrower = figure((-5.0, 30.0, 0), yaw=math.pi / 2, s=1.0,
                     color=(0.025, 0.018, 0.014))
    bomb_mat = simple('bomb_dark', (0.025, 0.022, 0.018), 0.8)
    bomb = sphere('bomb', 0.13, (-4.5, 29.0, 1.5), bomb_mat, 16, 8)
    flash_mat = emission('explosion_flash', (1.0, 0.42, 0.08), 0.0)
    flash = sphere('explosion', 0.8, (0.0, 39.0, 1.2), flash_mat, 24, 12)
    flash.hide_render = True
    me = pov_body(cam)
    def update(t, u):
        walk_pov(cam, t, (0.0, 10.0, EYE), speed=0.15, pitch=-1.5, seed=10.0)
        # a explosão (2,5 s) faz erguer os braços diante do rosto
        pov_pose(me, cam, t, speed=0.15, actions=[('shield', 2.55, 5.2, 0.35)])
        bomb.location = (-4.5 + 4.5 * min(1.0, t / 2.8),
                         29.0 + 8.0 * min(1.0, t / 2.8),
                         1.5 + 2.2 * min(1.0, t / 2.8))
        if t > 2.5:
            flash.hide_render = False
            flash.scale = (1.0 + 1.4 * min(1.0, t - 2.5),) * 3
        return None
    return update


def build_t5():
    cam = base_cortejo()
    for i in range(7):
        figure((-4.8 + i * 1.6, 35.0 + (i % 2) * 2.0, 0),
               yaw=math.pi, s=0.9, color=(0.035, 0.025, 0.02))
    smoke_mat = simple('smoke', (0.16, 0.15, 0.13), 1.0)
    smoke = sphere('smoke_cloud', 1.0, (0.0, 39.0, 2.0), smoke_mat, 24, 16)
    me = pov_body(cam)
    def update(t, u):
        walk_pov(cam, t, (0.0, 12.0, EYE), speed=0.08, pitch=-3.0, seed=11.0)
        pov_pose(me, cam, t, speed=0.08)
        smoke.scale = (1.0 + t * 0.12, 1.0 + t * 0.12, 0.7 + t * 0.09)
        return None
    return update
