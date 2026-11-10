"""Parquinho vazio ao entardecer, filmado de um tripé em VHS. O balanço do meio vai e volta sozinho; a sombra
dele na areia tem uma criança sentada, que só aparece na imagem durante o glitch."""
from lib import *
from nature import ground_mat, tree
import timeline as TL

SHOTS = {'a': 12.0}
HOLD_STATES = True              # cada frame tem um ângulo novo: o preview renderiza o movimento inteiro

TOP = 2.4                       # altura da barra do balanço
ROPE = 2.0                      # comprimento da corrente


def dusk_sky():
    w = bpy.context.scene.world; nt = w.node_tree; nt.nodes.clear()
    tc = n(nt, 'ShaderNodeTexCoord')
    sp = n(nt, 'ShaderNodeSeparateXYZ'); L(nt, tc.outputs['Generated'], sp.inputs[0])
    col = ramp(nt, [(0.0, (0.95, 0.55, 0.28)), (0.08, (0.85, 0.6, 0.45)), (0.3, (0.38, 0.42, 0.6)), (0.8, (0.12, 0.16, 0.32))],
               sp.outputs['Z']).outputs[0]
    b = n(nt, 'ShaderNodeBackground', Strength=0.4); L(nt, col, b.inputs['Color'])
    o = n(nt, 'ShaderNodeOutputWorld'); L(nt, b.outputs[0], o.inputs['Surface'])


def swing(x, steel, chain, seat):
    pivot = bpy.data.objects.new('pivot', None); link(pivot); pivot.location = (x, 0, TOP)
    for dx in (-0.22, 0.22):
        c = box('chain', (0.018, 0.018, ROPE), (dx, 0, -ROPE / 2), chain); c.parent = pivot
    s = box('seat', (0.5, 0.17, 0.03), (0, 0, -ROPE), seat); s.parent = pivot
    return pivot


def child(pivot):
    """criança sentada no balanço, de frente para a câmera; não aparece na imagem, só na sombra"""
    m = simple('kid', (0.02, 0.018, 0.02), 0.9)
    z = -ROPE + 0.02
    parts = []
    v, t = lathe([(0.0, 0.0), (0.13, 0.02), (0.12, 0.2), (0.14, 0.36), (0.07, 0.42), (0.0, 0.43)], 12)
    tor = fast_mesh('torso', v, t, m, True); tor.location = (0, 0.02, z); tor.scale = (1.0, 0.7, 1.0); parts.append(tor)
    hd = sphere('head', 0.1, (0, 0.02, z + 0.53), m, 24, 16); hd.scale = (0.95, 1.0, 1.1); parts.append(hd)
    for s_ in (-1, 1):
        parts.append(tube('leg', [(s_ * 0.07, 0.0, z + 0.04), (s_ * 0.08, -0.3, z + 0.05), (s_ * 0.08, -0.36, z - 0.28)],
                          [0.055, 0.045, 0.035], m))
        parts.append(tube('arm', [(s_ * 0.13, 0.02, z + 0.36), (s_ * 0.19, 0.0, z + 0.5), (s_ * 0.22, 0.0, z + 0.62)],
                          [0.035, 0.03, 0.025], m))
    for o in parts:
        o.parent = pivot
    return parts


def build_a():
    reset(48)
    dusk_sky()
    g = box('ground', (80, 80, 0.1), (0, 10, -0.05), ground_mat())
    sand = simple('sand', (0.55, 0.45, 0.33), 0.95)
    box('sand', (9.0, 6.5, 0.04), (1.0, -0.6, 0.0), sand)
    border = simple('border', (0.3, 0.2, 0.12), 0.8)
    box('borderF', (9.2, 0.15, 0.15), (1.0, -3.85, 0.05), border); box('borderB', (9.2, 0.15, 0.15), (1.0, 2.65, 0.05), border)
    box('borderL', (0.15, 6.5, 0.15), (-3.6, -0.6, 0.05), border); box('borderR', (0.15, 6.5, 0.15), (5.6, -0.6, 0.05), border)
    # estrutura do balanço: barra em cima e dois cavaletes em A
    steel = simple('steel', (0.18, 0.32, 0.5), 0.45, 0.6)
    tube('bar', [(-2.6, 0, TOP), (0, 0, TOP), (2.6, 0, TOP)], [0.05] * 3, steel, kind='POLY')
    for x in (-2.5, 2.5):
        for dy in (-0.9, 0.9):
            tube('leg', [(x, 0, TOP), (x, dy / 2, TOP / 2), (x * 1.04, dy, 0.0)], [0.045] * 3, steel, kind='POLY')
    chain = simple('chain', (0.5, 0.5, 0.48), 0.35, 0.9)
    seat = simple('seat', (0.08, 0.08, 0.08), 0.7)
    swings = [swing(x, steel, chain, seat) for x in (-1.55, 0.0, 1.55)]
    mid = swings[1]
    kid = child(mid)
    for o in kid:
        o.visible_camera = False
        o.visible_diffuse = False
        o.visible_glossy = False
    # escorregador ao fundo, à direita
    red = simple('slide', (0.55, 0.12, 0.08), 0.5)
    box('slide', (0.6, 3.2, 0.05), (6.4, 5.0, 0.85), red, rot=(math.radians(-32), 0, 0))
    box('ladder', (0.6, 0.08, 1.75), (6.4, 6.4, 0.87), steel)
    # cerca baixa e árvores
    wood = simple('fence', (0.42, 0.34, 0.26), 0.9)
    for x in np.arange(-12, 12.1, 1.5):
        box('post', (0.08, 0.08, 1.0), (x, 8.0, 0.5), wood)
    box('railA', (24, 0.05, 0.08), (0, 8.0, 0.8), wood); box('railB', (24, 0.05, 0.08), (0, 8.0, 0.4), wood)
    for i, (x, y, s) in enumerate([(-14, 26, 1.7), (-5.0, 30, 1.9), (5.0, 27, 1.6), (15, 29, 1.8), (-22, 31, 1.8)]):
        tree((x, y, 0), s, seed=i + 3)
    # sol baixo atrás e à esquerda: as sombras vêm pela areia em direção à câmera
    sun(6.0, (-0.35, 1.0, 0.5), (1.0, 0.68, 0.42), 0.6)
    camera((-1.0, -8.6, 3.2), (0.6, -1.2, 0.4), 30)

    def upd(t, u):
        a = math.radians(TL.SWING) * math.sin(2 * math.pi * t / TL.PERIOD)
        mid.rotation_euler.x = a
        seen = TL.SEEN[0] <= t < TL.SEEN[1]
        for o in kid:
            o.visible_camera = seen
        return (round(math.degrees(a), 2), seen)
    return upd
