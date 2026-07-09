-- AR Tourism Supabase スキーマ
-- Supabase SQL Editor で実行してください

-- ─── spots テーブル（管理画面から登録したスポット一覧） ───
CREATE TABLE IF NOT EXISTS spots (
  id         TEXT PRIMARY KEY,
  data       JSONB NOT NULL DEFAULT '[]',
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE spots ENABLE ROW LEVEL SECURITY;

CREATE POLICY IF NOT EXISTS "spots_select" ON spots FOR SELECT USING (true);
CREATE POLICY IF NOT EXISTS "spots_insert" ON spots FOR INSERT WITH CHECK (true);
CREATE POLICY IF NOT EXISTS "spots_update" ON spots FOR UPDATE USING (true) WITH CHECK (true);
CREATE POLICY IF NOT EXISTS "spots_delete" ON spots FOR DELETE USING (true);

-- ─── intro テーブル（案内メッセージ） ───
CREATE TABLE IF NOT EXISTS intro (
  id         TEXT PRIMARY KEY,
  data       JSONB NOT NULL DEFAULT '{}',
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE intro ENABLE ROW LEVEL SECURITY;

CREATE POLICY IF NOT EXISTS "intro_select" ON intro FOR SELECT USING (true);
CREATE POLICY IF NOT EXISTS "intro_insert" ON intro FOR INSERT WITH CHECK (true);
CREATE POLICY IF NOT EXISTS "intro_update" ON intro FOR UPDATE USING (true) WITH CHECK (true);

-- ─── analytics テーブル（閲覧ログ） ───
CREATE TABLE IF NOT EXISTS analytics (
  id         TEXT PRIMARY KEY,
  data       JSONB NOT NULL DEFAULT '{}',
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE analytics ENABLE ROW LEVEL SECURITY;

CREATE POLICY IF NOT EXISTS "analytics_select" ON analytics FOR SELECT USING (true);
CREATE POLICY IF NOT EXISTS "analytics_insert" ON analytics FOR INSERT WITH CHECK (true);
CREATE POLICY IF NOT EXISTS "analytics_update" ON analytics FOR UPDATE USING (true) WITH CHECK (true);

-- ─── tracks テーブル（GPS軌跡） ───
CREATE TABLE IF NOT EXISTS tracks (
  id         TEXT PRIMARY KEY,
  data       JSONB NOT NULL DEFAULT '{}',
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE tracks ENABLE ROW LEVEL SECURITY;

CREATE POLICY IF NOT EXISTS "tracks_select" ON tracks FOR SELECT USING (true);
CREATE POLICY IF NOT EXISTS "tracks_insert" ON tracks FOR INSERT WITH CHECK (true);
CREATE POLICY IF NOT EXISTS "tracks_update" ON tracks FOR UPDATE USING (true) WITH CHECK (true);

-- ─── pathways テーブル（通路・順路データ） ───
CREATE TABLE IF NOT EXISTS pathways (
  id         UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  name       TEXT,
  points     JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE pathways ENABLE ROW LEVEL SECURITY;

CREATE POLICY IF NOT EXISTS "pathways_select" ON pathways FOR SELECT USING (true);
CREATE POLICY IF NOT EXISTS "pathways_insert" ON pathways FOR INSERT WITH CHECK (true);
CREATE POLICY IF NOT EXISTS "pathways_delete" ON pathways FOR DELETE USING (true);
