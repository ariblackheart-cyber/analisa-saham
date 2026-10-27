"""Analisa teknikal harian saham BEI.

Contoh:
    python analisa.py                 # semua kode di saham.txt, data dari Yahoo Finance
    python analisa.py RAJA BBCA       # kode tertentu
    python analisa.py RAJA --csv data/RAJA.csv   # pakai file CSV (Date,Open,High,Low,Close,Volume)

Hasil:
    reports/<KODE>/<tanggal>.md   laporan harian
    reports/<KODE>/latest.md      laporan terbaru
    charts/<KODE>/<tanggal>.png   grafik harian (latest.png = terbaru)
    README.md                     tabel ringkasan semua saham diperbarui
"""
import argparse
import math
import re
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from candle import baca_candle
from skor import BOBOT, hitung as hitung_skor
import fundamental as fund
import portofolio as porto
import db
from indikator import hitung_semua

ROOT = Path(__file__).parent
DISCLAIMER = ("_Laporan ini dibuat otomatis dari aturan teknikal sederhana. "
              "Bukan rekomendasi beli atau jual; selalu kombinasikan dengan analisa sendiri dan manajemen risiko._")


# ---------------------------------------------------------------- data
def ambil_data(kode: str, csv: str | None = None) -> pd.DataFrame:
    if csv:
        df = pd.read_csv(csv, parse_dates=["Date"], index_col="Date")
    else:
        import yfinance as yf
        df = yf.download(f"{kode}.JK", period="1y", interval="1d",
                         auto_adjust=False, progress=False)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
    df = df[["Open", "High", "Low", "Close", "Volume"]].dropna()
    df = df[df["Volume"] > 0]  # buang hari libur / tanpa transaksi
    if not csv:
        df = buang_candle_berjalan(df)
    return df


def buang_candle_berjalan(df: pd.DataFrame, sekarang=None) -> pd.DataFrame:
    """Jika dijalankan saat bursa masih buka, candle hari ini belum final: buang.

    BEI tutup 16:00 WIB (pre-closing sampai ±16:15). Sebelum 16:30 WIB candle hari ini diabaikan.
    """
    from datetime import datetime, timedelta, timezone
    wib = timezone(timedelta(hours=7))
    sekarang = sekarang or datetime.now(wib)
    if len(df) and pd.Timestamp(df.index[-1]).date() == sekarang.date() and \
            (sekarang.hour, sekarang.minute) < (16, 30):
        return df.iloc[:-1]
    return df


# ---------------------------------------------------------------- helpers
def rp(x) -> str:
    return "-" if x is None or (isinstance(x, float) and math.isnan(x)) else f"{x:,.0f}".replace(",", ".")


def num(x, d=1) -> str:
    return "-" if x is None or (isinstance(x, float) and math.isnan(x)) else f"{x:.{d}f}"


def crossed(a_prev, a_now, b_prev, b_now) -> int:
    """+1 jika a memotong b ke atas, -1 ke bawah, 0 tidak."""
    if any(pd.isna(x) for x in (a_prev, a_now, b_prev, b_now)):
        return 0
    if a_prev <= b_prev and a_now > b_now:
        return 1
    if a_prev >= b_prev and a_now < b_now:
        return -1
    return 0


