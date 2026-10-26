"""Penilaian 0–10 per aspek dan keputusan akhir.

Setiap aspek mulai dari nilai 5 (netral). Setiap kondisi menambah atau mengurangi poin,
dan semua rinciannya ditampilkan di laporan supaya bisa dicek manual.
Nilai akhir dibatasi 0–10.

Bobot total:
    Tren 25%, Volume 20%, Stochastic 20%, Momentum (MACD & RSI) 20%, Candle 15%
"""
import pandas as pd

BOBOT = {"Tren": 0.25, "Volume": 0.20, "Stochastic": 0.20, "Momentum": 0.20, "Candle": 0.15}


def _clamp(x):
    return max(0.0, min(10.0, x))


def _aspek(rincian):
    """rincian: list (poin, alasan). Mengembalikan (nilai, rincian)."""
    return _clamp(5 + sum(p for p, _ in rincian)), rincian


def nilai_tren(d, t):
    r = []
    for ma, poin in (("MA5", 1.0), ("MA20", 1.5), ("MA100", 1.5)):
        if pd.isna(t[ma]):
            continue
        if t["Close"] > t[ma]:
            r.append((+poin, f"Harga di atas {ma}"))
        else:
            r.append((-poin, f"Harga di bawah {ma}"))
    if len(d) > 25 and not pd.isna(d["MA20"].iloc[-6]):
        slope = t["MA20"] - d["MA20"].iloc[-6]
        if slope > 0:
            r.append((+1.0, "MA20 menanjak dalam 5 hari"))
        elif slope < 0:
            r.append((-1.0, "MA20 menurun dalam 5 hari"))
    return _aspek(r)


def nilai_volume(d, t, y):
    r = []
    vr = t["Vol_ratio"]
    arah = 1 if t["Close"] > y["Close"] else -1 if t["Close"] < y["Close"] else 0
    if not pd.isna(vr) and arah:
        # volume besar menguatkan arah hari ini, maksimal ±3 poin pada 3x rata-rata
        kuat = min(vr, 3.0) / 3.0 * 3.0
        kata = "naik" if arah > 0 else "turun"
        r.append((arah * kuat, f"Harga {kata} dengan volume {vr:.2f}x rata-rata 20 hari"))
    last5 = d.tail(5)
    up = last5.loc[last5["Close"] > last5["Open"], "Volume"].sum()
    dn = last5.loc[last5["Close"] < last5["Open"], "Volume"].sum()
    if up + dn > 0:
        share = up / (up + dn)
        r.append(((share - 0.5) * 4, f"Volume hijau 5 hari {share:.0%} (akumulasi vs distribusi)"))
    return _aspek(r)


def nilai_stochastic(t, y):
    r = []
    for nama, k, dd, pk, pd_ in (("Stochastic", "Stoch_K", "Stoch_D", y["Stoch_K"], y["Stoch_D"]),
                                 ("Stoch RSI", "SRSI_K", "SRSI_D", y["SRSI_K"], y["SRSI_D"])):
        K, D = t[k], t[dd]
        if pd.isna(K) or pd.isna(D):
            continue
        if pk <= pd_ and K > D:
            r.append((+1.5, f"{nama}: K memotong D ke atas"))
        elif pk >= pd_ and K < D:
            r.append((-1.5, f"{nama}: K memotong D ke bawah"))
        elif K > D:
            r.append((+0.75, f"{nama}: K di atas D"))
        else:
            r.append((-0.75, f"{nama}: K di bawah D"))
        if K <= 20:
            r.append((+0.75, f"{nama} oversold ({K:.0f}): peluang pantulan"))
        elif K >= 80:
            r.append((-0.75, f"{nama} overbought ({K:.0f}): rawan koreksi"))
    return _aspek(r)


