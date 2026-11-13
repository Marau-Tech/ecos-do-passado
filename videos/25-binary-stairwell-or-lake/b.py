"""B: o lago. A cabana com a janela acesa no gelo, o gelo grosso visto de cima e a tábua do chão que pula."""
from lib import *
from places import *
import timeline as TL

SHOTS = {'b1': 4.5, 'b2': 4.0, 'b3': 5.2}


def lake_night():
    night_sky()
    box('lake', (400, 400, 0.1), (0, 0, -0.05), ice_mat())
    sun(0.35, (-0.5, 0.8, 0.45), (0.6, 0.7, 1.0), 1.0)          # lua atrás e à esquerda
    pines(160, 90, seed=3, h=(8, 16))


def build_b1():
    """A cabana sozinha no meio do lago, com neve caindo. O zoom é de lente, depois do nome."""
    reset(24)
    lake_night()
    cabin((0, 0, 0), math.radians(-12))
    flakes = snowfall(3000, (-12, -22, -2), (12, 10, 10), size=0.025)
    cam = camera((-3.5, -26.0, 1.7), (0, 0, 1.3), 30)
    def update(t, u):
        u = zoom_after(t, TL.NAME_HOLD, SHOTS['b1'])
        cam.data.lens = lerp(30, 62, ease(u))
        flakes.location = (0.15 * t, 0, -0.45 * t)
        return None
    return update


def ice_slab(thick=1.0):
    """gelo limpo: superfície quase toda transparente, volume que absorve azul; a lanterna atravessa"""
    m, nt = mat('clear_ice')
    tr = n(nt, 'ShaderNodeBsdfTransparent'); tr.inputs['Color'].default_value = (0.92, 0.97, 1.0, 1)
    gl = n(nt, 'ShaderNodeBsdfGlossy'); gl.inputs['Roughness'].default_value = 0.08
    lw = n(nt, 'ShaderNodeLayerWeight', Blend=0.25)
    ms = n(nt, 'ShaderNodeMixShader')
    L(nt, math_(nt, 'ADD', math_(nt, 'MULTIPLY', lw.outputs['Fresnel'], 0.6), 0.04), ms.inputs[0])
    L(nt, tr.outputs[0], ms.inputs[1]); L(nt, gl.outputs[0], ms.inputs[2])
    o = out(nt, ms.outputs[0])
    va = n(nt, 'ShaderNodeVolumeAbsorption', Density=0.9); va.inputs['Color'].default_value = (0.35, 0.65, 0.85, 1)
    L(nt, va.outputs[0], o.inputs['Volume'])
    return box('slab', (30, 30, thick), (0, 0, -thick / 2), m)


def build_b2():
    """De pé no gelo, a lanterna apontada para baixo: colunas de bolhas presas em um metro de gelo, e só escuro embaixo."""
    reset(32)
    world_flat((0.004, 0.006, 0.01), 1.0)
    bpy.context.scene.cycles.volume_bounces = 1
    ice_slab(1.0)
    box('water', (30, 30, 0.1), (0, 0, -1.08), simple('deep', (0.0, 0.004, 0.008), 0.2))
    rs = np.random.RandomState(11)
    v, t = lathe([(0.0, -0.3), (0.7, -0.15), (1.0, 0.0), (0.7, 0.15), (0.0, 0.3)], 10)
    pos, sc = [], []
    for c in range(28):                                              # colunas de bolhas, menores no fundo
        cx, cy = rs.uniform(-2.2, 2.2), rs.uniform(-1.0, 3.2)
        for k in range(rs.randint(5, 14)):
            d = 0.05 + k * rs.uniform(0.06, 0.09)
            if d > 0.95:
                break
            r = rs.uniform(0.02, 0.06) * (1.1 - d * 0.6)
            pos.append((cx + rs.uniform(-0.02, 0.02), cy + rs.uniform(-0.02, 0.02), -d))
            sc.append((r, r, r * 0.5))
    scatter('bubbles', v, t, pos, None, sc, emission('bubble', (0.75, 0.88, 0.95), 0.6))
    # neve fina por cima, em manchas
    pos = np.stack([rs.uniform(-3, 3, 2500), rs.uniform(-1.5, 4, 2500), np.full(2500, 0.003)], 1)
    pos = pos[np.sin(pos[:, 0] * 1.7 + pos[:, 1] * 0.9) + 0.6 * np.sin(pos[:, 0] * 4.1 - pos[:, 1] * 2.3) > 0.2]
    sv, st = lathe([(0.0, 0.0), (0.018, 0.0), (0.0, 0.002)], 5)
    scatter('dust', sv, st, pos, rs.uniform(0, 6, len(pos)), np.repeat(rs.uniform(0.4, 1.4, (len(pos), 1)), 3, 1),
            simple('frost', (0.3, 0.33, 0.36), 0.8), smooth=False)
    # riscos brancos de rachadura na superfície
    crack = simple('crackline', (0.8, 0.86, 0.92), 0.5)
    for x0, y0, a0 in ((-1.2, 0.2, 0.5), (0.6, 1.5, -0.3), (0.2, 2.8, 1.1)):
        pts = [(x0, y0, 0.002)]
        for k in range(6):
            a0 += rs.uniform(-0.5, 0.5)
            pts.append((pts[-1][0] + 0.35 * math.cos(a0), pts[-1][1] + 0.35 * math.sin(a0), 0.002))
        tube('crack', pts, [0.004] * len(pts), crack, kind='POLY')
    cam = camera((0.0, -1.4, 1.5), (0.1, 0.9, -0.7), 26)
    l = bpy.data.lights.new('torch', 'SPOT'); l.energy = 260; l.spot_size = math.radians(50); l.spot_blend = 0.6
    l.color = (1.0, 0.95, 0.85); l.shadow_soft_size = 0.05
    torch = bpy.data.objects.new('torch', l); link(torch)
    def update(t, u):
        cam.location = (0.0, lerp(-1.4, -0.9, ease(u)), lerp(1.5, 1.25, ease(u)))
        look(cam, (0.1, 0.9, -0.7))
        torch.location = cam.location + Vector((0.25, 0.0, -0.15))
        aim = Vector((0.1 + 0.2 * math.sin(t * 0.9), 1.0, -0.8)) - torch.location
        torch.rotation_euler = aim.to_track_quat('-Z', 'Y').to_euler()
        return None
    return update


