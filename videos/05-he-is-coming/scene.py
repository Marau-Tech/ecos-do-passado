from lib import *
from timeline import FLICKERS, MESSAGE, TYPE_AT, TYPE_STEP

SHOTS = {'a1': 6.0, 'a2': 10.0, 'a3': 8.0, 'c1': 10.0, 'a4': 10.0, 'c2': 10.0, 'c3': 8.0, 'a5': 8.0, 'a6': 6.0}
HOLD_STATES = True              # a câmera é fixa: só renderiza quando algo muda
TEX = f'{RENDER}/_tex'
FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf'
WIDE = ((-6.7, -4.7, 2.82), (1.0, 2.2, 0.0), 19)
CLOSE = ((-0.45, -2.75, 2.1), (-0.8, -1.0, 1.02), 30)
DESK = ((-0.8, -2.15, 1.72), (-0.8, -1.0, 1.08), 34)
ROWS = (-1.0, 2.0)
COLS = (-4.0, -2.4, -0.8, 0.8, 2.4, 4.0)

def carpet():
    m, nt = mat('carpet')
    pos = n(nt, 'ShaderNodeNewGeometry').outputs['Position']
    a = n(nt, 'ShaderNodeTexNoise', Scale=30.0, Detail=6.0, Roughness=0.7); L(nt, pos, a.inputs['Vector'])
    out(nt, principled(nt, ramp(nt, [(0.35, (0.10, 0.10, 0.11)), (0.65, (0.18, 0.18, 0.19))], a.outputs['Fac']).outputs[0], 0.95, spec=0.1).outputs[0])
    return m

class Monitor:
    def __init__(self, x, y):
        body = simple('monitor', (0.03, 0.03, 0.03), 0.5)
        box('bezel', (0.72, 0.05, 0.56), (x, y, 1.10), body)
        box('neck', (0.06, 0.05, 0.22), (x, y + 0.02, 0.84), body)
        box('foot', (0.3, 0.2, 0.02), (x, y, 0.765), body)
        self.m, nt = mat(f'screen{x}{y}')
        tc = n(nt, 'ShaderNodeTexCoord').outputs['Generated']
        sp = n(nt, 'ShaderNodeSeparateXYZ'); L(nt, tc, sp.inputs[0])
        cb = n(nt, 'ShaderNodeCombineXYZ'); L(nt, sp.outputs['X'], cb.inputs['X']); L(nt, sp.outputs['Z'], cb.inputs['Y'])
        self.tex = n(nt, 'ShaderNodeTexImage'); L(nt, cb.outputs[0], self.tex.inputs['Vector'])
        self.val = n(nt, 'ShaderNodeValue')
        self.em = n(nt, 'ShaderNodeEmission', Strength=0.0)
        L(nt, mix(nt, self.val.outputs[0], (0.42, 0.50, 0.62), self.tex.outputs['Color']), self.em.inputs['Color'])
        add = n(nt, 'ShaderNodeAddShader')
        L(nt, principled(nt, (0.01, 0.01, 0.012), 0.18, spec=0.6).outputs[0], add.inputs[0]); L(nt, self.em.outputs[0], add.inputs[1])
        out(nt, add.outputs[0])
        w, h, yy = 0.32, 0.24, y - 0.027
        mesh_from('screen', [(x - w, yy, 1.10 - h), (x + w, yy, 1.10 - h), (x + w, yy, 1.10 + h), (x - w, yy, 1.10 + h)], [(0, 1, 2, 3)], self.m)
        c = bpy.data.curves.new('txt', 'FONT'); c.font = bpy.data.fonts.load(FONT)
        c.align_x, c.align_y = 'CENTER', 'CENTER'; c.size = 0.17; c.space_line = 1.0
        c.materials.append(emission('txt', (1, 1, 1), 2.2))
        self.t = bpy.data.objects.new('txt', c); link(self.t)
        self.t.location = (x, yy - 0.002, 1.10); self.t.rotation_euler = (math.pi / 2, 0, 0); self.t.hide_render = True
        self.light = point((x, y - 0.5, 1.2), 0.0, (0.72, 0.8, 1.0), 0.2)
        self.mode = None

    def set(self, mode):
        if mode == self.mode:
            return
        self.mode = mode
        on = mode != 'off'
        self.em.inputs['Strength'].default_value = 1.2 if on else 0.0
        self.light.data.energy = 1.6 if on else 0.0
        self.t.hide_render = True
        self.val.outputs[0].default_value = 0.0
        if mode.startswith('img:'):
            self.tex.image = image(mode[4:]); self.val.outputs[0].default_value = 1.0
        elif mode.startswith('txt:'):
            self.em.inputs['Strength'].default_value = 0.0
            self.light.data.energy = 0.5
            self.t.data.body = mode[4:]; self.t.hide_render = False

