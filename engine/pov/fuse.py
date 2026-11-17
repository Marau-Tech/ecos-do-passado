"""Fusão da mão numa superfície contínua (Geometry Nodes).

A gaiola da mão é feita de tubos (palma, dedos, polegar). Depois do skinning de cada frame,
este modificador converte a malha em volume e de volta em malha, e suaviza a superfície:
os dedos saem da palma sem emenda, com a membrana e os nós formados pela própria união.
As coordenadas de repouso ('pov_rest') e o UV são copiados da gaiola para a malha nova, para
a textura acompanhar a pele. Tudo é função da geometria do frame: determinístico.
"""
import bpy


def _node(nt, typ, **props):
    n = nt.nodes.new(typ)
    for k, v in props.items():
        setattr(n, k, v)
    return n


def _set(node, name, value):
    """Valor de entrada por nome; em versões em que a opção virou propriedade, usa a propriedade."""
    if name in node.inputs:
        node.inputs[name].default_value = value
        return True
    return False


def fuse_group(voxel=0.0008, blur=4, material=None, name='pov_fuse'):
    key = f'{name}_{voxel:.5f}_{blur}_{material.name if material else ""}'
    if key in bpy.data.node_groups:
        return bpy.data.node_groups[key]
    nt = bpy.data.node_groups.new(key, 'GeometryNodeTree')
    nt.interface.new_socket('Geometry', in_out='INPUT', socket_type='NodeSocketGeometry')
    nt.interface.new_socket('Geometry', in_out='OUTPUT', socket_type='NodeSocketGeometry')
    gi = _node(nt, 'NodeGroupInput')
    go = _node(nt, 'NodeGroupOutput')
    L = nt.links.new

    m2v = _node(nt, 'GeometryNodeMeshToVolume')
    if hasattr(m2v, 'resolution_mode'):
        m2v.resolution_mode = 'VOXEL_SIZE'
    else:
        _set(m2v, 'Resolution Mode', 'Size')
    _set(m2v, 'Voxel Size', voxel)
    _set(m2v, 'Interior Band Width', voxel * 3)
    L(gi.outputs[0], m2v.inputs['Mesh'])

    v2m = _node(nt, 'GeometryNodeVolumeToMesh')
    if hasattr(v2m, 'resolution_mode'):
        v2m.resolution_mode = 'GRID'
    else:
        _set(v2m, 'Resolution Mode', 'Grid')
    _set(v2m, 'Threshold', 0.1)
    _set(v2m, 'Adaptivity', 0.0)
    L(m2v.outputs[0], v2m.inputs['Volume'])

    # suavização: arredonda as junções (membrana, nós) sem perder o volume dos dedos
    pos = _node(nt, 'GeometryNodeInputPosition')
    bl = _node(nt, 'GeometryNodeBlurAttribute', data_type='FLOAT_VECTOR')
    bl.inputs['Iterations'].default_value = blur
    L(pos.outputs[0], bl.inputs['Value'])
    sp = _node(nt, 'GeometryNodeSetPosition')
    L(v2m.outputs[0], sp.inputs['Geometry'])
    L(bl.outputs[0], sp.inputs['Position'])
    geo = sp.outputs[0]

    # copia 'pov_rest' (ponto) e UVMap (canto) da gaiola deformada
    for attr, dtype, domain in (('pov_rest', 'FLOAT_VECTOR', 'POINT'), ('UVMap', 'FLOAT2', 'CORNER')):
        na = _node(nt, 'GeometryNodeInputNamedAttribute', data_type='FLOAT_VECTOR')
        na.inputs['Name'].default_value = attr
        sn = _node(nt, 'GeometryNodeSampleNearestSurface', data_type='FLOAT_VECTOR')
        L(gi.outputs[0], sn.inputs['Mesh'])
        L(na.outputs['Attribute'], sn.inputs['Value'])
        st = _node(nt, 'GeometryNodeStoreNamedAttribute', data_type=dtype, domain=domain)
        st.inputs['Name'].default_value = attr
        L(geo, st.inputs['Geometry'])
        L(sn.outputs['Value'], st.inputs['Value'])
        geo = st.outputs[0]

    sm = _node(nt, 'GeometryNodeSetShadeSmooth')
    L(geo, sm.inputs['Geometry'])
    geo = sm.outputs[0]
    if material is not None:
        sm2 = _node(nt, 'GeometryNodeSetMaterial')
        sm2.inputs['Material'].default_value = material
        L(geo, sm2.inputs['Geometry'])
        geo = sm2.outputs[0]
    L(geo, go.inputs[0])
    return nt


def add_fuse(ob, material, voxel=0.0008, blur=4):
    mod = ob.modifiers.new('fuse', 'NODES')
    mod.node_group = fuse_group(voxel, blur, material)
    return mod