# ---------------------------------------------------------------- analisa
def analisa(kode: str, df: pd.DataFrame) -> dict:
    d = hitung_semua(df)
    t, y = d.iloc[-1], d.iloc[-2]
    tanggal = d.index[-1].date()
    skor = []  # (arah, alasan)

    # --- tren
    ma20_slope = t["MA20"] - d["MA20"].iloc[-6] if len(d) > 25 else float("nan")
    tren_turun = t["Close"] < t["MA20"] and ma20_slope < 0
    tren_naik = t["Close"] > t["MA20"] and ma20_slope > 0
    tren = []
    for ma in ("MA5", "MA20", "MA100"):
        if pd.isna(t[ma]):
            tren.append(f"- {ma}: belum cukup data.")
            continue
        posisi = "di atas" if t["Close"] > t[ma] else "di bawah"
        tren.append(f"- Harga {posisi} {ma} ({rp(t[ma])}).")
    if not pd.isna(t["MA100"]):
        if t["Close"] > t["MA100"]:
            skor.append((1, "Harga di atas MA100 (tren besar naik)"))
        else:
            skor.append((-1, "Harga di bawah MA100 (tren besar turun)"))
    if tren_naik:
        skor.append((1, "Harga di atas MA20 yang menanjak"))
    elif tren_turun:
        skor.append((-1, "Harga di bawah MA20 yang menurun"))
    x = crossed(y["MA5"], t["MA5"], y["MA20"], t["MA20"])
    if x == 1:
        tren.append("- **Golden cross pendek:** MA5 baru memotong MA20 ke atas.")
        skor.append((1, "MA5 memotong MA20 ke atas"))
    elif x == -1:
        tren.append("- **Death cross pendek:** MA5 baru memotong MA20 ke bawah.")
        skor.append((-1, "MA5 memotong MA20 ke bawah"))
    tren_label = "naik" if tren_naik else "turun" if tren_turun else "sideways / belum jelas"
    tren.insert(0, f"Tren jangka pendek: **{tren_label}** (MA20 berubah {rp(ma20_slope)} dalam 5 hari).")

    # --- candle
    rows = d[["Open", "High", "Low", "Close"]].tail(3).to_dict("records")
    candle_dasar, pola = baca_candle(rows, tren_turun, tren_naik)
    for nama, arah, _ in pola:
        if arah:
            skor.append((arah, f"Pola candle {nama}"))

    # --- volume
    vr = t["Vol_ratio"]
    vol = [f"Volume hari ini {rp(t['Volume'])} lembar, rata-rata 20 hari {rp(t['Vol_MA20'])} "
           f"(**{num(vr, 2)}x** rata-rata)."]
    naik_hari_ini = t["Close"] > y["Close"]
    if vr >= 1.5:
        if naik_hari_ini:
            vol.append("Volume tinggi saat harga naik: kenaikan didukung minat beli yang kuat.")
            skor.append((1, "Harga naik dengan volume tinggi"))
        else:
            vol.append("Volume tinggi saat harga turun: tekanan jual kuat (distribusi).")
            skor.append((-1, "Harga turun dengan volume tinggi"))
    elif vr < 0.7:
        vol.append("Volume sepi: pergerakan hari ini kurang meyakinkan.")
    else:
        vol.append("Volume normal.")
    last5 = d.tail(5)
    vol_up = last5.loc[last5["Close"] > last5["Open"], "Volume"].sum()
    vol_dn = last5.loc[last5["Close"] < last5["Open"], "Volume"].sum()
    if vol_up + vol_dn > 0:
        vol.append(f"5 hari terakhir: volume candle hijau {vol_up / (vol_up + vol_dn):.0%}, "
                   f"candle merah {vol_dn / (vol_up + vol_dn):.0%}.")

    # --- stochastic
    sto = []
    k, dd = t["Stoch_K"], t["Stoch_D"]
    zona = "jenuh beli (overbought)" if k >= 80 else "jenuh jual (oversold)" if k <= 20 else "tengah"
    sto.append(f"Stochastic (14,3,3): %K {num(k)}, %D {num(dd)}, zona **{zona}**.")
    x = crossed(y["Stoch_K"], k, y["Stoch_D"], dd)
    if x == 1:
        sto.append("%K memotong %D ke atas" + (" di area oversold: sinyal pantulan." if k < 30 else "."))
        skor.append((1, "Stochastic cross ke atas"))
    elif x == -1:
        sto.append("%K memotong %D ke bawah" + (" di area overbought: sinyal koreksi." if k > 70 else "."))
        skor.append((-1, "Stochastic cross ke bawah"))
    sk, sd = t["SRSI_K"], t["SRSI_D"]
    zona2 = "overbought" if sk >= 80 else "oversold" if sk <= 20 else "tengah"
    sto.append(f"Stoch RSI (14,14,3,3): K {num(sk)}, D {num(sd)}, zona **{zona2}**.")
    x = crossed(y["SRSI_K"], sk, y["SRSI_D"], sd)
    if x == 1:
        sto.append("Stoch RSI K memotong D ke atas: momentum mulai menguat.")
        skor.append((1, "Stoch RSI cross ke atas"))
    elif x == -1:
        sto.append("Stoch RSI K memotong D ke bawah: momentum mulai melemah.")
        skor.append((-1, "Stoch RSI cross ke bawah"))
    elif not pd.isna(sk) and not pd.isna(sd):
        sto.append("K di atas D: momentum masih naik." if sk > sd else "K di bawah D: momentum masih turun.")

    # --- MACD & RSI
    lain = []
    lain.append(f"MACD (12,26,9): garis {num(t['MACD'], 2)}, sinyal {num(t['MACD_sig'], 2)}, "
                f"histogram {num(t['MACD_hist'], 2)}.")
    x = crossed(y["MACD"], t["MACD"], y["MACD_sig"], t["MACD_sig"])
    if x == 1:
        lain.append("MACD memotong garis sinyal ke atas (bullish cross).")
        skor.append((1, "MACD bullish cross"))
    elif x == -1:
        lain.append("MACD memotong garis sinyal ke bawah (bearish cross).")
        skor.append((-1, "MACD bearish cross"))
    elif t["MACD_hist"] > y["MACD_hist"]:
        lain.append("Histogram membaik dibanding kemarin: tekanan turun berkurang / tekanan naik bertambah.")
    else:
        lain.append("Histogram memburuk dibanding kemarin.")
    if t["MACD"] < 0:
        lain.append("MACD masih di bawah nol: tren menengah masih lemah.")
    r = t["RSI"]
    lain.append(f"RSI (14): {num(r)}" + (" — overbought." if r >= 70 else " — oversold." if r <= 30 else "."))
    if r <= 30:
        skor.append((1, "RSI oversold"))
    elif r >= 70:
        skor.append((-1, "RSI overbought"))

    # --- Bollinger
    bb = []
    lebar = (t["BB_up"] - t["BB_low"]) / t["BB_mid"] if t["BB_mid"] else float("nan")
    pos = (t["Close"] - t["BB_low"]) / (t["BB_up"] - t["BB_low"]) if t["BB_up"] != t["BB_low"] else float("nan")
    bb.append(f"Bollinger (20,2): atas {rp(t['BB_up'])}, tengah {rp(t['BB_mid'])}, bawah {rp(t['BB_low'])}. "
              f"Posisi harga {num(pos * 100, 0)}% dari pita bawah ke atas, lebar pita {num(lebar * 100, 1)}%.")
    if t["Close"] <= t["BB_low"]:
        bb.append("Harga menyentuh / menembus pita bawah: jenuh jual, tapi bisa juga tanda tren turun kuat.")
    elif t["Close"] >= t["BB_up"]:
        bb.append("Harga menyentuh / menembus pita atas: jenuh beli, tapi bisa juga tanda tren naik kuat.")
    if not pd.isna(lebar):
        lebar_min = ((d["BB_up"] - d["BB_low"]) / d["BB_mid"]).tail(120).min()
        if lebar <= lebar_min * 1.1:
            bb.append("Pita sangat menyempit (squeeze): biasanya diikuti pergerakan besar.")

    # --- support / resistance
    sr = [f"Support 20 hari (low terendah): {rp(d['Low'].tail(20).min())}.",
          f"Resistance 20 hari (high tertinggi): {rp(d['High'].tail(20).max())}.",
          f"Resistance terdekat lain: MA20 {rp(t['MA20'])}, MA100 {rp(t['MA100'])}."]

    nilai = hitung_skor(d, t, y, pola)

    return dict(kode=kode, tanggal=tanggal, data=d, t=t, y=y, tren=tren, candle_dasar=candle_dasar,
                pola=pola, vol=vol, sto=sto, lain=lain, bb=bb, sr=sr, nilai=nilai, tren_label=tren_label)


