from lib import *
from planets import *
import timeline as TL

SHOTS = {'intro': 4.0}


def build_intro():
    reset(20)
    world_space((0.015, 0.012, 0.02), 1.0)
    sd = (-1.0, -0.6, 0.45)
    sun(4.0, sd, (1, 0.97, 0.94))
    a = planet_slow(1.0, (-1.6, 0, 0)); atmosphere(1.0, (1.0, 0.7, 0.4), sd, 1.02, power=5, strength=0.4, loc=(-1.6, 0, 0))
    b = planet_fast(1.0, (1.6, 0, 0)); atmosphere(1.0, (0.45, 0.65, 1.0), sd, 1.03, power=4, strength=0.7, loc=(1.6, 0, 0))
    cb = clouds(1.0, (1.6, 0, 0))
    for p in (a, b, cb):
        p.rotation_euler = (math.radians(15), math.radians(-10), 0)
    cam = camera((0, -7.4, 0), (0, 0, 0), 42)
    def update(t, u):
        b.rotation_euler.z = 2 * math.pi * t / TL.SPIN            # o rápido gira; o lento fica parado
        cb.rotation_euler.z = 2 * math.pi * t / (TL.SPIN * 0.7)
        cam.location = (0, -7.4 + 0.4 * u, 0.03 * math.sin(t))
    return update
