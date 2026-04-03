import time
import yfinance as yf


def fetch_market_data() -> dict:
    start_time = time.time()

    try:
        nifty = yf.Ticker("^NSEI")
        sensex = yf.Ticker("^BSESN")

        nifty_data = nifty.history(period="2d")
        sensex_data = sensex.history(period="2d")

        if nifty_data.empty or sensex_data.empty:
            raise ValueError("Market data unavailable")

        nifty_close = float(nifty_data["Close"].iloc[-1])
        sensex_close = float(sensex_data["Close"].iloc[-1])

        nifty_prev = float(nifty_data["Close"].iloc[-2]) if len(nifty_data) > 1 else nifty_close
        sensex_prev = float(sensex_data["Close"].iloc[-2]) if len(sensex_data) > 1 else sensex_close

        execution_time = round(time.time() - start_time, 4)

        return {
            "status": "success",
            "data": {
                "nifty": {
                    "current": nifty_close,
                    "previous_close": nifty_prev
                },
                "sensex": {
                    "current": sensex_close,
                    "previous_close": sensex_prev
                }
            },
            "error": None,
            "execution_time": execution_time
        }

    except Exception as e:
        execution_time = round(time.time() - start_time, 4)

        return {
            "status": "error",
            "data": None,
            "error": str(e),
            "execution_time": execution_time
        }