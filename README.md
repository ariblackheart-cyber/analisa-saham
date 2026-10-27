# Analisa Saham Harian

Analisa teknikal otomatis untuk saham Bursa Efek Indonesia. Setiap hari bursa, GitHub Actions mengambil data harga dari Yahoo Finance, menghitung indikator, lalu menyimpan laporan dan grafik ke repo ini.

**Dashboard:** https://ariblackheart-cyber.github.io/analisa-saham/ (login dengan akun Supabase). Berisi grafik, nilai tiap aspek, portofolio, simulasi average down, dan form catat transaksi.

## Ringkasan terbaru

<!-- RINGKASAN:START -->
| Saham | Tanggal | Close | Perubahan | Tren | Volume | Stoch | Momentum | Candle | Total | Keputusan | Fundamental |
|---|---|---|---|---|---|---|---|---|---|---|---|
| [AALI](reports/AALI/latest.md) | 2026-10-27 | 9.800 | +3.16% | 10.0 | 9.1 | 3.5 | 9.5 | 8.3 | **8.2** | 🟢 BELI | 9.2 Kuat |
| [BBRI](reports/BBRI/latest.md) | 2026-10-27 | 2.900 | -0.34% | 2.0 | 5.8 | 5.8 | 3.0 | 7.9 | **4.6** | ⚪ TUNGGU | 8.5 Kuat |
| [BRIS](reports/BRIS/latest.md) | 2026-10-27 | 1.050 | -0.47% | 2.0 | 0.4 | 6.5 | 4.0 | 4.3 | **3.3** | 🔴 HINDARI | 9.7 Kuat |
| [RAJA](reports/RAJA/latest.md) | 2026-10-27 | 452 | -4.24% | 0.0 | 3.7 | 5.0 | 4.0 | 4.4 | **3.2** | 🔴 HINDARI | 9.4 Kuat |
<!-- RINGKASAN:END -->

## Rekomendasi teknikal

<!-- REKOMENDASI:START -->
10 nilai teknikal tertinggi dari 81 saham likuid yang dipindai (2026-10-27). Hasil aturan mekanis, bukan rekomendasi investasi.

| # | Saham | Close | Perubahan | Total | Keputusan | Tren | Volume | Stoch | Momentum | Candle |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **PWON** | 294 | +3.52% | **8.5** | 🟢 BELI | 10.0 | 9.7 | 5.8 | 9.5 | 6.5 |
| 2 | **AALI** | 9.800 | +3.16% | **8.2** | 🟢 BELI | 10.0 | 9.1 | 3.5 | 9.5 | 8.3 |
| 3 | **UNTR** | 26.500 | +6.00% | **8.1** | 🟢 BELI | 10.0 | 7.3 | 5.0 | 9.5 | 8.5 |
| 4 | **INTP** | 5.950 | +5.78% | **8.1** | 🟢 BELI | 10.0 | 9.7 | 4.2 | 7.5 | 8.5 |
| 5 | **AADI** | 11.700 | +1.52% | **8.1** | 🟢 BELI | 10.0 | 9.6 | 6.5 | 9.5 | 2.9 |
| 6 | **CTRA** | 585 | +1.74% | **7.9** | 🟢 BELI | 10.0 | 8.8 | 5.0 | 7.5 | 7.8 |
| 7 | **AKRA** | 1.435 | +2.50% | **7.5** | 🟢 BELI | 8.0 | 10.0 | 5.8 | 7.5 | 5.6 |
| 8 | **JSMR** | 2.850 | +5.56% | **7.4** | 🟢 BELI | 8.0 | 9.9 | 5.0 | 7.5 | 6.2 |
| 9 | **HMSP** | 675 | +5.47% | **7.4** | 🟢 BELI | 7.0 | 8.9 | 4.2 | 7.5 | 10.0 |
| 10 | **DSNG** | 1.470 | +5.00% | **7.2** | 🟢 BELI | 8.0 | 6.6 | 5.8 | 7.5 | 8.5 |
<!-- REKOMENDASI:END -->