# ---------------------------------------------------------------- grafik
def gambar(hasil: dict, path: Path, n: int = 60):
    d = hasil["data"].tail(n)
    x = range(len(d))
    fig, ax = plt.subplots(4, 1, figsize=(11, 10), sharex=True,
                           gridspec_kw={"height_ratios": [4, 1.3, 1.3, 1.3]})
    a0, a1, a2, a3 = ax
    for i, (_, r) in enumerate(d.iterrows()):
        col = "#26a69a" if r["Close"] >= r["Open"] else "#ef5350"
        a0.vlines(i, r["Low"], r["High"], color=col, linewidth=1)
        a0.bar(i, abs(r["Close"] - r["Open"]) or (r["High"] - r["Low"]) * 0.02,
               bottom=min(r["Open"], r["Close"]), color=col, width=0.6)
        a1.bar(i, r["Volume"], color=col, alpha=0.6, width=0.8)
    a0.plot(x, d["MA5"], label="MA5", color="#4caf50", lw=1)
    a0.plot(x, d["MA20"], label="MA20", color="#29b6f6", lw=1.3)
    a0.plot(x, d["MA100"], label="MA100", color="#5c6bc0", lw=1.3)
    a0.fill_between(x, d["BB_low"], d["BB_up"], color="#90caf9", alpha=0.15, label="BB 20,2")
    a0.set_title(f"{hasil['kode']} — {hasil['tanggal']}  |  Close {rp(hasil['t']['Close'])}")
    a0.legend(loc="upper left", fontsize=8)
    a1.plot(x, d["Vol_MA20"], color="#3f51b5", lw=1)
    a1.set_ylabel("Volume")
    a2.bar(x, d["MACD_hist"], color=["#26a69a" if v >= 0 else "#ef5350" for v in d["MACD_hist"]], alpha=0.5)
    a2.plot(x, d["MACD"], color="#1e88e5", lw=1)
    a2.plot(x, d["MACD_sig"], color="#c62828", lw=1)
    a2.axhline(0, color="grey", lw=0.5)
    a2.set_ylabel("MACD")
    a3.plot(x, d["SRSI_K"], color="#2e7d32", lw=1, label="Stoch RSI K")
    a3.plot(x, d["SRSI_D"], color="#c62828", lw=1, label="D")
    for lvl in (20, 80):
        a3.axhline(lvl, color="grey", lw=0.6, ls="--")
    a3.set_ylim(-5, 105)
    a3.set_ylabel("Stoch RSI")
    a3.legend(loc="upper left", fontsize=8)
    step = max(1, len(d) // 8)
    a3.set_xticks(list(x)[::step])
    a3.set_xticklabels([ts.strftime("%d %b") for ts in d.index[::step]])
    for a in ax:
        a.grid(alpha=0.2)
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=110)
    plt.close(fig)


