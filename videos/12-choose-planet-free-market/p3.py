"""THE NOON: chão branco liso sem fim, nenhuma sombra, e um sol que fica sempre em cima de você."""
from lib import *
from planets import *

SHOTS = {'p3a': 6.0, 'p3b': 3.75, 'p3c': 3.5, 'p3d': 4.0}


def build_p3a():
    def extra():
        ico('sundisc', 0.3, (-1.75, -0.4, 1.15), emission('sunm', (1.0, 0.97, 0.88), 25.0), 3)
        glow(1.1, (-1.75, -0.4, 1.15), (1.0, 0.95, 0.8), 3.0)
    upd = orbit(planet_noon, (1.0, 0.95, 0.85), (-1.75, -0.4, 1.15), extra=extra)      # o sol na frente: o planeta brilha
    return lambda t, u: upd(t, u, SHOTS['p3a'])


def blank():
    """Chão branco com rachaduras quase invisíveis (só para o movimento aparecer) e céu estourado."""
    reset(16)
    w = bpy.context.scene.world; nt = w.node_tree; nt.nodes.clear()
    tc = n(nt, 'ShaderNodeTexCoord')
    sp = n(nt, 'ShaderNodeSeparateXYZ'); L(nt, tc.outputs['Generated'], sp.inputs[0])
    g = ramp(nt, [(0.0, (1.0, 0.98, 0.93)), (0.3, (0.85, 0.9, 0.95)), (1.0, (0.7, 0.8, 0.92))], sp.outputs['Z']).outputs[0]
    b = n(nt, 'ShaderNodeBackground', Strength=0.9); L(nt, g, b.inputs['Color'])
    o = n(nt, 'ShaderNodeOutputWorld'); L(nt, b.outputs[0], o.inputs['Surface'])
    m, nt = mat('ground')
    pos = n(nt, 'ShaderNodeNewGeometry').outputs['Position']
    v = n(nt, 'ShaderNodeTexVoronoi', {'feature': 'DISTANCE_TO_EDGE'}, Scale=0.35); L(nt, pos, v.inputs['Vector'])
    col = mix(nt, math_(nt, 'LESS_THAN', v.outputs['Distance'], 0.02), (0.82, 0.8, 0.76), (0.55, 0.52, 0.48))
    out(nt, principled(nt, col, 0.7, spec=0.2).outputs[0])
    box('ground', (4000, 4000, 0.1), (0, 0, -0.05), m)
    sun(2.6, (0, 0, 1), (1.0, 0.97, 0.9), 2.0)        # a pino: nada faz sombra para o lado


def sun_disc(loc, r):
    ico('sundisc', r, loc, emission('sunm', (1.0, 0.98, 0.92), 30.0), 3)
    glow(r * 4, loc, (1.0, 0.95, 0.8), 4.0)


def build_p3b():
    blank()
    cam = camera((0, 0, 1.7), (0, 50, 1.2), 32)
    def update(t, u):
        cam.location = (0, 0.8 * t, 1.7)
        look(cam, (0.2 * u, 0.8 * t + 50, 1.2))
    return update


def build_p3c():
    blank()
    sun_disc((0, 4, 400), 22)
    cam = camera((0, 0, 1.7), (0, 50, 1.7), 30)
    def update(t, u):
        a = ease(u) * math.radians(84)                 # do horizonte até quase a pino
        look(cam, (0, math.cos(a) * 50, 1.7 + math.sin(a) * 50))
    return update


def build_p3d():
    blank()
    cam = camera((0, 0, 1.7), (0, 50, 30), 30)
    sd = bpy.data.objects.new('sun_rig', None); link(sd)
    ico('sundisc', 9, (0, 120, 140), emission('sunm', (1.0, 0.98, 0.92), 30.0), 3).parent = sd
    glow(36, (0, 120, 140), (1.0, 0.95, 0.8), 4.0).parent = sd
    def update(t, u):
        y = 6.0 * t                                    # andando rápido
        cam.location = (0, y, 1.7 + 0.04 * abs(math.sin(t * 7)))
        look(cam, (0, y + 50, 26))
        sd.location = (0, y, 0)                        # o sol vem junto
    return update
