# Analisa Saham Harian

Analisa teknikal otomatis untuk saham Bursa Efek Indonesia. Setiap hari bursa, GitHub Actions mengambil data harga dari Yahoo Finance, menghitung indikator, lalu menyimpan laporan dan grafik ke repo ini.

**Dashboard:** https://ariblackheart-cyber.github.io/analisa-saham/ (login dengan akun Supabase). Berisi grafik, nilai tiap aspek, portofolio, simulasi average down, dan form catat transaksi.

## Ringkasan terbaru

<!-- RINGKASAN:START -->
| Saham | Tanggal | Close | Perubahan | Tren | Volume | Stoch | Momentum | Candle | Total | Keputusan | Fundamental |
|---|---|---|---|---|---|---|---|---|---|---|---|
| [BBRI](reports/BBRI/latest.md) | 2026-11-27 | 3.100 | +0.65% | 10.0 | 6.4 | 3.5 | 7.5 | 5.8 | **6.8** | 🟡 PANTAU | 9.0 Kuat |
| [BRIS](reports/BRIS/latest.md) | 2026-11-27 | 1.195 | +2.58% | 7.0 | 4.8 | 3.5 | 5.5 | 8.1 | **5.7** | 🟡 PANTAU | 8.9 Kuat |
| [RAJA](reports/RAJA/latest.md) | 2026-11-27 | 436 | +6.34% | 2.0 | 5.6 | 3.5 | 6.0 | 6.3 | **4.5** | ⚪ TUNGGU | 8.2 Kuat |
| [AALI](reports/AALI/latest.md) | 2026-11-27 | 9.450 | -0.26% | 3.0 | 3.2 | 7.2 | 4.5 | 4.8 | **4.5** | ⚪ TUNGGU | 10.0 Kuat |
<!-- RINGKASAN:END -->

## Rekomendasi teknikal

<!-- REKOMENDASI:START -->
10 nilai teknikal tertinggi dari 81 saham likuid yang dipindai (2026-11-27). Hasil aturan mekanis, bukan rekomendasi investasi.

| # | Saham | Close | Perubahan | Total | Keputusan | Tren | Volume | Stoch | Momentum | Candle |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **INTP** | 6.300 | +1.61% | **8.0** | 🟢 BELI | 10.0 | 7.6 | 5.0 | 9.5 | 7.2 |
| 2 | **ASII** | 5.750 | +1.32% | **8.0** | 🟢 BELI | 10.0 | 7.6 | 5.8 | 9.5 | 6.1 |
| 3 | **MAPA** | 640 | +4.07% | **8.0** | 🟢 BELI | 10.0 | 6.3 | 5.8 | 9.5 | 7.9 |
| 4 | **KLBF** | 820 | +1.86% | **7.7** | 🟢 BELI | 10.0 | 7.1 | 5.0 | 9.5 | 5.6 |
| 5 | **AVIA** | 340 | +1.80% | **7.4** | 🟢 BELI | 10.0 | 7.6 | 3.5 | 9.5 | 5.5 |
| 6 | **INDF** | 7.200 | +1.05% | **7.2** | 🟢 BELI | 10.0 | 6.5 | 3.5 | 9.5 | 5.6 |
| 7 | **BBCA** | 6.000 | +1.69% | **7.2** | 🟢 BELI | 7.0 | 7.7 | 5.0 | 9.5 | 6.4 |
| 8 | **UNVR** | 1.665 | +0.91% | **7.1** | 🟢 BELI | 10.0 | 7.6 | 5.0 | 7.5 | 3.9 |
| 9 | **SMGR** | 1.600 | +3.56% | **7.0** | 🟢 BELI | 10.0 | 4.2 | 3.5 | 7.5 | 10.0 |
| 10 | **BBNI** | 3.610 | +0.84% | **6.9** | 🟡 PANTAU | 10.0 | 4.2 | 5.8 | 7.5 | 6.1 |

### Setup day trade

Saham likuid yang cocok dengan aturan setup harian, diurutkan dari nilai transaksi terbesar. Calon watchlist untuk dipantau besok, bukan sinyal beli.

