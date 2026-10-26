-- Skema database Analisa Saham untuk Supabase.
-- Semua tabel memakai awalan saham_ supaya bisa berbagi project dengan aplikasi lain (misalnya dompetku).
-- Jalankan sekali: Supabase → SQL Editor → tempel seluruh file ini → Run.
-- Aman dijalankan ulang (memakai IF NOT EXISTS).

-- Daftar saham yang dianalisa setiap hari
create table if not exists saham_watchlist (
  kode      text primary key check (kode = upper(kode)),
  aktif     boolean not null default true,
  catatan   text,
  dibuat    timestamptz not null default now()
);

-- Catatan jual beli (1 lot = 100 lembar)
create table if not exists saham_transaksi (
  id        bigint generated always as identity primary key,
  tanggal   date not null,
  kode      text not null check (kode = upper(kode)),
  aksi      text not null check (aksi in ('beli', 'jual')),
  lot       integer not null check (lot > 0),
  harga     numeric(14, 2) not null check (harga > 0),
  catatan   text,
  dibuat    timestamptz not null default now()
);
create index if not exists saham_transaksi_kode_tanggal on saham_transaksi (kode, tanggal);

-- Harga harian (OHLCV)
create table if not exists saham_harga_harian (
  kode      text not null,
  tanggal   date not null,
  open      numeric(14, 2),
  high      numeric(14, 2),
  low       numeric(14, 2),
  close     numeric(14, 2),
  volume    bigint,
  primary key (kode, tanggal)
);

-- Hasil analisa teknikal per hari
create table if not exists saham_analisa_harian (
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
  keputusan         text check (keputusan in ('BELI', 'PANTAU', 'TUNGGU', 'HINDARI')),
  pola_candle       text[],
  ma5 numeric(14, 2), ma20 numeric(14, 2), ma100 numeric(14, 2),
  rsi numeric(6, 2), macd numeric(12, 4), macd_signal numeric(12, 4),
  stoch_k numeric(6, 2), stoch_d numeric(6, 2),
  stoch_rsi_k numeric(6, 2), stoch_rsi_d numeric(6, 2),
  volume_ratio      numeric(8, 2),
  support numeric(14, 2), resistance numeric(14, 2),
  stop_loss numeric(14, 2), target1 numeric(14, 2), target2 numeric(14, 2),
  rincian           jsonb,          -- rincian poin tiap aspek
  dibuat            timestamptz not null default now(),
  primary key (kode, tanggal)
);

-- Data fundamental per tanggal pengambilan
create table if not exists saham_fundamental (
  kode          text not null,
  tanggal       date not null,
  per numeric(12, 2), pbv numeric(12, 2), roe numeric(8, 4), der numeric(10, 2),
  npm numeric(8, 4), growth_pendapatan numeric(8, 4), growth_laba numeric(8, 4),
  market_cap    numeric(20, 0),
  nilai         numeric(4, 1),
  kuartal       jsonb,              -- laba rugi 5 kuartal terakhir
  primary key (kode, tanggal)
);

-- Analisa terbaru per saham
create or replace view saham_analisa_terbaru as
select distinct on (kode) *
from saham_analisa_harian
order by kode, tanggal desc;

-- Posisi saat ini (lot dan harga rata-rata tertimbang, tidak berubah saat menjual)
-- Dihitung ulang dengan urutan transaksi, sama seperti portofolio.py.
create or replace function saham_hitung_posisi()
returns table (kode text, lot bigint, harga_rata2 numeric, modal numeric)
language plpgsql stable
set search_path = public
as $$
declare
  r record;
  cur_kode text := null;
  lembar bigint := 0;
  avg numeric := 0;
begin
  for r in select t.* from saham_transaksi t order by t.kode, t.tanggal, t.id loop
    if cur_kode is distinct from r.kode then
      if cur_kode is not null and lembar > 0 then
        kode := cur_kode; lot := lembar / 100; harga_rata2 := round(avg, 2); modal := round(avg * lembar);
        return next;
      end if;
      cur_kode := r.kode; lembar := 0; avg := 0;
    end if;
    if r.aksi = 'beli' then
      avg := (avg * lembar + r.harga * r.lot * 100) / (lembar + r.lot * 100);
      lembar := lembar + r.lot * 100;
    else
      lembar := greatest(lembar - r.lot * 100, 0);
      if lembar = 0 then avg := 0; end if;
    end if;
  end loop;
  if cur_kode is not null and lembar > 0 then
    kode := cur_kode; lot := lembar / 100; harga_rata2 := round(avg, 2); modal := round(avg * lembar);
    return next;
  end if;
end $$;

create or replace view saham_posisi as
select p.*, a.close as harga_terakhir,
       round((a.close - p.harga_rata2) * p.lot * 100) as untung_rugi,
       round((a.close / nullif(p.harga_rata2, 0) - 1) * 100, 2) as untung_rugi_pct,
       a.keputusan, a.nilai_total, a.tanggal as tanggal_analisa
from saham_hitung_posisi() p
left join saham_analisa_terbaru a using (kode);

-- Keamanan: aktifkan RLS tanpa policy publik.
-- Hanya service_role key (dipakai GitHub Actions) yang bisa membaca/menulis.
-- Kamu tetap bisa mengedit lewat Table Editor di dashboard Supabase.
alter table saham_watchlist      enable row level security;
alter table saham_transaksi      enable row level security;
alter table saham_harga_harian   enable row level security;
alter table saham_analisa_harian enable row level security;
alter table saham_fundamental    enable row level security;
alter view saham_analisa_terbaru set (security_invoker = true);
alter view saham_posisi          set (security_invoker = true);
revoke execute on function saham_hitung_posisi() from public, anon, authenticated;
grant execute on function saham_hitung_posisi() to service_role;

-- Isi awal
insert into saham_watchlist (kode) values ('RAJA') on conflict do nothing;
