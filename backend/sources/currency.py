"""ExchangeRate API fetcher for currency rates."""

import httpx

from sources.types import SourceItem, SourceResult

EXCHANGE_API = "https://open.er-api.com/v6/latest"


async def fetch_currency(base: str = "USD") -> SourceResult:
    """Fetch exchange rates for common currency pairs."""
    target_currencies = ["INR", "EUR", "GBP", "JPY", "AED"]

    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{EXCHANGE_API}/{base}",
            timeout=5,
        )
        resp.raise_for_status()
        data = resp.json()

    rates = data.get("rates", {})
    rate_lines = []
    for currency in target_currencies:
        rate = rates.get(currency)
        if rate:
            rate_lines.append(f"{base}/{currency}: {rate:.2f}")

    summary = " | ".join(rate_lines) if rate_lines else "No rates available"

    item = SourceItem(
        title=f"Exchange Rates ({base})",
        summary=summary,
        url="https://www.exchangerate-api.com/",
        source="exchangerate",
        raw={"base": base, "rates": {c: rates.get(c) for c in target_currencies if c in rates}},
    )
    return SourceResult(source_name="exchangerate", items=(item,))
