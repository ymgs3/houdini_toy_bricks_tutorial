import os
# Houdini 上のpythonならhouはデフォルトインポートされているみたいなのでインポート処理を飛ばす
# 環境変数取れたら Houdini　上と判断
if not 'HFS' in os.environ:
    try:
        import hrpyc
        connection, hou = hrpyc.import_remote_module()
        toolutils = connection.modules["toolutils"]
    except:
        # 最後に定義されているhouのautocompleteが効くみたいなので例外側でインポート　
        import hou
        import toolutils

import math

# 01
hou.hipFile.clear(True)
project_dir = hou.getenv("HOME") + "/HoudiniProjects/" + "brickify_lesson2"
if not os.path.exists(project_dir):
    os.makedirs(project_dir)
hou.putenv("JOB", project_dir)

print(hou.getenv("JOB"))

# 02
geo = hou.node("/obj").createNode('geo',"box_object")
box = geo.createNode('box')
box.parmTuple('size').set((0.2,0.2,0.2))
box.parm('type').set(1)
box.parm('surftype').set(4)
box.parmTuple('divrate').set((3,2,3))

# 03
prim_indexes = []
for prim in box.geometry().prims():
    normal = prim.normal()
    '''
    points = prim.points()
    normal = hou.Vector3(0,1,0)
    if len(points) == 4:
        v0 = points[0].position() - points[2].position()
        v1 = points[1].position() - points[3].position()
        normal = v1.cross(v0)
    if len(points) == 3:
        v0 = points[1].position() - points[0].position()
        v1 = points[2].position() - points[0].position()
        normal = v1.cross(v0)

    normal = normal.normalized()
    '''
    if (normal.dot(hou.Vector3(0,1,0)) >= 0.8):
        prim_indexes.append(prim.number())

print(prim_indexes)
polyextrude = geo.createNode('polyextrude')
polyextrude.parm("group").set(' '.join(map(str, prim_indexes)))
polyextrude.parm("inset").set(0.04)
# この後操作するprimを取りやすくする
polyextrude.parm("outputfrontgrp").set(True)
polyextrude.parm("frontgrp").set("top_face")

polyextrude.setInput(0,box)

# 04
# Make Circle の処理がわからない。。
edit = geo.createNode('edit')
edit.setInput(0,polyextrude)
edit.setDisplayFlag(True)

for parm in edit.allParms():
    print(parm.name())

# タブの切り替え
edit.parmTuple('s').set((1.5,1,1.5))
edit.parm("modeswitcher1").set(1)
edit.parm("group").set(polyextrude.parm("frontgrp").eval())
edit.parm("fd").set(0)
edit.parm("flood").pressButton()
# タブの切り替え
edit.parm("modeswitcher1").set(0)
edit.parm("apply").pressButton()

# 05
polyextrude2 = geo.createNode('polyextrude')
polyextrude2.parm("group").set(polyextrude.parm("frontgrp").eval())
polyextrude2.parm("dist").set(0.05)
polyextrude2.setInput(0,edit)

prim_indexes = []
for prim in edit.geometry().prims():
    normal = prim.normal()
    if (normal.dot(hou.Vector3(0,-1,0)) >= 0.8):
        prim_indexes.append(prim.number())
polyextrude3 = geo.createNode('polyextrude')
polyextrude3.parm("group").set(' '.join(map(str, prim_indexes)))
polyextrude3.parm("inset").set(0.025)
polyextrude3.parm("outputfrontgrp").set(True)
polyextrude3.parm("frontgrp").set("bottom_face")
polyextrude3.setInput(0,polyextrude2)

polyextrude4 = geo.createNode('polyextrude')
polyextrude4.parm("group").set(polyextrude3.parm("frontgrp").eval())
polyextrude4.parm("dist").set(-0.175)
polyextrude4.setInput(0,polyextrude3)
polyextrude4.setDisplayFlag(True)

# 07
groupcreate = geo.createNode('groupcreate')
groupcreate.setParms(
    {
        "groupname":"bevel_edges",
        "grouptype":2,
        "groupbase":False,
        "groupedges":True,
        "dominedgeangle":True,
        "domaxedgeangle":True,
        "minedgeangle":89,
        "maxedgeangle":91,
    }
)
groupcreate.setInput(0,polyextrude4)

# 08
polybevel = geo.createNode('polybevel')
polybevel.setParms(
    {
        "group":"bevel_edges",
        "grouptype":2,
        "offset":0.006,
        "filletshape":4,
        "divisions":3,
    }
)
polybevel.setInput(0,groupcreate)
polybevel.setDisplayFlag(True)

# 09
settings = toolutils.sceneViewer().curViewport().settings()
# オブジェクト用のGeometryViewportDisplaySetを取得します。
tmplset = settings.displaySet(hou.displaySetType.SelectedObject)
# このサブセットのシェーディングモードをワイヤーフレーム表示にするようにHoudiniに伝えます。
tmplset.setShadedMode(hou.glShadingType.Smooth)


# 全ノードをいい位置に移動
for node in hou.node("/").allSubChildren():
    node.moveToGoodPosition()

# 保存
hou.hipFile.save("bricks_01.hip")