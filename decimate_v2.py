import bpy, bmesh, math, sys, time
src, dst, angle, ratio, min_faces = sys.argv[sys.argv.index("--")+1:]
angle=float(angle); ratio=float(ratio); min_faces=int(min_faces)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
rows=[]
for ob in [o for o in bpy.data.objects if o.type=="MESH"]:
    bpy.context.view_layer.objects.active=ob
    n0=len(ob.data.polygons)
    # 1) UV/노멀 분할로 끊긴 정점을 다시 붙인다 (dissolve는 연결된 면만 병합)
    bm=bmesh.new(); bm.from_mesh(ob.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-6)
    bm.to_mesh(ob.data); bm.free()
    if hasattr(ob.data,"has_custom_normals") and ob.data.has_custom_normals:
        with bpy.context.temp_override(object=ob): bpy.ops.mesh.customdata_custom_splitnormals_clear()
    # 2) 평면 병합 (delimit 없음)
    m=ob.modifiers.new("d","DECIMATE"); m.decimate_type="DISSOLVE"; m.angle_limit=math.radians(angle); m.delimit=set()
    bpy.ops.object.modifier_apply(modifier=m.name)
    m=ob.modifiers.new("t","TRIANGULATE"); bpy.ops.object.modifier_apply(modifier=m.name)
    n1=len(ob.data.polygons)
    # 3) 부품별 collapse — 작은 부품은 min_faces 바닥
    n2=n1
    if ratio<1 and n1>min_faces:
        m=ob.modifiers.new("c","DECIMATE"); m.decimate_type="COLLAPSE"; m.ratio=max(ratio,min_faces/n1); m.use_collapse_triangulate=True
        bpy.ops.object.modifier_apply(modifier=m.name); n2=len(ob.data.polygons)
    rows.append((n0,n1,n2,ob.name))
bpy.ops.export_scene.gltf(filepath=dst, export_format="GLB", export_apply=True)
rows.sort(reverse=True)
print("TOTAL orig=%d planar=%d final=%d"%tuple(sum(r[i] for r in rows) for i in range(3)))
for r in rows[:12]: print("  %6d -> %6d -> %6d  %s"%r)
