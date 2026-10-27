-- Data asing harian dari file "Ringkasan Saham" BEI (diunggah lewat dashboard). Jalankan setelah 003_screener.sql.
create table if not exists saham_asing (
  kode          text not null,
  tanggal       date not null,
  close         numeric(14, 2),
  volume        bigint,
  nilai         numeric(20, 0),
  foreign_buy   bigint not null default 0,
  foreign_sell  bigint not null default 0,
  dibuat        timestamptz not null default now(),
  primary key (kode, tanggal)
);
create index if not exists saham_asing_tanggal on saham_asing (tanggal desc);
alter table saham_asing enable row level security;
drop policy if exists saham_asing_baca on saham_asing;
create policy saham_asing_baca on saham_asing for select to authenticated
  using (exists (select 1 from saham_pemilik p where p.user_id = (select auth.uid())));
drop policy if exists saham_asing_tulis on saham_asing;
create policy saham_asing_tulis on saham_asing for all to authenticated
  using (exists (select 1 from saham_pemilik p where p.user_id = (select auth.uid())))
  with check (exists (select 1 from saham_pemilik p where p.user_id = (select auth.uid())));

-- Akumulasi asing untuk N hari bursa terakhir yang datanya tersedia.
create or replace function saham_asing_akumulasi(p_hari int)
returns table (kode text, hari_data int, hari_net_buy int, net_lembar bigint, net_rupiah numeric,
               tanggal_awal date, tanggal_akhir date)
language sql stable set search_path = public as $$
  with tgl as (select distinct tanggal from saham_asing order by tanggal desc limit greatest(p_hari, 1))
  select a.kode, count(*)::int, (count(*) filter (where a.foreign_buy > a.foreign_sell))::int,
         sum(a.foreign_buy - a.foreign_sell)::bigint,
         round(sum((a.foreign_buy - a.foreign_sell) * coalesce(a.close, 0))),
         min(a.tanggal), max(a.tanggal)
  from saham_asing a join tgl using (tanggal) group by a.kode
$$;

create or replace function saham_asing_tanggal()
returns table (tanggal date, jumlah int)
language sql stable set search_path = public as $$
  select tanggal, count(*)::int from saham_asing group by tanggal order by tanggal desc limit 60
$$;

revoke execute on function saham_asing_akumulasi(int) from public, anon;
grant execute on function saham_asing_akumulasi(int) to authenticated, service_role;
revoke execute on function saham_asing_tanggal() from public, anon;
grant execute on function saham_asing_tanggal() to authenticated, service_role;
