"""Os dois planetas, o chão e a figura do astronauta, usados pela intro e pelos dois trechos."""
from lib import *


def planet_dark(r=1.0, loc=(0, 0, 0)):
    """rocha quase preta, com um relevo que só aparece de raspão"""
    m, nt = mat('dark')
    tc = n(nt, 'ShaderNodeTexCoord').outputs['Object']
    a = n(nt, 'ShaderNodeTexNoise', Scale=2.4, Detail=9.0, Roughness=0.55); L(nt, tc, a.inputs['Vector'])
    col = ramp(nt, [(0.35, (0.004, 0.004, 0.005)), (0.65, (0.018, 0.018, 0.02))], a.outputs['Fac']).outputs[0]
    f = n(nt, 'ShaderNodeTexNoise', Scale=20.0, Detail=6.0, Roughness=0.6); L(nt, tc, f.inputs['Vector'])
    bp = n(nt, 'ShaderNodeBump', Strength=0.5, Distance=0.03); L(nt, f.outputs['Fac'], bp.inputs['Height'])
    out(nt, principled(nt, col, 0.75, spec=0.25, normal=bp.outputs[0]).outputs[0])
    return sphere('p_dark', r, loc, m, 192, 96)


def planet_bright(r=1.0, loc=(0, 0, 0)):
    """sal branco que brilha sozinho, com rachaduras cinza"""
    m, nt = mat('bright')
    tc = n(nt, 'ShaderNodeTexCoord').outputs['Object']
    a = n(nt, 'ShaderNodeTexNoise', Scale=2.0, Detail=8.0, Roughness=0.55); L(nt, tc, a.inputs['Vector'])
    col = ramp(nt, [(0.35, (0.78, 0.76, 0.7)), (0.65, (0.98, 0.97, 0.93))], a.outputs['Fac']).outputs[0]
    v = n(nt, 'ShaderNodeTexVoronoi', {'feature': 'DISTANCE_TO_EDGE'}, Scale=14.0); L(nt, tc, v.inputs['Vector'])
    crack = ramp(nt, [(0.0, (0.45, 0.45, 0.45)), (0.04, (1, 1, 1))], v.outputs['Distance']).outputs[0]
    col = mix(nt, 1.0, col, crack, 'MULTIPLY')
    out(nt, principled(nt, col, 0.8, spec=0.2, emis=(1.0, 0.97, 0.88), emis_str=0.35).outputs[0])
    return sphere('p_bright', r, loc, m, 192, 96)


def salt_mat():
    m, nt = mat('salt')
    pos = n(nt, 'ShaderNodeNewGeometry').outputs['Position']
    a = n(nt, 'ShaderNodeTexNoise', Scale=0.4, Detail=6.0, Roughness=0.6); L(nt, pos, a.inputs['Vector'])
    col = ramp(nt, [(0.35, (0.72, 0.7, 0.66)), (0.65, (0.84, 0.83, 0.79))], a.outputs['Fac']).outputs[0]
    v = n(nt, 'ShaderNodeTexVoronoi', {'feature': 'DISTANCE_TO_EDGE'}, Scale=0.9); L(nt, pos, v.inputs['Vector'])
    ridge = ramp(nt, [(0.0, (0.5, 0.5, 0.5)), (0.05, (1, 1, 1))], v.outputs['Distance']).outputs[0]
    col = mix(nt, 1.0, col, ridge, 'MULTIPLY')
    bp = n(nt, 'ShaderNodeBump', Strength=0.5, Distance=0.02); L(nt, v.outputs['Distance'], bp.inputs['Height'])
    out(nt, principled(nt, col, 0.9, spec=0.1, normal=bp.outputs[0]).outputs[0])
    return m


