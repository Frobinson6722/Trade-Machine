"""Technical indicator calculations from OHLCV data."""

from __future__ import annotations

import logging
from typing import Any

import pandas as pd

logger = logging.getLogger(__name__)


def compute_indicators(candles: list[dict[str, Any]]) -> dict[str, Any]:
    """Compute a full set of technical indicators from OHLCV candle data.

    Returns a dictionary with indicator values and interpretations.
    """
    if not candles or len(candles) < 14:
        return {"error": "Insufficient data for indicator calculation"}

    df = pd.DataFrame(candles)
    for col in ("open", "high", "low", "close", "volume"):
        df[col] = pd.to_numeric(df[col], errors="coerce")

    result: dict[str, Any] = {}

    # RSI (14-period)
    result["rsi"] = _compute_rsi(df["close"], period=14)

    # MACD
    result["macd"] = _compute_macd(df["close"])

    # Bollinger Bands (20-period, 2 std)
    result["bollinger"] = _compute_bollinger(df["close"], period=20, std_dev=2)

    # ATR (14-period)
    result["atr"] = _compute_atr(df, period=14)

    # Simple Moving Averages
    result["sma_20"] = float(df["close"].rolling(20).mean().iloc[-1]) if len(df) >= 20 else None
    result["sma_50"] = float(df["close"].rolling(50).mean().iloc[-1]) if len(df) >= 50 else None
    result["sma_200"] = float(df["close"].rolling(200).mean().iloc[-1]) if len(df) >= 200 else None

    # Volume analysis
    result["volume"] = _compute_volume_analysis(df)

    # Current price
    result["current_price"] = float(df["close"].iloc[-1])

    # Support / Resistance (simple pivot points)
    result["pivots"] = _compute_pivots(df)

    return result


def _compute_rsi(series: pd.Series, period: int = 14) -> dict[str, Any]:
    """Compute RSI and its interpretation."""
    delta = series.diff()
    gain = delta.where(delta > 0, 0.0).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0.0)).rolling(window=period).mean()
    rs = gain / loss.replace(0, float("inf"))
    rsi = 100 - (100 / (1 + rs))
    current = float(rsi.iloc[-1])

    if current > 70:
        signal = "overbought"
    elif current < 30:
        signal = "oversold"
    else:
        signal = "neutral"

    return {"value": round(current, 2), "signal": signal}


def _compute_macd(
    series: pd.Series, fast: int = 12, slow: int = 26, signal_period: int = 9
) -> dict[str, Any]:
    """Compute MACD, signal line, and histogram."""
    ema_fast = series.ewm(span=fast).mean()
    ema_slow = series.ewm(span=slow).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal_period).mean()
    histogram = macd_line - signal_line

    current_macd = float(macd_line.iloc[-1])
    current_signal = float(signal_line.iloc[-1])
    current_hist = float(histogram.iloc[-1])
    prev_hist = float(histogram.iloc[-2]) if len(histogram) > 1 else 0

    if current_macd > current_signal and prev_hist < 0 and current_hist > 0:
        crossover = "bullish_crossover"
    elif current_macd < current_signal and prev_hist > 0 and current_hist < 0:
        crossover = "bearish_crossover"
    elif current_macd > current_signal:
        crossover = "bullish"
    else:
        crossover = "bearish"

    return {
        "macd": round(current_macd, 4),
        "signal": round(current_signal, 4),
        "histogram": round(current_hist, 4),
        "crossover": crossover,
    }


def _compute_bollinger(
    series: pd.Series, period: int = 20, std_dev: int = 2
) -> dict[str, Any]:
    """Compute Bollinger Bands."""
    sma = series.rolling(period).mean()
    std = series.rolling(period).std()
    upper = sma + std_dev * std
    lower = sma - std_dev * std

    current_price = float(series.iloc[-1])
    upper_val = float(upper.iloc[-1])
    lower_val = float(lower.iloc[-1])
    middle_val = float(sma.iloc[-1])
    width = (upper_val - lower_val) / middle_val if middle_val else 0

    if current_price > upper_val:
        position = "above_upper"
    elif current_price < lower_val:
        position = "below_lower"
    else:
        pct = (current_price - lower_val) / (upper_val - lower_val) if (upper_val - lower_val) else 0.5
        position = f"within_bands_{pct:.0%}"

    return {
        "upper": round(upper_val, 2),
        "middle": round(middle_val, 2),
        "lower": round(lower_val, 2),
        "width": round(width, 4),
        "position": position,
    }


def _compute_atr(df: pd.DataFrame, period: int = 14) -> dict[str, Any]:
    """Compute Average True Range."""
    high_low = df["high"] - df["low"]
    high_close = (df["high"] - df["close"].shift()).abs()
    low_close = (df["low"] - df["close"].shift()).abs()
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    atr = tr.rolling(period).mean()
    current = float(atr.iloc[-1])
    price = float(df["close"].iloc[-1])
    pct = (current / price * 100) if price else 0

    return {
        "value": round(current, 2),
        "pct_of_price": round(pct, 2),
        "volatility": "high" if pct > 3 else "moderate" if pct > 1.5 else "low",
    }


def _compute_volume_analysis(df: pd.DataFrame) -> dict[str, Any]:
    """Analyze volume patterns."""
    avg_20 = float(df["volume"].rolling(20).mean().iloc[-1]) if len(df) >= 20 else float(df["volume"].mean())
    current = float(df["volume"].iloc[-1])
    ratio = current / avg_20 if avg_20 else 1

    return {
        "current": round(current, 0),
        "avg_20": round(avg_20, 0),
        "ratio": round(ratio, 2),
        "signal": "high_volume" if ratio > 1.5 else "low_volume" if ratio < 0.5 else "normal",
    }


def _compute_pivots(df: pd.DataFrame) -> dict[str, Any]:
    """Compute basic pivot point support/resistance levels."""
    h = float(df["high"].iloc[-1])
    l = float(df["low"].iloc[-1])
    c = float(df["close"].iloc[-1])
    pivot = (h + l + c) / 3

    return {
        "pivot": round(pivot, 2),
        "r1": round(2 * pivot - l, 2),
        "r2": round(pivot + (h - l), 2),
        "s1": round(2 * pivot - h, 2),
        "s2": round(pivot - (h - l), 2),
    }
