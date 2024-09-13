import requests
from ..models import MostTradedStock
from django.conf import settings
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

API_URL = "https://api.sectors.app/v1/most-traded/"

def fetch_most_traded_stocks(start=None, end=None, n_stock=5, adjusted=False, sub_sector=None):
    headers = {
        "Authorization": f"Bearer {settings.SECTORS_API_KEY}" 
    }

    params = {
        "start": start,
        "end": end,
        "n_stock": n_stock,
        "adjusted": adjusted,
    }

    if sub_sector:
        params["sub_sector"] = sub_sector

    try:
        response = requests.get(API_URL, headers=headers, params=params)
        response.raise_for_status()
        most_traded = response.json()
        return most_traded
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching most traded stocks: {e}")
        return {}

def update_most_traded_stocks_in_db(start=None, end=None, n_stock=5, adjusted=False, sub_sector=None):
    most_traded_data = fetch_most_traded_stocks(start, end, n_stock, adjusted, sub_sector)
    if not most_traded_data:
        logger.warning("No data returned from API.")
        return

    for date_str, stocks in most_traded_data.items():
        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
        for stock in stocks:
            symbol = stock.get("symbol")
            company_name = stock.get("company_name")
            volume = stock.get("volume", 0)
            price = stock.get("price", 0.0)

            MostTradedStock.objects.update_or_create(
                symbol=symbol,
                date=date_obj,
                defaults={
                    "company_name": company_name,
                    "volume": volume,
                    "price": price,
                    "adjusted": adjusted
                }
            )