def rock_mat():
    m, nt = mat('rock')
    pos = n(nt, 'ShaderNodeNewGeometry').outputs['Position']
    a = n(nt, 'ShaderNodeTexNoise', Scale=1.2, Detail=8.0, Roughness=0.65); L(nt, pos, a.inputs['Vector'])
    col = ramp(nt, [(0.3, (0.03, 0.03, 0.033)), (0.7, (0.11, 0.105, 0.1))], a.outputs['Fac']).outputs[0]
    f = n(nt, 'ShaderNodeTexNoise', Scale=7.0, Detail=8.0, Roughness=0.7); L(nt, pos, f.inputs['Vector'])
    bp = n(nt, 'ShaderNodeBump', Strength=0.8, Distance=0.05); L(nt, f.outputs['Fac'], bp.inputs['Height'])
    out(nt, principled(nt, col, 0.75, spec=0.3, normal=bp.outputs[0]).outputs[0])
    return m


def rocky_ground(seed=2):
    """chão de pedra preta com cascalho espalhado"""
    rm = rock_mat()
    def h(x, y):
        return 0.25 * fbm(x * 0.15, y * 0.15, 4) + 0.06 * fbm(x * 1.3 + 9, y * 1.3, 3)
    g = grid_mesh('ground', 80, 200, h, rm, center=(0, 20))
    rs = np.random.RandomState(seed)
    v, t = lathe([(0.0, -0.05), (0.18, 0.0), (0.2, 0.1), (0.12, 0.2), (0.0, 0.24)], 7)
    for i in range(140):
        x, y = rs.uniform(-9, 9), rs.uniform(0.5, 22)
        s = rs.uniform(0.3, 1.6)
        o = fast_mesh('stone', v, t, rm); o.location = (x, y, h(x, y) - 0.02)
        o.scale = (s * rs.uniform(0.7, 1.4), s, s * rs.uniform(0.5, 1.0)); o.rotation_euler.z = rs.uniform(0, 6.3)
    return h


def flashlight(cam, energy=900.0, size=34.0):
    """lanterna presa à câmera, um pouco abaixo e à direita, apontando para onde ela olha"""
    l = bpy.data.lights.new('torch', 'SPOT'); l.energy = energy; l.spot_size = math.radians(size)
    l.spot_blend = 0.35; l.shadow_soft_size = 0.03; l.color = (1.0, 0.92, 0.78)
    o = bpy.data.objects.new('torch', l); link(o)
    o.parent = cam; o.location = (0.18, -0.25, 0.0)
    return o


def astronaut(loc=(0, 0, 0), yaw=0.0, color=(0.85, 0.85, 0.82)):
    """traje branco: tronco, mochila, capacete com visor escuro, pernas e braços"""
    root = bpy.data.objects.new('astro', None); link(root); root.location = loc; root.rotation_euler.z = yaw
    suit = simple('suit', color, 0.6)
    visor = simple('visor', (0.02, 0.02, 0.025), 0.05, 0.6)
    v, t = lathe([(0.0, 0.85), (0.22, 0.9), (0.25, 1.2), (0.24, 1.45), (0.12, 1.52), (0.0, 1.53)], 16)
    parts = [fast_mesh('torso', v, t, suit, True),
             box('pack', (0.42, 0.22, 0.5), (0, 0.24, 1.22), suit),
             sphere('helmet', 0.17, (0, 0, 1.68), suit, 32, 16)]
    vz = sphere('visor', 0.13, (0, -0.07, 1.69), visor, 32, 16); vz.scale = (1.0, 0.8, 0.75); parts.append(vz)
    for s_ in (-1, 1):
        parts.append(tube('leg', [(s_ * 0.11, 0, 0.9), (s_ * 0.12, 0, 0.45), (s_ * 0.12, -0.02, 0.06)], [0.1, 0.09, 0.09], suit))
        parts.append(box('boot', (0.16, 0.28, 0.12), (s_ * 0.12, -0.05, 0.06), suit))
        parts.append(tube('arm', [(s_ * 0.27, 0, 1.4), (s_ * 0.32, 0, 1.1), (s_ * 0.3, -0.06, 0.85)], [0.08, 0.07, 0.07], suit))
    for o in parts:
        o.parent = root
    return root
