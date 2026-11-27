"""Setup harian untuk calon watchlist day trade (dipakai screener.py).

Lima aturan berbasis harga penutupan harian. Hasilnya daftar chart yang cocok dengan aturan,
bukan prediksi dan bukan rekomendasi beli.

    breakout_20d     close terakhir di atas semua close 20 sesi sebelumnya
    bull_flag        naik >10% dalam 10 sesi sebelum 5 sesi terakhir, lalu 5 close terakhir
                     berada dalam rentang 5%
    reclaim_ma20     close kemarin di bawah MA20, close terakhir di atas MA20
    oversold         RSI(14) Wilder < 30
    oversold_bounce  RSI(14) kemarin < 30 dan close hari ini naik
"""
import pandas as pd

from indikator import rsi, sma

SETUP = {
    "breakout_20d": "Breakout 20 hari",
    "bull_flag": "Bull flag",
    "reclaim_ma20": "Kembali di atas MA20",
    "oversold": "Oversold (RSI < 30)",
    "oversold_bounce": "Pantulan oversold",
}


def deteksi(df: pd.DataFrame) -> list[str]:
    """Kode setup yang cocok pada bar terakhir df (kolom Close wajib). Urut seperti SETUP."""
    c = df["Close"].astype(float).reset_index(drop=True)
    if len(c) < 22:
        return []
    hasil = set()

    if c.iloc[-1] > c.iloc[-21:-1].max():
        hasil.add("breakout_20d")

    if len(c) >= 16:
        naik = c.iloc[-6] / c.iloc[-16] - 1          # 10 sesi sebelum 5 sesi terakhir
        lima = c.iloc[-5:]
        if naik > 0.10 and (lima.max() - lima.min()) / lima.min() <= 0.05:
            hasil.add("bull_flag")

    ma20 = sma(c, 20)
    if pd.notna(ma20.iloc[-2]) and c.iloc[-2] < ma20.iloc[-2] and c.iloc[-1] > ma20.iloc[-1]:
        hasil.add("reclaim_ma20")

    r = rsi(c, 14)
    if pd.notna(r.iloc[-1]) and r.iloc[-1] < 30:
        hasil.add("oversold")
    if pd.notna(r.iloc[-2]) and r.iloc[-2] < 30 and c.iloc[-1] > c.iloc[-2]:
        hasil.add("oversold_bounce")

    return [k for k in SETUP if k in hasil]


def label(kode_setup: list[str]) -> str:
    return ", ".join(SETUP[k] for k in kode_setup)