# ---------------------------------------------------------------- laporan
def bar(nilai: float) -> str:
    isi = round(nilai)
    return "█" * isi + "░" * (10 - isi)


IKON = {"BELI": "🟢", "PANTAU": "🟡", "TUNGGU": "⚪", "HINDARI": "🔴"}


def blok_nilai(h: dict) -> list[str]:
    n = h["nilai"]
    r = n["rencana"]
    L = [f"### {IKON[n['label']]} Keputusan teknikal: **{n['label']}** — nilai total **{n['total']:.1f}/10**", "",
         n["alasan"], "",
         "| Aspek | Nilai | |", "|---|---|---|"]
    for nama, (nilai, _) in n["aspek"].items():
        L.append(f"| {nama} | **{nilai:.1f}**/10 | `{bar(nilai)}` |")
    L += ["", "**Level harga (otomatis):**", "",
          f"- Support 20 hari: {rp(r['support'])} · Resistance 20 hari: {rp(r['resist'])}",
          f"- Batas rugi (stop loss): {rp(r['stop'])} (di bawah support atau −5%)",
          f"- Target 1: {rp(r['target1'])} · Target 2: {rp(r['target2'])}",
          f"- Rasio untung : rugi ke target 1 = {num(r['rr'], 2)} : 1"
          + (" (kurang menarik, idealnya ≥ 1,5)" if not pd.isna(r['rr']) and r['rr'] < 1.5 else ""),
          ""]
    return L


