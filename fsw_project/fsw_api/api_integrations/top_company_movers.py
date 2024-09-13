import requests
from ..models import TopCompanyMover
from django.conf import settings
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

API_URL = "https://api.sectors.app/v1/companies/top-changes/"

def fetch_top_company_movers(classifications="all", n_stock=5, periods="all", sub_sector=None):
    headers = {
        "Authorization": f"Bearer {settings.SECTORS_API_KEY}"
    }

    params = {
        "classifications": classifications,
        "n_stock": n_stock,
        "periods": periods
    }

    if sub_sector:
        params["sub_sector"] = sub_sector

    try:
        response = requests.get(API_URL, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching top company movers: {e}")
        return {}

def update_top_company_movers_in_db(classifications="all", n_stock=5, periods="all", sub_sector=None):
    data = fetch_top_company_movers(classifications, n_stock, periods, sub_sector)
    
    if not data:
        logger.warning("No data returned from API.")
        return

    for classification, periods_data in data.items():
        for period, companies in periods_data.items():
            for company in companies:
                symbol = company.get("symbol")
                company_name = company.get("name")
                price_change = company.get("price_change", 0.0)
                last_close_price = company.get("last_close_price", 0.0)
                latest_close_date = datetime.strptime(company.get("latest_close_date"), "%Y-%m-%d").date()

                TopCompanyMover.objects.update_or_create(
                    symbol=symbol,
                    classification=classification,
                    period=period,
                    latest_close_date=latest_close_date,
                    defaults={
                        "company_name": company_name,
                        "price_change": price_change,
                        "last_close_price": last_close_price
                    }
                )
