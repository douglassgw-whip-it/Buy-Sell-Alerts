import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import pandas as pd
import yfinance as yf

# Email Configuration
SENDER_EMAIL = "douglassgw@gmail.com"
RECIPIENT_EMAIL = "douglassgw@gmail.com"
APP_PASSWORD = os.environ.get("EMAIL_PASS")


def fetch_stock_data(ticker, period="1y"):
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period=period)
        if df.empty:
            return None
        return df
    except Exception:
        return None


def calculate_indicators(df):
    df["MA50"] = df["Close"].rolling(window=50).mean()
    df["MA200"] = df["Close"].rolling(window=200).mean()

    delta = df["Close"].diff()
    gain = delta.clip(lower=0)
    loss = -1 * delta.clip(upper=0)

    ema_gain = gain.ewm(com=13, adjust=False).mean()
    ema_loss = loss.ewm(com=13, adjust=False).mean()

    rs = ema_gain / ema_loss.replace(0, 0.00001)
    df["RSI"] = 100 - (100 / (1 + rs))
    return df


def generate_signal(df):
    if len(df) < 200:
        return "Insufficient Data"

    latest = df.iloc[-1]
    current_price = latest["Close"]
    ma50 = latest["MA50"]
    ma200 = latest["MA200"]
    rsi = latest["RSI"]

    if current_price > ma50 and ma50 > ma200 and rsi < 65:
        return "BUY (Strong Uptrend)"
    elif current_price < ma50 or rsi > 80:
        return "SELL / TAKE PROFIT"
    else:
        return "HOLD / NEUTRAL"


def send_email(report_html):
    """Sends the final report via Gmail."""
    if not APP_PASSWORD:
        print("Error: EMAIL_PASS environment variable is not set.")
        return

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "📊 Daily Stock Screener Alerts"
    msg["From"] = SENDER_EMAIL
    msg["To"] = RECIPIENT_EMAIL

    part = MIMEText(report_html, "html")
    msg.attach(part)

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(SENDER_EMAIL, APP_PASSWORD)
            server.sendmail(SENDER_EMAIL, RECIPIENT_EMAIL, msg.as_string())
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")


def run_screener():
    # Customize your watchlist tickers here
    watchlist = ["AAPL", "MSFT", "NVDA", "AVGO", "AMZN", "TSLA"]
    results = []

    for ticker in watchlist:
        df = fetch_stock_data(ticker)
        if df is not None:
            df = calculate_indicators(df)
            signal = generate_signal(df)
            last_price = df.iloc[-1]["Close"]
            last_rsi = df.iloc[-1]["RSI"]

            results.append(
                {
                    "Ticker": ticker,
                    "Price": f"${last_price:.2f}",
                    "RSI": f"{last_rsi:.1f}",
                    "Signal": signal,
                }
            )

    # Convert results to an HTML table for clean email presentation
    results_df = pd.DataFrame(results)
    html_table = results_df.to_html(index=False, classes="table")

    # Basic HTML Email Styling
    email_content = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; }}
            table {{ border-collapse: collapse; width: 100%; max-width: 600px; }}
            th, td {{ border: 1px solid #dddddd; text-align: left; padding: 8px; }}
            th {{ background-color: #f2f2f2; }}
        </style>
    </head>
    <body>
        <h2>Daily Buy/Sell Stock Alerts</h2>
        <p>Here are the latest technical signals for your watchlist:</p>
        {html_table}
        <br>
        <p><small>Generated automatically via GitHub Actions.</small></p>
    </body>
    </html>
    """
    send_email(email_content)


if __name__ == "__main__":
    run_screener()