def blok_posisi(h: dict) -> list[str]:
    p = h.get("posisi")
    if not p:
        return []
    harga = float(h["t"]["Close"])
    L = ["## Posisi kamu & simulasi average down", ""]
    if p["lot"] > 0:
        v = porto.nilai_sekarang(p, harga)
        tanda = "🟢" if v["kotor"] >= 0 else "🔴"
        L += ["| Lot | Harga rata-rata | Harga sekarang | Modal | Nilai pasar | Untung/rugi | Bersih setelah fee jual |",
              "|---|---|---|---|---|---|---|",
              f"| {p['lot']} | {num(p['avg'], 1)} | {rp(harga)} | {rp(v['modal'])} | {rp(v['pasar'])} | "
              f"{tanda} {rp(v['kotor'])} ({v['persen']:+.2f}%) | {rp(v['bersih'])} |", ""]
        if harga < p["avg"]:
            L.append(f"Harga perlu naik **{(p['avg'] / harga - 1) * 100:.1f}%** untuk kembali ke harga rata-rata "
                     f"(belum termasuk fee).")
            L.append("")
    else:
        L += ["Saat ini tidak memegang saham ini (semua sudah dijual).", ""]
    if p["realized"]:
        L += [f"Untung/rugi yang sudah terealisasi dari penjualan: **{rp(p['realized'])}** (setelah fee jual).", ""]

    if p["lot"] > 0:
        r = h["nilai"]["rencana"]
        level = [("Harga sekarang", harga), ("Support 20 hari", float(r["support"])),
                 ("Batas rugi", float(r["stop"]))]
        sim = porto.simulasi_avg_down(p, level)
        if sim:
            L += ["**Simulasi beli lagi (average down):**", "",
                  "| Beli di | Harga | Tambah lot | Dana dibutuhkan | Total lot | Rata-rata baru | Rata-rata turun | Naik perlu untuk impas |",
                  "|---|---|---|---|---|---|---|---|"]
            for x in sim:
                L.append(f"| {x['level']} | {rp(x['harga'])} | {x['tambah_lot']} | {rp(x['dana'])} | {x['lot_total']} | "
                         f"{num(x['avg_baru'], 1)} | {x['turun']:+.1f}% | {x['naik_perlu']:+.1f}% |")
            L.append("")
            if harga < p["avg"]:
                target = (p["avg"] + harga) / 2
                n = porto.lot_untuk_target_avg(p, harga, target)
                if n:
                    L += [f"Supaya rata-rata turun ke tengah-tengah ({num(target, 0)}), perlu beli **{n} lot** "
                          f"di harga {rp(harga)} (dana ±{rp(n * 100 * harga * (1 + porto.FEE_BELI))}).", ""]
            if h["nilai"]["label"] in ("HINDARI", "TUNGGU"):
                L += ["⚠️ Keputusan teknikal hari ini **" + h["nilai"]["label"] + "**. Average down saat tren masih "
                      "turun menambah risiko. Biasanya lebih aman menunggu tanda pembalikan (misalnya harga kembali "
                      "di atas MA20) daripada menambah di tengah penurunan.", ""]

    L += ["<details><summary>Riwayat transaksi</summary>", "",
          "| Tanggal | Aksi | Lot | Harga | Sisa lot | Rata-rata | Untung/rugi jual |", "|---|---|---|---|---|---|---|"]
    for x in p["riwayat"]:
        L.append(f"| {x['tanggal']} | {x['aksi']} | {x['lot']} | {rp(x['harga'])} | {x['lot_sisa']} | "
                 f"{num(x['avg'], 1)} | {'-' if x['pl'] is None else rp(x['pl'])} |")
    L += ["", "</details>", ""]
    return L


