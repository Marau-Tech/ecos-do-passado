from lib import *
from planets import *

SHOTS = {'intro': 4.0}


def build_intro():
    reset(20)
    world_space((0.015, 0.012, 0.02), 1.0)
    sd = (-1.0, -0.6, 0.45)
    sun(4.0, sd, (1, 0.97, 0.94))
    a = planet_quiet(1.0, (-1.6, 0, 0)); atmosphere(1.0, (0.8, 0.8, 0.82), sd, 1.015, power=6, strength=0.3, loc=(-1.6, 0, 0))
    b = planet_kind(1.0, (1.6, 0, 0)); atmosphere(1.0, (1.0, 0.7, 0.8), sd, 1.03, power=4, strength=0.6, loc=(1.6, 0, 0))
    for p in (a, b):
        p.rotation_euler = (math.radians(15), math.radians(-10), 0)
    cam = camera((0, -7.4, 0), (0, 0, 0), 42)
    def update(t, u):
        a.rotation_euler.z = 0.15 * t
        b.rotation_euler.z = -0.2 * t + 1.0
        cam.location = (0, -7.4 + 0.4 * u, 0.03 * math.sin(t))
    return update
