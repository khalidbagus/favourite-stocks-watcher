import requests
from django.conf import settings
from ..models import Sector, Subsector
import logging

logger = logging.getLogger(__name__)

API_URL = "https://api.sectors.app/v1/subsectors/"

def fetch_subsectors():
    headers = {
        "Authorization": settings.SECTORS_API_KEY
    }
    try:
        response = requests.get(API_URL, headers=headers)
        response.raise_for_status()
        subsectors = response.json()
        return subsectors
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching subsectors: {e}")
        return []

def update_subsectors_in_db():
    subsectors = fetch_subsectors()
    for item in subsectors:
        sector_name = item.get("sector")
        subsector_name = item.get("subsector")
        if sector_name and subsector_name:
            # Ensure the sector exists
            sector, _ = Sector.objects.get_or_create(name=sector_name)
            # Create or update subsector under the correct sector
            Subsector.objects.update_or_create(
                sector=sector,
                name=subsector_name
            )
