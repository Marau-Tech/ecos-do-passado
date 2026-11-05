"""Câmera da torre da emissora: bairro em grade à noite, a lua e, no v1, uma segunda lua mais baixa."""
from lib import *
from bpy_extras.object_utils import world_to_camera_view
import timeline as TL

SHOTS = {s[0]: s[1] for s in TL.SHOTS if not TL.MODELO.drawn(TL, s[0])}
HOLD_STATES = True              # câmera parada: só renderiza quando uma janela muda
CAM, TARGET, LENS = (0, -15, 12), (0, 80, 5.5), 35
MOON_HI, MOON_LO = (0.52, 0.74), (-0.38, 0.33)     # posição na tela, de -1 a 1
MOON_DIST, MOON_R = 2000, 74
LIT = 5                         # janelas acesas no começo


def night_sky():
    """Estrelas e um brilho alaranjado da cidade perto do horizonte, que recorta os telhados."""
    w = bpy.context.scene.world; nt = w.node_tree; nt.nodes.clear()
    tc = n(nt, 'ShaderNodeTexCoord')
    v = n(nt, 'ShaderNodeTexVoronoi', Scale=70.0); L(nt, tc.outputs['Generated'], v.inputs['Vector'])
    sc = n(nt, 'ShaderNodeSeparateColor'); L(nt, v.outputs['Color'], sc.inputs[0])
    star = math_(nt, 'MULTIPLY', math_(nt, 'MULTIPLY', math_(nt, 'LESS_THAN', v.outputs['Distance'], 0.07),
                                       math_(nt, 'GREATER_THAN', sc.outputs[0], 0.75)), math_(nt, 'POWER', sc.outputs[1], 3.0))
    sp = n(nt, 'ShaderNodeSeparateXYZ'); L(nt, tc.outputs['Generated'], sp.inputs[0])
    sky = ramp(nt, [(0.0, (0.10, 0.075, 0.07)), (0.06, (0.035, 0.04, 0.065)), (0.3, (0.008, 0.012, 0.03))], sp.outputs['Z']).outputs[0]
    col = mix(nt, 1.0, sky, math_(nt, 'MULTIPLY', star, 2.2), 'ADD', clamp=False)
    b = n(nt, 'ShaderNodeBackground', Strength=1.0); L(nt, col, b.inputs['Color'])
    o = n(nt, 'ShaderNodeOutputWorld'); L(nt, b.outputs[0], o.inputs['Surface'])


def moon_mat(smooth):
    """A lua tem mares e crateras; a de baixo é lisa e branca demais."""
    m, nt = mat('moon_lo' if smooth else 'moon')
    if smooth:
        e = n(nt, 'ShaderNodeEmission', Strength=1.6)
        e.inputs['Color'].default_value = (0.92, 0.96, 1.0, 1)
        out(nt, e.outputs[0])
        return m
    tc = n(nt, 'ShaderNodeTexCoord').outputs['Object']
    a = n(nt, 'ShaderNodeTexNoise', Scale=1.3, Detail=4.0, Roughness=0.55); L(nt, tc, a.inputs['Vector'])
    v = n(nt, 'ShaderNodeTexVoronoi', Scale=7.0); L(nt, tc, v.inputs['Vector'])
    base = ramp(nt, [(0.42, (0.48, 0.47, 0.44)), (0.58, (0.85, 0.84, 0.80))], a.outputs['Fac']).outputs[0]
    crat = ramp(nt, [(0.0, (0.6, 0.6, 0.6)), (0.25, (1, 1, 1))], v.outputs['Distance']).outputs[0]
    e = n(nt, 'ShaderNodeEmission', Strength=1.25)
    L(nt, mix(nt, 1.0, base, crat, 'MULTIPLY'), e.inputs['Color'])
    out(nt, e.outputs[0])
    return m


