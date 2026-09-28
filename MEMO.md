# AR観光アプリ 引き継ぎメモ

## プロジェクト概要
- 観光地のスポットをARで案内するWebアプリ
- 現在のロケーション：羽黒山（山形県鶴岡市）
- 羽黒町観光協会と協力関係あり

## 技術構成
- フロントエンド：HTML/Vanilla JS
- バックエンド：Python（http.server）
- デプロイ：Render（無料プラン）
- データベース：Supabase
- リポジトリ：https://github.com/ohstuka-haruhi/ar-tourism
- 本番URL：https://ar-tourism.onrender.com

## 重要な注意事項
- Renderの無料プランはファイルへの書き込みが再起動で消えるため、データはすべてSupabaseに保存
- Supabase URL：https://pjcbjkjzxzwbxwmrebud.supabase.co
- Supabaseテーブル：spots、intro、pathways、analytics、tracks
  - spots：スポット一覧（id='main'の1行にJSONB配列として保存）
  - intro：案内メッセージ（id='main'の1行に保存）
  - analytics：閲覧ログ（セッションIDをキーに保存）
  - tracks：GPS軌跡（セッションIDをキーに保存）
  - pathways：通路・順路データ（UUIDをPKとして複数行）
- テーブルが存在しない場合は supabase_schema.sql をSupabase SQL Editorで実行して作成すること
- Supabase無料プランは1週間操作がないとプロジェクトが一時停止されるため注意

## 現在の機能
- 15言語対応（ja/en/zh/hi/es/fr/ar/bn/pt/ru/ur/id/de/ko/ms）
- AI道路認識矢印
- GPS軌跡記録・ヒートマップ
- 住所・営業時間フィールド
- 順路ナビ機能
- 通路録画モード（現地で参道を歩いて登録）
- 管理画面（admin.html）

## 登録済みスポット
- 山寺・蔵王エリアのスポット（既存）
- 羽黒山公共施設5箇所：いでは文化記念館、随神門前駐車場、羽黒山バス停、二の坂茶屋、山頂参集殿

## 今後の作業
- 掲載許可を取得したスポットを順次追加
- 通路ARナビの現地テスト（参道を歩いて通路データを記録）
- ランドマーク基準ナビの実装
- UI改善

## 作業方針
- 私は非エンジニアです
- やりたいことを日本語で説明するので、実装方法を提案してから実行してください
- 不明な点は質問してください
- 作業開始時は必ず「現状を確認して」と言ってファイルを読んでから始めてください

---

# セーブログ（新しいものが上）

## セーブ 2026-09-28 管理画面のパスワード保護(Basic認証)を実装（ローカルコミットまで）

