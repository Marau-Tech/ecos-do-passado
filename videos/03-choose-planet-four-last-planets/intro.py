from lib import *
from planets import *

SHOTS = {'intro': 5.0}
def build_intro():
    s = reset(20)
    world_space((0.018, 0.014, 0.03), 1.0)
    sd = (-1.0, -0.55, 0.5)
    sun(4.0, sd, (1, 0.97, 0.92))
    R = 1.0
    P = [(-1.95, 0.3, 1.16), (1.72, -0.2, 1.26), (-1.72, -0.2, -1.2), (1.98, 0.3, -1.1)]
    p1 = planet_salt(R, P[0]); atmosphere(R, (0.7, 0.85, 1.0), sd, 1.04, power=4, strength=1.0, loc=P[0])
    p2 = planet_cul(R, P[1]); atmosphere(R, (1.0, 0.65, 0.35), sd, 1.03, loc=P[1])
    p3, c3 = planet_white(R, P[2]); atmosphere(R, (0.75, 0.85, 1.0), sd, 1.03, power=4, strength=0.9, loc=P[2])
    p4 = planet_twin(R, P[3]); atmosphere(R, (0.6, 0.3, 0.9), sd, 1.02, power=5, strength=0.6, loc=P[3])
    tilt = (math.radians(18), math.radians(-12), 0)
    for p in (p1, p2, p3, c3, p4):
        p.rotation_euler = tilt
    cam = camera((0, -10.2, 0), (0, 0, 0), 42)
    def update(t, u):
        p1.rotation_euler.z = 0.22 * t + 1.0
        p2.rotation_euler.z = 0.18 * t + 2.0
        p3.rotation_euler.z = -0.16 * t
        c3.rotation_euler.z = -0.10 * t
        p4.rotation_euler.z = 0.14 * t
        cam.location = (0, -10.2 + 0.55 * u, 0.04 * math.sin(t))
    return update
