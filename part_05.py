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
color = geo.node('color1')
copytopoints = geo.node('copytopoints1')
switch = geo.node('switch1')

# 01
testgeometry_rubbertoy.setDisplayFlag(True)
testgeometry_rubbertoy.parm('addshader').set(False)

# 02
definition = testgeometry_rubbertoy.type().definition()
sections = definition.sections()
for section in sections:
    print(section)
    #print(sections[section].definition())
definition = testgeometry_rubbertoy.type().definition()
section = definition.sections()['toylowres.jpg']
save_file = hou.getenv("HIP") + '/tex/toylowres.jpg'
section_file = file(save_file, "wb")
section_file.write(section.contents())
section_file.close()

# 03
attribvop = geo.createNode('attribvop')
attribvop.parm('bindclass').set(3)
attribvop.setInput(0,switch)

attribvop.setDisplayFlag(True)

# 04
geometryvopglobal = None
geometryvopoutput = None
for child in attribvop.children():
    if child.type().nameComponents()[2] == "geometryvopglobal":
        geometryvopglobal = child
    elif child.type().nameComponents()[2] == "geometryvopoutput":
        geometryvopoutput = child

uvcoords = attribvop.createNode('uvcoords')
texture = attribvop.createNode('texture')
texture.setNamedInput('uv',uvcoords,'uv')
geometryvopoutput.setNamedInput('Cd',texture,'clr')

# 05
#ユーザパラメータの設定今回は関係ないけどメモとして残しておく
'''
group = hou.ParmTemplateGroup((
hou.FolderParmTemplate("folder", "Physical", (
    hou.FloatParmTemplate("mass", "Mass", 1),
    hou.FloatParmTemplate("density", "Density", 1),
)),
hou.FolderParmTemplate("folder", "Divisions", (
    hou.FloatParmTemplate("divisions", "Divisions", 3),
    hou.ToggleParmTemplate("laser", "Laser Scan", default_value=True),
)),
))

attribvop.setParmTemplateGroup(group)
'''
# vop の promote parameter
vopParm = texture.insertParmGenerator('map',hou.vopParmGenType.Parameter,True)
vopParm.parm('parmlabel').set('Texture Map')

# 06
attribpromote = geo.createNode('attribpromote')
attribpromote.parm('inname').set('Cd')
attribpromote.parm('inclass').set(3)
attribpromote.parm('outclass').set(2)
attribpromote.setInput(0,attribvop)

# 07
attribtransfer = geo.createNode('attribtransfer')

attribtransfer.parm('pointattriblist').set("Cd")
attribtransfer.setInput(0,pointsfromvolume)
attribtransfer.setInput(1,attribpromote)

texture_switch = geo.createNode('switch','texture_switch')
texture_switch.parm('input').set(1)
texture_switch.setInput(0,color)
texture_switch.setInput(1,attribtransfer)

copytopoints.setInput(1,texture_switch)
copytopoints.setDisplayFlag(True)

# 08
attribvop.parm(vopParm.parm('parmname').eval()).set('$HIP/tex/toylowres.jpg')

# 全ノードをいい位置に移動
networkboxs = []
for node in geo.allSubChildren():
    #node.moveToGoodPosition()
    networkboxs.extend(node.findNetworkBoxes('*'))

geo.layoutChildren()

networkboxs = list(set(networkboxs))
for networkbox in networkboxs:
    networkbox.fitAroundContents()

# 保存
hou.hipFile.save("bricks_05.hip")