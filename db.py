"""Penghubung ke Supabase (lewat REST API / PostgREST).

Aktif jika environment variable berikut diisi:
    SUPABASE_URL          contoh: https://abcd1234.supabase.co
    SUPABASE_SERVICE_KEY  Secret key (sb_secret_…) atau service_role key lama
                          (Project Settings → API Keys). RAHASIA, jangan di-commit.
                          BUKAN publishable/anon key.

Jika tidak diisi, program memakai file lokal (saham.txt dan transaksi.csv) seperti biasa.

Perintah tambahan:
    python db.py cek                 # tes koneksi dan hitung isi tabel
    python db.py impor-transaksi     # salin isi transaksi.csv ke tabel transaksi
    python db.py impor-watchlist     # salin isi saham.txt ke tabel watchlist
"""
import json
import math
import os
import sys
from datetime import date
from pathlib import Path

import pandas as pd
import requests

ROOT = Path(__file__).parent


def aktif() -> bool:
    return bool(os.environ.get("SUPABASE_URL") and os.environ.get("SUPABASE_SERVICE_KEY"))


SALAH_KEY = ("SUPABASE_SERVICE_KEY berisi {jenis}, bukan secret key. Key ini tidak bisa membaca tabel saham "
             "karena dilindungi Row Level Security. Buka Supabase → Project Settings → API Keys, salin "
             "**Secret key** (diawali sb_secret_) atau service_role key lama, lalu perbarui secret di GitHub.")


def cek_key(key: str):
    """Hentikan program jika key yang dipakai bukan secret/service_role key."""
    if key.startswith("sb_secret_"):
        return
    if key.startswith("sb_publishable_"):
        raise SystemExit(SALAH_KEY.format(jenis="publishable key (sb_publishable_…)"))
    parts = key.split(".")
    if len(parts) == 3:  # JWT lama: periksa role
        import base64
        try:
            pad = parts[1] + "=" * (-len(parts[1]) % 4)
            role = json.loads(base64.urlsafe_b64decode(pad)).get("role")
        except Exception:
            role = None
        if role == "service_role":
            return
        if role:
            raise SystemExit(SALAH_KEY.format(jenis=f"key dengan role '{role}'"))
    raise SystemExit("SUPABASE_SERVICE_KEY tidak dikenali. Gunakan Secret key (sb_secret_…) dari "
                     "Supabase → Project Settings → API Keys.")


def _bersih(v):
    """Ubah nilai numpy/pandas/NaN menjadi tipe JSON biasa."""
    if v is None:
        return None
    if isinstance(v, (date, pd.Timestamp)):
        return str(pd.Timestamp(v).date())
    if hasattr(v, "item"):
        v = v.item()
    if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
        return None
    if isinstance(v, dict):
        return {k: _bersih(x) for k, x in v.items()}
    if isinstance(v, (list, tuple)):
        return [_bersih(x) for x in v]
    return v


