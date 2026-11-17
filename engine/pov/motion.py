"""Movimento do personagem POV: marcha, poses de ação e agenda. Tudo é função pura do tempo.

A marcha usa a mesma fase da câmera de walk_pov (places.py): step = sin(pi * step_hz * t).
O balanço lateral da câmera vai para a direita quando step > 0, com o peso no pé direito;
por isso o pé direito está no meio do apoio quando step = 1.

Uma ação é (pose, início, fim) ou (pose, início, fim, rampa), em segundos do take. A pose
entra e sai com rampa suave; fora das ações, os braços balançam com a marcha.
"""
import math
import numpy as np
from .skeleton import (unit, frame, RX, RZ, smooth, foot_frames, FOOT_VEC, ANKLE_H,
                       shoulder0, PALM_POINT, EYE, HEAD_PIVOT)

STANCE = 0.6                 # fração do ciclo com o pé no chão
RIGHT_OFFSET = 0.05          # o pé direito está no meio do apoio (0,3) quando step = 1

RELAXED = [(0.22, 0.32, 0.18), (0.28, 0.38, 0.2), (0.34, 0.45, 0.24), (0.42, 0.52, 0.26)]
RELAXED_THUMB = (0.15, 0.2, 0.15, 0.2)
GRIP = [(1.2, 1.45, 0.75), (1.25, 1.5, 0.8), (1.3, 1.5, 0.8), (1.35, 1.45, 0.8)]
GRIP_THUMB = (0.35, 0.55, 0.45, 0.4)


def walk_k(speed):
    """0 parado, 1 andando normal (0,6 m/s ou mais)."""
    return min(1.0, max(0.0, speed / 0.6))


def foot_cycle(t, s, step_hz):
    phi = math.pi * step_hz * t
    return (phi / (2 * math.pi) + RIGHT_OFFSET + (0 if s > 0 else 0.5)) % 1.0


def leg_params(t, s, speed, step_hz):
    """Tornozelo e frames do pé para o lado s, com o pé plantado no chão durante o apoio."""
    k = walk_k(speed)
    stride = speed * 2.0 / step_hz                     # distância de um ciclo (dois passos)
    exc = stride * STANCE                              # quanto o pé anda para trás durante o apoio
    c = foot_cycle(t, s, step_hz)
    yaw = s * -0.08                                    # ponta do pé um pouco para fora
    x = s * 0.10
    if c < STANCE:
        u = c / STANCE
        y = exc * (0.5 - u)
        lift = 0.0
        if u < 0.12:
            pitch, pivot = 0.22 * k * (1 - u / 0.12), 'heel'
        elif u > 0.7:
            pitch, pivot = -0.55 * k * (u - 0.7) / 0.3, 'ball'
        else:
            pitch, pivot = 0.0, None
    else:
        v = (c - STANCE) / (1 - STANCE)
        y = exc * (smooth(v) - 0.5)
        lift = 0.055 * k * math.sin(math.pi * v) ** 0.8
        pitch = (-0.55 + 0.77 * smooth(v)) * k
        pivot = None
    A = np.array([x, 0.02 + y, ANKLE_H + lift])
    flat_ball = A + RZ(yaw) @ FOOT_VEC
    heel = A + RZ(yaw) @ np.array([0, -0.06, -0.065])
    Rf, Rt = foot_frames(s, pitch, 0.0, yaw)
    if pivot == 'heel':
        A = heel + RZ(yaw) @ RX(pitch) @ RZ(-yaw) @ (A - heel)
    elif pivot == 'ball':
        A = flat_ball + RZ(yaw) @ RX(pitch) @ RZ(-yaw) @ (A - flat_ball)
        Rt = RZ(yaw) @ frame((0, 1, 0), (0, 0, 1))       # os dedos ficam no chão
    elif c >= STANCE:                                   # os dedos ainda dobrados logo depois de sair do chão
        Rf, Rt = foot_frames(s, pitch, 0.35 * k * (1 - smooth((c - STANCE) / 0.2)), yaw)
    return {'A': A, 'Rf': Rf, 'Rt': Rt, 'pole': RZ(yaw) @ np.array([0, 1.0, 0.0])}


def rest_arm(t, s, speed, step_hz):
    """Braço solto, balançando ao contrário da perna do mesmo lado."""
    k = walk_k(speed)
    c = foot_cycle(t, s, step_hz)
    amp = 0.11 * min(1.0, speed / 1.0)
    fwd = -amp * math.cos(2 * math.pi * c)              # pé deste lado à frente -> braço atrás
    breath = 0.004 * math.sin(2 * math.pi * 0.25 * t)
    S = shoulder0(s)
    W = S + np.array([s * 0.05, 0.035 + fwd, -0.535 + fwd * fwd * 0.8 + breath])
    return {
        'W': W, 'F': unit((0, 0.12 + 0.6 * fwd, -1.0)), 'D': unit((s * 1.0, -0.2, 0.0)),
        'pole': np.array([s * 0.35, -1.0, -0.2]), 'curls': RELAXED, 'thumb': RELAXED_THUMB, 'raise': 0.0,
    }