Setiap hari bursa, semua saham di `universe.txt` (±85 saham likuid) dinilai dengan aturan yang sama. Saham dengan rata-rata transaksi di bawah Rp 5 miliar/hari dilewati. Daftar lengkap dan alasannya ada di tab **Rekomendasi** di dashboard. Ubah daftar saham di `universe.txt` dan batas likuiditas di `screener.py`.

## Data asing

Data beli/jual asing tidak tersedia di Yahoo Finance, dan situs BEI menolak akses otomatis dari server. Fitur ini **disembunyikan** di dashboard (cek foreign flow langsung di Stockbit); aktifkan dengan mengubah `FITUR_ASING = true` di `docs/index.html`. Jika diaktifkan, datanya diunggah manual: unduh file **Ringkasan Saham** harian dari idx.co.id, lalu unggah di dashboard (tab **Catat**, beberapa file sekaligus boleh). Tab **Rekomendasi** lalu menampilkan net beli asing 1 hari, 1 minggu, dan 1 bulan, bisa diurutkan berdasarkan asing, dan bisa disaring ke saham yang diakumulasi asing (net beli dan net beli di minimal 60% hari).

## Berita

Setiap 3 jam, workflow **Berita** mengambil berita dari feed RSS di `feeds.txt` (Antara Ekonomi Bursa, detikFinance, Liputan6 Bisnis) dan menyimpannya 30 hari. Di dashboard, berita bisa dicari dengan kata kunci; kode saham yang dipantau otomatis jadi kata kunci, dan kata kunci lain (misalnya nikel atau suku bunga) bisa ditambahkan di tab **Catat**. Halaman detail saham menampilkan berita yang menyebut kode saham itu.

## Portofolio saya

<!-- PORTOFOLIO:START -->
_Portofolio tidak ditampilkan di repo. Lihat di dashboard (perlu login)._
<!-- PORTOFOLIO:END -->

## Isi laporan

Setiap laporan (`reports/<KODE>/latest.md`) berisi:

1. **Candlestick**: warna, proporsi badan dan sumbu, serta pola doji, marubozu, hammer, hanging man, shooting star, inverted hammer, spinning top, engulfing, piercing line, dark cloud cover, harami, morning star dan evening star.
2. **Volume**: volume hari ini dibanding rata-rata 20 hari, dan porsi volume candle hijau vs merah selama 5 hari.
3. **Stochastic (14,3,3) dan Stoch RSI (14,14,3,3)**: zona overbought/oversold dan persilangan K–D.
4. **Tren**: posisi harga terhadap MA5, MA20, MA100, kemiringan MA20, dan persilangan MA5–MA20.
5. **Bollinger Bands (20,2)**: posisi harga di dalam pita dan deteksi squeeze.
6. **MACD (12,26,9) dan RSI (14)**.
7. **Support & resistance** 20 hari.
8. **Fundamental**: PER, PBV, ROE, DER, margin laba, pertumbuhan pendapatan dan laba (YoY), serta laba rugi 5 kuartal terakhir.

Tabel ringkasan di atas diurutkan dari nilai teknikal tertinggi.

## Cara penilaian

Setiap aspek teknikal dinilai **0–10**. Nilai dimulai dari 5 (netral), lalu ditambah atau dikurangi poin sesuai kondisi. Semua rincian poinnya ditampilkan di bagian akhir setiap laporan.

| Aspek | Bobot | Yang dinilai |
|---|---|---|
| Tren | 25% | Posisi harga terhadap MA5/MA20/MA100, arah MA20 |
| Volume | 20% | Volume vs rata-rata 20 hari searah kenaikan/penurunan harga, volume hijau vs merah 5 hari |
| Stochastic | 20% | Stochastic dan Stoch RSI: posisi dan persilangan K–D, zona oversold/overbought |
| Momentum | 20% | MACD vs sinyal, MACD vs nol, arah histogram, zona RSI |
| Candle | 15% | Warna dan ukuran badan, panjang sumbu, pola candle |

**Keputusan teknikal** diambil dari nilai total:

