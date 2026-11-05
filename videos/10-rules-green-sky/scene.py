"""Ilustrações do filme de segurança: a casa sob o céu verde, a sala com o rádio, a porta e a sala sem teto."""
from lib import *
import timeline as TL

SHOTS = {s[0]: s[1] for s in TL.SHOTS if not TL.MODELO.drawn(TL, s[0])}
HOLD_STATES = True


def still():
    def upd(t, u):
        return ('still',)
    return upd


def green_sky(night=False):
    """Céu verde doente, com nuvens finas."""
    w = bpy.context.scene.world; nt = w.node_tree; nt.nodes.clear()
    tc = n(nt, 'ShaderNodeTexCoord')
    sp = n(nt, 'ShaderNodeSeparateXYZ'); L(nt, tc.outputs['Generated'], sp.inputs[0])
    k = 0.35 if night else 1.0
    g = ramp(nt, [(0.0, (0.42 * k, 0.55 * k, 0.22 * k)), (0.15, (0.22 * k, 0.40 * k, 0.16 * k)), (0.7, (0.05 * k, 0.14 * k, 0.07 * k))], sp.outputs['Z']).outputs[0]
    z = math_(nt, 'MAXIMUM', sp.outputs['Z'], 0.05)
    cv = n(nt, 'ShaderNodeCombineXYZ')
    L(nt, math_(nt, 'DIVIDE', sp.outputs['X'], z), cv.inputs['X']); L(nt, math_(nt, 'DIVIDE', sp.outputs['Y'], z), cv.inputs['Y'])
    nz = n(nt, 'ShaderNodeTexNoise', Scale=0.6, Detail=8.0, Roughness=0.6); L(nt, cv.outputs[0], nz.inputs['Vector'])
    cl = ramp(nt, [(0.5, (0, 0, 0)), (0.7, (0.6, 0.6, 0.6))], nz.outputs['Fac']).outputs[0]
    col = mix(nt, cl, g, (0.55 * k, 0.68 * k, 0.35 * k))
    b = n(nt, 'ShaderNodeBackground', Strength=1.0); L(nt, col, b.inputs['Color'])
    o = n(nt, 'ShaderNodeOutputWorld'); L(nt, b.outputs[0], o.inputs['Surface'])


def lit_mat(name='lit', strength=4.0):
    return emission(name, (1.0, 0.72, 0.4), strength)


def house(lit=True):
    """Casa de dois andares com 3 janelas embaixo e 4 em cima. Devolve a janela a mais, no telhado, escondida."""
    wall = simple('siding', (0.62, 0.58, 0.50), 0.85)
    trim = simple('trim', (0.85, 0.84, 0.80), 0.7)
    roof = simple('roof', (0.18, 0.15, 0.14), 0.8)
    win = lit_mat() if lit else simple('glass', (0.02, 0.03, 0.03), 0.2)
    box('body', (10, 7, 6), (0, 0, 3), wall)
    v = [(-5.4, -3.9, 6), (5.4, -3.9, 6), (5.4, 3.9, 6), (-5.4, 3.9, 6), (-5.4, 0, 8.6), (5.4, 0, 8.6)]
    mesh_from('roof', v, [(0, 1, 5, 4), (2, 3, 4, 5), (0, 4, 3), (1, 2, 5)], roof)
    for x in (-3.4, 3.4, 1.4):                      # térreo, com a porta em -1
        box('win', (1.2, 0.1, 1.5), (x, -3.52, 2.0), win)
        box('frame', (1.4, 0.06, 1.7), (x, -3.5, 2.0), trim)
    box('door', (1.1, 0.12, 2.2), (-1.0, -3.52, 1.1), simple('doorm', (0.25, 0.08, 0.06), 0.6))
    for x in (-3.6, -1.2, 1.2, 3.6):                 # primeiro andar
        box('win', (1.1, 0.1, 1.3), (x, -3.52, 4.6), win)
        box('frame', (1.3, 0.06, 1.5), (x, -3.5, 4.6), trim)
    slope = math.atan2(2.6, 3.9)                      # janela deitada no telhado, onde não pode haver janela
    e = box('win_extra', (1.0, 0.05, 0.9), (0.6, -2.03, 7.32), win, (-(math.pi / 2 - slope), 0, 0))
    e.hide_render = True
    box('lawn', (200, 200, 0.1), (0, 0, -0.05), simple('lawn', (0.12, 0.2, 0.08), 0.95))
    box('walk', (1.2, 8, 0.06), (-1.0, -7.5, 0.0), simple('conc', (0.5, 0.5, 0.47), 0.9))
    for x in np.arange(-14, 15, 1.0):               # cerca
        if abs(x + 1) > 1:
            box('picket', (0.12, 0.08, 1.0), (x, -11.5, 0.5), trim)
    box('rail', (28, 0.06, 0.12), (0, -11.5, 0.75), trim)
    return e


def build_r1a():
    reset(48); green_sky()
    house(lit=True)
    sun(1.2, (-0.6, -0.8, 0.25), (0.75, 0.95, 0.55), 3.0)
    camera((3, -24, 3.2), (0, 0, 4.0), 32)
    return still()


def build_r3a():
    reset(48); green_sky(night=True)
    extra = house(lit=True)
    sun(0.3, (-0.6, -0.8, 0.25), (0.6, 0.85, 0.5), 3.0)
    camera((0, -20, 4.5), (0, 0, 4.0), 35)
    def upd(t, u):
        on = t >= TL.EXTRA_WINDOW
        extra.hide_render = not on
        return on
    return upd


