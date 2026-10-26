# Analisa Saham Harian

Analisa teknikal otomatis untuk saham Bursa Efek Indonesia. Setiap hari bursa, GitHub Actions mengambil data harga dari Yahoo Finance, menghitung indikator, lalu menyimpan laporan dan grafik ke repo ini.

## Ringkasan terbaru

<!-- RINGKASAN:START -->
_Belum ada data. Jalankan workflow **Analisa harian** sekali dari tab Actions._
<!-- RINGKASAN:END -->

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
fundamental.py  data laporan keuangan dan nilai fundamental
saham.txt       daftar saham
reports/        laporan harian per saham
charts/         grafik harian per saham
```

## Catatan

- Data Yahoo Finance gratis tetapi tidak resmi, dan bisa terlambat atau sesekali kosong.
- Jadwal otomatis berjalan Senin–Jumat pukul 17:15 WIB. Pada hari libur bursa, laporan hari sebelumnya akan ditimpa dengan isi yang sama.
- Data fundamental Yahoo Finance untuk saham kecil sering tidak lengkap. Bagian yang kosong tidak ikut dinilai.
- Keputusan BELI/PANTAU/TUNGGU/HINDARI berasal dari aturan mekanis di `skor.py`, bukan saran dari analis. Aturan ini tidak mengetahui berita, aksi korporasi, atau kondisi pasar. Ubah bobot dan batasnya sesuai gaya trading kamu, dan selalu gunakan batas rugi.
