"""THE TERMINAL: o planeta é um aeroporto vazio de madrugada."""
from lib import *
from planets import *
import timeline as TL

SHOTS = {'p1a': 6.0, 'p1b': 3.75, 'p1c': 3.5, 'p1d': 4.0}
FLIGHTS = [('TR 101', 'HALDEN'), ('TR 118', 'MARLOW'), ('KV 207', 'OSTERBY'), ('TR 230', 'NEW CALDER'),
           ('LM 044', 'VESTA'), ('TR 312', 'BRIDGEFORD'), ('KV 415', 'ARDEN'), ('TR 509', 'HOLLOWAY')]


def build_p1a():
    upd = orbit(planet_terminal, (0.8, 0.7, 0.6), (-1.0, -0.25, 0.25))
    return lambda t, u: upd(t, u, SHOTS['p1a'])


def concourse():
    """Saguão sem fim: carpete, fileiras de cadeiras, painéis de luz no teto, janelas escuras e a esteira."""
    reset(18)
    world_flat((0.02, 0.03, 0.05), 0.5)
    carpet, nt = mat('carpet')
    pos = n(nt, 'ShaderNodeNewGeometry').outputs['Position']
    a = n(nt, 'ShaderNodeTexNoise', Scale=6.0, Detail=6.0); L(nt, pos, a.inputs['Vector'])
    out(nt, principled(nt, ramp(nt, [(0.4, (0.08, 0.14, 0.18)), (0.6, (0.12, 0.2, 0.24))], a.outputs['Fac']).outputs[0], 0.95).outputs[0])
    box('floor', (24, 400, 0.1), (0, 190, -0.05), carpet)
    wall = simple('wall', (0.62, 0.62, 0.6), 0.6)
    box('ceil', (24, 400, 0.1), (0, 190, 4.5), simple('ceilm', (0.7, 0.7, 0.68), 0.8))
    box('wallR', (0.1, 400, 4.5), (12, 190, 2.25), wall)
    box('glass', (0.05, 400, 3.2), (-12, 190, 2.0), emission('night', (0.03, 0.06, 0.14), 1.0))
    v, t = cube_vt(2.4, 0.5, 0.06)
    scatter('panels', v, t, [(x, y, 4.38) for x in (-6, 0, 6) for y in range(-5, 380, 6)], m=emission('panel', (1.0, 0.95, 0.85), 3.5))
    seat = simple('seat', (0.08, 0.09, 0.1), 0.4, metal=0.3)
    v, t = cube_vt(0.55, 0.55, 0.45)
    pos_ = [(x + k * 0.6, y, 0.0) for x in (-9.5, 5.5) for y in range(4, 380, 5) for k in range(6)]
    scatter('seats', v, t, pos_, m=seat)
    v, t = cube_vt(0.55, 0.08, 0.5)
    scatter('backs', v, t, [(x, y + 0.25, 0.45) for x, y, _ in pos_], m=seat)
    belt, nt = mat('belt')                           # esteira com faixas que andam
    tc = n(nt, 'ShaderNodeNewGeometry').outputs['Position']
    mp = n(nt, 'ShaderNodeMapping'); L(nt, tc, mp.inputs['Vector'])
    br = n(nt, 'ShaderNodeTexBrick', Scale=3.0, Mortar_Size=0.05); L(nt, mp.outputs[0], br.inputs['Vector'])
    br.inputs['Color1'].default_value = (0.05, 0.05, 0.05, 1); br.inputs['Color2'].default_value = (0.06, 0.06, 0.06, 1)
    br.inputs['Mortar'].default_value = (0.3, 0.3, 0.3, 1)
    out(nt, principled(nt, br.outputs['Color'], 0.4).outputs[0])
    box('belt', (1.4, 380, 0.08), (0, 190, 0.04), belt)
    for x in (-0.8, 0.8):
        box('rail', (0.12, 380, 0.9), (x, 190, 0.45), simple('railm', (0.5, 0.5, 0.52), 0.3, metal=0.8))
    fog((0.05, 0.06, 0.08), 6.0, 90.0, 0.85)
    return mp


def build_p1b():
    mp = concourse()
    cam = camera((-2.2, 0, 1.6), (-2.2, 30, 1.4), 32)
    def update(t, u):
        y = 1.0 * t
        cam.location = (-2.2, y, 1.6 + 0.015 * math.sin(t * 5))
        look(cam, (-1.6, y + 30, 1.4))
        mp.inputs['Location'].default_value[1] = -0.7 * t     # a esteira anda sozinha
    return update


def board(boarding=False):
    """Painel de partidas: fundo preto, linhas âmbar; uma linha verde quando embarca."""
    reset(18)
    world_flat((0.02, 0.03, 0.05), 0.4)
    box('wall', (12, 0.1, 6), (0, 0.3, 2.5), simple('wall', (0.55, 0.55, 0.53), 0.7))
    box('panel', (4.6, 0.1, 3.0), (0, 0.2, 2.6), simple('black', (0.01, 0.01, 0.012), 0.3))
    text3d('DEPARTURES', (-2.1, 0.1, 3.75), 0.28, (1.0, 0.85, 0.5), 3.0)
    rows = []
    for k, (fl, dest) in enumerate(FLIGHTS):
        y = 3.3 - k * 0.3
        text3d(f'{fl}  {dest:<11}', (-2.1, 0.1, y), 0.2, (1.0, 0.62, 0.15), 3.0)
        d = text3d('DELAYED', (2.1, 0.1, y), 0.2, (1.0, 0.25, 0.15), 3.0, align='RIGHT')
        b = text3d('NOW BOARDING', (2.1, 0.1, y), 0.2, (0.3, 1.0, 0.4), 4.0, align='RIGHT')
        b.hide_render = True
        rows.append((d, b))
    point((0, -3, 3), 40.0, (1, 0.9, 0.8), 1.0)
    fog((0.05, 0.06, 0.08), 6.0, 60.0, 0.5)
    return rows


def build_p1c():
    board()
    cam = camera((0.4, -5.5, 2.4), (0, 0, 2.5), 35)
    def update(t, u):
        cam.location = (0.4 - 0.1 * u, -5.5 + 0.8 * u, 2.4)
        look(cam, (0, 0, 2.5))
    return update


def build_p1d():
    rows = board()
    d, b = rows[5]                                    # a linha que embarca
    cam = camera((0.1, -4.4, 2.2), (0, 0, 1.85), 30)
    def update(t, u):
        cam.location = (0.1 - 0.1 * u, -4.4 + 0.9 * ease(u), 2.2 - 0.2 * u)     # chega perto da linha que embarca, com o nome do voo
        look(cam, (0, 0, 1.85))
        on = t >= TL.BOARDING_AT
        d.hide_render = on
        b.hide_render = not on or (t - TL.BOARDING_AT) % 0.6 > 0.42     # pisca
    return update
