# houdini_soccerball_tutorial

## 概要
以下のチュートリアルの内容を python の hou モジュールで実装してみる
https://www.sidefx.com/tutorials/nodes-networks-digital-assets/?collection=74
https://d2wvmrjymyrujw.cloudfront.net/media/uploads/tutorial/foundations/brickify_houdini_foundation_tutorial.pdf

## 実行方法
基本はVisual Studio Code で記述して F5 で実行する
そのためにまずHoudini側の Python Source Editor で以下を実行しておく
```
import hrpyc
hrpyc.start_server()
```

https://www.sidefx.com/ja/docs/houdini/hom/rpc.html
https://www.sidefx.com/ja/docs/houdini/hom/hou/index

## houのインポート処理
Visual Studio Code である程度インテリセンスが効く様にしたいかつ問題なくコピペで実行できるようにするために各コードに以下のような感じで hou のインポート処理を書いてます。
いい方法があったら知りたい。
```
import os
# Houdini 上のpythonならhouはデフォルトインポートされているみたいなのでインポート処理を飛ばす
# 環境変数取れたら Houdini　上と判断
if not 'HFS' in os.environ:
    try:
        import hrpyc
        connection, hou = hrpyc.import_remote_module()
    except:
        # 最後に定義されているhouのautocompleteが効くみたいなので例外側でインポート　
        import hou

hou.hipFile.clear(True)
geo = hou.node("/obj").createNode('geo')
```

## ファイル構成
各パートごとにファイルを分割してパート1から順に実行していく想定。