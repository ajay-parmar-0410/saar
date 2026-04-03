from tools.retry import retry_tool
from tools.weather_api import fetch_weather
from tools.finance_api import fetch_market_data
from tools.weather_api import fetch_weather
from tools.news_api import fetch_news
result = retry_tool(fetch_news)


print(result)