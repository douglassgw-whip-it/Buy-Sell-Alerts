import os
import smtplib
import numpy as np
import pandas as pd
import yfinance as yf
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ==========================================
# 1. BULLETPROOF MULTI-INDEX DATA MIRROR SCRAPER
# ==========================================
def fetch_broad_market_universe():
    print("Executing broad extraction of institutional indices...")
    tickers = []
    
    try:
        sp500_df = pd.read_csv("https://raw.githubusercontent.com/datasets/s-and-p-500-companies/master/data/constituents.csv")
        sp500_list = sp500_df['Symbol'].tolist()
        tickers.extend([str(t).replace('.', '-') for t in sp500_list])
        print(f"✅ Successfully extracted {len(sp500_list)} S&P 500 components from GitHub repository mirror.")
    except Exception as e:
        print(f"⚠️ S&P 500 primary mirror failed: {e}. Trying secondary backup...")
        try:
            sp500_df = pd.read_csv("https://raw.githubusercontent.com/Ate329/top-us-stock-tickers/main/tickers/sp500.csv")
            col = 'symbol' if 'symbol' in sp500_df.columns else 'Symbol'
            sp500_list = sp500_df[col].tolist()
            tickers.extend([str(t).replace('.', '-') for t in sp500_list])
            print(f"✅ Successfully extracted {len(sp500_list)} S&P 500 components from secondary mirror.")
        except Exception as e2:
            print(f"❌ All S&P 500 mirrors bypassed: {e2}")

    try:
        nasdaq_df = pd.read_csv("https://raw.githubusercontent.com/Ate329/top-us-stock-tickers/main/tickers/top_100.csv")
        col = 'symbol' if 'symbol' in nasdaq_df.columns else 'Symbol'
        nasdaq_list = nasdaq_df[col].tolist()
        tickers.extend([str(t).replace('.', '-') for t in nasdaq_list])
        print(f"✅ Successfully extracted {len(nasdaq_list)} NASDAQ-100 components from GitHub mirror.")
    except Exception as e:
        print(f"❌ NASDAQ-100 mirror bypassed: {e}")

    macro_anchors = ["QQQ", "IWM", "DIA", "RKLB", "PLTR", "BBAI", "VLN", "ACHR"]
    full_universe = list(set(macro_anchors + tickers))
    print(f"📊 Total dynamic components integrated into the pipeline: {len(full_universe)}")
    return full_universe

# ==========================================
# 2. REPORT FORMATTING PIPELINE
# ==========================================
def build_markdown_matrix(group_a, group_b):
    output = "## SYSTEMATIC BROAD INDEX SCORING MATRIX\n"
    output += "=======================================================================\n\n"
    
    output += "### 📈 GROUP A: ALPHA MOMENTUM BREAKOUTS\n"
    output += "*Filter: Daily RSI >= 45*\n\n"
    output += "| Ticker | Price     | Ann Alpha | 20D Vol | Daily RSI | IV Rank | Tactical Score |\n"
    output += "| :---   | :---      | :---      | :---    | :---      | :---    | :---           |\n"
    for t, m in group_a:
        output += f"| {t:<6} | {m['Price']:<9} | {m['Alpha']:+9.1%} | {m['Vol']:<7} | {m['RSI']:<9} | {m['HVRank']:<7} | {m['ScoreA']:<14} |\n"
        
    output += "\n" + "---" * 20 + "\n\n"
    
    output += "### 📉 GROUP B: STRUCTURAL PULLBACKS\n"
    output += "*Filter: Daily RSI < 45*\n\n"
    output += "| Ticker | Price     | Ann Alpha | Daily RSI | 20D Vol | IV Rank | Suggested Strike Floor | Put Selling Score |\n"
    output += "| :---   | :---      | :---      | :---      | :---    | :---    | :---                   | :---              |\n"
    for t, m in group_b:
        output += f"| {t:<6} | {m['Price']:<9} | {m['Alpha']:+9.1%} | {m['RSI']:<9} | {m['Vol']:<7} | {m['HVRank']:<7} | {m['StrikeFloor']:<22} | {m['ScoreB']:<17} |\n"

    output += "\n=======================================================================\n"
    output += "🤖 *Automated Data Pipeline Engine via GitHub Cloud Workspace Universe Engine*"
    return output

# ==========================================
# 3. SECURE REPO-SECRETS SMTP TUNNEL
# ==========================================
def send_matrix_email(matrix_text):
    # Fixed to pull exactly from the keys established in image_a68fdf.png
    smtp_user = os.environ.get("EMAIL_USER")
    smtp_pass = os.environ.get("EMAIL_PASSWORD")
    to_email = os.environ.get("TO_EMAIL")

    if not all([smtp_user, smtp_pass, to_email]):
        raise ValueError("❌ CRITICAL CONFIG: Missing core environment secrets (EMAIL_USER, EMAIL_PASSWORD, TO_EMAIL).")

    msg = MIMEMultipart()
    msg["Subject"] = "📊 SYSTEMATIC BROAD INDEX SCORING MATRIX"
    msg["From"] = smtp_user
    msg["To"] = to_email
    
    body = f"Total-market multi-index macro scan complete. Optimized setups:\n\n{matrix_text}"
    msg.attach(MIMEText(body, "plain"))

    print("Opening secure SSL pipeline tunnel...")
    server = smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=15)
    server.login(smtp_user, smtp_pass)
    server.sendmail(smtp_user, to_email, msg.as_string())
    server.quit()
    print("✨ SUCCESS: Report delivered securely.")