# ---------- poses de ação ----------
def pose_shield(t, s, prof):
    """Proteção instintiva: mãos erguidas diante do rosto, costas das mãos para o olho, dedos
    semiflexionados. Os punhos ficam abaixo do quadro; mãos e dedos sobem pela metade de baixo."""
    tr = 0.005 * math.sin(2 * math.pi * 6.0 * t + s)       # tremor de susto
    return {
        'W': np.array([s * 0.15, 0.36, 1.50 + tr]), 'F': unit((s * -0.25, 0.42, 1.0)),
        'D': unit((s * 0.3, -1.0, -0.4)), 'pole': np.array([s * 1.0, -0.3, -1.0]),
        'curls': [(0.45, 0.5, 0.28), (0.4, 0.48, 0.26), (0.48, 0.52, 0.28), (0.55, 0.58, 0.3)],
        'thumb': (0.3, 0.15, 0.2, 0.2), 'raise': 0.04,
    }


def pose_watch(t, s, prof):
    """Mão esquerda com o relógio de bolso na palma, diante do peito."""
    return {
        'W': np.array([s * 0.05, 0.29, 1.31]), 'F': unit((s * -0.6, 0.75, 0.15)),
        'D': unit((s * 0.15, 0.1, -1.0)), 'pole': np.array([s * 1.0, -0.6, -1.0]),
        'curls': [(0.95, 0.85, 0.45), (0.95, 0.9, 0.5), (1.05, 0.95, 0.5), (1.15, 1.0, 0.55)],
        'thumb': (0.15, 0.45, 0.3, 0.35), 'raise': 0.0,
    }


def pose_reach(t, s, prof):
    """Mão estendida à frente, palma para baixo: afastar alguém, tocar um parapeito."""
    return {
        'W': np.array([s * 0.14, 0.46, 1.40]), 'F': unit((s * -0.05, 1.0, -0.05)),
        'D': unit((s * 0.25, 0.0, 1.0)), 'pole': np.array([s * 1.0, -0.4, -1.0]),
        'curls': [(0.12, 0.18, 0.1), (0.15, 0.2, 0.1), (0.18, 0.22, 0.12), (0.22, 0.28, 0.15)],
        'thumb': (0.35, 0.05, 0.1, 0.1), 'raise': 0.01,
    }


def pose_rail(t, s, prof):
    """Mão direita pousada no parapeito à direita e um pouco à frente: a borda da capa fica a
    0,42 m do centro do corpo e o topo a 1,07 m; o punho passa 8 cm da borda, a palma assenta na
    pedra e os dedos ficam soltos para a frente e para fora."""
    return {
        'W': np.array([s * 0.50, 0.26, 1.10]), 'F': unit((s * 0.55, 0.8, -0.12)),
        'D': unit((s * -0.04, 0.05, 1.0)), 'pole': np.array([s * 1.0, -0.5, -0.5]),
        'curls': [(0.12, 0.22, 0.18), (0.1, 0.2, 0.18), (0.14, 0.24, 0.2), (0.2, 0.3, 0.22)],
        'thumb': (0.35, 0.05, 0.1, 0.12), 'raise': 0.0,
    }


RIFLE_GRIP_Y = -0.02       # punho da coronha, no espaço do fuzil (Y = cano, Z = alça de mira)
RIFLE_FORE_Y = 0.27


def rifle_frame(t, speed, step_hz):
    """Fuzil pronto, atravessado diante do corpo: punho da coronha junto ao quadril direito, cano
    para a frente, para a esquerda e um pouco para cima. Com o olhar a -20 graus ou mais, a mão
    esquerda na telha e o fuzil entram juntos no terço de baixo do quadro."""
    k = walk_k(speed)
    sw = 0.02 * k * math.sin(math.pi * step_hz * t)
    breath = 0.004 * math.sin(2 * math.pi * 0.25 * t)
    R = RZ(sw) @ RX(0.6 * sw) @ frame((-0.42, 0.80, 0.42), (0.25, 0.35, 1.0))
    G = np.array([0.15, 0.26, 1.13 + breath + 0.01 * k * abs(math.sin(math.pi * step_hz * t))])
    return R, G - R @ np.array([0, RIFLE_GRIP_Y, 0])


def _grip_on(R, h, y, s, right):
    """Punho e frame da mão segurando o fuzil no ponto y do eixo dele."""
    X, Yr, Z = R[:, 0], R[:, 1], R[:, 2]
    if right:     # mão direita no punho da coronha, por cima e pela direita
        F = unit(-X * 0.85 - Z * 0.55 + Yr * 0.15)
        D = unit(X * 0.6 + Z * 0.75 - Yr * 0.2)
    else:         # mão esquerda por baixo da telha, dedos subindo pela direita
        F = unit(X * 0.75 + Z * 0.55 + Yr * 0.1)
        D = unit(-X * 0.55 - Z * 0.8)
    Rh = frame(F, D)
    grip = h + Yr * y
    W = grip - Rh @ (PALM_POINT + np.array([0, 0, -0.008]))
    return W, F, D


