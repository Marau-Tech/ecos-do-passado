from lib import *


def planet_quiet(r=1.0, loc=(0, 0, 0)):
    """poeira cinza lisa, sem relevo forte"""
    m, nt = mat('quiet')
    tc = n(nt, 'ShaderNodeTexCoord').outputs['Object']
    a = n(nt, 'ShaderNodeTexNoise', Scale=2.4, Detail=9.0, Roughness=0.55); L(nt, tc, a.inputs['Vector'])
    col = ramp(nt, [(0.35, (0.36, 0.36, 0.37)), (0.66, (0.66, 0.66, 0.67))], a.outputs['Fac']).outputs[0]
    f = n(nt, 'ShaderNodeTexNoise', Scale=30.0, Detail=6.0, Roughness=0.6); L(nt, tc, f.inputs['Vector'])
    bp = n(nt, 'ShaderNodeBump', Strength=0.2, Distance=0.02); L(nt, f.outputs['Fac'], bp.inputs['Height'])
    out(nt, principled(nt, col, 0.95, spec=0.1, normal=bp.outputs[0]).outputs[0])
    return sphere('p_quiet', r, loc, m, 192, 96)


def planet_kind(r=1.0, loc=(0, 0, 0)):
    """rosa e menta, com pontinhos de luz quente: cidades por toda parte"""
    m, nt = mat('kind')
    tc = n(nt, 'ShaderNodeTexCoord').outputs['Object']
    a = n(nt, 'ShaderNodeTexNoise', Scale=2.6, Detail=9.0, Roughness=0.55); L(nt, tc, a.inputs['Vector'])
    col = ramp(nt, [(0.38, (0.55, 0.80, 0.70)), (0.5, (0.92, 0.70, 0.75)), (0.66, (0.98, 0.88, 0.80))], a.outputs['Fac']).outputs[0]
    v = n(nt, 'ShaderNodeTexVoronoi', Scale=40.0); L(nt, tc, v.inputs['Vector'])
    dots = math_(nt, 'LESS_THAN', v.outputs['Distance'], 0.12)
    emis = mix(nt, dots, (0, 0, 0), (1.0, 0.75, 0.45))
    out(nt, principled(nt, col, 0.6, spec=0.3, emis=emis, emis_str=1.2).outputs[0])
    return sphere('p_kind', r, loc, m, 192, 96)


def pastel_sky():
    w = bpy.context.scene.world; nt = w.node_tree; nt.nodes.clear()
    tc = n(nt, 'ShaderNodeTexCoord')
    sp = n(nt, 'ShaderNodeSeparateXYZ'); L(nt, tc.outputs['Generated'], sp.inputs[0])
    g = ramp(nt, [(0.0, (1.0, 0.78, 0.66)), (0.15, (0.98, 0.66, 0.72)), (0.6, (0.55, 0.55, 0.85))], sp.outputs['Z']).outputs[0]
    b = n(nt, 'ShaderNodeBackground', Strength=0.9); L(nt, g, b.inputs['Color'])
    o = n(nt, 'ShaderNodeOutputWorld'); L(nt, b.outputs[0], o.inputs['Surface'])