def window_mat(i):
    """Janela com luz de dentro; o valor liga e desliga."""
    m, nt = mat(f'lit{i}')
    val = n(nt, 'ShaderNodeValue'); val.outputs[0].default_value = 1.0
    e = n(nt, 'ShaderNodeEmission'); e.inputs['Color'].default_value = (1.0, 0.6, 0.26, 1)
    L(nt, math_(nt, 'MULTIPLY', val.outputs[0], 7.0), e.inputs['Strength'])
    add = n(nt, 'ShaderNodeAddShader')
    L(nt, principled(nt, (0.01, 0.012, 0.015), 0.15, spec=0.6).outputs[0], add.inputs[0]); L(nt, e.outputs[0], add.inputs[1])
    out(nt, add.outputs[0])
    return m, val.outputs[0]


def house(loc, rot, w, d, h, wall, roof, glass):
    root = bpy.data.objects.new('house', None); link(root)
    b = box('b', (w, d, h), (0, 0, h / 2), wall); b.parent = root
    o, rh = 0.35, h * 0.45
    v = [(-w / 2 - o, -d / 2 - o, h), (w / 2 + o, -d / 2 - o, h), (w / 2 + o, d / 2 + o, h), (-w / 2 - o, d / 2 + o, h),
         (-w / 2 - o, 0, h + rh), (w / 2 + o, 0, h + rh)]
    r = mesh_from('roof', v, [(0, 1, 5, 4), (2, 3, 4, 5), (0, 4, 3), (1, 2, 5)], roof); r.parent = root
    wins = []
    for x in (-w / 4, w / 4):
        g = box('win', (1.0, 0.08, 1.2), (x, -d / 2 - 0.03, h * 0.52), glass); g.parent = root
        wins.append(g)
    root.location = loc; root.rotation_euler.z = rot
    return wins


def screen_dir(cam, sx, sy):
    """Direção no mundo do ponto (sx, sy) da tela, de -1 a 1."""
    hw = 18 / LENS
    return (cam.matrix_world.to_3x3() @ Vector((sx * hw, sy * hw * 0.75, -1))).normalized()


