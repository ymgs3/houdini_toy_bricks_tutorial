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

        
obj = hou.node('/obj')
geo = hou.node('/obj/box_object')
copytopoints = geo.node('copytopoints1')
pointsfromvolume = geo.node('pointsfromvolume1')

# 01
color = geo.createNode('color')
color.parmTuple('color').set((1.0,0.0,0.0))
color.setInput(0,pointsfromvolume)
copytopoints.setInput(1,color)
copytopoints.parm('resettargetattribs').pressButton()

# 02
matnet = obj.createNode('matnet')
principledshader = matnet.createNode('principledshader','brick_material')
# 03
material = geo.createNode('material')
material_to_principledshader = material.relativePathTo(principledshader)
material.parm('shop_materialpath1').set(material_to_principledshader)
material.setInput(0,copytopoints)
material.setDisplayFlag(True)
material.setRenderFlag(True)

# 04
principledshader.parmTuple('basecolor').set((0.5,0.5,0.5))
principledshader.parm('basecolor_usePackedColor').set(True)

toolutils.sceneViewer().setCurrentState("renderregion")


# 全ノードをいい位置に移動
networkboxs = []
for node in hou.node("/").allSubChildren():
    node.moveToGoodPosition(relative_to_inputs=False,move_unconnected=False)
    # networkboxs.extend(node.findNetworkBoxes('*'))

networkboxs = list(set(networkboxs))
for networkbox in networkboxs:
    networkbox.fitAroundContents()

# 保存
hou.hipFile.save("bricks_03.hip")