| Keputusan | Aturan |
|---|---|
| 🟢 BELI | Total ≥ 7 dan Tren ≥ 5 |
| 🟡 PANTAU | Total 5,5–7 (atau ≥ 7 tetapi tren masih turun) |
| ⚪ TUNGGU | Total 4–5,5 |
| 🔴 HINDARI | Total < 4 |

Laporan juga menampilkan level harga otomatis: support, resistance, batas rugi (di bawah support atau −5%), target, dan rasio untung:rugi.

**Nilai fundamental** (0–10) dihitung terpisah dan tidak memengaruhi keputusan teknikal. Fundamental menilai kualitas perusahaan untuk jangka panjang, sedangkan teknikal menilai waktu masuk dan keluar dalam jangka pendek.

Pengaturan indikator disamakan dengan default Stockbit, jadi angkanya bisa dibandingkan langsung dengan aplikasi. Selisih kecil tetap mungkin karena sumber data berbeda.

## Catat jual beli dan average down

Catat setiap transaksi di `transaksi.csv` (1 lot = 100 lembar):

```csv
tanggal,kode,aksi,lot,harga
2026-10-01,RAJA,beli,10,520
2026-10-15,RAJA,beli,10,480
2026-10-20,RAJA,jual,5,500
```

Saham yang sedang dipegang otomatis ikut dianalisa. Untuk setiap posisi, laporan menampilkan:

- Lot, harga rata-rata, modal, nilai pasar, serta untung/rugi kotor dan bersih setelah fee jual.
- Berapa persen harga perlu naik untuk kembali impas.
- **Tabel simulasi average down**: beli lagi 50%, 100%, atau 200% dari lot yang dipegang, di harga sekarang, di support, atau di batas rugi. Hasilnya adalah rata-rata baru, dana yang dibutuhkan, dan kenaikan yang diperlukan untuk impas.
- Jumlah lot yang perlu dibeli supaya rata-rata turun ke titik tengah.
- Peringatan jika keputusan teknikal hari itu TUNGGU atau HINDARI, karena average down saat tren turun menambah risiko.
- Riwayat transaksi dan untung/rugi yang sudah terealisasi.

Fee default: beli 0,15%, jual 0,25%. Ubah di `portofolio.py` sesuai sekuritas kamu.

> ⚠️ Tanpa Supabase, posisi dari `transaksi.csv` ditulis ke README dan laporan. Jika repo public, jangan isi `transaksi.csv`, dan gunakan Supabase saja. Dengan Supabase, posisi dan transaksi **tidak pernah ditulis ke repo**, sehingga repo aman dibuat public.

## Database Supabase (opsional)

Semua data bisa disimpan di satu database Supabase. Semua tabel memakai awalan `saham_`, sehingga bisa berbagi project dengan aplikasi lain. Program tetap berjalan tanpa Supabase, karena saat itu ia memakai `saham.txt` dan `transaksi.csv`.

| Tabel / view | Isi |
|---|---|
| `saham_watchlist` | Daftar saham yang dianalisa (kolom `aktif` untuk menonaktifkan tanpa menghapus) |
| `saham_transaksi` | Catatan jual beli. Isi lewat Table Editor Supabase, bisa dari HP |
| `saham_harga_harian` | Harga OHLCV harian |
| `saham_analisa_harian` | Nilai tiap aspek, keputusan, indikator, level harga, dan rincian poin, per saham per hari |
| `saham_fundamental` | PER, PBV, ROE, DER, pertumbuhan, nilai fundamental, laba rugi per kuartal |
| `saham_analisa_terbaru` (view) | Analisa terakhir tiap saham |
| `saham_screener` | Hasil pemindaian harian untuk tab Rekomendasi |
| `saham_asing` | Foreign buy/sell harian dari file Ringkasan Saham BEI (diunggah lewat dashboard) |
| `saham_berita`, `saham_kata_kunci` | Berita dari feed RSS dan kata kunci pencarian |
| `saham_posisi` (view) | Lot, harga rata-rata, modal, untung/rugi, dan keputusan hari ini untuk saham yang dipegang |

