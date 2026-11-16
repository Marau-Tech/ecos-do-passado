"""Prefeitura de Sarajevo: chegada, recepcao e partida."""
from lib import *
from places import *
import timeline as TL

SHOTS = {'t6': 15.0, 't7': 15.0, 't8': 15.0}


def town_hall():
    reset(24)
    summer_light()
    city_street(100, width=12, seed=5)

    stone = simple('hall_stone', (0.55, 0.43, 0.30), 0.85)
    trim = simple('hall_trim', (0.72, 0.61, 0.44), 0.8)
    dark = simple('hall_door', (0.10, 0.065, 0.04), 0.8)

    box('hall_front', (18, 1.2, 13), (0, 48, 6.5), stone)
    box('hall_roof', (19, 2.0, 0.7), (0, 48, 13.2), trim)
    box('hall_door', (2.4, 0.18, 4.2), (0, 47.3, 2.1), dark)

    for x in (-5.0, -2.5, 2.5, 5.0):
        box('hall_column', (0.55, 0.7, 7.5), (x, 46.9, 3.75), trim)
        box('hall_capital', (0.9, 0.9, 0.35), (x, 46.9, 7.6), stone)

    for x in (-3.5, 3.5):
        figure((x, 40.0, 0), yaw=math.pi, s=1.0,
               color=(0.035, 0.025, 0.02))

    return camera((0.0, 12.0, EYE), (0.0, 35.0, 3.0), 35)


def build_t6():
    cam = town_hall()
    def update(t, u):
        walk_pov(cam, t, (0.0, 12.0, EYE), speed=0.28, pitch=-2.0, seed=12.0)
        return None
    return update


def build_t7():
    cam = town_hall()
    figures = []
    for x, y in [(-2.0, 39.0), (2.0, 39.0), (-1.0, 43.0), (1.0, 43.0)]:
        figures.append(figure((x, y, 0), yaw=math.pi, s=1.0,
                              color=(0.035, 0.027, 0.02)))
    def update(t, u):
        walk_pov(cam, t, (0.0, 15.0, EYE), speed=0.0, pitch=-1.0, seed=13.0)
        return None
    return update


def build_t8():
    cam = town_hall()
    car = simple('departure_car', (0.12, 0.09, 0.055), 0.5)
    box('departure_body', (1.8, 3.0, 1.0), (0.0, 31.0, 1.1), car)
    box('departure_hood', (1.7, 1.0, 0.6), (0.0, 33.0, 1.3), car)
    for x in (-0.9, 0.9):
        for y in (29.8, 32.2):
            wheel = sphere('departure_wheel', 0.35, (x, y, 0.5),
                           simple('departure_tire', (0.02, 0.02, 0.02), 0.9), 24, 12)
            wheel.scale = (0.35, 1.0, 1.0)
    def update(t, u):
        walk_pov(cam, t, (0.0, 17.0, EYE), speed=0.12, pitch=-2.0, seed=14.0)
        return None
    return update
