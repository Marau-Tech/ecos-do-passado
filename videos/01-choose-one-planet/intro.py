from lib import *
from planets import *

SHOTS = {'intro': 5.0}
def build_intro():
    s = reset(20)
    world_space((0.018, 0.012, 0.035), 1.0)
    sd = (-1.0, -0.55, 0.5)
    sun(4.0, sd, (1, 0.97, 0.92))
    R = 1.0
    # disposição 2x2 desencontrada
    P = [(-1.95, 0.3, 1.16), (1.72, -0.2, 1.26), (-1.72, -0.2, -1.2), (1.98, 0.3, -1.1)]
    p1 = planet_maze(R, P[0]); atmosphere(R, (1.0, 0.75, 0.3), sd, 1.025, power=5, strength=0.8, loc=P[0])
    p2, c2 = planet_green(R, P[1]); atmosphere(R, (0.35, 0.65, 1.0), sd, 1.04, loc=P[1])
    p3 = planet_night(R, P[2]); atmosphere(R, (0.35, 0.12, 0.3), sd, 1.025, power=5, strength=0.5, loc=P[2])
    p4 = planet_flesh(R, P[3]); atmosphere(R, (1.0, 0.2, 0.15), sd, 1.09, power=5, strength=0.7, loc=P[3])
    for p in (p1, p2, p3, p4):
        p.rotation_euler = (math.radians(18), math.radians(-12), 0)
    c2.rotation_euler = p2.rotation_euler
    cam = camera((0, -10.2, 0), (0, 0, 0), 42)
    def update(t, u):
        p1.rotation_euler.z = 0.20 * t + 1.0
        p2.rotation_euler.z = 0.26 * t + 2.0
        c2.rotation_euler.z = 0.31 * t + 2.0
        p3.rotation_euler.z = -0.16 * t
        p4.rotation_euler.z = 0.22 * t
        sc = 1 + 0.018 * math.sin(t * 2.4)
        p4.scale = (sc, sc, sc)
        cam.location = (0, -10.2 + 0.55 * u, 0.04 * math.sin(t))
    return update
