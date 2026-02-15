# improvements log (append-only)

<!-- テンプレート：以下の形式で末尾に追記する -->

## 2026-02-15 — iTunes RSS API タイムアウト問題
- Symptom: appstore-top-gainers.py がレビュー取得時にハングアップする（iTunes RSS API応答なし）
- Root cause (config / prompt / procedure / permission / tool / external): 外部 (iTunes RSS API) - レスポンスが遅い、またはデータ形式が変わっている
- Fix (smallest change): urllib.request.urlopen に timeout=30 を追加し、例外を明示的に処理して次のカテゴリへスキップ。さらにテストモードと手動入力モードを追加してAPI依存を減らす
- Preventive check (1 line): API呼び出し前にテストリクエストを実行し、タイムアウト値を動的に調整
- Expected impact: ハングアップ防止、全体的な実行時間短縮、APIが不安定でもツールが動くようになる
- Risk & rollback: レビュー数が減る可能性あり（タイムアウト時） → rollback: timeout値を大きくする
- Status: applied

## YYYY-MM-DD — [short title]
- Symptom:
- Root cause (config / prompt / procedure / permission / tool / external):
- Fix (smallest change):
- Preventive check (1 line):
- Expected impact:
- Risk & rollback:
- Status: proposed / applied / verified
