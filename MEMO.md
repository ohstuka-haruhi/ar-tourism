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
