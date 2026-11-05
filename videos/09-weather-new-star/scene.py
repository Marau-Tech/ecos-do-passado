"""Mapa do condado visto de cima e a câmera do céu da emissora, com a estrela nova."""
from lib import *
import timeline as TL

SHOTS = {s[0]: s[1] for s in TL.SHOTS if not TL.MODELO.drawn(TL, s[0])}
HOLD_STATES = True              # tudo parado: um render por take


def still():
    def upd(t, u):
        return ('still',)
    return upd


def map_mat():
    """Relevo de mapa de TV: verde nas baixadas, marrom e bege nos morros, por altura."""
    m, nt = mat('map')
    z = n(nt, 'ShaderNodeSeparateXYZ'); L(nt, n(nt, 'ShaderNodeNewGeometry').outputs['Position'], z.inputs[0])
    col = ramp(nt, [(0.0, (0.14, 0.34, 0.10)), (0.25, (0.24, 0.42, 0.13)), (0.5, (0.45, 0.42, 0.20)),
                    (0.75, (0.55, 0.42, 0.26)), (1.0, (0.85, 0.80, 0.70))], math_(nt, 'DIVIDE', z.outputs['Z'], 12.0)).outputs[0]
    out(nt, principled(nt, col, 0.9, spec=0.1).outputs[0])
    return m


def county():
    reset(32)
    world_flat((0.02, 0.03, 0.06), 1.0)
    def h(x, y):
        hills = 14 * fbm(x * 0.025 + 3, y * 0.025 + 1, 6) ** 2.2
        river = 3.5 * np.exp(-((x - 18 * np.sin(y * 0.045) - 8) / 2.2) ** 2)
        lake = 4.0 * np.exp(-(((x + 38) / 9) ** 2 + ((y - 22) / 6) ** 2))
        return hills - river - lake + 0.6
    grid_mesh('land', 160, 400, h, map_mat())
    box('water', (160, 160, 0.05), (0, 0, 0.3), simple('water', (0.05, 0.16, 0.45), 0.2))
    sun(3.2, (-0.7, -0.2, 0.55), angle=2.0)          # luz de lado: o relevo aparece
    world_flat((0.35, 0.4, 0.5), 0.35)
    camera((0, -18, 85), (0, 2, 0), 35, (0.5, 1000))


def build_map1():
    county(); return still()


def build_map2():
    county(); return still()


def build_map3():
    county(); return still()


def night_sky():
    w = bpy.context.scene.world; nt = w.node_tree; nt.nodes.clear()
    tc = n(nt, 'ShaderNodeTexCoord')
    v = n(nt, 'ShaderNodeTexVoronoi', Scale=70.0); L(nt, tc.outputs['Generated'], v.inputs['Vector'])
    sc = n(nt, 'ShaderNodeSeparateColor'); L(nt, v.outputs['Color'], sc.inputs[0])
    star = math_(nt, 'MULTIPLY', math_(nt, 'MULTIPLY', math_(nt, 'LESS_THAN', v.outputs['Distance'], 0.07),
                                       math_(nt, 'GREATER_THAN', sc.outputs[0], 0.78)), math_(nt, 'POWER', sc.outputs[1], 3.0))
    sp = n(nt, 'ShaderNodeSeparateXYZ'); L(nt, tc.outputs['Generated'], sp.inputs[0])
    sky = ramp(nt, [(0.0, (0.06, 0.07, 0.11)), (0.08, (0.025, 0.035, 0.08)), (0.4, (0.006, 0.01, 0.03))], sp.outputs['Z']).outputs[0]
    col = mix(nt, 1.0, sky, math_(nt, 'MULTIPLY', star, 1.8), 'ADD', clamp=False)
    b = n(nt, 'ShaderNodeBackground', Strength=1.0); L(nt, col, b.inputs['Color'])
    o = n(nt, 'ShaderNodeOutputWorld'); L(nt, b.outputs[0], o.inputs['Surface'])


def glow(r, loc, color, strength):
    """Halo em volta da estrela: forte no centro, some na borda."""
    m, nt = mat('glow')
    lw = n(nt, 'ShaderNodeLayerWeight', Blend=0.5)
    a = math_(nt, 'POWER', math_(nt, 'SUBTRACT', 1.0, lw.outputs['Facing']), 3.0)
    e = n(nt, 'ShaderNodeEmission', Strength=strength); e.inputs['Color'].default_value = (*color, 1)
    tr = n(nt, 'ShaderNodeBsdfTransparent')
    ms = n(nt, 'ShaderNodeMixShader')
    L(nt, a, ms.inputs[0]); L(nt, tr.outputs[0], ms.inputs[1]); L(nt, e.outputs[0], ms.inputs[2])
    out(nt, ms.outputs[0])
    return sphere('glow', r, loc, m, 48, 24)


def skycam(star_at, star_r):
    """Morro escuro, a cidade embaixo com luzes, e a estrela nova a leste."""
    reset(64)
    night_sky()
    def h(x, y):
        return 14 * fbm(x * 0.012, y * 0.012 + 5, 4) - 4 + 0.0004 * (y - 80) ** 2
    grid_mesh('hills', 900, 300, h, simple('hill', (0.012, 0.014, 0.012), 0.95), (0, 400))
    rs = np.random.RandomState(3)
    lamp = emission('town', (1.0, 0.72, 0.38), 9.0)
    for i in range(160):                                  # luzes da cidade no vale
        x, y = rs.uniform(-140, 140), rs.uniform(90, 180)
        ico('light', 0.25 + 0.2 * rs.rand(), (x, y, h(np.array(x), np.array(y)) + 0.4), lamp, 1)
    sun(0.04, (0.3, 1, 0.4), (0.7, 0.8, 1.0))
    camera((0, -40, 22), (10, 200, 30), 30, (0.5, 5000))


def screen_dir(cam, sx, sy, lens):
    """Direção no mundo do ponto (sx, sy) da tela, de -1 a 1."""
    hw = 18 / lens
    return (cam.matrix_world.to_3x3() @ Vector((sx * hw, sy * hw * 0.75, -1))).normalized()


def place_star(sx, sy, dist, r):
    cam = bpy.context.scene.camera
    bpy.context.view_layer.update()
    at = Vector(cam.location) + screen_dir(cam, sx, sy, 30) * dist
    ico('star', r, at, emission('starm', (1.0, 0.97, 0.92), 30.0), 3)
    glow(r * 6, at, (0.85, 0.9, 1.0), 2.5)


def build_sky1():
    skycam(None, 0); place_star(0.55, 0.8, 900, 2.6); return still()          # alta e pequena


def build_sky2():
    skycam(None, 0); place_star(0.08, 0.56, 300, 7.0); return still()         # maior, logo acima do morro