def blok_fundamental(h: dict) -> list[str]:
    f = h.get("fund")
    if not f:
        return ["Data fundamental tidak diambil (mode CSV) atau tidak tersedia dari Yahoo Finance."]
    v = h["fund_nilai"]
    pct = lambda x: "-" if not fund._ok(x) else f"{x:.1%}"
    der = f"{f['DER'] / 100:.2f}x" if fund._ok(f.get("DER")) else "-"
    L = [f"**Nilai fundamental: {num(v)}/10 — {fund.label(v)}** "
         "(terpisah dari keputusan teknikal; dipakai untuk menilai kualitas perusahaan jangka panjang).", "",
         "| PER | PBV | ROE | DER | Margin laba | Pendapatan YoY | Laba YoY | Kapitalisasi |",
         "|---|---|---|---|---|---|---|---|",
         f"| {num(f.get('PER'))} | {num(f.get('PBV'), 2)} | {pct(f.get('ROE'))} | {der} | {pct(f.get('NPM'))} | "
         f"{pct(f.get('growth_rev'))} | {pct(f.get('growth_laba'))} | "
         f"{'-' if not fund._ok(f.get('MCAP')) else num(f['MCAP'] / 1e12, 2) + ' T'} |", ""]
    mu = f.get("mata_uang", "IDR")
    if mu != "IDR":
        kurs = f.get("kurs")
        L += [f"Laporan keuangan emiten ini disajikan dalam **{mu}**. "
              + (f"PBV dihitung ulang dengan kurs {mu}/IDR {rp(kurs)}." if kurs else
                 "Kurs tidak tersedia, sehingga PBV tidak dihitung."), ""]
    if f.get("kuartal"):
        if mu == "IDR":
            bagi, satuan = 1e9, "miliar Rp"
        else:
            bagi, satuan = 1e6, f"juta {mu}"
        L += [f"Laporan laba rugi per kuartal ({satuan}):", "", "| Periode | Pendapatan | Laba bersih |", "|---|---|---|"]
        for k in f["kuartal"]:
            pend = "-" if not fund._ok(k["pendapatan"]) else num(k["pendapatan"] / bagi, 1)
            laba = "-" if not fund._ok(k["laba"]) else num(k["laba"] / bagi, 1)
            L.append(f"| {k['periode']} | {pend} | {laba} |")
        L.append("")
    if h["fund_rincian"]:
        L += ["| Kondisi | Poin |", "|---|---|"] + [f"| {a} | {p:+.2f} |" for p, a in h["fund_rincian"]]
    L += ["", "_Sumber: Yahoo Finance. Untuk keputusan penting, cocokkan dengan laporan resmi di idx.co.id._"]
    return L


def laporan(h: dict, chart: str) -> str:
    t, y = h["t"], h["y"]
    chg = t["Close"] - y["Close"]
    pct = chg / y["Close"] * 100
    L = [f"# Analisa harian {h['kode']} — {h['tanggal']}", "",
         f"![grafik]({chart})", "",
         "## Ringkasan", "",
         f"| Open | High | Low | Close | Perubahan | Volume |",
         f"|---|---|---|---|---|---|",
         f"| {rp(t['Open'])} | {rp(t['High'])} | {rp(t['Low'])} | **{rp(t['Close'])}** | "
         f"{chg:+.0f} ({pct:+.2f}%) | {rp(t['Volume'])} |", "",
         ] + blok_nilai(h) + blok_posisi(h) + ["## 1. Candlestick", "", h["candle_dasar"], ""]
    if h["pola"]:
        for nama, arah, ket in h["pola"]:
            tanda = "🟢" if arah > 0 else "🔴" if arah < 0 else "⚪"
            L.append(f"- {tanda} **{nama}** — {ket}")
    else:
        L.append("- Tidak ada pola candle khusus yang terdeteksi.")
    L += ["", "## 2. Volume", ""] + [f"- {s}" for s in h["vol"]]
    L += ["", "## 3. Stochastic & Stoch RSI", ""] + [f"- {s}" for s in h["sto"]]
    L += ["", "## 4. Tren (Moving Average)", ""] + h["tren"]
    L += ["", "## 5. Bollinger Bands", ""] + [f"- {s}" for s in h["bb"]]
    L += ["", "## 6. MACD & RSI", ""] + [f"- {s}" for s in h["lain"]]
    L += ["", "## 7. Support & Resistance", ""] + [f"- {s}" for s in h["sr"]]
    L += ["", "## 8. Fundamental (laporan keuangan)", ""] + blok_fundamental(h)
    L += ["", "## 9. Cara nilai teknikal dihitung", "",
          "Setiap aspek mulai dari **5** (netral), lalu ditambah atau dikurangi poin di bawah ini, "
          "dan dibatasi 0–10. Nilai total = rata-rata berbobot.", ""]
    for nama, (nilai, rincian) in h["nilai"]["aspek"].items():
        L += [f"**{nama}: {nilai:.1f}/10** (bobot {BOBOT[nama]:.0%})", "", "| Kondisi | Poin |", "|---|---|"]
        for poin, alasan in rincian:
            L.append(f"| {alasan} | {poin:+.2f} |")
        L.append("")
    L += ["", DISCLAIMER, ""]
    return "\n".join(L)