class Town:
    def street_grid(self):
        """Bairro em grade: a rua principal sai da torre até o horizonte e cruza ruas transversais.
        As casas ficam dos dois lados de cada transversal, com o mesmo recuo e a frente para a rua.
        Guarda em self.cands uma janela de cada casa virada para a câmera."""
        rs = np.random.RandomState(6)
        asphalt = simple('asphalt', (0.022, 0.023, 0.026), 0.6)
        walk = simple('walk', (0.075, 0.075, 0.072), 0.9)
        yard = simple('yard', (0.028, 0.034, 0.026), 0.95)
        box('ground', (900, 900, 0.1), (0, 300, -0.05), yard)
        box('main', (8, 520, 0.02), (0, 240, 0.01), asphalt)
        for x in (-5, 5):
            box('walkM', (2, 520, 0.06), (x, 240, 0.03), walk)
        wall = [simple(f'wall{i}', c, 0.85) for i, c in enumerate(((0.11, 0.105, 0.10), (0.09, 0.09, 0.10), (0.12, 0.11, 0.095)))]
        roof = [simple(f'roof{i}', c, 0.8) for i, c in enumerate(((0.035, 0.035, 0.04), (0.05, 0.038, 0.032)))]
        dark = simple('dark', (0.01, 0.012, 0.015), 0.15)
        bark = simple('bark', (0.03, 0.025, 0.02), 0.9)
        leaf = simple('leaf', (0.015, 0.022, 0.015), 0.9)
        self.cands = []
        streets = (22, 85, 150, 225, 310, 410)
        for k, ys in enumerate(streets):
            box('cross', (520, 7, 0.02), (0, ys, 0.012), asphalt)
            for dy in (-4.5, 4.5):
                box('walkC', (520, 2, 0.06), (0, ys + dy, 0.03), walk)
            step = 11 if k < 4 else 13
            for side in (1, -1):                  # 1: lado de lá, de frente para a câmera
                d = 6.5
                yc = ys + side * (5.5 + 3.0 + d / 2)
                for xc in np.arange(11, 130 if k < 4 else 100, step):
                    for x in (xc, -xc):
                        w, h = 7.2 + 0.6 * rs.rand(), 3.4 + 0.6 * rs.rand()
                        wins = house((x, yc, 0), 0.0 if side == 1 else math.pi, w, d, h, wall[rs.randint(3)], roof[rs.randint(2)], dark)
                        box('drive', (2.6, 3.0, 0.04), (x + w / 4, ys + side * 7.0, 0.02), walk)
                        if side == 1 and k < 3:
                            self.cands.append(wins[rs.randint(2)])
            for x in np.arange(-6.8, 7, 13.6):      # árvores na calçada da rua principal
                for y in np.arange(ys + 14, ys + 60, 18):
                    if streets[-1] > y and all(abs(y - s_) > 10 for s_ in streets):
                        box('trunk', (0.3, 0.3, 2.4), (x, y, 1.2), bark)
                        ico('crown', 1.7 + 0.3 * rs.rand(), (x, y, 3.4), leaf, 2)
        for i, y in enumerate(range(10, 300, 34)):   # postes de sódio, alternando de lado
            x = -6.6 if i % 2 else 6.6
            box('pole', (0.18, 0.18, 6.0), (x, y, 3.0), bark)
            box('arm', (1.6, 0.14, 0.14), (x * 0.86, y, 6.0), bark)
            box('head', (0.6, 0.35, 0.12), (x * 0.74, y, 5.92), emission('sodium', (1.0, 0.6, 0.25), 6.0))
            point((x * 0.74, y, 5.6), 160.0, (1.0, 0.55, 0.2), 0.3)

    def __init__(self):
        reset(64)
        night_sky()
        cam = camera(CAM, TARGET, LENS, (0.1, 5000))
        bpy.context.view_layer.update()
        self.street_grid()
        bpy.context.view_layer.update()
        sc = bpy.context.scene
        def seen(o):                              # janela dentro do quadro e longe da borda
            p = world_to_camera_view(sc, cam, o.matrix_world.translation)
            return 0.1 < p.x < 0.9 and 0.12 < p.y < 0.62 and p.z > 0
        cands = [c for c in self.cands if seen(c)]
        pick = np.random.RandomState(7).choice(len(cands), LIT, replace=False)
        cam_at = Vector(CAM)                       # a mais próxima é a última: é a que fica acesa
        pick = sorted(pick, key=lambda c: -(cands[c].matrix_world.translation - cam_at).length)
        self.lit = []
        for i, c in enumerate(pick):
            m, val = window_mat(i)
            cands[c].data.materials[0] = m
            self.lit.append(val)
            lp = point(cands[c].matrix_world.translation + Vector((0, -1.5, 0)), 60.0, (1.0, 0.6, 0.3), 0.6)
            self.lit.append(lp)
        dh, dl = screen_dir(cam, *MOON_HI), screen_dir(cam, *MOON_LO)
        sphere('moon', MOON_R, Vector(CAM) + dh * MOON_DIST, moon_mat(False), 64, 32)
        self.lo = sphere('moon_lo', MOON_R, Vector(CAM) + dl * MOON_DIST, moon_mat(True), 64, 32)
        sun(0.22, tuple(dh), (0.72, 0.8, 1.0), 0.5)          # luar vindo da lua

    def windows(self, on):
        for k, flag in enumerate(on):
            self.lit[2 * k].default_value = 1.0 if flag else 0.0
            self.lit[2 * k + 1].data.energy = 60.0 if flag else 0.0


def build_v1():
    town = Town()
    def upd(t, u):
        town.windows([True] * LIT)
        return ('v1',)
    return upd


def build_v2():
    town = Town()
    town.lo.hide_render = True                    # a lua de baixo sumiu
    def upd(t, u):
        on = [True] * LIT
        for k, t0 in enumerate(TL.WINDOWS_OFF):
            if t >= t0:
                on[k] = False
        town.windows(on)
        return tuple(on)
    return upd
