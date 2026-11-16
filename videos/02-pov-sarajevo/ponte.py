"""Regiao da Ponte Latina e desfecho do atentado de Sarajevo."""
from lib import *
from places import *
import timeline as TL

SHOTS = {'t9': 15.0, 't10': 15.0, 't11': 15.0}


def bridge_scene():
    reset(24)
    summer_light()

    water = simple('miljacka_water', (0.12, 0.22, 0.25), 0.28, 0.15)
    stone = simple('bridge_stone', (0.42, 0.37, 0.29), 0.9)
    rail = simple('bridge_rail', (0.30, 0.27, 0.22), 0.8)
    road = simple('bridge_road', (0.25, 0.23, 0.20), 0.95)

    box('river', (45, 70, 0.25), (0, 35, -1.0), water)
    box('bridge_deck', (12, 28, 0.65), (0, 35, 0.0), road)

    for x in (-5.7, 5.7):
        box('bridge_parapet', (0.45, 28, 1.35), (x, 35, 0.85), stone)
        box('bridge_rail_top', (0.65, 28, 0.18), (x, 35, 1.6), rail)

    for y in (25, 31, 37, 43, 49):
        for x in (-5.7, 5.7):
            box('bridge_post', (0.55, 0.45, 0.55), (x, y, 1.85), rail)

    cam = camera((0.0, 5.0, EYE), (0.0, 25.0, 1.5), 35)
    return cam


def add_car():
    body = simple('final_car', (0.12, 0.09, 0.055), 0.5)
    metal = simple('final_metal', (0.22, 0.20, 0.16), 0.4, 0.5)
    box('final_car_body', (1.8, 3.0, 1.0), (0.0, 31.0, 1.15), body)
    box('final_car_hood', (1.7, 1.0, 0.55), (0.0, 33.0, 1.4), body)
    box('final_car_screen', (1.3, 0.08, 0.55), (0.0, 30.2, 1.9), metal)
    for x in (-0.95, 0.95):
        for y in (29.9, 32.5):
            w = sphere('final_wheel', 0.36, (x, y, 0.55),
                       simple('final_tire', (0.02, 0.02, 0.02), 0.9), 24, 12)
            w.scale = (0.35, 1.0, 1.0)


def build_t9():
    cam = bridge_scene()
    add_car()
    def update(t, u):
        walk_pov(cam, t, (0.0, 5.0, EYE), speed=0.22, pitch=-2.0, seed=15.0)
        return None
    return update


def build_t10():
    cam = bridge_scene()
    add_car()
    princip = figure((-3.2, 30.0, 0), yaw=math.pi / 2, s=1.0,
                     color=(0.018, 0.014, 0.012))
    def update(t, u):
        walk_pov(cam, t, (0.0, 8.0, EYE), speed=0.0, pitch=-1.5, seed=16.0)
        return None
    return update


def build_t11():
    cam = bridge_scene()
    add_car()
    for x, y in [(-3.0, 27.0), (3.0, 29.0), (-4.0, 34.0), (4.0, 35.0)]:
        figure((x, y, 0), yaw=math.pi, s=0.95,
               color=(0.035, 0.025, 0.02))
    flash_mat = emission('gun_flash', (1.0, 0.72, 0.25), 8.0)
    flash = sphere('shot_flash', 0.12, (-3.0, 30.0, 1.7), flash_mat, 16, 8)
    def update(t, u):
        walk_pov(cam, t, (0.0, 10.0, EYE), speed=0.0, pitch=-2.5, seed=17.0)
        flash.hide_render = int(t * 4) % 2 == 0
        return None
    return update
