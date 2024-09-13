import requests
from django.conf import settings
from ..models import Company, CompanyPerformance
import logging

logger = logging.getLogger(__name__)

API_URL = "https://api.sectors.app/v1/listing-performance/{ticker}/"

def fetch_company_performance(ticker):
    headers = {
        "Authorization": settings.SECTORS_API_KEY
    }
    try:
        url = API_URL.format(ticker=ticker)
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching performance for {ticker}: {e}")
        return None

def update_company_performance(ticker):
    data = fetch_company_performance(ticker)
    if not data:
        logger.warning(f"No data returned for {ticker}")
        return

    company_symbol = data.get("symbol")
    if not company_symbol:
        logger.warning(f"Invalid data format for {ticker}: {data}")
        return

    try:
        company = Company.objects.get(symbol=company_symbol)
        CompanyPerformance.objects.update_or_create(
            company=company,
            defaults={
                'chg_7d': data.get('chg_7d'),
                'chg_30d': data.get('chg_30d'),
                'chg_90d': data.get('chg_90d'),
                'chg_365d': data.get('chg_365d'),
            }
        )
        logger.info(f"Updated performance for {company.company_name}")
    except Company.DoesNotExist:
        logger.error(f"Company with symbol {ticker} does not exist.")