def room(ceiling=True):
    """Sala dos anos 70: carpete, papel de parede, sofá, mesinha com rádio, abajur e uma janela verde."""
    floor = simple('carpet', (0.32, 0.22, 0.14), 0.95)
    wall = simple('paper', (0.62, 0.55, 0.40), 0.9)
    box('floor', (8, 8, 0.1), (0, 0, -0.05), floor)
    box('wallN', (8, 0.1, 2.8), (0, 4, 1.4), wall); box('wallW', (0.1, 8, 2.8), (-4, 0, 1.4), wall)
    box('wallE', (0.1, 8, 2.8), (4, 0, 1.4), wall)
    if ceiling:
        box('ceil', (8, 8, 0.1), (0, 0, 2.85), simple('ceil', (0.75, 0.72, 0.65), 0.9))
    box('window', (1.6, 0.05, 1.1), (1.8, 3.96, 1.6), emission('outside', (0.35, 0.6, 0.25), 1.6))
    box('wframe', (1.8, 0.04, 1.3), (1.8, 3.98, 1.6), simple('wf', (0.85, 0.84, 0.8), 0.7))
    sofa = simple('sofa', (0.45, 0.30, 0.12), 0.9)
    box('seat', (2.6, 0.9, 0.45), (-1.2, 3.2, 0.25), sofa); box('back', (2.6, 0.25, 0.9), (-1.2, 3.65, 0.6), sofa)
    for x in (-2.6, 0.2):
        box('armrest', (0.25, 0.9, 0.65), (x, 3.2, 0.35), sofa)
    wood = simple('wood', (0.28, 0.16, 0.08), 0.5)
    box('table', (0.8, 0.6, 0.06), (1.0, 2.2, 0.62), wood)
    for dx in (-0.35, 0.35):
        for dy in (-0.25, 0.25):
            box('leg', (0.05, 0.05, 0.6), (1.0 + dx, 2.2 + dy, 0.3), wood)
    box('radio', (0.5, 0.22, 0.3), (1.0, 2.2, 0.8), simple('bakelite', (0.35, 0.18, 0.08), 0.35))
    box('grille', (0.22, 0.01, 0.2), (0.9, 2.085, 0.8), simple('cloth', (0.75, 0.65, 0.45), 0.95))
    box('dial', (0.12, 0.01, 0.08), (1.15, 2.085, 0.82), emission('dialm', (1.0, 0.75, 0.35), 3.0))
    box('lampbase', (0.12, 0.12, 0.5), (-3.2, 3.3, 0.25), wood)
    box('shade', (0.45, 0.45, 0.35), (-3.2, 3.3, 0.7), emission('shadem', (1.0, 0.8, 0.5), 1.5))
    point((-3.2, 3.0, 0.9), 60.0, (1.0, 0.75, 0.45), 0.4)


def build_r2a():
    reset(48); world_flat((0.1, 0.16, 0.08), 0.6)
    room(ceiling=True)
    point((1.0, 1.0, 2.4), 25.0, (1.0, 0.85, 0.6), 0.6)
    camera((2.6, -0.6, 1.4), (1.0, 2.2, 0.8), 35)
    return still()


def build_r4a():
    """Hall de entrada: a porta da frente vista de dentro, com o vidro verde."""
    reset(48); world_flat((0.1, 0.16, 0.08), 0.6)
    wall = simple('paper', (0.62, 0.55, 0.40), 0.9)
    box('floor', (3, 6, 0.1), (0, 0, -0.05), simple('wood', (0.30, 0.18, 0.09), 0.5))
    box('wallL', (0.1, 6, 2.8), (-1.5, 0, 1.4), wall); box('wallR', (0.1, 6, 2.8), (1.5, 0, 1.4), wall)
    box('ceil', (3, 6, 0.1), (0, 0, 2.85), simple('ceil', (0.75, 0.72, 0.65), 0.9))
    box('wallF', (3, 0.1, 2.8), (0, 3, 1.4), wall)
    box('door', (1.0, 0.08, 2.1), (0, 2.94, 1.05), simple('doorm', (0.42, 0.24, 0.12), 0.55))
    box('pane', (0.35, 0.02, 0.35), (0, 2.89, 1.65), emission('outside', (0.35, 0.6, 0.25), 1.4))
    box('knob', (0.06, 0.05, 0.06), (0.38, 2.88, 1.0), simple('brass', (0.8, 0.6, 0.25), 0.3, 0.9))
    box('mat', (0.9, 0.6, 0.02), (0, 2.4, 0.01), simple('matm', (0.35, 0.12, 0.08), 0.95))
    box('rack', (0.06, 0.06, 1.8), (-1.2, 2.5, 0.9), simple('wood2', (0.25, 0.14, 0.07), 0.5))
    box('coat', (0.35, 0.25, 0.9), (-1.2, 2.5, 1.2), simple('coatm', (0.2, 0.22, 0.26), 0.95))
    point((0, 0.5, 2.6), 30.0, (1.0, 0.82, 0.55), 0.3)
    camera((0.2, -1.8, 1.55), (0, 3, 1.25), 30)
    return still()


def build_r5a():
    """A mesma sala, sem teto: o céu verde em cima."""
    reset(48); green_sky()
    room(ceiling=False)
    sun(1.0, (-0.3, -0.5, 1.0), (0.7, 0.95, 0.55), 3.0)
    camera((2.6, -0.6, 1.4), (0.2, 3.0, 2.6), 30)
    return still()
