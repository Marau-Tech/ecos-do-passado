"""Esqueleto do personagem POV: medidas reais, frames dos ossos, IK de dois ossos e a mão.

Só usa numpy, para poder ser testado fora do Blender.

Coordenadas do corpo: X à direita, Y à frente, Z para cima; a origem fica no chão, sob o
centro do tronco. Cada osso é (R, h): R é 3x3 com as colunas X, Y, Z do osso (Y ao longo
do osso) e h é a cabeça do osso. Lado s = +1 direito, -1 esquerdo.

Medidas de um homem adulto de cerca de 1,75 m, olho a 1,65 m (o EYE das cenas).
"""
import math
import numpy as np

EYE = np.array([0.0, 0.09, 1.65])           # olho, um pouco à frente do eixo do tronco
HEAD_PIVOT = np.array([0.0, -0.02, 1.47])   # base do pescoço (C7): olhar para baixo dobra o pescoço inteiro
UPPER, FORE = 0.30, 0.26                     # braço e antebraço
THIGH, SHIN = 0.44, 0.415                    # coxa e perna
ANKLE_H = 0.075                              # altura do tornozelo acima do chão
FOOT_VEC = np.array([0.0, 0.135, -0.055])    # tornozelo -> bola do pé
TOE_LEN = 0.065
PELVIS_H, CHEST_H = 0.93, 1.07


def shoulder0(s):
    return np.array([s * 0.185, -0.015, 1.425])


def hip0(s):
    return np.array([s * 0.09, 0.0, PELVIS_H])


# ---------- álgebra ----------
def unit(v):
    v = np.asarray(v, float)
    n = np.linalg.norm(v)
    return v / n if n > 1e-9 else v


def frame(y, zhint):
    """Frame com Y na direção y e Z o mais perto possível de zhint; X = Y x Z."""
    Y = unit(y)
    z = np.asarray(zhint, float)
    Z = z - np.dot(z, Y) * Y
    if np.linalg.norm(Z) < 1e-6:
        alt = np.array([1.0, 0, 0]) if abs(Y[0]) < 0.9 else np.array([0, 0, 1.0])
        Z = alt - np.dot(alt, Y) * Y
    Z = unit(Z)
    return np.stack([np.cross(Y, Z), Y, Z], 1)


def rot(axis, ang):
    """Rotação de ang radianos em torno de axis (Rodrigues)."""
    a = unit(axis)
    c, s = math.cos(ang), math.sin(ang)
    K = np.array([[0, -a[2], a[1]], [a[2], 0, -a[0]], [-a[1], a[0], 0]])
    return np.eye(3) + s * K + (1 - c) * (K @ K)


RX = lambda a: rot((1, 0, 0), a)
RY = lambda a: rot((0, 1, 0), a)
RZ = lambda a: rot((0, 0, 1), a)


def smooth(u):
    u = min(1.0, max(0.0, u))
    return u * u * (3 - 2 * u)


# ---------- IK ----------
def two_bone(root, target, a, b, pole):
    """Junta do meio (cotovelo ou joelho) de uma cadeia a+b que vai de root a target.

    pole é a direção para onde a junta aponta. Se o alvo estiver longe demais, a cadeia
    estica na direção dele. Devolve (junta, ponta)."""
    root = np.asarray(root, float)
    d_vec = np.asarray(target, float) - root
    d = np.linalg.norm(d_vec)
    u = d_vec / d if d > 1e-9 else np.array([0, 0, -1.0])
    d = min(max(d, abs(a - b) + 1e-4), a + b - 1e-4)
    p = np.asarray(pole, float)
    v = p - np.dot(p, u) * u
    v = unit(v) if np.linalg.norm(v) > 1e-6 else frame(u, (0, 1, 0))[:, 2]
    cos_a = (a * a + d * d - b * b) / (2 * a * d)
    sin_a = math.sqrt(max(0.0, 1 - cos_a * cos_a))
    mid = root + a * (cos_a * u + sin_a * v)
    return mid, root + d * u


def limb_frames(root, mid, tip, pole):
    """Frames dos dois ossos: Z do primeiro aponta para onde o segundo dobra; X é a dobradiça."""
    y1 = unit(mid - root)
    y2 = unit(tip - mid)
    z = y2 - np.dot(y2, y1) * y1
    if np.linalg.norm(z) < 1e-4:                       # reto: a dobra vai para o lado oposto ao pólo
        p = -np.asarray(pole, float)
        z = p - np.dot(p, y1) * y1
    R1 = frame(y1, z)
    X = R1[:, 0]
    R2 = np.stack([X, y2, np.cross(X, y2)], 1)
    return R1, R2


# ---------- mão ----------
# dedo: (nome, x a partir do eixo da mão, positivo para o lado do mínimo; y; z; falanges; raio na base; abertura)
FINGERS = [
    ('index',  -0.0255, 0.088, 0.002, (0.039, 0.023, 0.018), 0.0103, -0.035),
    ('middle', -0.0065, 0.092, 0.003, (0.043, 0.026, 0.019), 0.0106, 0.0),
    ('ring',    0.0120, 0.088, 0.002, (0.041, 0.025, 0.018), 0.0100, 0.03),
    ('little',  0.0285, 0.078, 0.000, (0.031, 0.018, 0.016), 0.0088, 0.07),
]
THUMB_BASE = (-0.019, 0.014, -0.010)
THUMB_LEN = (0.046, 0.032, 0.027)
PALM_POINT = np.array([0.0, 0.062, -0.026])     # centro da palma, onde um objeto encosta


