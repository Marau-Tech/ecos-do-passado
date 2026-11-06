from lib import *
from planets import *

SHOTS = {'intro': 5.0}
def build_intro():
    reset(20)
    world_space((0.02, 0.012, 0.022), 1.0)
    sd = (-1.0, -0.55, 0.5)
    sun(4.0, sd, (1, 0.97, 0.92))
    P = [(-1.95, 0.3, 1.16), (1.72, -0.2, 1.26), (-1.72, -0.2, -1.2), (1.98, 0.3, -1.1)]
    ps = [planet_terminal(1.0, P[0]), planet_neon(1.0, P[1]), planet_noon(1.0, P[2]), planet_market(1.0, P[3])]
    for loc, c in zip(P, ((0.8, 0.7, 0.6), (0.9, 0.3, 1.0), (1.0, 0.95, 0.8), (0.9, 0.85, 0.6))):
        atmosphere(1.0, c, sd, 1.025, power=5, strength=0.5, loc=loc)
    glow(0.8, (-3.4, 1.5, -2.4), (1.0, 0.95, 0.8), 3.0)        # o sol branco do Noon, ao lado
    for p in ps:
        p.rotation_euler = (math.radians(18), math.radians(-12), 0)
    cam = camera((0, -10.2, 0), (0, 0, 0), 42)
    def update(t, u):
        for k, p in enumerate(ps):
            p.rotation_euler.z = (0.2 - 0.04 * k) * t + k
        cam.location = (0, -10.2 + 0.55 * u, 0.04 * math.sin(t))
    return update