| Saham | Close | Perubahan | Setup | Transaksi/hari | MA20 | RSI |
|---|---|---|---|---|---|---|
| **BBCA** | 6.000 | +1.69% | Breakout 20 hari | Rp 1052.4 M | 5.462 | 64.4 |
| **BMRI** | 4.020 | +0.75% | Breakout 20 hari | Rp 548.3 M | 3.832 | 62.1 |
| **ASII** | 5.750 | +1.32% | Breakout 20 hari | Rp 255.9 M | 5.324 | 67.3 |
| **ANTM** | 2.720 | +3.03% | Kembali di atas MA20 | Rp 196.7 M | 2.670 | 49.7 |
| **TPIA** | 1.305 | +10.13% | Kembali di atas MA20 | Rp 172.6 M | 1.253 | 50.3 |
| **GOTO** | 26 | -3.70% | Bull flag | Rp 168.3 M | 26 | 43.3 |
| **INCO** | 3.500 | +2.94% | Kembali di atas MA20 | Rp 49.9 M | 3.418 | 48.0 |
| **EXCL** | 1.735 | +2.06% | Breakout 20 hari, Bull flag | Rp 41.2 M | 1.601 | 51.3 |
| **UNVR** | 1.665 | +0.91% | Breakout 20 hari | Rp 35.4 M | 1.524 | 70.1 |
| **KLBF** | 820 | +1.86% | Breakout 20 hari | Rp 28.9 M | 768 | 66.0 |
| **NCKL** | 725 | +2.11% | Kembali di atas MA20 | Rp 28.8 M | 723 | 46.5 |
| **ERAA** | 515 | +3.00% | Kembali di atas MA20 | Rp 24.4 M | 504 | 48.0 |
| **AKRA** | 1.295 | +2.37% | Kembali di atas MA20 | Rp 20.6 M | 1.290 | 48.1 |
| **EMTK** | 268 | +4.69% | Pantulan oversold | Rp 15.9 M | 287 | 35.0 |
| **SMGR** | 1.600 | +3.56% | Bull flag | Rp 15.1 M | 1.520 | 57.6 |
| **MIKA** | 1.490 | +0.34% | Breakout 20 hari | Rp 11.3 M | 1.361 | 60.1 |
| **MYOR** | 1.520 | -1.30% | Bull flag | Rp 11.1 M | 1.442 | 58.4 |
| **PWON** | 312 | +1.30% | Breakout 20 hari | Rp 10.9 M | 276 | 71.2 |
| **MAPA** | 640 | +4.07% | Breakout 20 hari, Bull flag | Rp 10.8 M | 599 | 61.5 |
| **AVIA** | 340 | +1.80% | Breakout 20 hari | Rp 10.3 M | 308 | 64.9 |
| **INTP** | 6.300 | +1.61% | Breakout 20 hari | Rp 8.7 M | 5.929 | 66.4 |
| **HRUM** | 675 | +1.50% | Kembali di atas MA20 | Rp 8.1 M | 670 | 45.4 |
| **BUKA** | 118 | +0.85% | Bull flag | Rp 7.7 M | 109 | 62.7 |
| **CMRY** | 4.260 | +3.40% | Kembali di atas MA20 | Rp 7.6 M | 4.208 | 51.8 |
| **TKIM** | 5.675 | +4.13% | Pantulan oversold | Rp 6.6 M | 5.929 | 38.0 |
| **MTEL** | 262 | +3.97% | Oversold (RSI < 30), Pantulan oversold | Rp 6.5 M | 312 | 25.0 |
| **MAPI** | 1.035 | +0.98% | Oversold (RSI < 30), Pantulan oversold | Rp 6.1 M | 1.157 | 28.3 |
| **SCMA** | 135 | +1.50% | Kembali di atas MA20 | Rp 5.4 M | 134 | 43.1 |
<!-- REKOMENDASI:END -->

Setiap hari bursa, semua saham di `universe.txt` (±85 saham likuid) dinilai dengan aturan yang sama. Saham dengan rata-rata transaksi di bawah Rp 5 miliar/hari dilewati. Daftar lengkap dan alasannya ada di tab **Rekomendasi** di dashboard. Ubah daftar saham di `universe.txt` dan batas likuiditas di `screener.py`.

Pemindai juga menandai **setup day trade harian** (`setup_harian.py`), dari harga penutupan: breakout 20 hari (close di atas semua close 20 sesi sebelumnya), bull flag (naik lebih dari 10% dalam 10 sesi lalu 5 close terakhir dalam rentang 5%), kembali di atas MA20, oversold (RSI 14 di bawah 30), dan pantulan oversold (RSI kemarin di bawah 30 lalu close naik). Hasilnya tampil di bagian **Setup day trade** di atas dan di tab **Rekomendasi** (centang "Hanya yang punya setup day trade"). Untuk menyimpannya ke Supabase, jalankan `supabase/006_setup_dan_emas.sql` sekali. Ini daftar chart yang cocok dengan aturan, bukan sinyal beli.

## Emas

Tab **Emas** di dashboard menganalisa harga emas setiap hari bursa (`emas.py`). Harga emas dunia (COMEX, USD per troy ounce) dikonversi ke **rupiah per gram** dengan kurs USD/IDR, lalu dinilai dengan aturan yang sama seperti saham: tren, volume, stochastic, momentum, candle, ditambah support/resistance, batas rugi, dan target. Laporannya ada di `reports/EMAS/latest.md`. Ini harga spot hasil konversi, bukan harga jual atau buyback Antam. Untuk menyimpannya ke Supabase, jalankan `supabase/006_setup_dan_emas.sql` sekali.

## Data asing

Data beli/jual asing tidak tersedia di Yahoo Finance, dan situs BEI menolak akses otomatis dari server. Fitur ini **disembunyikan** di dashboard (cek foreign flow langsung di Stockbit); aktifkan dengan mengubah `FITUR_ASING = true` di `docs/index.html`. Jika diaktifkan, datanya diunggah manual: unduh file **Ringkasan Saham** harian dari idx.co.id, lalu unggah di dashboard (tab **Catat**, beberapa file sekaligus boleh). Tab **Rekomendasi** lalu menampilkan net beli asing 1 hari, 1 minggu, dan 1 bulan, bisa diurutkan berdasarkan asing, dan bisa disaring ke saham yang diakumulasi asing (net beli dan net beli di minimal 60% hari).

## Berita

Setiap 3 jam, workflow **Berita** mengambil berita dari feed RSS di `feeds.txt` (Antara Ekonomi Bursa, detikFinance, Liputan6 Bisnis, Republika Ekonomi) dan menyimpannya 30 hari. Di dashboard, berita bisa dicari dengan kata kunci; kode saham yang dipantau otomatis jadi kata kunci, dan kata kunci lain (misalnya nikel atau suku bunga) bisa ditambahkan di tab **Catat**. Halaman detail saham menampilkan berita yang menyebut kode saham itu.

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
setup_harian.py aturan setup day trade harian (dipakai screener.py)
universe.txt    daftar saham yang dipindai
emas.py         analisa harian emas (Rp/gram) untuk tab Emas
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