def thumb_rest(s):
    """Frame de repouso do polegar no espaço da mão: aponta para frente, para fora e para a palma."""
    d = (s * -0.55, 1.0, -0.42)
    return frame(d, (s * -0.65, -0.1, 0.75))


def hand_bones(side, s, Rh, hh, curls, thumb):
    """Ossos dos dedos a partir do frame da mão.

    curls: 4x3 ângulos de flexão (rad) de cada falange; thumb: (abertura, cmc, mcp, ip)."""
    out = {}
    for i, (name, x, y, z, lens, _, spread) in enumerate(FINGERS):
        R = RZ(-s * spread * (1 + 0.6 * curls[i][0])) @ RX(-curls[i][0])
        h = np.array([s * x, y, z])
        for j, ln in enumerate(lens):
            if j:
                R = R @ RX(-curls[i][j])
            out[f'{side}_{name}_{j}'] = (Rh @ R, hh + Rh @ h)
            h = h + R[:, 1] * ln
    spread_t, cmc, mcp, ip = thumb
    R = RZ(-s * -spread_t) @ thumb_rest(s) @ RX(-cmc)
    h = np.array([s * THUMB_BASE[0], THUMB_BASE[1], THUMB_BASE[2]])
    for j, (ln, ang) in enumerate(zip(THUMB_LEN, (0.0, mcp, ip))):
        if j:
            R = R @ RX(-ang)
        out[f'{side}_thumb_{j}'] = (Rh @ R, hh + Rh @ h)
        h = h + R[:, 1] * ln
    return out


# ---------- corpo inteiro ----------
def arm(side, s, chest_R, arm_p):
    """Braço por IK até o punho. arm_p: W (punho), D (dorso da mão), F (dedos), pole, raise."""
    S = np.array([0, 0, CHEST_H]) + chest_R @ (shoulder0(s) - np.array([0, 0, CHEST_H]))
    S = S + np.array([0, 0, arm_p.get('raise', 0.0)])
    E, W = two_bone(S, arm_p['W'], UPPER, FORE, arm_p['pole'])
    Ru, Rf = limb_frames(S, E, W, arm_p['pole'])
    fore = Rf[:, 1]
    F = unit(arm_p.get('F', fore))
    # o punho dobra no máximo 70 graus em relação ao antebraço
    ang = math.acos(max(-1.0, min(1.0, float(np.dot(F, fore)))))
    if ang > math.radians(70):
        k = math.radians(70) / ang
        F = unit(fore * (1 - k) + F * k)
    Rh = frame(F, arm_p['D'])
    bones = {f'{side}_upper': (Ru, S), f'{side}_fore': (Rf, E), f'{side}_hand': (Rh, W)}
    bones.update(hand_bones(side, s, Rh, W, arm_p['curls'], arm_p['thumb']))
    return bones


def leg(side, s, pelvis_R, leg_p):
    """Perna por IK até o tornozelo; o pé e os dedos vêm prontos em leg_p (frames)."""
    H = np.array([0, 0, PELVIS_H]) + pelvis_R @ (hip0(s) - np.array([0, 0, PELVIS_H]))
    K, A = two_bone(H, leg_p['A'], THIGH, SHIN, leg_p['pole'])
    Rt, Rs = limb_frames(H, K, A, leg_p['pole'])
    return {f'{side}_thigh': (Rt, H), f'{side}_shin': (Rs, K),
            f'{side}_foot': (leg_p['Rf'], A), f'{side}_toe': (leg_p['Rt'], A + leg_p['Rf'] @ np.array([0, np.linalg.norm(FOOT_VEC), 0]))}


TORSO_BASE = frame((0, 0, 1), (0, 1, 0))       # Y para cima, Z para a frente


def solve(p):
    """Esqueleto completo para os parâmetros p (ver motion.pose_params)."""
    Rp = RZ(p.get('yaw_p', 0.0)) @ TORSO_BASE
    Rc = RZ(p.get('yaw_c', 0.0)) @ TORSO_BASE
    bones = {'pelvis': (Rp, np.array([0, 0, PELVIS_H])), 'chest': (Rc, np.array([0, 0, CHEST_H]))}
    for side, s in (('R', 1), ('L', -1)):
        bones.update(arm(side, s, Rc @ TORSO_BASE.T, p['arms'][side]))
        bones.update(leg(side, s, Rp @ TORSO_BASE.T, p['legs'][side]))
    for name, fr in p.get('props', {}).items():
        bones[name] = fr
    return bones


def foot_frames(s, pitch, toe_bend=0.0, yaw=0.0):
    """Frames do pé e dos dedos: pitch positivo levanta a ponta."""
    base = RZ(yaw) @ RX(pitch)
    Rf = base @ frame(FOOT_VEC, (0, 0, 1))
    Rt = base @ RX(toe_bend) @ frame((0, 1, 0), (0, 0, 1))
    return Rf, Rt


def bone_matrix(R, h):
    M = np.eye(4)
    M[:3, :3] = R
    M[:3, 3] = h
    return M
