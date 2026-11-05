"""Imagens da VESPER-2: Planet Nine de longe até a superfície, e a própria sonda vista de cima.
Cada take é uma imagem parada: um render só."""
from lib import *
import timeline as TL

SHOTS = {s[0]: s[1] for s in TL.SHOTS if not TL.MODELO.drawn(TL, s[0])}
HOLD_STATES = True
SUN = Vector((-0.55, 0.45, 0.25)).normalized()       # sol baixo, para sombras longas na superfície
GRID = 3.2, 9.0                                      # espaçamento das fileiras: entre fileiras, dentro da fileira
SUN5 = Vector((-0.88, 0.12, 0.46)).normalized()      # i5: sombras de 6 m ao longo da fileira, sem encostar na próxima


def still():
    def upd(t, u):
        return ('still',)
    return upd


def space():
    world_space(nebula=(0, 0, 0), neb_strength=1.0, star=0.25)


def ice_mat(name, scale=1.0, crater=1.0):
    """Gelo cinza com manchas, crateras e relevo fino."""
    m, nt = mat(name)
    tc = n(nt, 'ShaderNodeTexCoord').outputs['Object']
    a = n(nt, 'ShaderNodeTexNoise', Scale=2.2 * scale, Detail=9.0, Roughness=0.6); L(nt, tc, a.inputs['Vector'])
    col = ramp(nt, [(0.35, (0.34, 0.35, 0.36)), (0.66, (0.78, 0.79, 0.80))], a.outputs['Fac']).outputs[0]
    for k, sc_ in enumerate((7.0, 19.0)):          # crateras soltas, de dois tamanhos
        v = n(nt, 'ShaderNodeTexVoronoi', {'distance': 'EUCLIDEAN'}, Scale=sc_ * scale * crater, Randomness=1.0)
        L(nt, tc, v.inputs['Vector'])
        pit = ramp(nt, [(0.0, (0.62, 0.62, 0.62)), (0.07, (0.9, 0.9, 0.9)), (0.09, (1.15, 1.15, 1.15)), (0.13, (1, 1, 1))], v.outputs['Distance']).outputs[0]
        col = mix(nt, 1.0, col, pit, 'MULTIPLY', clamp=False)
    m2 = n(nt, 'ShaderNodeTexNoise', Scale=0.9 * scale, Detail=3.0, Roughness=0.5); L(nt, tc, m2.inputs['Vector'])
    col = mix(nt, ramp(nt, [(0.45, (0, 0, 0)), (0.6, (1, 1, 1))], m2.outputs['Fac']).outputs[0], col,
              mix(nt, 1.0, col, (0.7, 0.7, 0.72), 'MULTIPLY'))                # mares mais escuros
    f = n(nt, 'ShaderNodeTexNoise', Scale=60.0 * scale, Detail=6.0, Roughness=0.65); L(nt, tc, f.inputs['Vector'])
    bp = n(nt, 'ShaderNodeBump', Strength=0.35, Distance=0.02); L(nt, f.outputs['Fac'], bp.inputs['Height'])
    out(nt, principled(nt, col, 0.75, spec=0.3, normal=bp.outputs[0]).outputs[0])
    return m


def dots_mat(name, k, r, box_, base=(0.62, 0.63, 0.64)):
    """Planície de gelo com uma grade regular de pontos escuros dentro do retângulo box_ (x0, y0, x1, y1).
    k é quantos pontos por unidade e r o raio de cada ponto, de 0 a 0.5."""
    m, nt = mat(name)
    pos = n(nt, 'ShaderNodeNewGeometry').outputs['Position']
    nz = n(nt, 'ShaderNodeTexNoise', Scale=0.02 / k * 40, Detail=8.0, Roughness=0.6); L(nt, pos, nz.inputs['Vector'])
    col = ramp(nt, [(0.35, tuple(c * 0.7 for c in base)), (0.65, base)], nz.outputs['Fac']).outputs[0]
    sc = n(nt, 'ShaderNodeVectorMath', {'operation': 'SCALE'}); L(nt, pos, sc.inputs[0]); sc.inputs['Scale'].default_value = k
    fr = n(nt, 'ShaderNodeVectorMath', {'operation': 'FRACTION'}); L(nt, sc.outputs[0], fr.inputs[0])
    sub = n(nt, 'ShaderNodeVectorMath', {'operation': 'SUBTRACT'}); L(nt, fr.outputs[0], sub.inputs[0]); sub.inputs[1].default_value = (0.5, 0.5, 0.0)
    sp = n(nt, 'ShaderNodeSeparateXYZ'); L(nt, sub.outputs[0], sp.inputs[0])
    d = math_(nt, 'ADD', math_(nt, 'POWER', sp.outputs['X'], 2.0), math_(nt, 'POWER', sp.outputs['Y'], 2.0))
    dot = math_(nt, 'LESS_THAN', d, r * r)
    ps = n(nt, 'ShaderNodeSeparateXYZ'); L(nt, pos, ps.inputs[0])
    x0, y0, x1, y1 = box_
    inside = math_(nt, 'MULTIPLY',
                   math_(nt, 'MULTIPLY', math_(nt, 'GREATER_THAN', ps.outputs['X'], x0), math_(nt, 'LESS_THAN', ps.outputs['X'], x1)),
                   math_(nt, 'MULTIPLY', math_(nt, 'GREATER_THAN', ps.outputs['Y'], y0), math_(nt, 'LESS_THAN', ps.outputs['Y'], y1)))
    col = mix(nt, math_(nt, 'MULTIPLY', dot, inside), col, (0.05, 0.05, 0.05))
    out(nt, principled(nt, col, 0.8, spec=0.25).outputs[0])
    return m


