import requests
from django.conf import settings
from ..models import Index, Company
import logging

logger = logging.getLogger(__name__)

# Base URL for the API
API_URL = "https://api.sectors.app/v1/index/"

def fetch_companies_by_index(index_name):
    """Fetch companies by index name from the Sectors API."""
    headers = {
        "Authorization": settings.SECTORS_API_KEY
    }

    url = f"{API_URL}{index_name}/"
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch companies for index {index_name}: {e}")
        return []

def update_companies_by_index(index_name):
    """Fetch and store companies from the API for a given index."""
    companies_data = fetch_companies_by_index(index_name)
    
    # Get or create the Index instance
    index, created = Index.objects.get_or_create(name=index_name)
    
    for company_data in companies_data:
        symbol = company_data.get('symbol')
        company_name = company_data.get('company_name')
        
        """
        # Ensure both symbol and company_name are present
        if symbol and company_name:
            # Create or update the company under the given index
            Company.objects.update_or_create(
                index=index,
                symbol=symbol,
                defaults={'company_name': company_name}
            )
        """
        if symbol and company_name:
            # Get or create the company
            company, _ = Company.objects.update_or_create(
                symbol=symbol,
                defaults={'company_name': company_name}
            )
            # Add the index to the company's indices
            company.index.add(index)
