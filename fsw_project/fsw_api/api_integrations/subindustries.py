import requests
from django.conf import settings
from ..models import SubIndustry, Industry
import logging

logger = logging.getLogger(__name__)

API_URL = "https://api.sectors.app/v1/subindustries/"

def fetch_subindustries():
    headers = {
        "Authorization": settings.SECTORS_API_KEY
    }
    try:
        response = requests.get(API_URL, headers=headers)
        response.raise_for_status()
        subindustries = response.json()
        return subindustries
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching subindustries: {e}")
        return []
    
def update_subindustries_in_db():
    """Update the database with subindustries fetched from the API."""
    subindustries_data = fetch_subindustries()

    for item in subindustries_data:
        industry_name = item.get("industry")
        sub_industry_name = item.get("sub_industry")

        if industry_name and sub_industry_name:
            try:
                # Get the Industry object (assuming a unique name constraint)
                industry = Industry.objects.get(name=industry_name)

                # Check if the SubIndustry already exists or create it
                subindustry, created = SubIndustry.objects.get_or_create(name=sub_industry_name)

                # Since `industry` is a ManyToManyField, we set the relationship
                # Add the Industry to the SubIndustry's industries (using .add() or .set())
                subindustry.industry.add(industry)  # You can also use `.set([industry])` if replacing all industries

                # Save the subindustry to persist the ManyToMany relationship
                subindustry.save()

            except Industry.DoesNotExist:
                logger.warning(f"Industry '{industry_name}' not found.")
"""
def update_subindustries_in_db():
    subindustries = fetch_subindustries()
    for item in subindustries:
        industry_name = item.get("industry")
        sub_industry_name = item.get("sub_industry")

        if industry_name and sub_industry_name:
            try:
                industry = Industry.objects.get(name=industry_name)
                SubIndustry.objects.update_or_create(
                    industry=industry,
                    name=sub_industry_name
                )
            except Industry.DoesNotExist:
                logger.warning(f"Industry '{industry_name}' not found.")
"""
