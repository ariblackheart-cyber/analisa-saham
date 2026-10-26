"""Catatan jual beli, harga rata-rata, untung/rugi, dan simulasi average down.

transaksi.csv:
    tanggal,kode,aksi,lot,harga
    2026-10-01,RAJA,beli,10,520
    2026-10-15,RAJA,beli,10,480
    2026-10-20,RAJA,jual,5,500

1 lot = 100 lembar. Harga rata-rata dihitung seperti aplikasi sekuritas (rata-rata tertimbang,
tidak berubah saat menjual). Fee bisa diubah di bawah sesuai sekuritas kamu.
"""
from pathlib import Path

import pandas as pd

LEMBAR_PER_LOT = 100
FEE_BELI = 0.0015   # 0,15%
FEE_JUAL = 0.0025   # 0,25% (sudah termasuk PPh final 0,1%)


def baca(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame(columns=["tanggal", "kode", "aksi", "lot", "harga"])
    df = pd.read_csv(path, comment="#", skipinitialspace=True)
    df.columns = [c.strip().lower() for c in df.columns]
    df["kode"] = df["kode"].str.strip().str.upper()
    df["aksi"] = df["aksi"].str.strip().str.lower()
    df["tanggal"] = pd.to_datetime(df["tanggal"])
    return df.sort_values("tanggal", kind="stable")


def posisi(trx: pd.DataFrame, kode: str) -> dict | None:
    """Hitung posisi satu saham dari riwayat transaksinya."""
    t = trx[trx["kode"] == kode]
    if t.empty:
        return None
    lembar, avg, realized, fee_total, modal_masuk = 0, 0.0, 0.0, 0.0, 0.0
    riwayat = []
    for r in t.itertuples():
        n = int(r.lot) * LEMBAR_PER_LOT
        nilai = n * float(r.harga)
        if r.aksi == "beli":
            avg = (avg * lembar + nilai) / (lembar + n)
            lembar += n
            fee = nilai * FEE_BELI
            modal_masuk += nilai + fee
            pl = None
        elif r.aksi == "jual":
            n = min(n, lembar)
            nilai = n * float(r.harga)
            fee = nilai * FEE_JUAL
            pl = (float(r.harga) - avg) * n - fee
            realized += pl
            lembar -= n
            if lembar == 0:
                avg = 0.0
        else:
            raise ValueError(f"aksi tidak dikenal: {r.aksi} (pakai 'beli' atau 'jual')")
        fee_total += fee
        riwayat.append(dict(tanggal=r.tanggal.date(), aksi=r.aksi, lot=int(r.lot), harga=float(r.harga),
                            lot_sisa=lembar // LEMBAR_PER_LOT, avg=avg, pl=pl))
    return dict(kode=kode, lembar=lembar, lot=lembar // LEMBAR_PER_LOT, avg=avg,
                realized=realized, fee=fee_total, riwayat=riwayat)


def nilai_sekarang(p: dict, harga: float) -> dict:
    modal = p["avg"] * p["lembar"]
    pasar = harga * p["lembar"]
    kotor = pasar - modal
    bersih = kotor - pasar * FEE_JUAL
    return dict(modal=modal, pasar=pasar, kotor=kotor, bersih=bersih,
                persen=(kotor / modal * 100) if modal else 0.0)


def simulasi_avg_down(p: dict, level: list[tuple[str, float]]):
    """Untuk tiap level harga dan jumlah lot tambahan, hitung rata-rata baru.

    level: list (nama, harga). Jumlah lot tambahan = 50%, 100%, 200% dari lot yang dipegang.
    """
    hasil = []
    if p["lot"] == 0:
        return hasil
    pilihan_lot = sorted({max(1, round(p["lot"] * f)) for f in (0.5, 1.0, 2.0)})
    for nama, harga in level:
        if pd.isna(harga) or harga <= 0:
            continue
        for tambah in pilihan_lot:
            n = tambah * LEMBAR_PER_LOT
            avg_baru = (p["avg"] * p["lembar"] + harga * n) / (p["lembar"] + n)
            hasil.append(dict(level=nama, harga=harga, tambah_lot=tambah,
                              dana=harga * n * (1 + FEE_BELI),
                              lot_total=p["lot"] + tambah, avg_baru=avg_baru,
                              turun=(avg_baru - p["avg"]) / p["avg"] * 100 if p["avg"] else 0.0,
                              naik_perlu=(avg_baru / harga - 1) * 100))
    return hasil


def lot_untuk_target_avg(p: dict, harga: float, target_avg: float):
    """Berapa lot harus dibeli di `harga` supaya rata-rata turun ke `target_avg`."""
    if not (harga < target_avg < p["avg"]):
        return None
    n = p["lembar"] * (p["avg"] - target_avg) / (target_avg - harga)
    return int(-(-n // LEMBAR_PER_LOT))  # dibulatkan ke atas per lot
