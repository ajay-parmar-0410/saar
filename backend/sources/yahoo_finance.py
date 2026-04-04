"""Yahoo Finance / yfinance fetcher for Indian markets."""

import httpx

from sources.types import SourceItem, SourceResult

# Key Indian market indices and popular stocks
DEFAULT_SYMBOLS = ["^NSEI", "^BSESN"]  # Nifty 50, Sensex


async def fetch_yahoo_finance(
    symbols: list[str] | None = None,
    max_items: int = 10,
) -> SourceResult:
    """Fetch stock data from Yahoo Finance API.

    Uses the Yahoo Finance v8 quote endpoint (no API key required).
    """
    tickers = symbols or DEFAULT_SYMBOLS

    async with httpx.AsyncClient() as client:
        resp = await client.get(
            "https://query1.finance.yahoo.com/v8/finance/spark",
            params={
                "symbols": ",".join(tickers),
                "range": "1d",
                "interval": "1d",
            },
            headers={"User-Agent": "Saar/1.0"},
            timeout=5,
        )
        resp.raise_for_status()
        data = resp.json()

    items: list[SourceItem] = []
    for symbol, info in data.get("spark", {}).get("result", [{}])[0:max_items]:
        pass  # v8 spark returns minimal data

    # Fallback: use v6 quote endpoint for richer data
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            "https://query1.finance.yahoo.com/v6/finance/quote",
            params={"symbols": ",".join(tickers)},
            headers={"User-Agent": "Saar/1.0"},
            timeout=5,
        )
        if resp.status_code != 200:
            # v6 may be blocked, try scraping approach
            return await _fetch_via_search(tickers)
        data = resp.json()

    for quote in data.get("quoteResponse", {}).get("result", []):
        name = quote.get("shortName", quote.get("symbol", ""))
        price = quote.get("regularMarketPrice", 0)
        change = quote.get("regularMarketChange", 0)
        change_pct = quote.get("regularMarketChangePercent", 0)
        direction = "up" if change >= 0 else "down"

        items.append(SourceItem(
            title=f"{name} ({quote.get('symbol', '')})",
            summary=f"Price: {price:.2f}, {direction} {abs(change):.2f} ({abs(change_pct):.2f}%)",
            url=f"https://finance.yahoo.com/quote/{quote.get('symbol', '')}",
            source="yahoo_finance",
            raw={"price": price, "change": change, "change_pct": change_pct},
        ))

    return SourceResult(source_name="yahoo_finance", items=tuple(items))


async def _fetch_via_search(tickers: list[str]) -> SourceResult:
    """Fallback: search Yahoo Finance for basic quote info."""
    items: list[SourceItem] = []
    async with httpx.AsyncClient() as client:
        for ticker in tickers:
            try:
                resp = await client.get(
                    "https://query2.finance.yahoo.com/v1/finance/search",
                    params={"q": ticker, "newsCount": 0},
                    headers={"User-Agent": "Saar/1.0"},
                    timeout=5,
                )
                if resp.status_code == 200:
                    results = resp.json().get("quotes", [])
                    if results:
                        q = results[0]
                        items.append(SourceItem(
                            title=f"{q.get('shortname', ticker)} ({q.get('symbol', ticker)})",
                            summary=f"Exchange: {q.get('exchange', 'N/A')}",
                            url=f"https://finance.yahoo.com/quote/{q.get('symbol', ticker)}",
                            source="yahoo_finance",
                        ))
            except Exception:
                continue

    return SourceResult(source_name="yahoo_finance", items=tuple(items))
