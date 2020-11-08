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

# 01
geo = hou.node("/obj").createNode('geo',"testgeometry_rubbertoy_object")
testgeometry_rubbertoy = geo.createNode('testgeometry_rubbertoy')

testgeometry_rubbertoy.setParms(
    {
        "uniformscale":3,
        "ty":1.5,
    }
)

pane = toolutils.sceneViewer()
pane.setViewportLayout(hou.geometryViewportLayout.Quad)
viewports = pane.viewports()
view_port_type = [
    hou.geometryViewportType.Top,
    hou.geometryViewportType.Front,
    hou.geometryViewportType.Right,
    hou.geometryViewportType.Perspective,
]

# 処理が帰ってこないことがあるので一旦やらない。無限ループになる？
'''
for i, viewport in enumerate(viewports):
    if viewport.type() != view_port_type[i]:
        viewport.changeType(view_port_type[i])
    viewport.homeAll()
'''

# 02
pointsfromvolume = geo.createNode('pointsfromvolume')

pointsfromvolume.setInput(0,testgeometry_rubbertoy)
pointsfromvolume.setDisplayFlag(True)

# 03
geo_box = hou.node("/obj/box_object")
polybevel = hou.node("/obj/box_object/polybevel1")

testgeometry_rubbertoy.setSelected(True,True)
pointsfromvolume.setSelected(True)
copyNodes = hou.copyNodesTo(hou.selectedNodes(), geo_box)
geo.destroy()
geo = geo_box
testgeometry_rubbertoy = copyNodes[0]
pointsfromvolume = copyNodes[1]

# 04
polybevel.setDisplayFlag(True)

# 05
copytopoints = geo.createNode('copytopoints')
copytopoints.parm("pack").set(True)
copytopoints.setInput(0,polybevel)
copytopoints.setInput(1,pointsfromvolume)
copytopoints.setDisplayFlag(True)

# 06
pointsfromvolume.parm("particlesep").set(0.2)

# 07
settings = toolutils.sceneViewer().curViewport().settings()
settings.setDistanceBasedPackedCulling(False)

# 08
network_box = geo.createNetworkBox()

network_box.setPosition(polybevel.position())
network_box.addNode(polybevel)
node = polybevel.inputs()
while(len(node) > 0):
    node = node[0]
    network_box.addNode(node)
    node = node.inputs()

network_box.fitAroundContents()

# 全ノードをいい位置に移動
for node in hou.node("/").allSubChildren():
    node.moveToGoodPosition()

network_box.fitAroundContents()
network_box.setMinimized(True)

# 保存
hou.hipFile.save("bricks_02.hip")