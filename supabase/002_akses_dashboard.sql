-- Akses dashboard: hanya akun yang terdaftar di saham_pemilik yang bisa membaca/menulis tabel saham.
-- Jalankan setelah schema.sql. Lalu daftarkan akunmu:
--   insert into saham_pemilik (user_id) select id from auth.users where email = 'EMAIL_KAMU';

create table if not exists saham_pemilik (
  user_id uuid primary key references auth.users (id) on delete cascade,
  dibuat  timestamptz not null default now()
);
alter table saham_pemilik enable row level security;

drop policy if exists saham_pemilik_diri on saham_pemilik;
create policy saham_pemilik_diri on saham_pemilik
  for select to authenticated using (user_id = (select auth.uid()));

-- Baca: semua tabel saham
do $$
declare t text;
begin
  foreach t in array array['saham_watchlist','saham_transaksi','saham_harga_harian',
                           'saham_analisa_harian','saham_fundamental'] loop
    execute format('drop policy if exists %I on %I', t || '_baca', t);
    execute format($p$create policy %I on %I for select to authenticated
                     using (exists (select 1 from saham_pemilik p where p.user_id = (select auth.uid()))))$p$,
                   t || '_baca', t);
  end loop;
end $$;

-- Tulis: watchlist dan transaksi bisa diubah dari dashboard
do $$
declare t text;
begin
  foreach t in array array['saham_watchlist','saham_transaksi'] loop
    execute format('drop policy if exists %I on %I', t || '_tulis', t);
    execute format($p$create policy %I on %I for all to authenticated
                     using (exists (select 1 from saham_pemilik p where p.user_id = (select auth.uid())))
                     with check (exists (select 1 from saham_pemilik p where p.user_id = (select auth.uid()))))$p$,
                   t || '_tulis', t);
  end loop;
end $$;

-- View posisi dihitung dengan hak akses pengguna (RLS tetap berlaku)
grant execute on function saham_hitung_posisi() to authenticated;
