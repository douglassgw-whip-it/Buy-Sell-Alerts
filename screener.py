def generate_signal(df):
    """Evaluates trading rules based on moving averages, trailing stops, RSI, and daily momentum."""
    # Check for sufficient data
    if df is None or len(df) < 2:
        return "⚪ HOLD", "#4A4A4A"
        
    latest = df.iloc[-1]
    prior = df.iloc[-2]
    
    # Use .get() to prevent KeyError if columns are missing
    current_price = latest.get("Close")
    prior_price = prior.get("Close")
    ma50 = latest.get("MA50")
    ma200 = latest.get("MA200")
    rsi = latest.get("RSI")
    recent_peak = latest.get("Recent_Peak")

    # Safety Check: If core data is missing, don't crash, just hold
    if None in [current_price, prior_price]:
        return "⚪ HOLD (Missing Price Data)", "#4A4A4A"

    # Calculate today's performance safely
    daily_return = (current_price - prior_price) / prior_price if prior_price else 0
    
    # Prevent ZeroDivisionError for recent_peak
    if recent_peak and recent_peak > 0:
        drop_from_peak = (recent_peak - current_price) / recent_peak
    else:
        drop_from_peak = 0

    # 1. 🔥 BULLISH OVERRIDE: Catch high-momentum breakout/reversal days
    if daily_return >= 0.03:
        if ma50 and ma200 and current_price > ma50 and ma50 > ma200:
            return "🚀 BULLISH BREAKOUT (Strong Momentum)", "#2E7D32"
        else:
            return "🔄 BULLISH REVERSAL (Volume Surge)", "#0288D1"

    # 2. Trailing Stop-Loss Trigger
    elif drop_from_peak >= 0.10:
        return "🔴 STOP-LOSS BREACHED (-10%)", "#D32F2F"
        
    # 3. Standard Trend Following Buy Setup
    elif ma50 and ma200 and rsi and current_price > ma50 and ma50 > ma200 and rsi < 65:
        return "🟢 BUY (Strong Uptrend)", "#2E7D32"
        
    # 4. Moving Average / Overbought Breakdown
    elif (ma50 and current_price < ma50) or (rsi and rsi > 80):
        return "🚨 TREND WEAKENING (Exit Setup)", "#E65100"
        
    else:
        return "⚪ HOLD", "#4A4A4A"
