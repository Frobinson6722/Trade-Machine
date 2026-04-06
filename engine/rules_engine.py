"""Rules-based trading engine — no LLM needed for trade decisions.

Pure math: RSI, MACD, Bollinger Bands, Volume, EMA trends.
Trades execute instantly based on signals. No API costs for decisions.
Learns from past trades and adjusts thresholds automatically.
"""

from __future__ import annotations

import asyncio
import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Callable

from engine.config import DEFAULT_CONFIG
from engine.dataflows.binance_provider import BinanceProvider
from engine.dataflows.technical_indicators import compute_indicators
from engine.execution.paper_trader import PaperTrader
from engine.execution.position_manager import PositionManager
from engine.execution.stage_manager import StageManager
from engine.memory.memory_manager import MemoryManager

logger = logging.getLogger(__name__)


# Adaptive thresholds — these get tuned by the learning loop
DEFAULT_THRESHOLDS = {
    "rsi_oversold": 30,        # Tighter than before (was 35)
    "rsi_mild_oversold": 40,   # was 45
    "rsi_overbought": 70,
    "macd_weight": 2,
    "bb_weight": 2,
    "volume_confirm_ratio": 1.3,
    "min_score_to_buy": 3,     # Raised from 2 — need stronger signals
    "take_profit_pct": 0.5,    # Raised from 0.3% — let winners run more
    "stop_loss_pct": 0.4,      # Tightened from 0.5% — cut losers faster
    "trailing_stop_pct": 0.2,  # New: trailing stop activates after 0.15% gain
    "trailing_activate_pct": 0.15,  # When to activate trailing stop
    "position_size_pct": 8.0,
    "cooldown_seconds": 120,   # Don't re-enter same pair within 2 min
}