def nilai_momentum(t, y):
    r = []
    if t["MACD"] > t["MACD_sig"]:
        r.append((+1.5, "MACD di atas garis sinyal"))
    else:
        r.append((-1.5, "MACD di bawah garis sinyal"))
    if t["MACD"] > 0:
        r.append((+1.0, "MACD di atas nol"))
    else:
        r.append((-1.0, "MACD di bawah nol"))
    if t["MACD_hist"] > y["MACD_hist"]:
        r.append((+1.0, "Histogram MACD membaik"))
    else:
        r.append((-1.0, "Histogram MACD memburuk"))
    rsi = t["RSI"]
    if rsi >= 70:
        r.append((-1.0, f"RSI {rsi:.0f} overbought"))
    elif rsi >= 50:
        r.append((+1.0, f"RSI {rsi:.0f} di zona kuat (50–70)"))
    elif rsi > 30:
        r.append((-0.5, f"RSI {rsi:.0f} di zona lemah (30–50)"))
    else:
        r.append((+0.5, f"RSI {rsi:.0f} oversold, peluang pantulan"))
    return _aspek(r)


def nilai_candle(t, pola):
    r = []
    rng = max(t["High"] - t["Low"], 1e-9)
    body = (t["Close"] - t["Open"]) / rng  # -1..+1
    r.append((body * 1.5, f"Badan candle {'hijau' if body > 0 else 'merah' if body < 0 else 'netral'} "
                          f"{abs(body):.0%} dari rentang"))
    upper = (t["High"] - max(t["Open"], t["Close"])) / rng
    lower = (min(t["Open"], t["Close"]) - t["Low"]) / rng
    if lower - upper > 0.3:
        r.append((+0.5, "Sumbu bawah lebih panjang: ada penolakan harga rendah"))
    elif upper - lower > 0.3:
        r.append((-0.5, "Sumbu atas lebih panjang: ada penolakan harga tinggi"))
    for nama, arah, _ in pola:
        if arah:
            r.append((arah * 2.0, f"Pola {nama}"))
    return _aspek(r)


def keputusan(total, aspek):
    """Aturan keputusan mekanis dari nilai total dan nilai tren."""
    tren = aspek["Tren"][0]
    if total >= 7 and tren >= 5:
        return "BELI", "Mayoritas indikator searah naik dan tren mendukung."
    if total >= 5.5:
        if tren < 5:
            return "PANTAU", ("Momentum membaik tetapi tren masih turun. Tunggu harga kembali di atas MA20 "
                              "sebelum masuk.")
        return "PANTAU", "Cukup positif, tetapi belum kuat. Tunggu konfirmasi candle/volume berikutnya."
    if total >= 4:
        return "TUNGGU", "Sinyal campur aduk. Belum ada alasan teknikal yang jelas untuk masuk."
    return "HINDARI", "Mayoritas indikator searah turun. Bagi yang memegang, pertimbangkan batas rugi."


def rencana(d, t):
    """Level harga mekanis: area masuk, batas rugi, target."""
    support = d["Low"].tail(20).min()
    resist = d["High"].tail(20).max()
    stop = min(support, t["Close"] * 0.95)
    target1 = t["MA20"] if t["MA20"] > t["Close"] else resist
    target2 = resist if resist > target1 else t["BB_up"]
    risk = t["Close"] - stop
    reward = target1 - t["Close"]
    rr = reward / risk if risk > 0 else float("nan")
    return dict(support=support, resist=resist, stop=stop, target1=target1, target2=target2, rr=rr)


def hitung(d, t, y, pola):
    aspek = {
        "Tren": nilai_tren(d, t),
        "Volume": nilai_volume(d, t, y),
        "Stochastic": nilai_stochastic(t, y),
        "Momentum": nilai_momentum(t, y),
        "Candle": nilai_candle(t, pola),
    }
    total = sum(aspek[k][0] * w for k, w in BOBOT.items())
    label, alasan = keputusan(total, aspek)
    return dict(aspek=aspek, total=total, label=label, alasan=alasan, rencana=rencana(d, t))