# ---- i1: o planeta inteiro ----
def build_i1():
    reset(64); space()
    sphere('p9', 1.0, (0, 0, 0), ice_mat('ice'), 192, 96)
    atmosphere(1.0, (0.85, 0.88, 0.92), (1, -0.25, 0.3), 1.02, 4.0, 0.35)
    sun(4.0, (1, -0.25, 0.3), angle=0.5)
    camera((0, -4.2, 0), (0, 0, 0), 35)
    return still()


# ---- i2: a borda, com névoa ----
def build_i2():
    reset(64); space()
    p = sphere('p9', 1.0, (0, 0, 0), ice_mat('ice', 3.0, 1.4), 256, 128)
    atmosphere(1.0, (0.85, 0.88, 0.92), (1, -0.4, 0.5), 1.01, 3.5, 0.5)
    sun(4.0, (1, -0.4, 0.5), angle=0.5)
    camera((0.0, -1.55, 0.25), (0.15, 0, 0.92), 35)
    return still()


# ---- i3: superfície oblíqua, cordilheira e planície ----
def build_i3():
    reset(64); space()
    def h(x, y):
        ridge = 1 - np.abs(fbm(x * 0.01, y * 0.01, 6) * 2 - 1)
        band = np.exp(-((x + 0.35 * y + 60) / 75) ** 2)                 # a cordilheira corta em diagonal
        return 26 * ridge ** 2 * band + 6 * fbm(x * 0.02, y * 0.02, 5) * band + 1.5 * fbm(x * 0.06, y * 0.06, 4)
    grid_mesh('terrain', 420, 420, h, ice_mat('ice', 0.02, 1.0), (0, 120))
    sun(5.0, tuple(SUN), angle=0.4)
    camera((0, -150, 70), (10, 90, 0), 32, (0.5, 5000))
    return still()


# ---- i4: a planície de cima, com a grade de pontos ----
def build_i4():
    reset(48); space()
    m = dots_mat('plain', 0.5, 0.16, (-14, -22, 18, 6))
    box('plain', (600, 600, 0.1), (0, 0, 0), m)
    sun(5.0, tuple(SUN), angle=0.4)
    camera((0, -0.01, 120), (0, 0, 0), 35, (0.5, 5000))
    return still()


def figure_field(cx, cy, w, h, odd, s=1.6):
    """Fileiras de figuras em pé, numa malha só. A figura mais perto de odd sai separada,
    sem sombra de verdade, e ganha a sombra virada ao contrário."""
    v, t = lathe(FIG, 10)
    xs = np.arange(cx - w / 2, cx + w / 2, GRID[1])
    ys = np.arange(cy - h / 2, cy + h / 2, GRID[0])
    pos = np.array([(x + (j % 2) * GRID[1] / 2, y, 0) for j, y in enumerate(ys) for x in xs], np.float32)
    k = int(np.argmin(((pos[:, :2] - np.asarray(odd)) ** 2).sum(1)))
    m = simple('fig', (0.02, 0.02, 0.022), 0.9)
    scatter('rows', v, t, np.delete(pos, k, 0), scale=np.full(len(pos) - 1, s), m=m)
    one = scatter('odd', v, t, pos[k:k + 1], scale=np.full(1, s), m=m)
    one.visible_shadow = False
    wrong_shadow(tuple(pos[k]), s)


def wrong_shadow(loc, s=1.6):
    """Uma sombra com forma de gente no chão, virada para o lado contrário das outras."""
    v, t = lathe(FIG, 10)
    v = np.asarray(v, np.float32) * s
    d = Vector((SUN5.x, SUN5.y, 0)).normalized()      # as sombras de verdade vão para -d; esta vai para +d
    L_ = 1 / math.tan(math.asin(SUN5.z))
    side = Vector((-d.y, d.x, 0))
    pts = [Vector(loc) + d * (float(p[2]) * L_) + side * float(p[0]) + Vector((0, 0, 0.02 + float(p[1]) * 0.001)) for p in v]
    return fast_mesh('wrong', [tuple(p) for p in pts], t, simple('shadow', (0.035, 0.035, 0.04), 1.0))


