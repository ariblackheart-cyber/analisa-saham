"""Pemindai harian (tab Rekomendasi): nilai teknikal semua saham di universe.txt.

Memakai aturan penilaian yang sama dengan analisa.py (skor.py). Saham yang kurang likuid
(rata-rata nilai transaksi 20 hari < MIN_TRANSAKSI) dilewati.

    python screener.py                 # pindai universe.txt
    python screener.py --csv-dir data  # uji dengan file CSV per kode (data/KODE.csv)

Hasil:
    - tabel saham_screener di Supabase (jika SUPABASE_URL/SUPABASE_SERVICE_KEY diisi)
    - tabel 10 teratas di README.md (bagian REKOMENDASI)
"""
import argparse
import re
import sys
from datetime import date
from pathlib import Path

import pandas as pd

import db
from analisa import ROOT, IKON, analisa, num, rp

MIN_TRANSAKSI = 5e9     # Rp 5 miliar per hari
MIN_HARI = 120          # butuh data cukup untuk MA100


def baca_universe() -> list[str]:
    kode = []
    for s in (ROOT / "universe.txt").read_text().splitlines():
        s = s.strip().upper()
        if s and not s.startswith("#") and s not in kode:
            kode.append(s)
    return kode


def unduh(kode_list: list[str], csv_dir: str | None) -> dict[str, pd.DataFrame]:
    hasil = {}
    if csv_dir:
        for k in kode_list:
            p = Path(csv_dir) / f"{k}.csv"
            if p.exists():
                hasil[k] = pd.read_csv(p, parse_dates=["Date"], index_col="Date")
        return hasil
    import yfinance as yf
    tickers = [f"{k}.JK" for k in kode_list]
    raw = yf.download(tickers, period="1y", interval="1d", auto_adjust=False,
                      group_by="ticker", threads=True, progress=False)
    for k, t in zip(kode_list, tickers):
        try:
            df = raw[t] if isinstance(raw.columns, pd.MultiIndex) else raw
            hasil[k] = df
        except KeyError:
            continue
    return hasil


def bersihkan(df: pd.DataFrame) -> pd.DataFrame:
    df = df[["Open", "High", "Low", "Close", "Volume"]].dropna()
    return df[df["Volume"] > 0]


def pindai(data: dict[str, pd.DataFrame]):
    baris, lewat = [], []
    tgl_terbaru = max((d.index[-1] for d in data.values() if len(d)), default=None)
    for kode, df in data.items():
        df = bersihkan(df)
        if len(df) < MIN_HARI:
            lewat.append((kode, "data kurang"))
            continue
        if tgl_terbaru is not None and (tgl_terbaru - df.index[-1]).days > 5:
            lewat.append((kode, "tidak diperdagangkan / suspensi"))
            continue
        transaksi = float((df["Close"] * df["Volume"]).tail(20).mean())
        if transaksi < MIN_TRANSAKSI:
            lewat.append((kode, f"kurang likuid (Rp {transaksi / 1e9:.1f} M/hari)"))
            continue
        try:
            h = analisa(kode, df)
        except Exception as e:
            lewat.append((kode, f"gagal: {e}"))
            continue
        h["transaksi"] = transaksi
        baris.append(h)
    baris.sort(key=lambda h: -h["nilai"]["total"])
    return baris, lewat


def ke_row(h: dict) -> dict:
    t, y, n = h["t"], h["y"], h["nilai"]
    a, r = n["aspek"], n["rencana"]
    return dict(
        kode=h["kode"], tanggal=h["tanggal"], close=t["Close"],
        perubahan_pct=(t["Close"] - y["Close"]) / y["Close"] * 100,
        nilai_tren=a["Tren"][0], nilai_volume=a["Volume"][0], nilai_stochastic=a["Stochastic"][0],
        nilai_momentum=a["Momentum"][0], nilai_candle=a["Candle"][0], nilai_total=n["total"],
        keputusan=n["label"], pola_candle=[p[0] for p in h["pola"]],
        ma20=t["MA20"], ma100=t["MA100"], rsi=t["RSI"], volume_ratio=t["Vol_ratio"],
        nilai_transaksi=h["transaksi"], support=r["support"], stop_loss=r["stop"], target1=r["target1"],
        rincian={k: [{"poin": p, "alasan": s} for p, s in v[1]] for k, v in a.items()},
    )


def update_readme(baris: list[dict], jumlah: int):
    readme = ROOT / "README.md"
    teks = readme.read_text(encoding="utf-8")
    if "<!-- REKOMENDASI:START -->" not in teks:
        teks = teks.replace("## Portofolio saya", "## Rekomendasi teknikal\n\n<!-- REKOMENDASI:START -->\n"
                            "<!-- REKOMENDASI:END -->\n\n## Portofolio saya", 1)
    top = baris[:10]
    tgl = top[0]["tanggal"] if top else date.today()
    L = [f"10 nilai teknikal tertinggi dari {jumlah} saham likuid yang dipindai ({tgl}). "
         "Hasil aturan mekanis, bukan rekomendasi investasi.", "",
         "| # | Saham | Close | Perubahan | Total | Keputusan | Tren | Volume | Stoch | Momentum | Candle |",
         "|---|---|---|---|---|---|---|---|---|---|---|"]
    for i, h in enumerate(top, 1):
        t, y, n = h["t"], h["y"], h["nilai"]
        pct = (t["Close"] - y["Close"]) / y["Close"] * 100
        L.append(f"| {i} | **{h['kode']}** | {rp(t['Close'])} | {pct:+.2f}% | **{n['total']:.1f}** | "
                 f"{IKON[n['label']]} {n['label']} | " + " | ".join(f"{v[0]:.1f}" for v in n["aspek"].values()) + " |")
    blok = "<!-- REKOMENDASI:START -->\n" + "\n".join(L) + "\n<!-- REKOMENDASI:END -->"
    teks = re.sub(r"<!-- REKOMENDASI:START -->.*?<!-- REKOMENDASI:END -->", blok, teks, flags=re.S)
    readme.write_text(teks, encoding="utf-8")


def main():
    ap = argparse.ArgumentParser(description="Pemindai teknikal harian")
    ap.add_argument("--csv-dir", help="folder berisi KODE.csv untuk pengujian")
    a = ap.parse_args()
    kode_list = baca_universe()
    print(f"Memindai {len(kode_list)} saham…")
    data = unduh(kode_list, a.csv_dir)
    baris, lewat = pindai(data)
    print(f"{len(baris)} lolos, {len(lewat)} dilewati.")
    for k, alasan in lewat:
        print(f"  - {k}: {alasan}")
    for h in baris[:10]:
        print(f"  {h['kode']:5} {h['nilai']['total']:.1f} {h['nilai']['label']}")
    if not baris:
        sys.exit("Tidak ada saham yang lolos pemindaian.")
    update_readme(baris, len(kode_list))
    if db.aktif() and not a.csv_dir:
        db.Supabase().upsert("saham_screener", [ke_row(h) for h in baris], "kode,tanggal")
        print("Tersimpan ke Supabase.")


if __name__ == "__main__":
    main()