# ==========================================
# 4. EXECUTION DISPATCH MATRIX
# ==========================================
def main():
    print("🚀 BOOTING BROAD NETWORK INDEX EXTRACTION PROCESSING ENGINE")
    
    spy_df = yf.download("SPY", period="1y", interval="1d", progress=False)
    if isinstance(spy_df.columns, pd.MultiIndex):
        spy_df.columns = spy_df.columns.get_level_values(0)
    
    spy_close = spy_df['Close'].dropna()
    spy_returns = spy_close.pct_change().dropna()
    spy_cum = (1 + spy_returns).prod() - 1
    spy_vol_20d = spy_returns.tail(20).std() * np.sqrt(252)

    watchlist = fetch_broad_market_universe()
    if "SPY" not in watchlist:
        watchlist.append("SPY")
        
    group_a_pool = []
    group_b_pool = []

    print("Parsing down individual historical footprints...")
    for ticker in watchlist:
        if ticker == "SPY":
            continue
        try:
            # Individual calls handle data structuring bugs cleaner across large indices
            ticker_df = yf.download(ticker, period="1y", interval="1d", progress=False)
            if ticker_df.empty or len(ticker_df) < 50:
                continue
                
            if isinstance(ticker_df.columns, pd.MultiIndex):
                ticker_df.columns = ticker_df.columns.get_level_values(0)

            close_series = ticker_df['Close']
            volume_series = ticker_df['Volume']
            high_series = ticker_df['High']
            low_series = ticker_df['Low']

            avg_volume_10d = volume_series.tail(10).mean()
            if avg_volume_10d < 1000000:
                continue

            combined_stock_spy = pd.concat([close_series.rename('Stock'), spy_close.rename('SPY')], axis=1).dropna()
            stock_returns = combined_stock_spy['Stock'].pct_change().dropna()
            
            stock_cum = (1 + stock_returns).prod() - 1
            alpha = stock_cum - spy_cum

            stock_vol_20d = stock_returns.tail(20).std() * np.sqrt(252)
            relative_vol = stock_vol_20d / spy_vol_20d if spy_vol_20d > 0 else 1.0

            # Volatility engine mapping
            historical_20d_vols = stock_returns.rolling(20).std() * np.sqrt(252)
            current_20d_vol = historical_20d_vols.iloc[-1]

            if len(historical_20d_vols.dropna()) > 0 and not np.isnan(current_20d_vol):
                valid_vols = historical_20d_vols.dropna()
                hv_rank = (valid_vols < current_20d_vol).sum() / len(valid_vols)
            else:
                hv_rank = 0.5

            delta = combined_stock_spy['Stock'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rsi_series = 100 - (100 / (1 + (gain / loss)))
            latest_price = combined_stock_spy['Stock'].iloc[-1]
            latest_rsi = rsi_series.iloc[-1] if not np.isnan(rsi_series.iloc[-1]) else 50.0

            high_low = high_series - low_series
            high_close = (high_series - close_series.shift()).abs()
            low_close = (low_series - close_series.shift()).abs()
            true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
            atr = true_range.rolling(14).mean().iloc[-1]
            suggested_strike_margin = latest_price - (2 * atr)

            score_a = 0
            if latest_rsi > 55: score_a += 1
            if alpha > 0.05: score_a += 1
            if hv_rank < 0.40: score_a += 1

            score_b = 0
            if latest_rsi < 35: score_b += 1
            if alpha < 0: score_b += 1
            if hv_rank > 0.60: score_b += 1

            metrics = {
                "Price": f"${latest_price:,.2f}",
                "Alpha": alpha,
                "Vol": f"{relative_vol:.2f}x",
                "HVRank": f"{hv_rank * 100:.0f}%",
                "RSI": int(latest_rsi),
                "StrikeFloor": f"${suggested_strike_margin:,.2f}",
                "ScoreA": f"{score_a} / 3",
                "ScoreB": f"{score_b} / 3",
                "RawHVRank": hv_rank
            }

            if latest_rsi >= 45:
                group_a_pool.append((ticker, metrics))
            else:
                group_b_pool.append((ticker, metrics))
        except Exception:
            continue

    group_a_pool.sort(key=lambda x: x[1]["Alpha"], reverse=True)
    group_b_pool.sort(key=lambda x: x[1]["RawHVRank"], reverse=True)

    matrix_output = build_markdown_matrix(group_a_pool[:20], group_b_pool[:20])
    print("\n" + matrix_output + "\n")
    
    send_matrix_email(matrix_output)

if __name__ == "__main__":
    main()
