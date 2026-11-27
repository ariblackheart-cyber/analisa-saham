-- Setup harian day trade (setup_harian.py) untuk tab Rekomendasi. Jalankan setelah 003_screener.sql.
-- Isi: breakout_20d, bull_flag, reclaim_ma20, oversold, oversold_bounce.
alter table saham_screener add column if not exists setup text[] not null default '{}';