class Supabase:
    def __init__(self, url=None, key=None, session=None):
        self.url = (url or os.environ["SUPABASE_URL"]).rstrip("/") + "/rest/v1"
        key = (key or os.environ["SUPABASE_SERVICE_KEY"]).strip()
        cek_key(key)
        self.s = session or requests.Session()
        self.s.headers.update({"apikey": key, "Content-Type": "application/json"})
        if not key.startswith("sb_"):  # key lama (JWT) juga dikirim sebagai Bearer
            self.s.headers["Authorization"] = f"Bearer {key}"

    def _cek(self, r):
        if r.status_code >= 400:
            raise RuntimeError(f"Supabase {r.status_code}: {r.text[:300]}")
        return r

    def ambil(self, tabel, params=None):
        hasil, mulai = [], 0
        while True:  # paging 1000 baris
            p = dict(params or {}, limit=1000, offset=mulai)
            r = self._cek(self.s.get(f"{self.url}/{tabel}", params=p, timeout=30))
            data = r.json()
            hasil += data
            if len(data) < 1000:
                return hasil
            mulai += 1000

    def upsert(self, tabel, rows, on_conflict):
        rows = [_bersih(r) for r in rows]
        for i in range(0, len(rows), 500):
            self._cek(self.s.post(f"{self.url}/{tabel}", params={"on_conflict": on_conflict},
                                  data=json.dumps(rows[i:i + 500]),
                                  headers={"Prefer": "resolution=merge-duplicates,return=minimal"},
                                  timeout=60))

    def insert(self, tabel, rows):
        rows = [_bersih(r) for r in rows]
        if rows:
            self._cek(self.s.post(f"{self.url}/{tabel}", data=json.dumps(rows),
                                  headers={"Prefer": "return=minimal"}, timeout=60))

    # ------------------------------------------------------------ baca
    def watchlist(self) -> list[str]:
        return [r["kode"] for r in self.ambil("saham_watchlist", {"aktif": "eq.true", "select": "kode",
                                                             "order": "kode"})]

    def transaksi(self) -> pd.DataFrame:
        rows = self.ambil("saham_transaksi", {"select": "tanggal,kode,aksi,lot,harga", "order": "tanggal,id"})
        df = pd.DataFrame(rows, columns=["tanggal", "kode", "aksi", "lot", "harga"])
        if not df.empty:
            df["tanggal"] = pd.to_datetime(df["tanggal"])
            df["harga"] = df["harga"].astype(float)
            df["lot"] = df["lot"].astype(int)
        return df

    # ------------------------------------------------------------ tulis
    def simpan_harga(self, kode, df: pd.DataFrame):
        rows = [dict(kode=kode, tanggal=idx, open=r.Open, high=r.High, low=r.Low, close=r.Close,
                     volume=int(r.Volume)) for idx, r in zip(df.index, df.itertuples())]
        self.upsert("saham_harga_harian", rows, "kode,tanggal")

    def simpan_analisa(self, h: dict):
        t, y, n = h["t"], h["y"], h["nilai"]
        a, r = n["aspek"], n["rencana"]
        row = dict(
            kode=h["kode"], tanggal=h["tanggal"], close=t["Close"],
            perubahan_pct=(t["Close"] - y["Close"]) / y["Close"] * 100,
            nilai_tren=a["Tren"][0], nilai_volume=a["Volume"][0], nilai_stochastic=a["Stochastic"][0],
            nilai_momentum=a["Momentum"][0], nilai_candle=a["Candle"][0],
            nilai_total=n["total"], keputusan=n["label"],
            pola_candle=[p[0] for p in h["pola"]],
            ma5=t["MA5"], ma20=t["MA20"], ma100=t["MA100"], rsi=t["RSI"],
            macd=t["MACD"], macd_signal=t["MACD_sig"], stoch_k=t["Stoch_K"], stoch_d=t["Stoch_D"],
            stoch_rsi_k=t["SRSI_K"], stoch_rsi_d=t["SRSI_D"], volume_ratio=t["Vol_ratio"],
            support=r["support"], resistance=r["resist"], stop_loss=r["stop"],
            target1=r["target1"], target2=r["target2"],
            rincian={k: [{"poin": p, "alasan": s} for p, s in v[1]] for k, v in a.items()},
        )
        self.upsert("saham_analisa_harian", [row], "kode,tanggal")

    def simpan_fundamental(self, h: dict):
        f = h.get("fund")
        if not f:
            return
        row = dict(kode=h["kode"], tanggal=date.today(), per=f.get("PER"), pbv=f.get("PBV"),
                   roe=f.get("ROE"), der=f.get("DER"), npm=f.get("NPM"),
                   growth_pendapatan=f.get("growth_rev"), growth_laba=f.get("growth_laba"),
                   market_cap=f.get("MCAP"), nilai=h.get("fund_nilai"), kuartal=f.get("kuartal"))
        self.upsert("saham_fundamental", [row], "kode,tanggal")


# ---------------------------------------------------------------- CLI
def main():
    if not aktif():
        sys.exit("Isi SUPABASE_URL dan SUPABASE_SERVICE_KEY dulu.")
    db = Supabase()
    cmd = sys.argv[1] if len(sys.argv) > 1 else "cek"
    if cmd == "cek":
        for t in ("saham_watchlist", "saham_transaksi", "saham_harga_harian", "saham_analisa_harian", "saham_fundamental"):
            print(f"{t:15} {len(db.ambil(t, {'select': '*'}))} baris")
    elif cmd == "impor-transaksi":
        import portofolio
        df = portofolio.baca(ROOT / "transaksi.csv")
        db.insert("saham_transaksi", df[["tanggal", "kode", "aksi", "lot", "harga"]].to_dict("records"))
        print(f"{len(df)} transaksi disalin. Setelah ini, catat transaksi baru langsung di Supabase.")
    elif cmd == "impor-watchlist":
        kode = [s.strip().upper() for s in (ROOT / "saham.txt").read_text().splitlines()
                if s.strip() and not s.startswith("#")]
        db.upsert("saham_watchlist", [{"kode": k} for k in kode], "kode")
        print(f"{len(kode)} kode disalin.")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
