import requests
from django.conf import settings
from ..models import Subsector, SubsectorReport
import logging

logger = logging.getLogger(__name__)

API_URL = "https://api.sectors.app/v1/subsector/report/"

def fetch_subsector_report(subsector_name):
    url = f"{API_URL}{subsector_name}/"
    headers = {
        "Authorization": settings.SECTORS_API_KEY
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching subsector report: {e}")
        return None

def update_subsector_report_in_db(subsector_name):
    report_data = fetch_subsector_report(subsector_name)
    if report_data:
        try:
            subsector = Subsector.objects.get(name=subsector_name)
            # Update or create the report
            SubsectorReport.objects.update_or_create(
                subsector=subsector,
                defaults={
                    'statistics': report_data.get('statistics'),
                    'market_cap': report_data.get('market_cap'),
                    'stability': report_data.get('stability'),
                    'valuation': report_data.get('valuation'),
                    'growth': report_data.get('growth'),
                    'companies': report_data.get('companies'),
                }
            )
            logger.info(f"Updated report for subsector: {subsector_name}")
        except Subsector.DoesNotExist:
            logger.warning(f"Subsector '{subsector_name}' not found in database.")
