"""Data fundamental (laporan keuangan) dari Yahoo Finance dan penilaian 0–10.

Sumber: yfinance Ticker.info, quarterly_income_stmt, balance_sheet.
Untuk saham kecil di BEI datanya sering tidak lengkap; bagian yang kosong ditulis "tidak tersedia"
dan tidak ikut dinilai.
"""
import math

import pandas as pd


def _ok(x):
    return x is not None and not (isinstance(x, float) and math.isnan(x))


def _baris(df, nama_list):
    """Ambil satu baris laporan (deret per periode, terbaru di kiri) dari beberapa kemungkinan nama."""
    if df is None or getattr(df, "empty", True):
        return None
    for n in nama_list:
        if n in df.index:
            s = pd.to_numeric(df.loc[n], errors="coerce").dropna()
            if len(s):
                return s
    return None


def ambil(kode: str) -> dict:
    import yfinance as yf
    tk = yf.Ticker(f"{kode}.JK")
    data = {}
    try:
        info = tk.info or {}
    except Exception:
        info = {}
    data["PER"] = info.get("trailingPE")
    data["PBV"] = info.get("priceToBook")
    data["ROE"] = info.get("returnOnEquity")           # desimal, 0.15 = 15%
    data["NPM"] = info.get("profitMargins")            # margin laba bersih
    data["DER"] = info.get("debtToEquity")             # persen, 80 = 0,8x
    data["DY"] = info.get("dividendYield")
    data["MCAP"] = info.get("marketCap")

    try:
        q = tk.quarterly_income_stmt
    except Exception:
        q = None
    rev = _baris(q, ["Total Revenue", "Operating Revenue"])
    ni = _baris(q, ["Net Income", "Net Income Common Stockholders"])
    data["kuartal"] = []
    if ni is not None:
        for tgl in list(ni.index)[:5]:
            data["kuartal"].append(dict(periode=pd.Timestamp(tgl).date(),
                                        pendapatan=rev.get(tgl) if rev is not None else None,
                                        laba=ni.get(tgl)))
    # pertumbuhan YoY: kuartal terbaru vs kuartal yang sama tahun lalu (indeks 0 vs 4)
    def yoy(s):
        if s is None or len(s) < 5 or s.iloc[4] == 0:
            return None
        return (s.iloc[0] - s.iloc[4]) / abs(s.iloc[4])
    data["growth_rev"] = yoy(rev) if rev is not None else info.get("revenueGrowth")
    data["growth_laba"] = yoy(ni) if ni is not None else info.get("earningsGrowth")
    if data["growth_rev"] is None:
        data["growth_rev"] = info.get("revenueGrowth")
    if data["growth_laba"] is None:
        data["growth_laba"] = info.get("earningsGrowth")

    if not _ok(data["DER"]):
        try:
            bs = tk.quarterly_balance_sheet
            debt = _baris(bs, ["Total Debt"])
            eq = _baris(bs, ["Stockholders Equity", "Total Equity Gross Minority Interest"])
            if debt is not None and eq is not None and eq.iloc[0]:
                data["DER"] = debt.iloc[0] / eq.iloc[0] * 100
        except Exception:
            pass
    return data


def nilai(f: dict):
    """Nilai 0–10 mulai dari 5. Mengembalikan (nilai atau None, rincian)."""
    r = []
    per, pbv, roe, der, npm = f.get("PER"), f.get("PBV"), f.get("ROE"), f.get("DER"), f.get("NPM")
    g_rev, g_laba = f.get("growth_rev"), f.get("growth_laba")
    if _ok(per):
        if per <= 0:
            r.append((-1.5, "PER negatif: perusahaan rugi"))
        elif per < 10:
            r.append((+1.0, f"PER {per:.1f}x: murah"))
        elif per <= 20:
            r.append((+0.25, f"PER {per:.1f}x: wajar"))
        else:
            r.append((-0.75, f"PER {per:.1f}x: mahal"))
    if _ok(pbv):
        if pbv < 1:
            r.append((+0.75, f"PBV {pbv:.2f}x: di bawah nilai buku"))
        elif pbv > 4:
            r.append((-0.75, f"PBV {pbv:.2f}x: jauh di atas nilai buku"))
    if _ok(roe):
        if roe >= 0.15:
            r.append((+1.25, f"ROE {roe:.0%}: sangat efisien"))
        elif roe >= 0.08:
            r.append((+0.5, f"ROE {roe:.0%}: cukup"))
        else:
            r.append((-0.75, f"ROE {roe:.0%}: rendah"))
    if _ok(der):
        x = der / 100
        if x < 0.5:
            r.append((+0.75, f"DER {x:.2f}x: utang rendah"))
        elif x > 1.5:
            r.append((-1.0, f"DER {x:.2f}x: utang tinggi"))
    if _ok(npm):
        if npm >= 0.10:
            r.append((+0.5, f"Margin laba bersih {npm:.0%}: sehat"))
        elif npm < 0:
            r.append((-0.75, f"Margin laba bersih {npm:.0%}: rugi"))
    if _ok(g_rev):
        r.append((max(-1.0, min(1.0, g_rev * 4)), f"Pendapatan tumbuh {g_rev:+.0%} YoY"))
    if _ok(g_laba):
        r.append((max(-1.5, min(1.5, g_laba * 3)), f"Laba bersih tumbuh {g_laba:+.0%} YoY"))
    if not r:
        return None, r
    return max(0.0, min(10.0, 5 + sum(p for p, _ in r))), r


def label(v):
    if v is None:
        return "Data tidak tersedia"
    return "Kuat" if v >= 7 else "Cukup" if v >= 5.5 else "Lemah" if v >= 4 else "Buruk"