class RulesEngine:
    """Pure rules-based trading — no LLM calls for decisions."""

    def __init__(
        self,
        config: dict[str, Any] | None = None,
        on_trade: Callable | None = None,
        on_agent_log: Callable | None = None,
        on_status: Callable | None = None,
    ):
        self.config = {**DEFAULT_CONFIG, **(config or {})}
        self.on_trade = on_trade
        self.on_agent_log = on_agent_log
        self.on_status = on_status

        self.running = False
        self.paused = False
        self._task: asyncio.Task | None = None
        self._last_prices: dict[str, float] = {}

        # Adaptive thresholds — loaded from DB if available
        self.thresholds = dict(DEFAULT_THRESHOLDS)

        # Trade tracking
        self._peak_prices: dict[str, float] = {}  # For trailing stops
        self._last_trade_time: dict[str, float] = {}  # For cooldowns
        self._trade_results: list[dict] = []  # For learning

        self.memory = MemoryManager()
        self.stage_manager = StageManager(self.config)
        self.paper_trader = PaperTrader(self.config["stages"]["paper"]["initial_balance"])
        self.position_manager = PositionManager()
        self.data_provider = BinanceProvider()

        # Executor reference for compatibility
        self.executor = type('obj', (object,), {'mode': 'paper', 'paper_trader': self.paper_trader})()

    async def start(self) -> None:
        if self.running:
            return
        self.running = True
        self.paused = False

        # Load learned thresholds from DB
        await self._load_thresholds()

        self._task = asyncio.create_task(self._run_loop())
        logger.info(f"Rules engine started — thresholds: min_score={self.thresholds['min_score_to_buy']}, TP={self.thresholds['take_profit_pct']}%, SL={self.thresholds['stop_loss_pct']}%")
        if self.on_status:
            await self.on_status("running")

    async def stop(self) -> None:
        self.running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("Rules engine stopped")
        if self.on_status:
            await self.on_status("stopped")

    async def pause(self) -> None:
        self.paused = True
        if self.on_status:
            await self.on_status("paused")

    async def resume(self) -> None:
        self.paused = False
        if self.on_status:
            await self.on_status("running")

    async def _run_loop(self) -> None:
        interval = self.config["cycle_interval_seconds"]
        cycle_count = 0

        while self.running:
            try:
                if self.paused:
                    await asyncio.sleep(5)
                    continue

                for pair in self.config["trading_pairs"]:
                    if not self.running or self.paused:
                        break
                    await self._run_cycle(pair)

                cycle_count += 1

                # Run learning every 10 cycles
                if cycle_count % 10 == 0:
                    self._learn_from_trades()

                await asyncio.sleep(interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Loop error: {e}", exc_info=True)
                await asyncio.sleep(30)

    async def _run_cycle(self, pair: str) -> None:
        cycle_id = str(uuid.uuid4())[:8]

        try:
            # 1. Get price data
            candles = await self.data_provider.get_ohlcv(pair)
            if not candles or len(candles) < 20:
                return

            ticker = await self.data_provider.get_ticker(pair)
            current_price = ticker.get("price", 0)
            if not current_price:
                return

            # 2. Check open positions first (trailing stop + take profit + stop loss)
            await self._check_position(pair, current_price, cycle_id)

            # 3. Cooldown check
            now = datetime.now(timezone.utc).timestamp()
            last_trade = self._last_trade_time.get(pair, 0)
            if now - last_trade < self.thresholds["cooldown_seconds"]:
                return

            # 4. Compute indicators on 1-minute candles
            indicators = compute_indicators(candles)
            if "error" in indicators:
                return

            # 5. Multi-timeframe: also check 15-minute candles
            candles_15m = await self.data_provider.get_ohlcv(pair, interval="15m", limit=50)
            indicators_15m = compute_indicators(candles_15m) if candles_15m and len(candles_15m) >= 20 else None

            # 6. BTC correlation: check if BTC is dumping (skip for BTC itself)
            btc_bearish = False
            if pair != "BTC-USD":
                btc_bearish = await self._is_btc_bearish()

            # 7. Generate signal from rules
            signal = self._evaluate_rules(pair, current_price, indicators, indicators_15m, btc_bearish, candles)

            if self.on_agent_log:
                await self.on_agent_log("system",
                    f"Cycle {cycle_id}: {pair} @ ${current_price:.4f} | "
                    f"RSI: {signal['rsi']:.0f} | MACD: {signal['macd_signal']} | "
                    f"Score: {signal['score']} | Signal: {signal['action']}")

            # 6. Execute if signal says BUY and we don't have a position
            if signal["action"] == "BUY" and pair not in self.paper_trader.positions:
                size_pct = self.thresholds["position_size_pct"]
                size_usd = self.paper_trader.cash_balance * (size_pct / 100)

                if size_usd > 1:
                    # ATR-based dynamic stops: tighter in calm markets, wider in volatile
                    atr_data = indicators.get("atr", {})
                    atr_pct = atr_data.get("pct_of_price", 1.5) if isinstance(atr_data, dict) else 1.5
                    sl_multiplier = max(0.3, min(1.0, atr_pct * 0.3))  # 0.3% to 1.0% based on volatility
                    tp_multiplier = sl_multiplier * 1.5  # Always 1.5:1 reward:risk ratio
                    stop_loss = current_price * (1 - sl_multiplier / 100)
                    take_profit = current_price * (1 + tp_multiplier / 100)

                    result = await self.paper_trader.place_order(
                        pair=pair, side="BUY", size_usd=size_usd,
                        current_price=current_price,
                        stop_loss=stop_loss, take_profit=take_profit,
                    )

                    if result.get("success"):
                        self._peak_prices[pair] = current_price
                        self._last_trade_time[pair] = now

                        self.position_manager.update_position(pair, {
                            "cycle_id": cycle_id,
                            "entry_price": current_price,
                            "quantity": size_usd / current_price,
                            "side": "long",
                            "stop_loss": stop_loss,
                            "take_profit": take_profit,
                            "signal_score": signal["score"],
                            "signal_reason": signal["reason"],
                        })

                        self.memory.record_trade_entry(
                            pair=pair, action="BUY", entry_price=current_price,
                            size_usd=size_usd, stop_loss=stop_loss,
                            take_profit=take_profit,
                            agent_reasoning={"signal": signal["reason"], "rsi": signal["rsi"], "score": signal["score"]},
                            stage=self.stage_manager.get_current_stage(),
                            cycle_id=cycle_id,
                        )

                        if self.on_agent_log:
                            await self.on_agent_log("system",
                                f"TRADE: BUY {pair} @ ${current_price:.4f} | "
                                f"Size: ${size_usd:.2f} | Stop: ${stop_loss:.4f} | Target: ${take_profit:.4f}")

                        if self.on_trade:
                            await self.on_trade({
                                "cycle_id": cycle_id, "pair": pair, "action": "BUY",
                                "price": current_price, "size_usd": size_usd,
                                "stop_loss": stop_loss, "take_profit": take_profit,
                                "stage": self.stage_manager.get_current_stage(),
                                "mode": "paper", "reason": signal["reason"],
                            })

        except Exception as e:
            logger.error(f"Cycle {cycle_id} failed: {e}", exc_info=True)

    async def _is_btc_bearish(self) -> bool:
        """Check if BTC is in a bearish state. If so, altcoins will likely drop too."""
        try:
            btc_candles = await self.data_provider.get_ohlcv("BTC-USD", interval="5m", limit=30)
            if not btc_candles or len(btc_candles) < 14:
                return False
            btc_indicators = compute_indicators(btc_candles)
            btc_rsi = btc_indicators.get("rsi", {})
            btc_rsi_val = btc_rsi.get("value", 50) if isinstance(btc_rsi, dict) else 50
            btc_macd = btc_indicators.get("macd", {})
            btc_crossover = btc_macd.get("crossover", "neutral") if isinstance(btc_macd, dict) else "neutral"

            # BTC is bearish if RSI dropping AND MACD bearish
            if btc_rsi_val < 40 and btc_crossover in ("bearish", "bearish_crossover"):
                return True
            # BTC is dumping hard
            if btc_rsi_val < 30:
                return True
            return False
        except Exception:
            return False  # If we can't check, don't block trades

    def _compute_advanced_signals(self, candles: list[dict]) -> dict[str, Any]:
        """Compute additional signals from raw candle data. Pure math."""
        closes = [c["close"] for c in candles]
        highs = [c["high"] for c in candles]
        lows = [c["low"] for c in candles]
        opens = [c["open"] for c in candles]
        volumes = [c["volume"] for c in candles]

        result: dict[str, Any] = {}

        # ── MOMENTUM: Rate of Change (ROC) ──
        if len(closes) >= 10:
            roc_10 = ((closes[-1] - closes[-10]) / closes[-10]) * 100
            result["roc_10"] = round(roc_10, 3)
        else:
            result["roc_10"] = 0

        # ── VWAP ──
        if len(closes) >= 5:
            typical_prices = [(h + l + c) / 3 for h, l, c in zip(highs, lows, closes)]
            cum_tp_vol = sum(tp * v for tp, v in zip(typical_prices, volumes))
            cum_vol = sum(volumes)
            result["vwap"] = cum_tp_vol / cum_vol if cum_vol > 0 else closes[-1]
        else:
            result["vwap"] = closes[-1] if closes else 0

        # ── EMA RIBBON (8, 13, 21, 55) ──
        emas = {}
        for period in (8, 13, 21, 55):
            if len(closes) >= period:
                emas[period] = self._calc_ema(closes, period)
            else:
                emas[period] = closes[-1] if closes else 0
        result["ema_ribbon"] = emas
        # Ribbon bullish = 8 > 13 > 21 > 55
        result["ribbon_bullish"] = emas[8] > emas[13] > emas[21] > emas[55]
        result["ribbon_bearish"] = emas[8] < emas[13] < emas[21] < emas[55]

        # ── STOCHASTIC RSI ──
        if len(closes) >= 14:
            rsi_values = self._calc_rsi_series(closes, 14)
            if len(rsi_values) >= 14:
                min_rsi = min(rsi_values[-14:])
                max_rsi = max(rsi_values[-14:])
                rsi_range = max_rsi - min_rsi
                stoch_rsi = ((rsi_values[-1] - min_rsi) / rsi_range * 100) if rsi_range > 0 else 50
                result["stoch_rsi"] = round(stoch_rsi, 1)
            else:
                result["stoch_rsi"] = 50
        else:
            result["stoch_rsi"] = 50

        # ── CANDLESTICK PATTERNS ──
        result["candle_pattern"] = self._detect_candle_patterns(opens, highs, lows, closes)

        # ── CONSECUTIVE CANDLE ANALYSIS ──
        result["consecutive_red"] = 0
        result["consecutive_green"] = 0
        for i in range(len(closes) - 1, max(len(closes) - 10, 0) - 1, -1):
            if closes[i] < opens[i]:
                result["consecutive_red"] += 1
            else:
                break
        for i in range(len(closes) - 1, max(len(closes) - 10, 0) - 1, -1):
            if closes[i] >= opens[i]:
                result["consecutive_green"] += 1
            else:
                break

        # ── ADX (Average Directional Index) for market regime ──
        result["adx"] = self._calc_adx(highs, lows, closes)

        return result

    def _calc_ema(self, data: list[float], period: int) -> float:
        """Calculate EMA of a series."""
        multiplier = 2 / (period + 1)
        ema = data[0]
        for price in data[1:]:
            ema = (price - ema) * multiplier + ema
        return ema

    def _calc_rsi_series(self, closes: list[float], period: int = 14) -> list[float]:
        """Calculate RSI values for the full series."""
        if len(closes) < period + 1:
            return [50.0]
        deltas = [closes[i] - closes[i - 1] for i in range(1, len(closes))]
        gains = [d if d > 0 else 0 for d in deltas]
        losses = [-d if d < 0 else 0 for d in deltas]

        avg_gain = sum(gains[:period]) / period
        avg_loss = sum(losses[:period]) / period

        rsi_values = []
        for i in range(period, len(deltas)):
            avg_gain = (avg_gain * (period - 1) + gains[i]) / period
            avg_loss = (avg_loss * (period - 1) + losses[i]) / period
            rs = avg_gain / avg_loss if avg_loss > 0 else 100
            rsi_values.append(100 - (100 / (1 + rs)))
        return rsi_values

    def _detect_candle_patterns(self, opens: list, highs: list, lows: list, closes: list) -> str:
        """Detect simple candlestick patterns from last few candles."""
        if len(closes) < 3:
            return "none"

        # Last candle
        o, h, l, c = opens[-1], highs[-1], lows[-1], closes[-1]
        body = abs(c - o)
        full_range = h - l if h > l else 0.0001
        upper_wick = h - max(o, c)
        lower_wick = min(o, c) - l

        # Hammer: small body at top, long lower wick (bullish reversal)
        if lower_wick > body * 2 and upper_wick < body * 0.5 and body < full_range * 0.35:
            return "hammer"

        # Bullish engulfing: previous red, current green body covers previous
        po, pc = opens[-2], closes[-2]
        if pc < po and c > o and c > po and o < pc:
            return "bullish_engulfing"

        # Bearish engulfing
        if pc > po and c < o and c < po and o > pc:
            return "bearish_engulfing"

        # Doji: very small body relative to range
        if body < full_range * 0.1:
            return "doji"

        return "none"

    def _calc_adx(self, highs: list, lows: list, closes: list, period: int = 14) -> float:
        """Calculate ADX to determine trend strength. >25 = trending, <20 = ranging."""
        if len(closes) < period + 2:
            return 20  # Default to borderline

        plus_dm = []
        minus_dm = []
        tr_list = []

        for i in range(1, len(closes)):
            up_move = highs[i] - highs[i - 1]
            down_move = lows[i - 1] - lows[i]
            plus_dm.append(up_move if up_move > down_move and up_move > 0 else 0)
            minus_dm.append(down_move if down_move > up_move and down_move > 0 else 0)
            tr = max(highs[i] - lows[i], abs(highs[i] - closes[i - 1]), abs(lows[i] - closes[i - 1]))
            tr_list.append(tr)

        if len(tr_list) < period:
            return 20

        # Smoothed averages
        atr = sum(tr_list[:period]) / period
        plus_di_smooth = sum(plus_dm[:period]) / period
        minus_di_smooth = sum(minus_dm[:period]) / period

        dx_values = []
        for i in range(period, len(tr_list)):
            atr = (atr * (period - 1) + tr_list[i]) / period
            plus_di_smooth = (plus_di_smooth * (period - 1) + plus_dm[i]) / period
            minus_di_smooth = (minus_di_smooth * (period - 1) + minus_dm[i]) / period

            plus_di = (plus_di_smooth / atr * 100) if atr > 0 else 0
            minus_di = (minus_di_smooth / atr * 100) if atr > 0 else 0
            di_sum = plus_di + minus_di
            dx = abs(plus_di - minus_di) / di_sum * 100 if di_sum > 0 else 0
            dx_values.append(dx)

        if not dx_values:
            return 20

        adx = sum(dx_values[-period:]) / min(len(dx_values), period)
        return round(adx, 1)

    def _evaluate_rules(self, pair: str, price: float, indicators: dict,
                        indicators_15m: dict | None, btc_bearish: bool,
                        candles: list[dict]) -> dict[str, Any]:
        """Advanced rules-based signal generation. Multi-timeframe + BTC correlation + 11 signals."""
        t = self.thresholds

        # ── EXTRACT 1-MINUTE INDICATORS ──
        rsi = indicators.get("rsi", {})
        rsi_value = rsi.get("value", 50) if isinstance(rsi, dict) else 50

        macd = indicators.get("macd", {})
        macd_crossover = macd.get("crossover", "neutral") if isinstance(macd, dict) else "neutral"
        macd_histogram = macd.get("histogram", 0) if isinstance(macd, dict) else 0

        bollinger = indicators.get("bollinger", {})
        bb_position = bollinger.get("position", "") if isinstance(bollinger, dict) else ""

        volume = indicators.get("volume", {})
        vol_ratio = volume.get("ratio", 1) if isinstance(volume, dict) else 1

        atr = indicators.get("atr", {})
        atr_pct = atr.get("pct_of_price", 1.5) if isinstance(atr, dict) else 1.5

        sma_20 = indicators.get("sma_20")
        sma_50 = indicators.get("sma_50")

        # ── COMPUTE ADVANCED SIGNALS ──
        advanced = self._compute_advanced_signals(candles)

        # ── SCORING SYSTEM ──
        action = "HOLD"
        reasons = []
        score = 0

        # === HARD BLOCKERS (instant reject) ===

        # BTC dumping = don't buy altcoins
        if btc_bearish:
            return {
                "action": "HOLD", "reason": "BTC bearish — altcoin risk too high",
                "score": -10, "rsi": rsi_value, "macd_signal": macd_crossover,
                "bb_position": bb_position, "vol_ratio": vol_ratio,
            }

        # 5+ consecutive red candles = don't catch falling knife
        if advanced["consecutive_red"] >= 5:
            return {
                "action": "HOLD", "reason": f"{advanced['consecutive_red']} consecutive red candles — falling knife",
                "score": -10, "rsi": rsi_value, "macd_signal": macd_crossover,
                "bb_position": bb_position, "vol_ratio": vol_ratio,
            }

        # === ORIGINAL SIGNALS (kept) ===

        # RSI oversold
        if rsi_value < t["rsi_oversold"]:
            score += 2
            reasons.append(f"RSI oversold ({rsi_value:.0f})")
        elif rsi_value < t["rsi_mild_oversold"]:
            score += 1
            reasons.append(f"RSI low ({rsi_value:.0f})")

        # MACD bullish crossover
        if macd_crossover == "bullish_crossover":
            score += 3
            reasons.append("MACD bullish crossover")
        elif macd_crossover == "bullish" and macd_histogram > 0:
            score += 1
            reasons.append("MACD bullish")

        # Bollinger Band
        if "below_lower" in bb_position:
            score += t["bb_weight"]
            reasons.append("Below lower BB")

        # High volume
        if vol_ratio > t["volume_confirm_ratio"]:
            score += 1
            reasons.append(f"High volume ({vol_ratio:.1f}x)")

        # SMA trend
        if sma_20 and price > sma_20:
            score += 1
            reasons.append("Above SMA20")

        # === NEW SIGNALS ===

        # Multi-timeframe: 15m trend must also be bullish
        if indicators_15m:
            macd_15m = indicators_15m.get("macd", {})
            crossover_15m = macd_15m.get("crossover", "neutral") if isinstance(macd_15m, dict) else "neutral"
            rsi_15m = indicators_15m.get("rsi", {})
            rsi_15m_val = rsi_15m.get("value", 50) if isinstance(rsi_15m, dict) else 50

            if crossover_15m in ("bullish", "bullish_crossover") and rsi_15m_val < 60:
                score += 2
                reasons.append("15m timeframe confirms bullish")
            elif crossover_15m in ("bearish", "bearish_crossover"):
                score -= 2
                reasons.append("15m timeframe bearish")

        # Momentum: positive rate of change
        roc = advanced.get("roc_10", 0)
        if roc > 0.1:
            score += 1
            reasons.append(f"Momentum up (ROC: {roc:.2f}%)")
        elif roc < -0.3:
            score -= 1
            reasons.append(f"Momentum down (ROC: {roc:.2f}%)")

        # VWAP: price above = bullish
        vwap = advanced.get("vwap", price)
        if price > vwap * 1.001:
            score += 1
            reasons.append("Above VWAP")
        elif price < vwap * 0.999:
            score -= 1
            reasons.append("Below VWAP")

        # EMA ribbon: all aligned = strong trend
        if advanced.get("ribbon_bullish"):
            score += 2
            reasons.append("EMA ribbon bullish (8>13>21>55)")
        elif advanced.get("ribbon_bearish"):
            score -= 2
            reasons.append("EMA ribbon bearish")

        # Stochastic RSI: more sensitive oversold/overbought
        stoch_rsi = advanced.get("stoch_rsi", 50)
        if stoch_rsi < 20:
            score += 1
            reasons.append(f"StochRSI oversold ({stoch_rsi:.0f})")
        elif stoch_rsi > 80:
            score -= 1
            reasons.append(f"StochRSI overbought ({stoch_rsi:.0f})")

        # Candlestick patterns
        pattern = advanced.get("candle_pattern", "none")
        if pattern == "hammer":
            score += 2
            reasons.append("Hammer candle (reversal)")
        elif pattern == "bullish_engulfing":
            score += 2
            reasons.append("Bullish engulfing")
        elif pattern == "bearish_engulfing":
            score -= 2
            reasons.append("Bearish engulfing")

        # Market regime: ADX > 25 = trending (good for our strategy)
        adx = advanced.get("adx", 20)
        if adx > 25:
            score += 1
            reasons.append(f"Trending market (ADX: {adx:.0f})")
        elif adx < 15:
            score -= 1
            reasons.append(f"Choppy market (ADX: {adx:.0f})")

        # === NEGATIVE SIGNALS ===

        if rsi_value > t["rsi_overbought"]:
            score -= 3
            reasons.append(f"RSI overbought ({rsi_value:.0f})")

        if macd_crossover == "bearish_crossover":
            score -= 3
            reasons.append("MACD bearish crossover")
        elif macd_crossover == "bearish":
            score -= 1

        if sma_20 and sma_50 and price < sma_20 and price < sma_50:
            score -= 2
            reasons.append("Below SMA20 & SMA50 (downtrend)")

        # === DECISION ===
        reason = " + ".join(reasons) if reasons else "No clear signal"
        if score >= t["min_score_to_buy"]:
            action = "BUY"

        return {
            "action": action,
            "reason": reason,
            "score": score,
            "rsi": rsi_value,
            "macd_signal": macd_crossover,
            "bb_position": bb_position,
            "vol_ratio": vol_ratio,
            "adx": adx,
            "stoch_rsi": stoch_rsi,
            "roc": roc,
            "candle_pattern": pattern,
        }

    async def _check_position(self, pair: str, current_price: float, cycle_id: str) -> None:
        """Check if open position should be closed. Includes trailing stop."""
        pos = self.position_manager.get_position(pair)
        if not pos:
            return

        entry = pos.get("entry_price", 0)
        if not entry:
            return

        pnl_pct = ((current_price / entry) - 1) * 100

        # Update peak price for trailing stop
        peak = self._peak_prices.get(pair, entry)
        if current_price > peak:
            self._peak_prices[pair] = current_price
            peak = current_price

        should_close = False
        trigger = "manual"

        # 1. Take profit
        tp = pos.get("take_profit")
        if tp and current_price >= tp:
            should_close = True
            trigger = "take_profit"
        elif pnl_pct >= self.thresholds["take_profit_pct"]:
            should_close = True
            trigger = "take_profit"

        # 2. Trailing stop: if we're up past the activation threshold,
        #    close if price drops trailing_stop_pct from peak
        if not should_close and pnl_pct > self.thresholds["trailing_activate_pct"]:
            drop_from_peak = ((peak - current_price) / peak) * 100
            if drop_from_peak >= self.thresholds["trailing_stop_pct"]:
                should_close = True
                trigger = "trailing_stop"

        # 3. Stop loss
        sl = pos.get("stop_loss")
        if not should_close:
            if sl and current_price <= sl:
                should_close = True
                trigger = "stop_loss"
            elif pnl_pct <= -self.thresholds["stop_loss_pct"]:
                should_close = True
                trigger = "stop_loss"

        if should_close:
            old_cycle = pos.get("cycle_id", cycle_id)
            result = await self.paper_trader.place_order(
                pair=pair, side="SELL", size_usd=0, current_price=current_price
            )
            if result.get("success"):
                trade = result.get("trade", {})
                pnl = trade.get("pnl", 0)
                pnl_pct_actual = trade.get("pnl_pct", pnl_pct)

                self.position_manager.close_position(pair)
                self._peak_prices.pop(pair, None)
                self.memory.record_trade_exit(
                    cycle_id=old_cycle, exit_price=current_price,
                    pnl=pnl, pnl_pct=pnl_pct_actual, trigger=trigger,
                )
                self.stage_manager.record_trade(pnl)
                self._last_trade_time[pair] = datetime.now(timezone.utc).timestamp()

                # Record for learning
                self._trade_results.append({
                    "pair": pair,
                    "pnl": pnl,
                    "pnl_pct": pnl_pct_actual,
                    "trigger": trigger,
                    "signal_score": pos.get("signal_score", 0),
                    "signal_reason": pos.get("signal_reason", ""),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                })

                # Persist lesson to DB
                asyncio.create_task(self._persist_lesson(pair, pnl, pnl_pct_actual, trigger, pos))

                result_label = "WIN" if pnl > 0 else "LOSS"
                if self.on_agent_log:
                    await self.on_agent_log("system",
                        f"CLOSED {pair} ({trigger}): {result_label} ${pnl:+.2f} ({pnl_pct_actual:+.1f}%)")

                if self.on_trade:
                    await self.on_trade({
                        "cycle_id": old_cycle, "pair": pair, "action": "SELL",
                        "price": current_price, "pnl": pnl, "pnl_pct": pnl_pct_actual,
                        "trigger": trigger, "stage": self.stage_manager.get_current_stage(),
                    })
            return

        # Log unrealized P&L
        if self.on_agent_log:
            qty = pos.get("quantity", 0)
            unrealized = (current_price - entry) * qty
            await self.on_agent_log("system",
                f"Open {pair}: ${entry:.4f} -> ${current_price:.4f} | P&L: ${unrealized:+.2f} ({pnl_pct:+.1f}%)")

    def _learn_from_trades(self) -> None:
        """Analyze recent trade results and adjust thresholds."""
        if len(self._trade_results) < 5:
            return  # Need enough data

        recent = self._trade_results[-20:]  # Last 20 trades
        wins = [t for t in recent if t["pnl"] > 0]
        losses = [t for t in recent if t["pnl"] <= 0]
        win_rate = len(wins) / len(recent) if recent else 0

        old_thresholds = dict(self.thresholds)

        # If win rate is low, tighten entry requirements
        if win_rate < 0.5 and len(recent) >= 5:
            self.thresholds["min_score_to_buy"] = min(5, self.thresholds["min_score_to_buy"] + 1)
            self.thresholds["stop_loss_pct"] = max(0.2, self.thresholds["stop_loss_pct"] - 0.05)
            logger.info(f"LEARNING: Win rate {win_rate:.0%} low — tightened entry to score >= {self.thresholds['min_score_to_buy']}, SL to {self.thresholds['stop_loss_pct']}%")

        # If win rate is high, can be slightly more aggressive
        elif win_rate > 0.65 and len(recent) >= 10:
            self.thresholds["min_score_to_buy"] = max(2, self.thresholds["min_score_to_buy"] - 1)
            self.thresholds["take_profit_pct"] = min(1.0, self.thresholds["take_profit_pct"] + 0.05)
            logger.info(f"LEARNING: Win rate {win_rate:.0%} good — loosened entry to score >= {self.thresholds['min_score_to_buy']}, TP to {self.thresholds['take_profit_pct']}%")

        # If too many stop losses, tighten stops
        stop_losses = [t for t in recent if t["trigger"] == "stop_loss"]
        if len(stop_losses) > len(recent) * 0.4:
            self.thresholds["stop_loss_pct"] = max(0.2, self.thresholds["stop_loss_pct"] - 0.05)
            logger.info(f"LEARNING: Too many stop losses — tightened SL to {self.thresholds['stop_loss_pct']}%")

        # Log and persist changes
        changes = {k: (old_thresholds[k], v) for k, v in self.thresholds.items() if old_thresholds[k] != v}
        if changes:
            logger.info(f"LEARNING: Threshold changes: {changes}")
            asyncio.create_task(self._save_thresholds(old_thresholds, changes, win_rate))

    async def _persist_lesson(self, pair: str, pnl: float, pnl_pct: float, trigger: str, pos: dict) -> None:
        """Save trade outcome as a lesson in the database."""
        try:
            from backend.database import async_session
            from backend.models import ReflectionEntry

            outcome = "win" if pnl > 0 else "loss"
            score = pos.get("signal_score", 0)
            reason = pos.get("signal_reason", "unknown")

            reflection = (
                f"{'Won' if pnl > 0 else 'Lost'} ${abs(pnl):.2f} ({pnl_pct:+.1f}%) on {pair}. "
                f"Entry signal score: {score} ({reason}). "
                f"Exit trigger: {trigger}. "
                f"Current thresholds: min_score={self.thresholds['min_score_to_buy']}, "
                f"TP={self.thresholds['take_profit_pct']}%, SL={self.thresholds['stop_loss_pct']}%"
            )

            async with async_session() as session:
                entry = ReflectionEntry(
                    pair=pair,
                    reflection_text=reflection,
                    tags=[trigger, outcome, f"score_{score}"],
                    trade_outcome=outcome,
                )
                session.add(entry)
                await session.commit()
                logger.info(f"Lesson saved: {outcome} on {pair}")
        except Exception as e:
            logger.error(f"Failed to persist lesson: {e}")

    async def _load_thresholds(self) -> None:
        """Load learned thresholds from DB. If none exist, use defaults."""
        try:
            from backend.database import async_session
            from backend.models import StrategyUpdate
            from sqlalchemy import select

            async with async_session() as session:
                result = await session.execute(
                    select(StrategyUpdate).order_by(StrategyUpdate.created_at.desc()).limit(1)
                )
                latest = result.scalar_one_or_none()

                if latest and latest.parameter_changes:
                    saved = latest.parameter_changes
                    # Merge saved values into defaults (in case new keys were added)
                    for key in self.thresholds:
                        if key in saved:
                            self.thresholds[key] = saved[key]
                    logger.info(f"Loaded learned thresholds from DB: min_score={self.thresholds['min_score_to_buy']}, TP={self.thresholds['take_profit_pct']}%, SL={self.thresholds['stop_loss_pct']}%")
                else:
                    logger.info("No saved thresholds found — using defaults")
        except Exception as e:
            logger.error(f"Failed to load thresholds: {e} — using defaults")

    async def _save_thresholds(self, old_values: dict, changes: dict, win_rate: float) -> None:
        """Persist current thresholds to DB so they survive restarts."""
        try:
            from backend.database import async_session
            from backend.models import StrategyUpdate

            description = (
                f"Learning update: win_rate={win_rate:.0%}, "
                f"adjusted {', '.join(f'{k}: {v[0]}->{v[1]}' for k, v in changes.items())}"
            )

            async with async_session() as session:
                update = StrategyUpdate(
                    description=description,
                    parameter_changes=dict(self.thresholds),  # Save ALL current thresholds
                    old_values={k: v[0] for k, v in changes.items()},
                )
                session.add(update)
                await session.commit()
                logger.info(f"Thresholds saved to DB")
        except Exception as e:
            logger.error(f"Failed to save thresholds: {e}")

    def get_status(self) -> dict[str, Any]:
        return {
            "running": self.running,
            "paused": self.paused,
            "mode": "paper",
            "stage": self.stage_manager.get_status(),
            "positions": self.position_manager.get_all_positions(),
            "stats": self.memory.get_trading_stats(),
        }
