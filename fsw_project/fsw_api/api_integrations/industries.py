import requests
from django.conf import settings
from ..models import Subsector, Industry
import logging

logger = logging.getLogger(__name__)

API_URL = "https://api.sectors.app/v1/industries/"

def fetch_industries():
    headers = {
        "Authorization": settings.SECTORS_API_KEY
    }
    try:
        response = requests.get(API_URL, headers=headers)
        response.raise_for_status()
        industries = response.json()
        return industries
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching industries: {e}")
        return []

def update_industries_in_db():
    industries = fetch_industries()
    for item in industries:
        subsector_name = item.get("subsector")
        industry_name = item.get("industry")
        if subsector_name and industry_name:
            # Ensure the subsector exists
            subsector_name, _ = Subsector.objects.get_or_create(name=subsector_name)
            # Create or update subsector under the correct sector
            Industry.objects.update_or_create(
                subsector=subsector_name,
                name=industry_name
            )
