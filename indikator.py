"""Perhitungan indikator teknikal (setara pengaturan default Stockbit)."""
import numpy as np
import pandas as pd


def sma(s: pd.Series, n: int) -> pd.Series:
    return s.rolling(n).mean()


def ema(s: pd.Series, n: int) -> pd.Series:
    return s.ewm(span=n, adjust=False).mean()


def rsi(close: pd.Series, n: int = 14) -> pd.Series:
    """RSI metode Wilder."""
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1 / n, adjust=False, min_periods=n).mean()
    avg_loss = loss.ewm(alpha=1 / n, adjust=False, min_periods=n).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    out = 100 - 100 / (1 + rs)
    return out.where(avg_loss != 0, 100.0)


def bollinger(close: pd.Series, n: int = 20, k: float = 2.0):
    mid = sma(close, n)
    std = close.rolling(n).std(ddof=0)
    return mid + k * std, mid, mid - k * std


def macd(close: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9):
    line = ema(close, fast) - ema(close, slow)
    sig = ema(line, signal)
    return line, sig, line - sig


def stochastic(high, low, close, k: int = 14, smooth_k: int = 3, d: int = 3):
    """Stochastic oscillator klasik (14, 3, 3)."""
    ll = low.rolling(k).min()
    hh = high.rolling(k).max()
    raw = 100 * (close - ll) / (hh - ll).replace(0, np.nan)
    k_line = raw.rolling(smooth_k).mean()
    return k_line, k_line.rolling(d).mean()


def stoch_rsi(close, rsi_len: int = 14, stoch_len: int = 14, k: int = 3, d: int = 3):
    """Stoch RSI (14, 14, 3, 3), sama seperti di Stockbit/TradingView."""
    r = rsi(close, rsi_len)
    ll = r.rolling(stoch_len).min()
    hh = r.rolling(stoch_len).max()
    raw = 100 * (r - ll) / (hh - ll).replace(0, np.nan)
    k_line = raw.rolling(k).mean()
    return k_line, k_line.rolling(d).mean()


def hitung_semua(df: pd.DataFrame) -> pd.DataFrame:
    """Menambah kolom indikator ke DataFrame OHLCV."""
    out = df.copy()
    c, h, l, v = out["Close"], out["High"], out["Low"], out["Volume"]
    out["MA5"] = sma(c, 5)
    out["MA20"] = sma(c, 20)
    out["MA100"] = sma(c, 100)
    out["BB_up"], out["BB_mid"], out["BB_low"] = bollinger(c)
    out["MACD"], out["MACD_sig"], out["MACD_hist"] = macd(c)
    out["RSI"] = rsi(c)
    out["Stoch_K"], out["Stoch_D"] = stochastic(h, l, c)
    out["SRSI_K"], out["SRSI_D"] = stoch_rsi(c)
    out["Vol_MA20"] = sma(v, 20)
    out["Vol_ratio"] = v / out["Vol_MA20"]
    return out
