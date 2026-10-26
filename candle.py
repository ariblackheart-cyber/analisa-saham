"""Deteksi pola candlestick dan penjelasannya dalam bahasa Indonesia.

Setiap pola mengembalikan (nama, arah, penjelasan).
arah: +1 = cenderung naik (bullish), -1 = cenderung turun (bearish), 0 = netral.
"""


def _parts(o, h, l, c):
    body = abs(c - o)
    rng = max(h - l, 1e-9)
    upper = h - max(o, c)
    lower = min(o, c) - l
    return body, rng, upper, lower


def baca_candle(rows, tren_turun: bool, tren_naik: bool):
    """rows: list dict OHLC, minimal 1, maksimal 3 candle terakhir (urut lama -> baru)."""
    cur = rows[-1]
    o, h, l, c = cur["Open"], cur["High"], cur["Low"], cur["Close"]
    body, rng, upper, lower = _parts(o, h, l, c)
    hijau, merah = c > o, c < o
    pola = []

    # ---- satu candle ----
    if body / rng <= 0.1:
        if lower > 0.6 * rng:
            pola.append(("Dragonfly doji", 1 if tren_turun else 0,
                         "Badan sangat kecil dengan sumbu bawah panjang: penjual sempat menekan, tetapi pembeli mengembalikan harga."))
        elif upper > 0.6 * rng:
            pola.append(("Gravestone doji", -1 if tren_naik else 0,
                         "Badan sangat kecil dengan sumbu atas panjang: pembeli sempat mendorong, tetapi penjual mengembalikan harga."))
        else:
            pola.append(("Doji", 0,
                         "Badan sangat kecil: pasar ragu, kekuatan beli dan jual seimbang."))
    elif body / rng >= 0.9:
        if hijau:
            pola.append(("Marubozu hijau", 1, "Hampir tanpa sumbu: pembeli menguasai sepanjang hari."))
        else:
            pola.append(("Marubozu merah", -1, "Hampir tanpa sumbu: penjual menguasai sepanjang hari."))
    else:
        if lower >= 2 * body and upper <= body:
            if tren_turun:
                pola.append(("Hammer", 1,
                             "Sumbu bawah panjang setelah tren turun: ada penolakan harga rendah, potensi pembalikan naik."))
            elif tren_naik:
                pola.append(("Hanging man", -1,
                             "Bentuk seperti hammer tetapi muncul setelah tren naik: tanda awal tekanan jual."))
        if upper >= 2 * body and lower <= body:
            if tren_naik:
                pola.append(("Shooting star", -1,
                             "Sumbu atas panjang setelah tren naik: harga tinggi ditolak penjual, potensi pembalikan turun."))
            elif tren_turun:
                pola.append(("Inverted hammer", 1,
                             "Sumbu atas panjang setelah tren turun: pembeli mulai mencoba masuk, perlu konfirmasi."))
        if upper > 2 * body and lower > 2 * body:
            pola.append(("Spinning top", 0, "Sumbu atas dan bawah panjang, badan kecil: pasar ragu."))

    # ---- dua candle ----
    if len(rows) >= 2:
        p = rows[-2]
        po, pc = p["Open"], p["Close"]
        p_hijau, p_merah = pc > po, pc < po
        if hijau and p_merah and c >= po and o <= pc:
            pola.append(("Bullish engulfing", 1,
                         "Badan hijau menelan badan merah sebelumnya: pembeli mengambil alih."))
        if merah and p_hijau and c <= po and o >= pc:
            pola.append(("Bearish engulfing", -1,
                         "Badan merah menelan badan hijau sebelumnya: penjual mengambil alih."))
        p_mid = (po + pc) / 2
        if hijau and p_merah and o < pc and p_mid < c < po:
            pola.append(("Piercing line", 1,
                         "Dibuka di bawah penutupan kemarin lalu naik melewati separuh badan merah sebelumnya."))
        if merah and p_hijau and o > pc and po < c < p_mid:
            pola.append(("Dark cloud cover", -1,
                         "Dibuka di atas penutupan kemarin lalu turun melewati separuh badan hijau sebelumnya."))
        p_body = abs(pc - po)
        if p_body > 0 and body < 0.5 * p_body and max(o, c) < max(po, pc) and min(o, c) > min(po, pc):
            arah = 1 if p_merah else -1 if p_hijau else 0
            pola.append(("Harami", arah,
                         "Badan kecil berada di dalam badan besar sebelumnya: momentum sebelumnya melemah."))

    # ---- tiga candle ----
    if len(rows) >= 3:
        a, b = rows[-3], rows[-2]
        a_body = abs(a["Close"] - a["Open"])
        b_body = abs(b["Close"] - b["Open"])
        a_mid = (a["Open"] + a["Close"]) / 2
        if a["Close"] < a["Open"] and b_body < 0.5 * a_body and hijau and c > a_mid:
            pola.append(("Morning star", 1,
                         "Merah besar, lalu candle kecil, lalu hijau kuat: pola pembalikan naik."))
        if a["Close"] > a["Open"] and b_body < 0.5 * a_body and merah and c < a_mid:
            pola.append(("Evening star", -1,
                         "Hijau besar, lalu candle kecil, lalu merah kuat: pola pembalikan turun."))

    # deskripsi dasar
    warna = "hijau (ditutup naik)" if hijau else "merah (ditutup turun)" if merah else "netral"
    dasar = (f"Candle {warna}. Badan {body / rng:.0%} dari rentang hari ini, "
             f"sumbu atas {upper / rng:.0%}, sumbu bawah {lower / rng:.0%}.")
    return dasar, pola