def pose_rifle(t, s, prof, speed=0.0, step_hz=1.8):
    R, h = rifle_frame(t, speed, step_hz)
    right = s > 0
    W, F, D = _grip_on(R, h, RIFLE_GRIP_Y if right else RIFLE_FORE_Y, s, right)
    return {
        'W': W, 'F': F, 'D': D, 'pole': np.array([s * 1.0, -0.6, -0.9]),
        'curls': GRIP, 'thumb': GRIP_THUMB, 'raise': 0.0,
    }


# nome -> (função, lados, objeto que aparece com a pose)
POSES = {
    'shield': (pose_shield, ('R', 'L'), None),
    'watch': (pose_watch, ('L',), 'watch'),
    'reach': (pose_reach, ('R',), None),
    'rail': (pose_rail, ('R',), None),
    'rifle': (pose_rifle, ('R', 'L'), 'rifle'),
}


def action_weight(t, a):
    pose, t0, t1 = a[:3]
    ramp = a[3] if len(a) > 3 else 0.6
    if t <= t0 - 1e-9 or t >= t1 + 1e-9:
        return 0.0
    return smooth((t - t0) / ramp) * smooth((t1 - t) / ramp) if ramp > 0 else 1.0


def blend(params, weights):
    tot = sum(weights)
    out = {}
    for key in ('W', 'F', 'D', 'pole', 'curls', 'thumb', 'raise'):
        acc = sum(np.asarray(p[key], float) * w for p, w in zip(params, weights)) / tot
        out[key] = unit(acc) if key in ('F', 'D', 'pole') else acc
    return out


def pose_params(t, speed=0.0, step_hz=1.8, actions=(), profile=None):
    """Parâmetros do esqueleto no tempo t do take. Mesma entrada, mesma pose."""
    k = walk_k(speed)
    phi = math.pi * step_hz * t
    p = {'yaw_p': 0.05 * k * math.sin(phi), 'yaw_c': -0.03 * k * math.sin(phi), 'arms': {}, 'legs': {}}
    shown = {}
    for side, s in (('R', 1), ('L', -1)):
        p['legs'][side] = leg_params(t, s, speed, step_hz)
        ps, ws = [rest_arm(t, s, speed, step_hz)], []
        for a in actions:
            fn, sides, prop = POSES[a[0]]
            w = action_weight(t, a)
            if prop:
                shown[prop] = max(shown.get(prop, 0.0), w)
            if w <= 0 or side not in sides:
                continue
            extra = {'speed': speed, 'step_hz': step_hz} if a[0] == 'rifle' else {}
            ps.append(fn(t, s, profile, **extra))
            ws.append(w)
        rest_w = max(0.0, 1.0 - sum(ws))
        p['arms'][side] = blend(ps, [rest_w] + ws) if ws else ps[0]
    p['props'] = {'rifle': rifle_frame(t, speed, step_hz)}    # sempre calculado; o personagem esconde quando não usa
    p['shown'] = shown
    return p


# ---------- corpo em relação à câmera ----------
def body_from_camera(cam_loc, cam_forward, heading=None):
    """Origem e rumo do corpo a partir da câmera: o corpo segue a posição e o rumo,
    mas não o tremor nem a inclinação da cabeça. heading (rad, 0 = +Y) fixa o rumo do
    corpo; sem ele, vem da direção horizontal da câmera."""
    f = unit(cam_forward)
    yaw = math.atan2(-f[0], f[1]) if heading is None else heading
    pitch = math.asin(max(-1.0, min(1.0, f[2])))
    look_yaw = math.atan2(-f[0], f[1])                  # a cabeça pode girar para o lado do rumo
    head_R = RZ(look_yaw) @ RX(pitch)
    pivot = np.asarray(cam_loc, float) - head_R @ (EYE - HEAD_PIVOT)
    root = pivot - RZ(yaw) @ HEAD_PIVOT
    return root, yaw


def head_eye(level_eye, pitch, yaw=0.0, heading=None):
    """Onde fica o olho quando a cabeça inclina pitch radianos em torno do pescoço, partindo
    do olho na cabeça reta. Olhar para baixo leva o olho uns 12 cm para baixo e 3 cm para a
    frente: é o que deixa ver o peito e os pés. Use nas cenas que dirigem um olhar para baixo."""
    off = EYE - HEAD_PIVOT
    heading = yaw if heading is None else heading      # heading: rumo do corpo, se a cabeça girar para o lado
    d = RZ(yaw) @ RX(pitch) @ off - RZ(heading) @ off
    return np.asarray(level_eye, float) + d
