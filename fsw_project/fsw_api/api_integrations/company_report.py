import requests
from django.conf import settings
from ..models import Company, CompanyReport
import logging

logger = logging.getLogger(__name__)

API_URL = "https://api.sectors.app/v1/company/report/"

def fetch_company_report(symbol):
    headers = {
        "Authorization": settings.SECTORS_API_KEY
    }
    try:
        response = requests.get(f"{API_URL}{symbol}/", headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching report for {symbol}: {e}")
        return None

def update_company_report(symbol):
    report_data = fetch_company_report(symbol)
    if not report_data:
        logger.warning(f"No report data fetched for {symbol}.")
        return

    try:
        company = Company.objects.get(symbol=symbol)
    except Company.DoesNotExist:
        logger.warning(f"Company with symbol {symbol} does not exist.")
        return

    CompanyReport.objects.update_or_create(
        company=company,
        defaults={
            'overview': report_data.get('overview'),
            'valuation': report_data.get('valuation'),
            'future': report_data.get('future'),
            'financials': report_data.get('financials'),
            'dividend': report_data.get('dividend'),
            'management': report_data.get('management'),
            'ownership': report_data.get('ownership'),
            'peers': report_data.get('peers')
        }
    )
    logger.info(f"Report for {company.company_name} ({symbol}) has been updated.")