def update_readme(semua: list[dict]):
    readme = ROOT / "README.md"
    semua = sorted(semua, key=lambda h: -h["nilai"]["total"])  # nilai tertinggi di atas
    rows = ["| Saham | Tanggal | Close | Perubahan | Tren | Volume | Stoch | Momentum | Candle | Total | Keputusan | Fundamental |",
            "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for h in semua:
        t, y = h["t"], h["y"]
        pct = (t["Close"] - y["Close"]) / y["Close"] * 100
        rows.append(f"| [{h['kode']}](reports/{h['kode']}/latest.md) | {h['tanggal']} | {rp(t['Close'])} | "
                    f"{pct:+.2f}% | " + " | ".join(f"{v[0]:.1f}" for v in h["nilai"]["aspek"].values())
                    + f" | **{h['nilai']['total']:.1f}** | {IKON[h['nilai']['label']]} {h['nilai']['label']} | "
                    + f"{num(h.get('fund_nilai'))} {fund.label(h.get('fund_nilai')) if h.get('fund') else ''} |")
    port = ["| Saham | Lot | Rata-rata | Harga | Modal | Untung/rugi | Keputusan hari ini |",
            "|---|---|---|---|---|---|---|"]
    tot_modal = tot_pl = 0.0
    for h in semua:
        p = h.get("posisi")
        if not p or p["lot"] == 0:
            continue
        v = porto.nilai_sekarang(p, float(h["t"]["Close"]))
        tot_modal += v["modal"]
        tot_pl += v["kotor"]
        port.append(f"| [{h['kode']}](reports/{h['kode']}/latest.md) | {p['lot']} | {num(p['avg'], 1)} | "
                    f"{rp(h['t']['Close'])} | {rp(v['modal'])} | {'🟢' if v['kotor'] >= 0 else '🔴'} "
                    f"{rp(v['kotor'])} ({v['persen']:+.2f}%) | {IKON[h['nilai']['label']]} {h['nilai']['label']} |")
    if db.aktif():
        port = ["_Portofolio tidak ditampilkan di repo. Lihat di dashboard (perlu login)._"]
    elif len(port) > 2:
        port.append(f"| **Total** | | | | **{rp(tot_modal)}** | **{rp(tot_pl)} "
                    f"({(tot_pl / tot_modal * 100 if tot_modal else 0):+.2f}%)** | |")
    else:
        port = ["_Belum ada posisi. Isi `transaksi.csv`._"]
    blok_p = "<!-- PORTOFOLIO:START -->\n" + "\n".join(port) + "\n<!-- PORTOFOLIO:END -->"
    blok = "<!-- RINGKASAN:START -->\n" + "\n".join(rows) + "\n<!-- RINGKASAN:END -->"
    teks = readme.read_text(encoding="utf-8")
    teks = re.sub(r"<!-- RINGKASAN:START -->.*?<!-- RINGKASAN:END -->", blok, teks, flags=re.S)
    teks = re.sub(r"<!-- PORTOFOLIO:START -->.*?<!-- PORTOFOLIO:END -->", blok_p, teks, flags=re.S)
    readme.write_text(teks, encoding="utf-8")


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description="Analisa teknikal harian saham BEI")
    ap.add_argument("kode", nargs="*", help="kode saham, misal RAJA BBCA (default: isi saham.txt)")
    ap.add_argument("--csv", help="pakai file CSV, hanya untuk satu kode")
    ap.add_argument("--tanpa-fundamental", action="store_true", help="lewati data laporan keuangan")
    a = ap.parse_args()
    sb = db.Supabase() if db.aktif() and not a.csv else None
    if sb:
        print("Memakai database Supabase.")
        kode_list = [k.upper() for k in a.kode] or sb.watchlist()
        trx = sb.transaksi()
        if not kode_list and trx.empty:
            sys.exit("Tabel saham_watchlist kosong (atau tidak bisa dibaca). Tambahkan kode saham di "
                     "Supabase, lalu pastikan SUPABASE_SERVICE_KEY berisi Secret key.")
    else:
        kode_list = [k.upper() for k in a.kode] or [
            s.strip().upper() for s in (ROOT / "saham.txt").read_text().splitlines()
            if s.strip() and not s.startswith("#")]
        trx = porto.baca(ROOT / "transaksi.csv")
    if not a.kode:  # saham yang sedang dipegang ikut dianalisa
        for k in trx["kode"].unique():
            p = porto.posisi(trx, k)
            if p and p["lot"] > 0 and k not in kode_list:
                kode_list.append(k)

    semua, gagal = [], []
    for kode in kode_list:
        try:
            df = ambil_data(kode, a.csv)
            if len(df) < 30:
                raise ValueError(f"data terlalu sedikit ({len(df)} hari)")
            h = analisa(kode, df)
            h["fund"] = None
            if not a.csv and not a.tanpa_fundamental:
                try:
                    h["fund"] = fund.ambil(kode)
                except Exception as e:
                    print(f"[{kode}] data fundamental gagal: {e}", file=sys.stderr)
            h["fund_nilai"], h["fund_rincian"] = fund.nilai(h["fund"]) if h["fund"] else (None, [])
            # Mode Supabase: posisi pribadi tidak ditulis ke repo (repo bisa public);
            # posisi hanya tampil di dashboard setelah login.
            h["posisi"] = None if sb else porto.posisi(trx, kode)
        except Exception as e:  # lanjut ke saham lain
            gagal.append(kode)
            print(f"[{kode}] gagal: {e}", file=sys.stderr)
            continue
        folder = ROOT / "reports" / kode
        folder.mkdir(parents=True, exist_ok=True)
        tgl = h["tanggal"]
        gambar(h, ROOT / "charts" / kode / f"{tgl}.png")
        gambar(h, ROOT / "charts" / kode / "latest.png")
        (folder / f"{tgl}.md").write_text(laporan(h, f"../../charts/{kode}/{tgl}.png"), encoding="utf-8")
        (folder / "latest.md").write_text(laporan(h, f"../../charts/{kode}/latest.png"), encoding="utf-8")
        if sb:
            try:
                sb.simpan_harga(kode, df)
                sb.simpan_analisa(h)
                sb.simpan_fundamental(h)
                if h.get("fund") and h["fund"].get("nama"):   # nama perusahaan untuk pencarian berita
                    sb.upsert("saham_watchlist", [{"kode": kode, "nama": h["fund"]["nama"]}], "kode")
            except Exception as e:
                gagal.append(kode)
                print(f"[{kode}] gagal menyimpan ke Supabase: {e}", file=sys.stderr)
        semua.append(h)
        print(f"[{kode}] {h['tanggal']} close {rp(h['t']['Close'])} -> {h['nilai']['label']} "
              f"({h['nilai']['total']:.1f}/10)")

    if semua:
        update_readme(semua)
    if gagal and not semua:
        sys.exit(1)


if __name__ == "__main__":
    main()