def image(name):
    i = bpy.data.images.get(name + '.png')
    return i or bpy.data.images.load(f'{TEX}/{name}.png')

class Office:
    def __init__(self):
        reset(18)
        world_flat((0.03, 0.033, 0.038), 1.0)
        wall = simple('wall', (0.30, 0.30, 0.29), 0.8)
        box('floor', (14.4, 10.4, 0.1), (0, 0, -0.05), carpet())
        box('ceil', (14.4, 10.4, 0.1), (0, 0, 3.05), simple('ceil', (0.32, 0.32, 0.31), 0.9))
        box('wallN', (14.4, 0.1, 3.1), (0, 5.2, 1.5), wall); box('wallS', (14.4, 0.1, 3.1), (0, -5.2, 1.5), wall)
        box('wallE', (0.1, 10.4, 3.1), (7.2, 0, 1.5), wall); box('wallW', (0.1, 10.4, 3.1), (-7.2, 0, 1.5), wall)
        for x in range(-6, 7, 2):                             # grade do forro
            box('grid', (0.03, 10.4, 0.02), (x, 0, 2.99), simple('gridm', (0.12, 0.12, 0.12), 0.8))
        for y in range(-4, 5, 2):
            box('grid', (14.4, 0.03, 0.02), (0, y, 2.99), simple('gridm', (0.12, 0.12, 0.12), 0.8))
        for x in (-5.6, -2.0, 2.0, 5.6):                      # janelas com a cidade ao longe
            box('window', (2.4, 0.04, 1.3), (x, 5.14, 1.75), emission('city', (0.42, 0.46, 0.55), 0.20))
            for z in (1.2, 1.5, 1.8, 2.1):
                box('blind', (2.5, 0.05, 0.03), (x, 5.1, z), simple('blindm', (0.05, 0.05, 0.05), 0.8))
        self.panel = emission('panel', (0.95, 0.97, 1.0), 0.0)
        self.lamps = []
        for x in (-4.5, 0, 4.5):
            for y in (-2.5, 2.5):
                box('panel', (1.2, 0.6, 0.03), (x, y, 2.97), self.panel)
                self.lamps.append(point((x, y, 2.6), 0.0, (0.95, 0.97, 1.0), 0.5))
        self.exit = emission('exit', (0.8, 1.0, 0.86), 2.0)
        box('exit', (0.5, 0.05, 0.2), (6.2, 5.1, 2.6), self.exit)
        self.exit_light = point((6.2, 4.6, 2.5), 5.0, (0.6, 1.0, 0.7), 0.2)
        desk = simple('desk', (0.20, 0.19, 0.17), 0.6)
        side = simple('side', (0.10, 0.11, 0.13), 0.9)
        chair = simple('chair', (0.04, 0.04, 0.05), 0.7)
        self.mons = []
        for y in ROWS[::-1]:
            box('part', (10.2, 0.05, 1.25), (0, y + 0.42, 0.62), side)
            for x in COLS:
                box('top', (1.45, 0.75, 0.04), (x, y + 0.05, 0.74), desk)
                box('leg', (0.05, 0.7, 0.72), (x - 0.68, y + 0.05, 0.36), desk)
                box('leg', (0.05, 0.7, 0.72), (x + 0.68, y + 0.05, 0.36), desk)
                box('keys', (0.42, 0.14, 0.02), (x, y - 0.22, 0.77), simple('keys', (0.05, 0.05, 0.05), 0.6))
                box('seat', (0.46, 0.46, 0.07), (x + 0.1, y - 0.75, 0.48), chair, (0, 0, 0.2))
                box('back', (0.44, 0.06, 0.5), (x + 0.1, y - 1.0, 0.78), chair, (0, 0, 0.2))
                box('post', (0.05, 0.05, 0.45), (x + 0.1, y - 0.75, 0.22), chair)
                self.mons.append(Monitor(x, y))
        # do mais longe para o mais perto da CAM 04
        self.mons.sort(key=lambda m: -math.dist(m.light.location, WIDE[0]))

    def screens(self, modes):
        for m, mode in zip(self.mons, modes):
            m.set(mode)

    def all(self, mode):
        self.screens([mode] * len(self.mons))

    def lights(self, on):
        self.panel.node_tree.nodes['Emission'].inputs['Strength'].default_value = 1.6 if on else 0.0
        for l in self.lamps:
            l.data.energy = 60.0 if on else 0.0

    def exit_on(self, on):
        self.exit.node_tree.nodes['Emission'].inputs['Strength'].default_value = 2.0 if on else 0.0
        self.exit_light.data.energy = 5.0 if on else 0.0

