"""Andar de baias à noite, pela webcam de um notebook esquecido aberto numa mesa. As luzes apagam faixa por
faixa, do fundo até a câmera; a silhueta está sempre parada na faixa que acabou de apagar. Quando a última
apaga, a tela do notebook mostra um tronco colado na lente. No glitch, tudo volta aceso e vazio."""
from lib import *
import timeline as TL

SHOTS = {'a': 12.0}
HOLD_STATES = True

ZONES = [(-1.0, 5.0), (5.0, 10.0), (10.0, 15.0), (15.0, 21.0)]    # faixa 1 (câmera) até a 4 (fundo)
ROWS = [(1.25, 3.75), (6.25, 8.75), (11.25, 13.75), (16.25, 18.75)]
CEIL = 2.8
PART = 1.35                     # altura das divisórias


def build_a():
    reset(48)
    world_flat((0.0, 0.0, 0.0), 0.0)
    carpet = simple('carpet', (0.16, 0.17, 0.19), 0.95)
    wall = simple('wall', (0.52, 0.52, 0.5), 0.85)
    tile = simple('tile', (0.58, 0.58, 0.56), 0.9)
    box('floor', (16, 23, 0.1), (0, 10, -0.05), carpet)
    box('ceil', (16, 23, 0.1), (0, 10, CEIL + 0.05), tile)
    box('wallL', (0.1, 23, CEIL), (-7.5, 10, CEIL / 2), wall); box('wallR', (0.1, 23, CEIL), (7.5, 10, CEIL / 2), wall)
    box('wallB', (16, 0.1, CEIL), (0, 21.05, CEIL / 2), wall); box('wallF', (16, 0.1, CEIL), (0, -1.5, CEIL / 2), wall)
    # porta de saída no fim do corredor, com a placa verde acesa por cima
    box('door', (1.0, 0.06, 2.1), (0, 20.98, 1.05), simple('doorm', (0.3, 0.31, 0.3), 0.6))
    box('bar', (0.8, 0.06, 0.05), (0, 20.93, 1.0), simple('barm', (0.5, 0.5, 0.5), 0.3, 0.8))
    box('exit', (0.55, 0.05, 0.2), (0, 20.97, 2.3), emission('exitm', (0.15, 1.0, 0.3), 6.0))
    point((0, 20.6, 2.15), 6.0, (0.2, 1.0, 0.35), 0.2)
    # baias: duas fileiras de cada lado, com o corredor do meio livre
    fab = simple('fabric', (0.3, 0.32, 0.37), 0.95)
    trim = simple('trim', (0.62, 0.62, 0.6), 0.5)
    mon = simple('monitor', (0.05, 0.05, 0.055), 0.4)
    desk = simple('desk', (0.45, 0.42, 0.38), 0.6)
    for s in (-1, 1):
        for x0, x1 in ((1.0, 3.9), (4.7, 7.4)):
            xa, xb = s * x0, s * x1
            cx = (xa + xb) / 2
            w = abs(xb - xa)
            for j in range(8):
                y0 = 0.6 + 2.5 * j
                box('cross', (w, 0.06, PART), (cx, y0, PART / 2), fab)
                box('crossT', (w, 0.08, 0.03), (cx, y0, PART + 0.015), trim)
                # divisória do lado do corredor, com a entrada perto do fim de cada baia
                box('side', (0.06, 1.6, PART), (xa, y0 + 0.8, PART / 2), fab)
                box('sideT', (0.08, 1.6, 0.03), (xa, y0 + 0.8, PART + 0.015), trim)
                box('back', (0.06, 2.5, PART), (xb, y0 + 1.25, PART / 2), fab)
                box('desk', (w - 0.2, 0.7, 0.04), (cx, y0 + 2.1, 0.74), desk)
                box('mon', (0.42, 0.35, 0.38), (cx + s * 0.3, y0 + 2.1, 0.95), mon)
    # luminárias: painel aceso (some quando a faixa apaga) por cima do painel apagado, e um spot para baixo
    off_m = simple('paneloff', (0.42, 0.43, 0.42), 0.5)
    lamps = []
    for k, rows in enumerate(ROWS):
        on_m = emission(f'panel{k}', (0.9, 0.97, 1.0), 4.0)
        objs = []
        for y in rows:
            for x in (-4.3, 0.0, 4.3):
                box('panelOff', (0.6, 1.2, 0.01), (x, y, CEIL - 0.005), off_m)
                objs.append(box('panel', (0.6, 1.2, 0.02), (x, y, CEIL - 0.015), on_m))
                l = bpy.data.lights.new('sp', 'SPOT'); l.energy = 200.0; l.color = (0.92, 0.98, 1.0)
                l.spot_size = math.radians(105); l.spot_blend = 0.35; l.shadow_soft_size = 0.3
                o = bpy.data.objects.new('sp', l); link(o); o.location = (x, y, CEIL - 0.05)
                objs.append(o)
        lamps.append(objs)
    # a tela do notebook, logo abaixo da lente, sempre acesa
    point((0.0, -0.05, 0.88), 1.4, (0.6, 0.72, 1.0), 0.15)
    fig = pale_figure((0, TL.SPOT[0], 0))
    figs = [fig] + list(fig.children_recursive)
    camera((0.0, 0.0, 1.05), (0.0, 20.0, 1.25), 24)

    fps = FPS
    offs = [int(z * fps + 1e-6) for z in TL.OFF]
    back = int(TL.BACK * fps + 1e-6)

    def upd(t, u):
        f = int(round(t * fps))
        dark = 0 if f >= back else sum(f >= o for o in offs)       # quantas faixas apagadas, do fundo para a frente
        for k, objs in enumerate(lamps):
            off = k >= 4 - dark
            for o in objs:
                o.hide_render = off
        where = None
        if 1 <= dark <= 3:
            where = TL.SPOT[dark - 1]
            fig.location = (0.0, where, 0.0)
        elif dark == 4:                                              # colado na lente, só na luz da tela
            where = 0.55
            fig.location = (0.04, where, -0.45)       # o peito na altura da lente
        for o in figs:
            o.hide_render = where is None
        return (dark, where)
    return upd
