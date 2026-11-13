from lib import *
from planets import *

SHOTS = {'intro': 4.0}


def build_intro():
    reset(20)
    world_space((0.015, 0.012, 0.02), 1.0)
    sd = (-1.0, -0.6, 0.45)
    sun(4.0, sd, (1, 0.97, 0.94))
    a = planet_dark(1.0, (-1.6, 0, 0))
    atmosphere(1.0, (0.55, 0.62, 0.8), (0.9, 0.3, 0.2), 1.012, power=7, strength=1.4, loc=(-1.6, 0, 0))  # anel fino de raspão
    b = planet_bright(1.0, (1.6, 0, 0))
    atmosphere(1.0, (1.0, 0.95, 0.8), sd, 1.06, power=2.5, strength=1.2, loc=(1.6, 0, 0))
    for p in (a, b):
        p.rotation_euler = (math.radians(15), math.radians(-10), 0)
    cam = camera((0, -7.4, 0), (0, 0, 0), 42)
    def update(t, u):
        a.rotation_euler.z = 0.12 * t
        b.rotation_euler.z = -0.15 * t + 1.0
        cam.location = (0, -7.4 + 0.4 * u, 0.03 * math.sin(t))
    return update