def look_at_cam(fig, cam_loc):
    d = Vector(cam_loc) - Vector(fig.location)
    fig.rotation_euler.z = math.atan2(d.x, -d.y)

def still(path, cam=None):
    s = bpy.context.scene
    s.render.filepath = path
    bpy.ops.render.render(write_still=True)

def corridor(dist):
    reset(24)
    world_flat((0.0, 0.0, 0.0), 1.0)
    w = simple('cwall', (0.34, 0.34, 0.33), 0.7)
    box('cfloor', (3.2, 80, 0.1), (0, 36, -0.05), simple('cfloor', (0.22, 0.22, 0.22), 0.3))
    box('cceil', (3.2, 80, 0.1), (0, 36, 2.8), w)
    box('cl', (0.1, 80, 2.9), (-1.6, 36, 1.4), w); box('cr', (0.1, 80, 2.9), (1.6, 36, 1.4), w)
    box('cend', (3.2, 0.1, 2.9), (0, 76, 1.4), w)
    dark = simple('door', (0.05, 0.05, 0.05), 0.5)
    for i in range(10):
        box('door', (0.06, 1.0, 2.1), (-1.56 if i % 2 else 1.56, 4 + i * 6, 1.05), dark)
        box('lamp', (0.5, 1.4, 0.03), (0, 3 + i * 7, 2.74), emission('clamp', (1, 1, 1), 1.4))
        point((0, 3 + i * 7, 2.45), 22, (1, 1, 1), 0.4)
    fig = pale_figure((0, dist, 0))
    camera((0, -0.5, 1.7), (0, 30, 1.5), 34)
    return fig

def build_prep():
    os.makedirs(TEX, exist_ok=True)
    for i, dist in enumerate((34, 19, 10, 3.6)):
        p = f'{TEX}/fig{i}.png'
        if not os.path.exists(p):
            corridor(dist); still(p)
    for i, pos in enumerate(((2.4, -2.6), (-3.2, -2.6))):
        p = f'{TEX}/live{i}.png'
        if not os.path.exists(p):
            o = Office(); o.mons[0].set('off'); o.all('boot')
            fig = pale_figure((*pos, 0)); look_at_cam(fig, WIDE[0])
            o.lights(True)                                     # a imagem da tela precisa ser legível de perto
            camera(*WIDE)
            bpy.context.scene.cycles.samples = 24
            still(p)
    return None

def wide():
    o = Office(); camera(*WIDE)
    return o

def close():
    o = Office(); camera(*CLOSE)
    return o

def build_a1():
    o = wide()
    def update(t, u):
        on = int(t >= 3.0)
        o.screens(['boot'] * on + ['off'] * (12 - on))
        return on
    return update

def build_a2():
    o = wide()
    def update(t, u):
        on = 1 + sum(t >= x for x in (1.5, 4.5, 7.5))
        o.screens(['boot'] * on + ['off'] * (12 - on))
        return on
    return update

def build_a3():
    o = wide()
    def update(t, u):
        fig = t >= 5.0
        o.all('img:fig0' if fig else 'boot')
        return fig
    return update

def build_c1():
    o = close()
    def update(t, u):
        o.all('img:fig0')
        return 0
    return update

def build_a4():
    o = wide()
    def update(t, u):
        lit = any(f <= t < f + 0.25 for f in FLICKERS)
        i = min(3, sum(t >= f + 0.25 for f in FLICKERS))
        o.lights(lit); o.all(f'img:fig{i}')
        return lit, i
    return update

def build_c2():
    o = close()
    def update(t, u):
        k = max(0, int((t - TYPE_AT) / TYPE_STEP) + 1) if t >= TYPE_AT else 0
        k = min(k, len(MESSAGE))
        o.all(f'txt:{MESSAGE[:k]}' if t >= 1.5 else 'img:fig3')
        return k, t >= 1.5
    return update

def build_c3():
    o = Office(); camera(*DESK)
    def update(t, u):
        i = int(t >= 4.0)
        o.all(f'img:live{i}')
        return i
    return update

def build_a5():
    o = wide()
    def update(t, u):
        k = max(0, min(12, int((t - 1.0) / 0.5) + 1)) if t >= 1.0 else 0
        o.screens(['off'] * k + ['img:live1'] * (12 - k))
        return k
    return update

def build_a6():
    o = wide()
    o.all('off')
    def update(t, u):
        return 0
    return update