### やったこと
- 管理画面(admin.html)と、管理者専用の書き込みAPIにBasic認証で鍵をかけた。
  - 鍵をかけた対象：admin.html の表示 / PUT /spots.json / PUT /intro /
    画像・ARマーカーのアップロード(PUT /qr/*.png, PUT /compiled/*.mind) / POST /routes.json
- 一般ユーザーが使う書き込みは鍵なしのまま（POST /analytics, /tracks, /api/analyze）。
  各種の読み取り(GET spots.json / intro / routes.json)も従来どおり無認証。
- パスワードはRenderの環境変数 ADMIN_USER / ADMIN_PASSWORD で管理。
  コードには直書きせず、予備の初期値も置かない。照合は hmac.compare_digest。
  環境変数が未設定のときは管理画面・書き込みを閉じる(503)。
- 実装は server.py のみ変更。index.html など一般利用には影響なし。
- 作業ブランチ：feature/admin-auth。

### 本番で有効化するために残っている作業（未実施）
- Renderのダッシュボードで環境変数 ADMIN_USER / ADMIN_PASSWORD を設定してから手動デプロイする。
  設定前にデプロイすると管理画面は503(閉じる)になるため順番に注意。
- GitHubへのpush・PR作成・デプロイはまだ未実施（ローカルのコミットまで）。

## セーブ 2026-07-22 テストモード実装〜本番反映まで完了、順路ナビの不具合が残課題

### ここまでにやったこと
- Claude Maxプランに加入。Claude Codeをデスクトップアプリ(Codeタブ)で使えるようにした
  （ターミナルではなく見やすい画面で作業する環境に移行）。
- ローカルのANTHROPIC_API_KEYは未設定＝Claude CodeはMaxログインで動作（API課金は発生しない）。
- 「現地(羽黒山5km圏内)でしかナビが起動しない」位置制限の仕組みを調査。
  - index.html 2761〜2827行あたりが起動ゲート。AREA_CENTER=(38.720,139.973)、半径5km。
  - 既存の開発用抜け穴 ?debug=1 で制限スキップ可能。
- 机の上/スマホで動作確認するため、テストモードを新規実装した。
  - 位置更新を applyPosition(lat,lng) に一本化（GPSもテストも同じ入口を通す）。
  - URLパラメータで位置ソースを指定：
    - ?mock=<スポットID> … 現在地を指定スポットに固定
    - ?mock=<緯度>,<経度> … 現在地を座標で固定
    - ?play=<順路ID> … 順路を自動再生／&speed=<倍率> で速度変更
  - テストモード時は起動ゲート(5km制限)を通過できるようにした。
  - 変更は index.html の1ファイルのみ（+92 -9）。一般ユーザーには無影響
    （合言葉なしの通常アクセスは従来通り）。
- git作業：feature/test-location-mode ブランチで作業→コミット→
  差出人を PADOC <info@padoc.jp> に設定（このプロジェクト限定）→GitHubへpush→
  PR #1 作成→mainへマージ(64c0600)→ローカルmainも同期済み。
- Renderで手動デプロイ(Deploy latest commit)実行→本番反映済み(Live)。
  - 本番URL: https://ar-tourism.onrender.com
  - Renderは autoDeploy: false（手動デプロイのみ）。無料プランのまま。
  - 環境変数 ANTHROPIC_API_KEY / SUPABASE_KEY / SUPABASE_URL は設定済み。

### 今の状態（動いている／動いていない）
- ✅ スマホ本番で ?debug=1&mock=haguro-bus-stop を開くと起動する。GPS表示が「🧪 TEST」。
- ✅ カメラ映像が映る。地図が羽黒山(須賀の滝周辺)を表示し、現在地マーカーが参道上に出る。
- ✅ 「近くのスポット」に羽黒山のスポット(いでは文化記念館・随神門授与所 等)が正しく並ぶ。
      → mock によるテスト座標は、地図・スポット表示には効いている。
- ❌ 「順路ナビ開始」を押しても矢印・到着ポップアップが出ない。
- ❌ 「通路」を押すと「GPS未取得 — しばらくお待ちください」が出て、OKで画面が固まりカメラ停止。
- ⚠️ 全体的に動作が重い（無料プランのコールドスタート＋AR/カメラ/地図同時＋GPS未取得の詰まり）。

### 推定原因（要検証）
- 順路ナビ／通路機能の一部が、テスト座標の共通入口 applyPosition を通らず、
  まだ本物のGPS(getCurrentPosition や 空の userPos)を直接見に行っている疑い。
- 併せて、順路ナビは s.inRoute / s.routeOrder を参照するが、
  spots.json にこのキーがなくSupabase側付与想定。順路データ側の準備不足の可能性も。

### 次にやること
1. クロードコードで「順路ナビ/通路がテスト座標を使っていない箇所」を特定（まず変更せず調査）。
   - GPS未取得判定を出している場所、順路ナビが位置を取得している場所を洗い出す。
2. 特定できたら、その箇所も applyPosition 経由（テスト座標対応）に直す。
3. 直したら再度スマホで ?debug=1&mock=haguro-bus-stop → 順路ナビ開始 で矢印・到着を確認。
4. 順路データ(inRoute/routeOrder)がSupabaseに入っているか確認。なければ順路の並び順を用意。
5. （別課題）羽黒山を通る順路データ(routes.json)を用意すれば ?play= の再生テストも可能に。
6. （別課題・フィールドテスト直前）Render有料化(Starter $7/月〜)でコールドスタート解消を検討。
   後からいつでも切替可。当日は事前に一度開いて「起こしておく」裏技でも代用可。

### 合言葉
- 中断＝「セーブ」／再開＝「リスタート」
- 再開時は、このMEMO.mdの最新セーブ内容をClaudeに貼るか、
  クロードコードに「MEMO.mdの最新セーブを見せて」と言って出力→Claudeに渡す。
