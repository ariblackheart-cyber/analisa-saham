-- Tabel hasil pemindaian harian (tab Rekomendasi). Jalankan setelah 002_akses_dashboard.sql.
create table if not exists saham_screener (
  kode              text not null,
  tanggal           date not null,
  close             numeric(14, 2),
  perubahan_pct     numeric(8, 2),
  nilai_tren        numeric(4, 1),
  nilai_volume      numeric(4, 1),
  nilai_stochastic  numeric(4, 1),
  nilai_momentum    numeric(4, 1),
  nilai_candle      numeric(4, 1),
  nilai_total       numeric(4, 1),
  keputusan         text,
  pola_candle       text[],
  ma20 numeric(14, 2), ma100 numeric(14, 2), rsi numeric(6, 2),
  volume_ratio      numeric(8, 2),
  nilai_transaksi   numeric(20, 0),
  support numeric(14, 2), stop_loss numeric(14, 2), target1 numeric(14, 2),
  rincian           jsonb,
  dibuat            timestamptz not null default now(),
  primary key (kode, tanggal)
);
create index if not exists saham_screener_tanggal on saham_screener (tanggal desc, nilai_total desc);
alter table saham_screener enable row level security;
drop policy if exists saham_screener_baca on saham_screener;
create policy saham_screener_baca on saham_screener for select to authenticated
  using (exists (select 1 from saham_pemilik p where p.user_id = (select auth.uid())));
