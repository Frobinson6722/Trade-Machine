"""Trading pattern library — every classic chart pattern with the psychology behind it.

Each pattern includes:
- What it looks like (detection logic)
- The crowd psychology that creates it
- What typically happens next
- Confidence level and expected move
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


# ── The Pattern Library ──────────────────────────────────────────────────────
# Every pattern a trader should know, with the mass psychology explanation.

PATTERN_DEFINITIONS: list[dict[str, Any]] = [
    # ── REVERSAL PATTERNS (trend is about to flip) ──

    {
        "name": "Double Bottom (W Pattern)",
        "type": "bullish_reversal",
        "psychology": "Price hits a low, bounces, drops back to the same low but sellers are exhausted. "
                      "Buyers who missed the first bounce step in aggressively. The second bounce confirms "
                      "a floor — fear turns to greed.",
        "signal": "BUY",
        "confidence": 0.75,
        "expected_move_pct": 8,
    },
    {
        "name": "Double Top (M Pattern)",
        "type": "bearish_reversal",
        "psychology": "Price hits a high twice but can't break through. Buyers who bought the top panic "
                      "and sell. Each failed attempt to break resistance creates more sellers. "
                      "Greed turns to fear.",
        "signal": "SELL",
        "confidence": 0.75,
        "expected_move_pct": -8,
    },
    {
        "name": "Head and Shoulders",
        "type": "bearish_reversal",
        "psychology": "Three peaks: left shoulder, higher head, right shoulder that fails to match the head. "
                      "The crowd pushed prices up but momentum is dying. Smart money exits on the right "
                      "shoulder while retail holds. Neckline break triggers panic selling.",
        "signal": "SELL",
        "confidence": 0.80,
        "expected_move_pct": -12,
    },
    {
        "name": "Inverse Head and Shoulders",
        "type": "bullish_reversal",
        "psychology": "Three troughs with the middle one deepest. Sellers exhausted themselves pushing to "
                      "the head low. Each higher low shows buyers gaining control. Neckline break triggers "
                      "FOMO buying — everyone realizes the bottom is in.",
        "signal": "BUY",
        "confidence": 0.80,
        "expected_move_pct": 12,
    },
    {
        "name": "Triple Bottom",
        "type": "bullish_reversal",
        "psychology": "Price tests the same support three times and holds. Each test with less volume means "
                      "sellers are running out of coins to dump. The support level becomes a psychological "
                      "fortress — buyers defend it religiously.",
        "signal": "BUY",
        "confidence": 0.82,
        "expected_move_pct": 10,
    },
    {
        "name": "Triple Top",
        "type": "bearish_reversal",
        "psychology": "Three failed attempts at resistance. Each failure creates bag holders who bought "
                      "the top expecting a breakout. By the third failure, even optimists give up. "
                      "The wall of sell orders at resistance is too thick.",
        "signal": "SELL",
        "confidence": 0.82,
        "expected_move_pct": -10,
    },
    {
        "name": "Rounding Bottom (Cup)",
        "type": "bullish_reversal",
        "psychology": "Slow, gradual shift from selling pressure to buying pressure. Panic sellers exhaust "
                      "themselves over weeks. Accumulation by patient smart money creates a smooth curve. "
                      "By the time retail notices, the reversal is confirmed.",
        "signal": "BUY",
        "confidence": 0.70,
        "expected_move_pct": 15,
    },

    # ── CONTINUATION PATTERNS (trend will resume) ──

    {
        "name": "Bull Flag",
        "type": "bullish_continuation",
        "psychology": "After a sharp rally, price consolidates in a slight downward channel. This is "
                      "profit-taking by short-term traders — NOT a reversal. The underlying demand is "
                      "still strong. When the flag breaks up, sidelined buyers rush in.",
        "signal": "BUY",
        "confidence": 0.72,
        "expected_move_pct": 8,
    },
    {
        "name": "Bear Flag",
        "type": "bearish_continuation",
        "psychology": "After a sharp drop, price bounces slightly in an upward channel. This is a dead "
                      "cat bounce — short sellers covering, not real buying. The relief rally traps "
                      "optimistic buyers who get crushed when selling resumes.",
        "signal": "SELL",
        "confidence": 0.72,
        "expected_move_pct": -8,
    },
    {
        "name": "Ascending Triangle",
        "type": "bullish_continuation",
        "psychology": "Price makes higher lows while hitting the same resistance. Buyers are more "
                      "aggressive each time — willing to pay more. Sellers at resistance slowly get "
                      "overwhelmed. The breakout is explosive because all the stops above resistance "
                      "trigger simultaneously.",
        "signal": "BUY",
        "confidence": 0.75,
        "expected_move_pct": 10,
    },
    {
        "name": "Descending Triangle",
        "type": "bearish_continuation",
        "psychology": "Lower highs pressing against flat support. Each bounce is weaker — buyers losing "
                      "conviction. When support finally breaks, all the stops below trigger a cascade "
                      "of selling. Holders who defended support capitulate.",
        "signal": "SELL",
        "confidence": 0.75,
        "expected_move_pct": -10,
    },
    {
        "name": "Symmetrical Triangle (Pennant)",
        "type": "neutral_continuation",
        "psychology": "Converging trendlines = indecision. Both buyers and sellers are waiting for the "
                      "other side to blink. Volume dries up. The breakout direction matters — it usually "
                      "continues the prior trend because the crowd's bias hasn't changed.",
        "signal": "HOLD",
        "confidence": 0.65,
        "expected_move_pct": 7,
    },
    {
        "name": "Cup and Handle",
        "type": "bullish_continuation",
        "psychology": "Rounded bottom (cup) followed by a small pullback (handle). The cup represents "
                      "gradual accumulation. The handle is final shakeout of weak hands — a last dip "
                      "to scare remaining sellers before the real move up.",
        "signal": "BUY",
        "confidence": 0.78,
        "expected_move_pct": 15,
    },

    # ── VOLATILITY PATTERNS (big move coming, direction unclear) ──

    {
        "name": "Bollinger Band Squeeze",
        "type": "volatility_expansion",
        "psychology": "Volatility compresses to extreme lows — the market is coiling like a spring. "
                      "Traders are bored, volume is low, nobody's paying attention. This calm ALWAYS "
                      "precedes a storm. The breakout direction depends on the prevailing bias.",
        "signal": "HOLD",
        "confidence": 0.85,
        "expected_move_pct": 12,
    },
    {
        "name": "Volume Climax",
        "type": "reversal_signal",
        "psychology": "Extreme volume on a big price move = capitulation. In a selloff, it means the "
                      "last panicked holders finally dumped. In a rally, it means the last FOMO buyers "
                      "piled in. Either way, the crowd has fully committed — there's nobody left to "
                      "push the price further.",
        "signal": "CONTRARIAN",
        "confidence": 0.70,
        "expected_move_pct": 8,
    },

    # ── PSYCHOLOGICAL LEVELS ──

    {
        "name": "Round Number Support/Resistance",
        "type": "psychological",
        "psychology": "Humans anchor to round numbers ($1.00, $0.50, $2.00). Limit orders cluster at "
                      "these levels creating artificial walls. DOGE at $0.20 or XRP at $2.00 will see "
                      "massive order books. These levels act as magnets and barriers.",
        "signal": "WATCH",
        "confidence": 0.60,
        "expected_move_pct": 5,
    },
    {
        "name": "FOMO Breakout (Fear of Missing Out)",
        "type": "momentum",
        "psychology": "Price breaks above a well-watched resistance. Social media explodes. People who "
                      "were waiting buy aggressively. This creates a self-reinforcing loop — price goes "
                      "up, more people FOMO in, price goes higher. Works until it doesn't.",
        "signal": "BUY",
        "confidence": 0.55,
        "expected_move_pct": 10,
    },
    {
        "name": "Panic Capitulation",
        "type": "reversal_signal",
        "psychology": "Price crashes on massive volume with extreme fear readings. Reddit/X is full of "
                      "'I sold everything' posts. This is maximum pain — the exact moment the crowd "
                      "gives up is often the bottom. Smart money buys when there's blood in the streets.",
        "signal": "BUY",
        "confidence": 0.65,
        "expected_move_pct": 15,
    },
    {
        "name": "Bullish Divergence (RSI)",
        "type": "bullish_reversal",
        "psychology": "Price makes a lower low but RSI makes a higher low. Sellers are pushing price "
                      "down but with less momentum each time. The crowd thinks it's still falling "
                      "but under the surface, selling pressure is drying up.",
        "signal": "BUY",
        "confidence": 0.72,
        "expected_move_pct": 8,
    },
    {
        "name": "Bearish Divergence (RSI)",
        "type": "bearish_reversal",
        "psychology": "Price makes a higher high but RSI makes a lower high. The rally looks strong "
                      "on the surface but buying momentum is fading. Smart money is distributing "
                      "(selling into strength) while retail chases the high.",
        "signal": "SELL",
        "confidence": 0.72,
        "expected_move_pct": -8,
    },
]


def detect_patterns(candles: list[dict[str, Any]], indicators: dict[str, Any]) -> list[dict[str, Any]]:
    """Scan price data for known patterns and return detected ones with psychology.

    Args:
        candles: OHLCV candle data (most recent last)
        indicators: Pre-computed technical indicators (RSI, MACD, Bollinger, etc.)

    Returns:
        List of detected patterns with name, signal, confidence, and psychology
    """
    if len(candles) < 20:
        return []

    detected = []
    prices = [c["close"] for c in candles]
    volumes = [c.get("volume", 0) for c in candles]

    # Extract indicator values
    rsi = indicators.get("rsi", {})
    rsi_value = rsi.get("value", 50) if isinstance(rsi, dict) else 50
    bollinger = indicators.get("bollinger", {})
    bb_width = bollinger.get("width", 0) if isinstance(bollinger, dict) else 0
    macd = indicators.get("macd", {})
    volume_info = indicators.get("volume", {})
    vol_ratio = volume_info.get("ratio", 1) if isinstance(volume_info, dict) else 1

    # ── Double Bottom detection ──
    if len(prices) >= 20:
        recent = prices[-20:]
        mid = len(recent) // 2
        left_min = min(recent[:mid])
        right_min = min(recent[mid:])
        left_min_idx = recent[:mid].index(left_min)
        right_min_idx = mid + recent[mid:].index(right_min)
        current = recent[-1]

        # Two similar lows with a bounce in between
        if abs(left_min - right_min) / left_min < 0.03 and current > left_min * 1.02:
            peak_between = max(recent[left_min_idx:right_min_idx + 1])
            if peak_between > left_min * 1.03:
                pattern = dict(PATTERN_DEFINITIONS[0])  # Double Bottom
                pattern["detected_at"] = candles[-1]["timestamp"]
                pattern["price_at_detection"] = current
                detected.append(pattern)

    # ── Double Top detection ──
    if len(prices) >= 20:
        recent = prices[-20:]
        mid = len(recent) // 2
        left_max = max(recent[:mid])
        right_max = max(recent[mid:])
        current = recent[-1]

        if abs(left_max - right_max) / left_max < 0.03 and current < left_max * 0.98:
            pattern = dict(PATTERN_DEFINITIONS[1])  # Double Top
            pattern["detected_at"] = candles[-1]["timestamp"]
            pattern["price_at_detection"] = current
            detected.append(pattern)

    # ── Bollinger Squeeze ──
    if bb_width > 0 and bb_width < 0.03:
        pattern = dict(PATTERN_DEFINITIONS[14])  # Bollinger Squeeze
        pattern["detected_at"] = candles[-1]["timestamp"]
        pattern["price_at_detection"] = prices[-1]
        pattern["detail"] = f"Band width: {bb_width:.4f} (very tight)"
        detected.append(pattern)

    # ── RSI Divergence (Bullish) ──
    if rsi_value < 40 and len(prices) >= 10:
        price_making_lower_low = prices[-1] < prices[-5]
        # Simplified: if RSI is low but price recently dropped, potential bullish divergence
        if price_making_lower_low and rsi_value > 25:
            pattern = dict(PATTERN_DEFINITIONS[19])  # Bullish Divergence
            pattern["detected_at"] = candles[-1]["timestamp"]
            pattern["price_at_detection"] = prices[-1]
            pattern["detail"] = f"RSI: {rsi_value} while price at local low"
            detected.append(pattern)

    # ── RSI Divergence (Bearish) ──
    if rsi_value > 60 and len(prices) >= 10:
        price_making_higher_high = prices[-1] > prices[-5]
        if price_making_higher_high and rsi_value < 75:
            pattern = dict(PATTERN_DEFINITIONS[20])  # Bearish Divergence
            pattern["detected_at"] = candles[-1]["timestamp"]
            pattern["price_at_detection"] = prices[-1]
            pattern["detail"] = f"RSI: {rsi_value} while price at local high"
            detected.append(pattern)

    # ── Volume Climax ──
    if vol_ratio > 2.5:
        pattern = dict(PATTERN_DEFINITIONS[15])  # Volume Climax
        pattern["detected_at"] = candles[-1]["timestamp"]
        pattern["price_at_detection"] = prices[-1]
        pattern["detail"] = f"Volume is {vol_ratio:.1f}x the 20-day average"
        detected.append(pattern)

    # ── Bull Flag ──
    if len(prices) >= 15:
        # Sharp rally in first half, small pullback in second half
        first_half = prices[:len(prices)//2]
        second_half = prices[len(prices)//2:]
        rally = (max(first_half) - first_half[0]) / first_half[0] if first_half[0] else 0
        pullback = (max(second_half) - second_half[-1]) / max(second_half) if max(second_half) else 0

        if rally > 0.05 and 0.01 < pullback < 0.04:
            pattern = dict(PATTERN_DEFINITIONS[7])  # Bull Flag
            pattern["detected_at"] = candles[-1]["timestamp"]
            pattern["price_at_detection"] = prices[-1]
            detected.append(pattern)

    # ── Panic Capitulation ──
    if rsi_value < 25 and vol_ratio > 2.0:
        pattern = dict(PATTERN_DEFINITIONS[18])  # Panic Capitulation
        pattern["detected_at"] = candles[-1]["timestamp"]
        pattern["price_at_detection"] = prices[-1]
        pattern["detail"] = f"RSI: {rsi_value}, Volume: {vol_ratio:.1f}x average — possible capitulation"
        detected.append(pattern)

    # ── FOMO Breakout ──
    if len(prices) >= 10:
        recent_high = max(prices[-10:-1]) if len(prices) > 10 else max(prices[:-1])
        if prices[-1] > recent_high * 1.03 and vol_ratio > 1.5:
            pattern = dict(PATTERN_DEFINITIONS[17])  # FOMO Breakout
            pattern["detected_at"] = candles[-1]["timestamp"]
            pattern["price_at_detection"] = prices[-1]
            pattern["detail"] = f"Broke above {recent_high:.6f} on {vol_ratio:.1f}x volume"
            detected.append(pattern)

    # ── Round Number ──
    current_price = prices[-1]
    round_levels = _get_round_levels(current_price)
    for level in round_levels:
        if abs(current_price - level) / level < 0.02:  # Within 2% of round number
            pattern = dict(PATTERN_DEFINITIONS[16])  # Round Number
            pattern["detected_at"] = candles[-1]["timestamp"]
            pattern["price_at_detection"] = current_price
            pattern["detail"] = f"Price near psychological level ${level}"
            detected.append(pattern)
            break

    logger.info(f"Detected {len(detected)} patterns")
    return detected


def _get_round_levels(price: float) -> list[float]:
    """Get psychologically significant round numbers near the current price."""
    if price < 0.01:
        return [0.005, 0.01, 0.02, 0.05]
    elif price < 0.10:
        return [0.05, 0.10, 0.15, 0.20, 0.25]
    elif price < 1:
        return [0.25, 0.50, 0.75, 1.00]
    elif price < 10:
        return [1.0, 2.0, 3.0, 5.0, 10.0]
    elif price < 100:
        return [10, 20, 25, 50, 75, 100]
    elif price < 1000:
        return [100, 200, 250, 500, 750, 1000]
    else:
        base = round(price, -3)
        return [base - 1000, base - 500, base, base + 500, base + 1000]


def get_full_pattern_library() -> list[dict[str, Any]]:
    """Return the complete pattern library for reference/display."""
    return PATTERN_DEFINITIONS