# ---- i5: as fileiras de perto, sombras longas ----
def build_i5():
    reset(64); space()
    box('plain', (400, 400, 0.1), (0, 0, -0.05), ice_mat('plain', 0.03, 0.6))
    figure_field(0, 0, 130, 110, (4, 6))
    sun(7.0, tuple(SUN5), angle=0.3)
    camera((2, -20, 36), (0, 6, 0), 35, (0.5, 5000))
    return still()


def probe(loc=(0, 0, 0)):
    """VESPER-2: corpo, antena parabólica para cima (para a Terra), dois painéis, braço do RTG e do magnetômetro."""
    root = bpy.data.objects.new('vesper', None); link(root)
    foil = simple('foil', (0.72, 0.72, 0.7), 0.35, metal=0.6)
    white = simple('white', (0.85, 0.85, 0.84), 0.5)
    cell = simple('cell', (0.05, 0.06, 0.08), 0.25, metal=0.3)
    frame = simple('frame', (0.5, 0.5, 0.5), 0.5, metal=0.7)
    parts = [box('body', (1.4, 1.4, 1.0), (0, 0, 0), foil)]
    v, t = lathe([(0.0, 0.5), (0.5, 0.54), (0.95, 0.64), (1.3, 0.8), (1.32, 0.82)], 40)
    parts.append(fast_mesh('dish', v, t, white, True))
    parts.append(box('engine', (0.5, 0.5, 0.35), (0, 0, -0.65), frame))      # motor, embaixo
    parts.append(box('cam', (0.3, 0.3, 0.4), (0.45, -0.45, -0.6), white))     # a câmera da sonda, que aponta para o chão
    for s_ in (-1, 1):
        parts.append(box('arm', (1.2, 0.1, 0.1), (s_ * 1.3, 0, 0), frame))
        for i in range(3):
            parts.append(box('panel', (1.25, 1.5, 0.04), (s_ * (2.6 + i * 1.32), 0, 0), cell))
            parts.append(box('rib', (0.04, 1.52, 0.06), (s_ * (1.97 + i * 1.32), 0, 0), frame))
    parts.append(box('rtg_arm', (0.08, 3.2, 0.08), (0, -2.2, -0.2), frame))
    parts.append(box('rtg', (0.45, 0.9, 0.45), (0, -3.9, -0.2), white))
    parts.append(box('mag', (0.04, 0.04, 6.0), (0.5, 0.6, -3.4), frame))
    for o in parts:
        o.parent = root
    root.location = loc; root.rotation_euler = (0, 0, 0.35)
    return root


def earth_mat():
    """Terra azul clara: oceano, pouca terra e poucas nuvens. É a única cor do vídeo (GRADE i6)."""
    m, nt = mat('earth')
    tc = n(nt, 'ShaderNodeTexCoord').outputs['Object']
    a = n(nt, 'ShaderNodeTexNoise', Scale=2.2, Detail=8.0, Roughness=0.55); L(nt, tc, a.inputs['Vector'])
    col = mix(nt, math_(nt, 'GREATER_THAN', a.outputs['Fac'], 0.6), (0.22, 0.5, 0.95), (0.35, 0.55, 0.65))
    c = n(nt, 'ShaderNodeTexNoise', Scale=4.5, Detail=8.0, Roughness=0.6); L(nt, tc, c.inputs['Vector'])
    col = mix(nt, ramp(nt, [(0.58, (0, 0, 0)), (0.7, (0.8, 0.8, 0.8))], c.outputs['Fac']).outputs[0], col, (0.9, 0.94, 1.0))
    out(nt, principled(nt, col, 0.6).outputs[0])
    return m


def screen_dir(cam, sx, sy, lens):
    """Direção no mundo do ponto (sx, sy) da tela, de -1 a 1."""
    hw = 18 / lens
    return (cam.matrix_world.to_3x3() @ Vector((sx * hw, sy * hw * 0.75, -1))).normalized()


# ---- i6: a própria sonda, vista de baixo, da superfície, com a Terra ao fundo ----
def build_i6():
    reset(80); space()
    probe((0, 0, 0))
    lens = 40
    cam = camera((2.2, -3.6, -13.5), (0, 0, 0), lens, (0.5, 5000))
    bpy.context.view_layer.update()
    sun_dir = (0.55, -0.35, -0.75)                    # sol baixo, do lado da câmera: a barriga da sonda fica acesa
    d = screen_dir(cam, 0.48, 0.52, lens)
    sphere('earth', 12, Vector(cam.location) + d * 600, earth_mat(), 96, 48)
    atmosphere(12, (0.45, 0.7, 1.0), sun_dir, 1.04, 3.0, 1.2, tuple(Vector(cam.location) + d * 600))
    sun(5.0, sun_dir, angle=0.3)
    return still()
