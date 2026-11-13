from lib import *
from planets import *
import timeline as TL

SHOTS = {'intro': 4.0}


def build_intro():
    reset(20)
    world_space((0.015, 0.012, 0.02), 1.0)
    sd = (-1.0, -0.6, 0.45)
    sun(4.0, sd, (1, 0.97, 0.94))
    la, lb = (-1.55, 0, 0), (1.75, 0, 0.05)
    a = planet_heavy(1.15, la); atmosphere(1.15, (0.9, 0.45, 0.25), sd, 1.02, power=5, strength=0.5, loc=la).scale = (1, 1, TL.FLAT)
    ca = heavy_clouds(1.15, la)
    b = planet_light(0.55, lb)
    rocks = orbit_rocks(18, 0.75, 1.05, lb, (0.015, 0.045))
    for p in (a, ca, b):
        p.rotation_euler = (math.radians(12), math.radians(-8), 0)
    cam = camera((0, -7.4, 0), (0.05, 0, 0), 42)
    def update(t, u):
        a.rotation_euler.z = 0.08 * t                                  # o pesado gira devagar
        ca.rotation_euler.z = 0.1 * t
        b.rotation_euler.z = -0.3 * t + 1.0
        move_rocks(rocks, t)
        cam.location = (0, -7.4 + 0.4 * u, 0.03 * math.sin(t))
    return update