def build_b3():
    """Dentro da cabana, rente ao chão de tábuas, com o lampião pendurado. Na chave, a tábua do meio pula e fica torta."""
    reset(32)
    world_flat((0, 0, 0), 0.0)
    wd = wood('floor', (0.26, 0.16, 0.09), 0.8)
    box('under', (6, 6, 0.05), (0, 0, -0.2), simple('void', (0.0, 0.0, 0.0), 1.0))
    planks = []
    W_ = 0.19
    for i in range(-7, 8):
        p = box('plank', (W_ - 0.012, 3.4, 0.05), (0, 0, 0), wd)
        if i == 0:
            piv = bpy.data.objects.new('hinge', None); link(piv); piv.location = (i * W_, 1.7, -0.025)
            p.parent = piv; p.location = (0, -1.7, 0.0)
            mid = piv
        else:
            p.location = (i * W_, 0, -0.025)
        planks.append(p)
    nail = simple('nail', (0.15, 0.15, 0.16), 0.3, 0.9)
    for i in range(-7, 8):
        for y in (-1.2, 0.0, 1.2):
            ico('nail', 0.008, (i * W_, y, 0.002), nail, 1)
    walls = wood('walls', (0.2, 0.12, 0.07), 0.8)
    box('wallB', (3.0, 0.08, 2.2), (0, 1.75, 1.1), walls)
    box('wallL', (0.08, 3.6, 2.2), (-1.45, 0, 1.1), walls); box('wallR', (0.08, 3.6, 2.2), (1.45, 0, 1.1), walls)
    box('window', (0.6, 0.02, 0.45), (0.7, 1.7, 1.35), simple('night', (0.01, 0.015, 0.03), 0.1))
    # mesa e cadeira à direita, um balde de pesca à esquerda
    tb = wood('table', (0.3, 0.2, 0.12))
    box('top', (0.7, 0.5, 0.04), (1.0, 0.9, 0.72), tb)
    for dx in (-0.3, 0.3):
        for dy in (-0.2, 0.2):
            box('leg', (0.04, 0.04, 0.7), (1.0 + dx, 0.9 + dy, 0.35), tb)
    v, t = lathe([(0.12, 0.0), (0.15, 0.32), (0.0, 0.32)], 16)
    bucket = fast_mesh('bucket', v, t, simple('bucket', (0.12, 0.2, 0.3), 0.6)); bucket.location = (-0.9, 0.7, 0.0)
    # lampião pendurado num gancho
    hang = bpy.data.objects.new('hang', None); link(hang); hang.location = (0.15, 0.6, 2.2)
    cord = tube('cord', [(0, 0, 0), (0, 0, -0.3), (0, 0, -0.6)], [0.006] * 3, simple('cordm', (0.05, 0.05, 0.05), 0.8), kind='POLY')
    cord.parent = hang
    glass = box('glass', (0.12, 0.12, 0.18), (0, 0, -0.72), emission('flame', (1.0, 0.62, 0.25), 12.0)); glass.parent = hang
    glass.visible_shadow = False
    capm = simple('cap', (0.1, 0.08, 0.05), 0.5, 0.6)
    box('lcap', (0.16, 0.16, 0.04), (0, 0, -0.61), capm).parent = hang
    box('lbase', (0.16, 0.16, 0.05), (0, 0, -0.83), capm).parent = hang
    lt = point((0, 0, -0.72), 110.0, (1.0, 0.62, 0.3), 0.06); lt.parent = hang
    cam = camera((-0.15, -1.45, 0.62), (0.05, 0.6, 0.0), 24)
    base = cam.location.copy()
    def update(t, u):
        a = t - TL.TURN
        if a < 0:
            lift = 0.0
            sway = math.radians(1.2) * math.sin(2 * math.pi * t / 1.6)
        else:
            lift = 12.0 * math.sin(math.pi * a / 0.16) + 5.0 * a / 0.16 if a < 0.16 else 5.0
            sway = math.radians(1.2 + 7.0 * math.exp(-a * 1.1)) * math.sin(2 * math.pi * a / 1.6 + 0.3)
        mid.rotation_euler.x = -math.radians(lift)                   # a ponta perto da câmera sobe
        hang.rotation_euler.x = sway
        hang.rotation_euler.y = 0.4 * sway
        jolt = 0.02 * math.exp(-max(0.0, a) * 6) if a >= 0 else 0.0
        cam.location = base + Vector((jolt * math.sin(a * 60), 0, jolt * math.cos(a * 47))) if a >= 0 else base
        look(cam, (0.05, 0.6, 0.0))
        return None
    return update
