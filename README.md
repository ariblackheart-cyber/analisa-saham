# Analisa Saham Harian

Analisa teknikal otomatis untuk saham Bursa Efek Indonesia. Setiap hari bursa, GitHub Actions mengambil data harga dari Yahoo Finance, menghitung indikator, lalu menyimpan laporan dan grafik ke repo ini.

**Dashboard:** https://ariblackheart-cyber.github.io/analisa-saham/ (login dengan akun Supabase). Berisi grafik, nilai tiap aspek, portofolio, simulasi average down, dan form catat transaksi.

## Ringkasan terbaru

<!-- RINGKASAN:START -->
| Saham | Tanggal | Close | Perubahan | Tren | Volume | Stoch | Momentum | Candle | Total | Keputusan | Fundamental |
|---|---|---|---|---|---|---|---|---|---|---|---|
| [RAJA](reports/RAJA/latest.md) | 2026-10-26 | 472 | -5.60% | 0.0 | 4.4 | 6.5 | 4.0 | 1.6 | **3.2** | 🔴 HINDARI | 9.4 Kuat |
<!-- RINGKASAN:END -->

## Portofolio saya

<!-- PORTOFOLIO:START -->
_Belum ada posisi. Isi `transaksi.csv`._
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
| `saham_posisi` (view) | Lot, harga rata-rata, modal, untung/rugi, dan keputusan hari ini untuk saham yang dipegang |

**Cara memasang:**

1. Buat project di [supabase.com](https://supabase.com) (paket gratis cukup).
2. Buka **SQL Editor**, tempel isi `supabase/schema.sql`, lalu klik **Run**.
3. Buka **Project Settings → API Keys**, lalu salin **Secret key** (diawali `sb_secret_`). Jangan gunakan *publishable key*. Project URL ada di **Project Settings → Data API**.
4. Di GitHub, buka **Settings → Secrets and variables → Actions → New repository secret**, lalu tambahkan:
   - `SUPABASE_URL`
   - `SUPABASE_SERVICE_KEY` (isi dengan Secret key)
5. Untuk dashboard: jalankan `supabase/002_akses_dashboard.sql` di SQL Editor, lalu daftarkan akunmu:
   `insert into saham_pemilik (user_id) select id from auth.users where email = 'EMAIL_KAMU';`
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
