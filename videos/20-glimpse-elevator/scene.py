"""Elevador de madrugada, pela câmera do canto do teto. As portas de aço abrem para um corredor escuro e
fecham sem ninguém entrar; depois disso, o reflexo das portas mostra uma pessoa parada no fundo da cabine."""
from lib import *
import timeline as TL

SHOTS = {'a': 12.0}
HOLD_STATES = True

W, D, H = 0.85, 0.75, 2.4       # meia largura, meia profundidade e altura da cabine
GAP = 0.45                      # meia largura do vão da porta


def door_open(t):
    """0 fechada, 1 aberta"""
    a0, a1 = TL.OPEN
    c0, c1 = TL.CLOSE
    if t < a0 or t >= c1:
        return 0.0
    if t < a1:
        return ease((t - a0) / (a1 - a0))
    if t < c0:
        return 1.0
    return 1.0 - ease((t - c0) / (c1 - c0))


def steel(name, rough):
    m, nt = mat(name)
    tc = n(nt, 'ShaderNodeTexCoord').outputs['Object']
    mp = n(nt, 'ShaderNodeMapping'); L(nt, tc, mp.inputs['Vector']); mp.inputs['Scale'].default_value = (1.0, 1.0, 60.0)
    nz = n(nt, 'ShaderNodeTexNoise', Scale=6.0, Detail=4.0); L(nt, mp.outputs[0], nz.inputs['Vector'])
    r = ramp(nt, [(0.3, (rough * 0.7,) * 3), (0.7, (rough * 1.3,) * 3)], nz.outputs['Fac']).outputs[0]
    p = principled(nt, (0.62, 0.63, 0.65), 0.2, 1.0)
    L(nt, r, p.inputs['Roughness'])
    out(nt, p.outputs[0])
    return m


def build_a():
    reset(48)
    world_flat((0, 0, 0), 0.0)
    panel = simple('panel', (0.55, 0.5, 0.42), 0.7)
    floor = simple('floor', (0.1, 0.1, 0.1), 0.6)
    trim = steel('trim', 0.35)
    mirror = steel('door', 0.14)
    # cabine
    box('floor', (2 * W, 2 * D, 0.05), (0, 0, -0.025), floor)
    box('ceil', (2 * W, 2 * D, 0.05), (0, 0, H + 0.025), simple('ceilm', (0.3, 0.3, 0.3), 0.8))
    box('back', (2 * W, 0.04, H), (0, -D - 0.02, H / 2), panel)
    box('left', (0.04, 2 * D, H), (-W - 0.02, 0, H / 2), panel)
    box('right', (0.04, 2 * D, H), (W + 0.02, 0, H / 2), panel)
    for x in (-0.58, 0.0, 0.58):                                  # frisos dos painéis do fundo
        box('seam', (0.012, 0.01, H), (x, -D + 0.002, H / 2), trim)
    # parede da frente em aço, com o vão da porta e o letreiro do andar
    box('frontL', ((W - GAP), 0.04, H), (-(W + GAP) / 2, D + 0.02, H / 2), trim)
    box('frontR', ((W - GAP), 0.04, H), ((W + GAP) / 2, D + 0.02, H / 2), trim)
    box('header', (2 * GAP, 0.04, H - 2.1), (0, D + 0.02, (H + 2.1) / 2), trim)
    doors = []
    for s_ in (-1, 1):
        d = box('door', (GAP + 0.01, 0.03, 2.1), (s_ * GAP / 2, D + 0.065, 1.05), mirror)
        doors.append((d, s_))
    cu = bpy.data.curves.new('ind', 'FONT'); cu.body = '4'; cu.size = 0.13; cu.align_x = 'CENTER'
    ind = bpy.data.objects.new('ind', cu); link(ind)
    ind.location = (0, D - 0.012, 2.19); ind.rotation_euler = (math.radians(90), 0, 0)
    ind.data.materials.append(emission('led', (1.0, 0.45, 0.1), 6.0))
    box('indbg', (0.22, 0.01, 0.17), (0, D - 0.001, 2.245), simple('indbg', (0.02, 0.02, 0.02), 0.4))
    # botoeira à direita da porta
    box('panelbox', (0.16, 0.012, 0.55), (0.66, D - 0.004, 1.15), simple('btnplate', (0.25, 0.25, 0.26), 0.3, 0.8))
    lit = emission('btnlit', (1.0, 0.85, 0.6), 3.0)
    dim = simple('btn', (0.5, 0.5, 0.5), 0.3, 0.5)
    for k in range(6):
        box('btn', (0.035, 0.012, 0.035), (0.66, D - 0.012, 0.95 + k * 0.075), lit if k == 3 else dim)
    # corrimão no fundo e nas laterais
    for pts in ([(-W + 0.08, -D + 0.06, 0.92), (0, -D + 0.06, 0.92), (W - 0.08, -D + 0.06, 0.92)],
                [(-W + 0.06, -D + 0.1, 0.92), (-W + 0.06, 0, 0.92), (-W + 0.06, D - 0.2, 0.92)],
                [(W - 0.06, -D + 0.1, 0.92), (W - 0.06, 0, 0.92), (W - 0.06, D - 0.2, 0.92)]):
        tube('rail', pts, [0.022] * 3, trim, kind='POLY')
    # luz do teto
    box('lamp', (1.1, 0.9, 0.02), (0, -0.05, H - 0.01), emission('lampm', (1.0, 0.97, 0.9), 1.6))
    point((0, -0.1, H - 0.25), 32.0, (1.0, 0.97, 0.9), 0.5)
    # corredor escuro além da porta, com a placa verde de saída no fundo
    dark = simple('hall', (0.12, 0.12, 0.12), 0.9)
    box('hfloor', (3.0, 5.0, 0.05), (0, D + 2.6, -0.025), simple('hfl', (0.04, 0.04, 0.04), 0.7))
    box('hceil', (3.0, 5.0, 0.05), (0, D + 2.6, 2.6), dark)
    box('hL', (0.05, 5.0, 2.6), (-1.2, D + 2.6, 1.3), dark); box('hR', (0.05, 5.0, 2.6), (1.2, D + 2.6, 1.3), dark)
    box('hEnd', (3.0, 0.05, 2.6), (0, D + 5.0, 1.3), dark)
    box('exit', (0.4, 0.03, 0.15), (0.1, D + 4.94, 1.2), emission('exitm', (0.2, 1.0, 0.35), 14.0))
    point((0.1, D + 4.4, 1.3), 30.0, (0.2, 1.0, 0.35), 0.2)
    # a pessoa: só aparece no reflexo, nunca direto na câmera
    fig = figure((0.3, -0.52, 0.0), yaw=math.radians(180), s=0.9, color=(0.03, 0.03, 0.035))
    parts = list(fig.children_recursive)
    for o in parts:
        o.visible_camera = False
        o.visible_diffuse = False
        o.visible_shadow = False
    cam = camera((-0.74, -0.66, 2.32), (0.05, D, 1.25), 16)

    def upd(t, u):
        o = door_open(t)
        for d, s_ in doors:
            d.location.x = s_ * (GAP / 2 + o * (GAP + 0.02))
        seen = TL.SEEN[0] <= t < TL.SEEN[1]
        for p in parts:
            p.hide_render = not seen
        return (round(o, 3), seen)
    return upd
