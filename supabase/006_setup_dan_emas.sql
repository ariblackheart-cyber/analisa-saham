-- Jalankan sekali di Supabase SQL Editor, setelah 003_screener.sql. Aman dijalankan ulang.

-- Setup harian day trade (setup_harian.py) untuk tab Rekomendasi. Jalankan setelah 003_screener.sql.
-- Isi: breakout_20d, bull_flag, reclaim_ma20, oversold, oversold_bounce.
alter table saham_screener add column if not exists setup text[] not null default '{}';

-- Harga dan analisa harian emas (tab Emas). Jalankan setelah 002_akses_dashboard.sql.
-- Harga dalam rupiah per gram (spot dunia × kurs), bukan harga Antam.
-- Kolom analisa hanya terisi pada tanggal saat analisa dijalankan.
create table if not exists saham_emas_harian (
  tanggal           date primary key,
  open numeric(14, 2), high numeric(14, 2), low numeric(14, 2), close numeric(14, 2),
  volume            bigint,
  usd_oz            numeric(12, 2),
  kurs              numeric(12, 2),
  perubahan_pct     numeric(8, 2),
  nilai_tren        numeric(4, 1),
  nilai_volume      numeric(4, 1),
  nilai_stochastic  numeric(4, 1),
  nilai_momentum    numeric(4, 1),
  nilai_candle      numeric(4, 1),
  nilai_total       numeric(4, 1),
  keputusan         text,
  pola_candle       text[],
  ma5 numeric(14, 2), ma20 numeric(14, 2), ma100 numeric(14, 2), rsi numeric(6, 2),
  volume_ratio      numeric(8, 2),
  support numeric(14, 2), resistance numeric(14, 2),
  stop_loss numeric(14, 2), target1 numeric(14, 2), target2 numeric(14, 2),
  rincian           jsonb,
  dibuat            timestamptz not null default now()
);
alter table saham_emas_harian enable row level security;
drop policy if exists saham_emas_baca on saham_emas_harian;
create policy saham_emas_baca on saham_emas_harian for select to authenticated
  using (exists (select 1 from saham_pemilik p where p.user_id = (select auth.uid())));
