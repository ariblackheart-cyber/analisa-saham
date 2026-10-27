-- Berita dari feed RSS (berita.py, setiap 3 jam) dan kata kunci pencarian. Jalankan setelah 004_asing.sql.
create table if not exists saham_berita (
  link text primary key, judul text not null, ringkasan text, sumber text, terbit timestamptz,
  dibuat timestamptz not null default now()
);
create index if not exists saham_berita_terbit on saham_berita (terbit desc);
alter table saham_berita enable row level security;
drop policy if exists saham_berita_baca on saham_berita;
create policy saham_berita_baca on saham_berita for select to authenticated
  using (exists (select 1 from saham_pemilik p where p.user_id = (select auth.uid())));

create table if not exists saham_kata_kunci (
  kata text primary key check (length(trim(kata)) between 2 and 60),
  dibuat timestamptz not null default now()
);
alter table saham_kata_kunci enable row level security;
drop policy if exists saham_kata_kunci_semua on saham_kata_kunci;
create policy saham_kata_kunci_semua on saham_kata_kunci for all to authenticated
  using (exists (select 1 from saham_pemilik p where p.user_id = (select auth.uid())))
  with check (exists (select 1 from saham_pemilik p where p.user_id = (select auth.uid())));

-- Kode saham (4 huruf kapital) dicocokkan sebagai kata utuh dan peka huruf besar; kata lain tidak.
create or replace function saham_cari_berita(p_q text default null, p_hari int default 7)
returns table (link text, judul text, ringkasan text, sumber text, terbit timestamptz, cocok text[])
language sql stable set search_path = public as $$
  with kunci as (
    select k as kata from unnest(array[nullif(trim(p_q), '')]) k where k is not null
    union select kode from saham_watchlist where aktif and nullif(trim(p_q), '') is null
    union select kata from saham_kata_kunci where nullif(trim(p_q), '') is null
  ),
  b as (select * from saham_berita where terbit >= now() - make_interval(days => greatest(p_hari, 1)))
  select b.link, b.judul, b.ringkasan, b.sumber, b.terbit, array_agg(distinct k.kata order by k.kata)
  from b join kunci k on (
    case when k.kata ~ '^[A-Z]{4}$'
      then (b.judul || ' ' || coalesce(b.ringkasan, '')) ~ ('\m' || k.kata || '\M')
      else (b.judul || ' ' || coalesce(b.ringkasan, '')) ilike '%' || k.kata || '%' end)
  group by b.link, b.judul, b.ringkasan, b.sumber, b.terbit
  order by b.terbit desc limit 200
$$;
revoke execute on function saham_cari_berita(text, int) from public, anon;
grant execute on function saham_cari_berita(text, int) to authenticated, service_role;

-- Nama perusahaan (diisi otomatis oleh analisa.py) ikut dipakai untuk mencocokkan berita.
alter table saham_watchlist add column if not exists nama text;
