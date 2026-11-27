"""Analisa teknikal harian emas (tab Emas di dashboard).

Harga emas dunia (Yahoo GC=F, USD per troy ounce) dikonversi ke rupiah per gram dengan kurs
USD/IDR (Yahoo IDR=X), lalu dinilai dengan aturan yang sama seperti saham (skor.py).
Ini harga spot hasil konversi, bukan harga jual/buyback Antam (yang memakai premi dan spread).

    python emas.py                    # data Yahoo Finance
    python emas.py --csv data/EMAS.csv  # uji: CSV Date,Open,High,Low,Close,Volume,usd_oz,kurs (Rp/gram)

Hasil:
    reports/EMAS/<tanggal>.md, reports/EMAS/latest.md, charts/EMAS/...
    tabel saham_emas_harian di Supabase (jika SUPABASE_URL/SUPABASE_SERVICE_KEY diisi)
"""
import argparse
import re
import sys
from datetime import datetime
from zoneinfo import ZoneInfo

import pandas as pd

import db
from analisa import ROOT, analisa, gambar, laporan, rp

KODE = "EMAS"
GRAM_PER_OZ = 31.1034768


def unduh() -> pd.DataFrame:
    import yfinance as yf

    def satu(ticker):
        df = yf.download(ticker, period="1y", interval="1d", auto_adjust=False, progress=False)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        return df

    emas, kurs = satu("GC=F"), satu("IDR=X")
    emas = emas[["Open", "High", "Low", "Close", "Volume"]].dropna()
    # Candle emas hari ini (waktu New York) belum selesai saat workflow jalan: buang.
    hari_ini = datetime.now(ZoneInfo("America/New_York")).date()
    emas = emas[[d.date() < hari_ini for d in emas.index]]
    k = kurs["Close"].dropna()
    k = k[k > 1000]                      # buang data kurs yang rusak
    emas["kurs"] = k.reindex(emas.index, method="ffill")
    emas = emas.dropna(subset=["kurs"])
    return ke_rupiah(emas)


def ke_rupiah(emas: pd.DataFrame) -> pd.DataFrame:
    """OHLC USD/oz + kolom kurs → OHLC Rp/gram, dengan kolom usd_oz dan kurs."""
    out = pd.DataFrame(index=emas.index)
    for c in ("Open", "High", "Low", "Close"):
        out[c] = emas[c] * emas["kurs"] / GRAM_PER_OZ
    out["Volume"] = emas["Volume"].fillna(0)
    out["usd_oz"] = emas["Close"]
    out["kurs"] = emas["kurs"]
    return out


def tulis_laporan(h: dict, usd_oz: float, kurs: float):
    h.update(fund=None, fund_nilai=None, fund_rincian=[], posisi=None)
    tgl = h["tanggal"]
    folder = ROOT / "reports" / KODE
    folder.mkdir(parents=True, exist_ok=True)
    gambar(h, ROOT / "charts" / KODE / f"{tgl}.png")
    gambar(h, ROOT / "charts" / KODE / "latest.png")
    info = (f"Harga emas dunia **USD {usd_oz:,.2f}/oz** × kurs **Rp {rp(kurs)}** ÷ {GRAM_PER_OZ:.2f} gram "
            f"= **Rp {rp(h['t']['Close'])}/gram** (spot, belum termasuk premi Antam/toko emas).")
    for nama, chart in ((f"{tgl}.md", f"../../charts/{KODE}/{tgl}.png"), ("latest.md", f"../../charts/{KODE}/latest.png")):
        teks = laporan(h, chart)
        teks = re.sub(r"## 8\. Fundamental.*?(?=## 9\.)", "", teks, flags=re.S)   # emas tanpa laporan keuangan
        teks = teks.replace("## Ringkasan\n", "## Ringkasan\n\n" + info + "\n", 1)
        (folder / nama).write_text(teks, encoding="utf-8")


def ke_rows(h: dict, df: pd.DataFrame) -> tuple[list[dict], dict]:
    harga = [dict(tanggal=idx.date(), open=r.Open, high=r.High, low=r.Low, close=r.Close,
                  volume=int(r.Volume), usd_oz=r.usd_oz, kurs=r.kurs) for idx, r in zip(df.index, df.itertuples())]
    t, y, n = h["t"], h["y"], h["nilai"]
    a, r = n["aspek"], n["rencana"]
    analisa_row = dict(
        tanggal=h["tanggal"], perubahan_pct=(t["Close"] - y["Close"]) / y["Close"] * 100,
        nilai_tren=a["Tren"][0], nilai_volume=a["Volume"][0], nilai_stochastic=a["Stochastic"][0],
        nilai_momentum=a["Momentum"][0], nilai_candle=a["Candle"][0], nilai_total=n["total"],
        keputusan=n["label"], pola_candle=[p[0] for p in h["pola"]],
        ma5=t["MA5"], ma20=t["MA20"], ma100=t["MA100"], rsi=t["RSI"], volume_ratio=t["Vol_ratio"],
        support=r["support"], resistance=r["resist"], stop_loss=r["stop"],
        target1=r["target1"], target2=r["target2"],
        rincian={k: [{"poin": p, "alasan": s} for p, s in v[1]] for k, v in a.items()},
    )
    return harga, analisa_row


def main():
    ap = argparse.ArgumentParser(description="Analisa teknikal harian emas")
    ap.add_argument("--csv", help="file CSV untuk pengujian (Rp/gram, dengan kolom usd_oz dan kurs)")
    a = ap.parse_args()
    df = pd.read_csv(a.csv, parse_dates=["Date"], index_col="Date") if a.csv else unduh()
    if len(df) < 30:
        sys.exit(f"Data emas terlalu sedikit ({len(df)} hari).")
    h = analisa(KODE, df[["Open", "High", "Low", "Close", "Volume"]])
    usd_oz, kurs = float(df["usd_oz"].iloc[-1]), float(df["kurs"].iloc[-1])
    tulis_laporan(h, usd_oz, kurs)
    print(f"[{KODE}] {h['tanggal']} Rp {rp(h['t']['Close'])}/gram (USD {usd_oz:,.2f}/oz, kurs {rp(kurs)}) "
          f"-> {h['nilai']['label']} ({h['nilai']['total']:.1f}/10)")
    if db.aktif() and not a.csv:
        harga, row = ke_rows(h, df)
        sb = db.Supabase()
        sb.upsert("saham_emas_harian", harga, "tanggal")
        sb.upsert("saham_emas_harian", [row], "tanggal")
        print("Tersimpan ke Supabase.")


if __name__ == "__main__":
    main()
