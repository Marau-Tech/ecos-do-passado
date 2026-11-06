"""THE NEON: a cidade de uma espécie extinta, ainda ligada. Máquinas cheias de comida e água."""
from lib import *
from planets import *
import timeline as TL

SHOTS = {'p2a': 6.0, 'p2b': 3.75, 'p2c': 3.5, 'p2d': 4.0}
GLYPHS = '◈⌬◇◬⌘⊛⋔⨀'                  # só os que a DejaVu Sans Bold tem
NEON = ((1.0, 0.1, 0.7), (0.1, 0.9, 1.0), (0.7, 0.2, 1.0), (1.0, 0.6, 0.1))


def build_p2a():
    upd = orbit(planet_neon, (0.9, 0.3, 1.0), (-1.0, -0.25, 0.25))
    return lambda t, u: upd(t, u, SHOTS['p2a'])


def tower_mat():
    """Prédio escuro com janelas acesas em grade."""
    m, nt = mat('tower')
    tc = n(nt, 'ShaderNodeTexCoord').outputs['Object']
    b = n(nt, 'ShaderNodeTexBrick', Scale=1.2, Mortar_Size=0.25, Brick_Width=0.4, Row_Height=0.5); L(nt, tc, b.inputs['Vector'])
    b.inputs['Color1'].default_value = (1.0, 0.7, 0.9, 1); b.inputs['Color2'].default_value = (0.02, 0.02, 0.03, 1)
    b.inputs['Mortar'].default_value = (0, 0, 0, 1)
    out(nt, principled(nt, (0.03, 0.03, 0.04), 0.4, emis=b.outputs['Color'], emis_str=0.6).outputs[0])
    return m


def street():
    reset(20)
    world_flat((0.03, 0.01, 0.05), 0.6)
    box('street', (16, 400, 0.1), (0, 180, -0.05), simple('wet', (0.02, 0.02, 0.025), 0.06, metal=0.2))
    rs = np.random.RandomState(8)
    tm = tower_mat()
    for side in (-1, 1):
        y = -5.0
        while y < 300:
            w = 6 + 6 * rs.rand(); h = 20 + 70 * rs.rand()
            box('tower', (8, w, h), (side * 12, y + w / 2, h / 2), tm)
            c = NEON[rs.randint(4)]
            if rs.rand() < 0.8:                       # placa vertical de neon com escrita alienígena
                box('sign', (0.15, 1.1, 5.0), (side * 7.9, y + w / 2, 6 + 6 * rs.rand()), emission('signbg', (0.01, 0.01, 0.02), 1.0))
                txt = ''.join(GLYPHS[rs.randint(len(GLYPHS))] for _ in range(4))
                text3d('\n'.join(txt), (side * 7.8, y + w / 2, 10 + 3 * rs.rand()), 0.9, c, 6.0,
                       rot=(math.pi / 2, 0, -side * math.pi / 2), align='CENTER', font='DejaVuSans-Bold')
            box('strip', (0.1, w * 0.9, 0.12), (side * 7.95, y + w / 2, 3.2), emission('strip', c, 8.0))
            y += w + 1.0 + 2 * rs.rand()
    fog((0.08, 0.02, 0.12), 8.0, 140.0, 0.8)


def build_p2b():
    street()
    cam = camera((0, 0, 1.7), (0, 40, 6), 30)
    def update(t, u):
        y = 2.0 * t
        cam.location = (0.6 * math.sin(t * 0.4), y, 1.7 + 0.03 * math.sin(t * 6))
        look(cam, (0, y + 40, 7 + 2 * u))
    return update


def machine(x, y, empty_slot=None):
    """Máquina de venda: corpo, frente de vidro acesa e produtos em prateleiras. Devolve o produto do espaço vazio."""
    body = simple('mach', (0.12, 0.14, 0.2), 0.4, metal=0.4)
    box('body', (1.2, 0.9, 2.1), (x, y, 1.05), body)
    box('glow', (0.9, 0.02, 1.4), (x - 0.08, y - 0.46, 1.25), emission('glass', (0.6, 0.9, 1.0), 0.6))
    rs = np.random.RandomState(int(x * 10) % 97)
    cols = ((0.9, 0.2, 0.3), (0.2, 0.7, 0.9), (0.95, 0.85, 0.3), (0.4, 0.9, 0.5), (0.9, 0.9, 0.95))
    mats = [simple(f'prod{i}', c, 0.35) for i, c in enumerate(cols)]
    held = None
    for r in range(5):
        for c in range(5):
            o = box('item', (0.13, 0.12, 0.2), (x - 0.4 + c * 0.16, y - 0.49, 0.72 + r * 0.27), mats[rs.randint(5)])
            if empty_slot == (r, c):
                held = o
    box('slot', (0.5, 0.05, 0.2), (x - 0.08, y - 0.47, 0.3), simple('slotm', (0.01, 0.01, 0.01), 0.5))
    box('pad', (0.15, 0.02, 0.5), (x + 0.48, y - 0.46, 1.3), emission('pad', (1.0, 0.3, 0.8), 2.0))
    point((x, y - 1.2, 1.4), 12.0, (0.6, 0.9, 1.0), 0.5)
    return held


def alley():
    reset(20)
    world_flat((0.03, 0.01, 0.05), 0.5)
    box('floor', (30, 30, 0.1), (0, 0, -0.05), simple('wet', (0.02, 0.02, 0.025), 0.06, metal=0.2))
    box('wall', (30, 0.2, 10), (0, 0.6, 5), simple('wallm', (0.05, 0.04, 0.06), 0.7))
    text3d('⌬◈⊛', (0, 0.45, 3.2), 0.8, (1.0, 0.1, 0.7), 8.0, align='CENTER', font='DejaVuSans-Bold')
    fog((0.08, 0.02, 0.12), 4.0, 40.0, 0.6)


def build_p2c():
    alley()
    for x in (-1.4, 0.0, 1.4):
        machine(x, 0.0)
    cam = camera((0.6, -4.5, 1.5), (0, 0, 1.2), 32)
    def update(t, u):
        cam.location = (0.6 - 0.3 * u, -4.5 + 1.2 * ease(u), 1.5)
        look(cam, (0, 0, 1.2))
    return update


def build_p2d():
    alley()
    held = machine(0.0, 0.0, empty_slot=(2, 3))
    cam = camera((0.4, -2.4, 1.4), (0.1, 0, 1.3), 32)
    def update(t, u):
        cam.location = (0.4 - 0.1 * u, -2.4 + 0.5 * u, 1.4)
        look(cam, (0.1, 0, 1.3))
        held.hide_render = t < TL.RESTOCK_AT            # o espaço vazio aparece cheio
    return update
