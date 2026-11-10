"""Os dois planetas, as nuvens e o módulo de pouso, usados pela intro e pelos dois trechos."""
from lib import *


def planet_slow(r=1.0, loc=(0, 0, 0)):
    """deserto âmbar e ocre, com faixas de poeira"""
    m, nt = mat('slow')
    tc = n(nt, 'ShaderNodeTexCoord').outputs['Object']
    a = n(nt, 'ShaderNodeTexNoise', Scale=2.2, Detail=9.0, Roughness=0.55); L(nt, tc, a.inputs['Vector'])
    col = ramp(nt, [(0.32, (0.45, 0.22, 0.08)), (0.5, (0.78, 0.48, 0.2)), (0.7, (0.92, 0.72, 0.42))], a.outputs['Fac']).outputs[0]
    f = n(nt, 'ShaderNodeTexNoise', Scale=24.0, Detail=6.0, Roughness=0.6); L(nt, tc, f.inputs['Vector'])
    bp = n(nt, 'ShaderNodeBump', Strength=0.25, Distance=0.02); L(nt, f.outputs['Fac'], bp.inputs['Height'])
    out(nt, principled(nt, col, 0.9, spec=0.15, normal=bp.outputs[0]).outputs[0])
    return sphere('p_slow', r, loc, m, 192, 96)


def planet_fast(r=1.0, loc=(0, 0, 0)):
    """oceano azul e continentes verdes"""
    m, nt = mat('fast')
    tc = n(nt, 'ShaderNodeTexCoord').outputs['Object']
    a = n(nt, 'ShaderNodeTexNoise', Scale=1.8, Detail=10.0, Roughness=0.6); L(nt, tc, a.inputs['Vector'])
    col = ramp(nt, [(0.5, (0.03, 0.12, 0.32)), (0.53, (0.12, 0.32, 0.12)), (0.7, (0.3, 0.45, 0.18))], a.outputs['Fac']).outputs[0]
    rough = ramp(nt, [(0.5, (0.25, 0.25, 0.25)), (0.53, (0.9, 0.9, 0.9))], a.outputs['Fac']).outputs[0]
    p = principled(nt, col, 0.6, spec=0.4)
    L(nt, rough, p.inputs['Roughness'])
    out(nt, p.outputs[0])
    return sphere('p_fast', r, loc, m, 192, 96)


def clouds(r=1.0, loc=(0, 0, 0), cover=0.55):
    """casca de nuvens um pouco acima da superfície; girar a casca move as nuvens"""
    m, nt = mat('clouds')
    tc = n(nt, 'ShaderNodeTexCoord').outputs['Object']
    a = n(nt, 'ShaderNodeTexNoise', Scale=3.0, Detail=8.0, Roughness=0.6); L(nt, tc, a.inputs['Vector'])
    fac = ramp(nt, [(cover, (0, 0, 0)), (cover + 0.15, (1, 1, 1))], a.outputs['Fac']).outputs[0]
    tr = n(nt, 'ShaderNodeBsdfTransparent')
    d = n(nt, 'ShaderNodeBsdfDiffuse'); d.inputs['Color'].default_value = (0.95, 0.95, 0.95, 1)
    ms = n(nt, 'ShaderNodeMixShader')
    L(nt, fac, ms.inputs[0]); L(nt, tr.outputs[0], ms.inputs[1]); L(nt, d.outputs[0], ms.inputs[2])
    out(nt, ms.outputs[0])
    return sphere('clouds', r * 1.012, loc, m, 128, 64)


def lander(loc=(0, 0, 0), rot=0.0):
    """módulo de pouso: corpo, escotilha, quatro pernas e antena"""
    root = bpy.data.objects.new('lander', None); link(root); root.location = loc; root.rotation_euler.z = rot
    hull = simple('hull', (0.72, 0.72, 0.7), 0.45, 0.3)
    foil = simple('foil', (0.75, 0.55, 0.15), 0.3, 0.9)
    dark = simple('hatch', (0.05, 0.05, 0.06), 0.6)
    parts = [box('body', (1.8, 1.8, 1.3), (0, 0, 1.75), hull),
             box('skirt', (2.0, 2.0, 0.35), (0, 0, 0.95), foil),
             box('hatch', (0.7, 0.04, 0.95), (0, -0.92, 1.7), dark),
             box('cap', (1.1, 1.1, 0.4), (0, 0, 2.6), hull),
             tube('mast', [(0.3, 0.3, 2.8), (0.3, 0.3, 3.4), (0.3, 0.3, 3.9)], [0.025] * 3, hull, kind='POLY')]
    for sx in (-1, 1):
        for sy in (-1, 1):
            parts.append(tube('leg', [(sx * 0.8, sy * 0.8, 1.1), (sx * 1.3, sy * 1.3, 0.5), (sx * 1.5, sy * 1.5, 0.05)], [0.05] * 3, hull, kind='POLY'))
            parts.append(box('pad', (0.4, 0.4, 0.06), (sx * 1.5, sy * 1.5, 0.03), hull))
    for o in parts:
        o.parent = root
    return root


def ground(colors, name='dust'):
    m, nt = mat(name)
    pos = n(nt, 'ShaderNodeNewGeometry').outputs['Position']
    a = n(nt, 'ShaderNodeTexNoise', Scale=0.6, Detail=8.0, Roughness=0.6); L(nt, pos, a.inputs['Vector'])
    col = ramp(nt, [(0.35, colors[0]), (0.65, colors[1])], a.outputs['Fac']).outputs[0]
    f = n(nt, 'ShaderNodeTexNoise', Scale=9.0, Detail=6.0, Roughness=0.6); L(nt, pos, f.inputs['Vector'])
    bp = n(nt, 'ShaderNodeBump', Strength=0.4, Distance=0.03); L(nt, f.outputs['Fac'], bp.inputs['Height'])
    out(nt, principled(nt, col, 0.95, spec=0.05, normal=bp.outputs[0]).outputs[0])
    return box('ground', (400, 400, 0.1), (0, 0, -0.05), m)
