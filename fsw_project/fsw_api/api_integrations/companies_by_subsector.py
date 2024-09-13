import requests
from django.conf import settings
from ..models import Subsector, Company
import logging

logger = logging.getLogger(__name__)

# Base URL for the API
API_URL = "https://api.sectors.app/v1/companies/"

def fetch_companies_by_subsector(subsector_name):
    """Fetch companies by subsector from the Sectors API."""
    headers = {
        "Authorization": settings.SECTORS_API_KEY
    }
    params = {'sub_sector': subsector_name}
    try:
        response = requests.get(API_URL, params=params, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch companies for subsector {subsector_name}: {e}")
        return []

def update_companies_by_subsector(subsector_name):
    """Fetch and store companies from the API for a given subsector."""
    companies_data = fetch_companies_by_subsector(subsector_name)
    
    try:
        subsector = Subsector.objects.get(name=subsector_name)
    except Subsector.DoesNotExist:
        logger.error(f"Subsector '{subsector_name}' not found in the database.")
        return
    
    """
    for company_data in companies_data:
        symbol = company_data.get('symbol')
        company_name = company_data.get('company_name')

        if symbol and company_name:
            Company.objects.update_or_create(
                subsector=subsector,
                symbol=symbol,
                defaults={'company_name': company_name}
            )
    """
    for company_data in companies_data:
        symbol = company_data.get('symbol')
        company_name = company_data.get('company_name')

        if symbol and company_name:
            company, _ = Company.objects.update_or_create(
                symbol=symbol,
                defaults={'company_name': company_name}
            )
            company.subsector = subsector
            company.save()
