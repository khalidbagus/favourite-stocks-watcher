import requests
from ..models import TopCompanyGrowth
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

API_URL = "https://api.sectors.app/v1/companies/top-growth/"

def fetch_top_company_growth(classifications='all', n_stock=5, sub_sector=None):
    headers = {
        "Authorization": f"Bearer {settings.SECTORS_API_KEY}"
    }
    
    params = {
        "classifications": classifications,
        "n_stock": n_stock
    }
    
    if sub_sector:
        params["sub_sector"] = sub_sector
    
    try:
        response = requests.get(API_URL, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching top company growth: {e}")
        return {}

def update_top_company_growth_in_db(classifications='all', n_stock=5, sub_sector=None):
    growth_data = fetch_top_company_growth(classifications, n_stock, sub_sector)
    if not growth_data:
        logger.warning("No data returned from API.")
        return
    
    for classification, companies in growth_data.items():
        for company in companies:
            symbol = company.get("symbol")
            company_name = company.get("company_name")
            yoy_growth = company.get("yoy_quarter_earnings_growth") or company.get("yoy_quarter_revenue_growth")
            
            TopCompanyGrowth.objects.update_or_create(
                symbol=symbol,
                classification=classification,
                defaults={
                    "company_name": company_name,
                    "yoy_growth": yoy_growth
                }
            )