**Cara memasang:**

1. Buat project di [supabase.com](https://supabase.com) (paket gratis cukup).
2. Buka **SQL Editor**, tempel isi `supabase/schema.sql`, lalu klik **Run**.
3. Buka **Project Settings → API Keys**, lalu salin **Secret key** (diawali `sb_secret_`). Jangan gunakan *publishable key*. Project URL ada di **Project Settings → Data API**.
4. Di GitHub, buka **Settings → Secrets and variables → Actions → New repository secret**, lalu tambahkan:
   - `SUPABASE_URL`
   - `SUPABASE_SERVICE_KEY` (isi dengan Secret key)
5. Untuk dashboard: jalankan `supabase/002_akses_dashboard.sql` lalu `supabase/003_screener.sql` `supabase/004_asing.sql`, dan `supabase/005_berita.sql` di SQL Editor, lalu daftarkan akunmu:
   (ganti `EMAIL_KAMU` di baris terakhir file dengan email akun Supabase kamu).
6. (Opsional) Salin data lama: `python db.py impor-watchlist` dan `python db.py impor-transaksi`.

Setelah terpasang, watchlist dan transaksi dibaca dari Supabase. Laporan Markdown dan grafik tetap disimpan di repo.

> 🔒 **Secret key** punya akses penuh ke database. Simpan hanya di GitHub Secrets, jangan ditulis di file mana pun. Semua tabel memakai Row Level Security tanpa akses publik, jadi isi database tidak bisa dibaca orang lain. Dalam mode Supabase, posisi, transaksi, dan untung/rugi tidak ditulis ke README maupun laporan.

## Cara pakai

**Menambah saham:** edit `saham.txt`, tulis satu kode per baris (tanpa `.JK`).

**Menjalankan manual di GitHub:** tab **Actions** → **Analisa harian** → **Run workflow**. Kolom kode boleh diisi, misalnya `RAJA BBCA`.

**Menjalankan di komputer sendiri:**

```bash
pip install -r requirements.txt
python analisa.py            # semua saham di saham.txt
python analisa.py RAJA BBCA  # saham tertentu
python analisa.py RAJA --csv data/RAJA.csv   # dari file CSV (Date,Open,High,Low,Close,Volume)
```

## Struktur

```
analisa.py      program utama: ambil data, analisa, tulis laporan dan grafik
indikator.py    rumus MA, Bollinger, MACD, RSI, Stochastic, Stoch RSI
candle.py       deteksi pola candlestick
skor.py         penilaian 0–10 dan keputusan
portofolio.py   harga rata-rata, untung/rugi, simulasi average down
transaksi.csv   catatan jual beli kamu
fundamental.py  data laporan keuangan dan nilai fundamental
saham.txt       daftar saham (jika tidak memakai Supabase)
db.py           penghubung ke Supabase
screener.py     pemindai harian untuk tab Rekomendasi
universe.txt    daftar saham yang dipindai
berita.py       pengambil berita dari feed RSS
feeds.txt       daftar feed berita
supabase/       skema database dan aturan akses dashboard
docs/           dashboard web (GitHub Pages)
reports/        laporan harian per saham
charts/         grafik harian per saham
```

## Catatan

- Data Yahoo Finance gratis tetapi tidak resmi, dan bisa terlambat atau sesekali kosong.
- Jadwal otomatis berjalan Senin–Jumat pukul 17:15 WIB. Pada hari libur bursa, laporan hari sebelumnya akan ditimpa dengan isi yang sama.
- Data fundamental Yahoo Finance untuk saham kecil sering tidak lengkap. Bagian yang kosong tidak ikut dinilai.
- Keputusan BELI/PANTAU/TUNGGU/HINDARI berasal dari aturan mekanis di `skor.py`, bukan saran dari analis. Aturan ini tidak mengetahui berita, aksi korporasi, atau kondisi pasar. Ubah bobot dan batasnya sesuai gaya trading kamu, dan selalu gunakan batas rugi.
