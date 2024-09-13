import requests
from ..models import TopRankedCompany, Subsector
from django.conf import settings
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

API_URL = "https://api.sectors.app/v1/companies/top/"

def fetch_top_ranked_companies(classifications="all", n_stock=5, year=None, sub_sector=None):
    headers = {
        "Authorization": settings.SECTORS_API_KEY
    }

    params = {
        "classifications": classifications,
        "n_stock": n_stock,
        "year": year or datetime.now().year,
    }

    if sub_sector:
        params["sub_sector"] = sub_sector

    try:
        response = requests.get(API_URL, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching top ranked companies: {e}")
        return {}

def update_top_ranked_companies_in_db(classifications="all", n_stock=5, year=None, sub_sector=None):
    ranked_data = fetch_top_ranked_companies(classifications, n_stock, year, sub_sector)
    if not ranked_data:
        logger.warning("No data returned from API.")
        return

    for classification, companies in ranked_data.items():
        for company in companies:
            symbol = company.get("symbol")
            company_name = company.get("company_name")
            value = company.get(classification)

            TopRankedCompany.objects.update_or_create(
                symbol=symbol,
                classification=classification,
                year=year or datetime.now().year,
                defaults={
                    "company_name": company_name,
                    "value": value,
                    "subsector": Subsector.objects.filter(name=sub_sector).first() if sub_sector else None
                }
            )
