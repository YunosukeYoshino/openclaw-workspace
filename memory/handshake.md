# Handshake Protocol (main ⇄ ops/coach)

## main → coach（タスク完了時に記入）
以下を最大8行で記載する:
1) やったこと
2) 結果
3) 詰まり/違和感
4) 次回の懸念

## coach → improvements.md
handshakeの内容と直近の行動履歴から、改善点を1つだけ抽出して
improvements.md に追記するか、HEARTBEAT_OK で終わる。

## 不可侵ルール
- main は改善提案をしない
- coach はタスクを実行しない
