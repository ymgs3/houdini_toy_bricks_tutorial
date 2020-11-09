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
else:
    # 最後に定義されているhouのautocompleteが効くみたいなので例外側でインポート　
    import hou
    import toolutils


obj = hou.node('/obj')
geo = hou.node('/obj/box_object')
testgeometry_rubbertoy = geo.node('testgeometry_rubbertoy1')
pointsfromvolume = geo.node('pointsfromvolume1')

# 01
switch = geo.createNode('switch')
switch.setInput(0,testgeometry_rubbertoy)
pointsfromvolume.setInput(0,switch)

# 02 
platonic = geo.createNode('platonic')
platonic.setParms(
    {
        "type":6,
        "radius":4,
        "t2":1.9,
    }
)

# 03
switch.setInput(1,platonic)
switch.parm('input').set(1)


# 04
switch.parm('input').set(0)


# 全ノードをいい位置に移動
networkboxs = []
for node in hou.node("/").allSubChildren():
    node.moveToGoodPosition(relative_to_inputs=False,move_unconnected=False)
    # networkboxs.extend(node.findNetworkBoxes('*'))

networkboxs = list(set(networkboxs))
for networkbox in networkboxs:
    networkbox.fitAroundContents()

# 保存
hou.hipFile.save("bricks_04.hip")