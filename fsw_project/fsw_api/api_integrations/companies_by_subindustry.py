import requests
from django.conf import settings
from ..models import SubIndustry, Company, Industry
import logging

logger = logging.getLogger(__name__)

# Base URL for the API
API_URL = "https://api.sectors.app/v1/companies/"

def fetch_companies_by_subindustry(sub_industry_name):
    """Fetch companies by subindustry from the Sectors API."""
    headers = {
        "Authorization": settings.SECTORS_API_KEY
    }
    params = {'sub_industry': sub_industry_name}
    try:
        response = requests.get(API_URL, params=params, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch companies for subindustry {sub_industry_name}: {e}")
        return []

def update_companies_by_subindustry(sub_industry_name):
    """Fetch and store companies from the API for a given subindustry."""
    companies_data = fetch_companies_by_subindustry(sub_industry_name)

    # Fetch the subindustry from the database
    subindustry, created = SubIndustry.objects.get_or_create(name=sub_industry_name)

    if not subindustry:
        logger.error(f"SubIndustry '{sub_industry_name}' not found in the database.")
        return

    # For each company in the fetched data
    for company_data in companies_data:
        symbol = company_data.get('symbol')
        company_name = company_data.get('company_name')

        if symbol and company_name:
            # Update or create the company
            company, _ = Company.objects.update_or_create(
                symbol=symbol,
                defaults={'company_name': company_name}
            )
            company.subindustry = subindustry
            company.save()

            # Fetch the industries associated with the subsector of the subindustry
            subsector = Industry.objects.filter(subindustries=subindustry).first().subsector if Industry.objects.filter(subindustries=subindustry).exists() else None

            if subsector:
                # Fetch all industries associated with the subsector of the subindustry
                industries = Industry.objects.filter(subsector=subsector)

                if industries.exists():
                    # Set the industry relationship for the subindustry using .set()
                    subindustry.industry.set(industries)
                    subindustry.save()
                else:
                    logger.warning(f"No industries found for subsector: {subsector}")
            else:
                logger.warning(f"No subsector found for subindustry: {subindustry.name}")


# def update_companies_by_subindustry(sub_industry_name):
#     """Fetch and store companies from the API for a given subindustry."""
#     companies_data = fetch_companies_by_subindustry(sub_industry_name)
    
#     try:
#         subindustry = SubIndustry.objects.get(name=sub_industry_name)
#     except SubIndustry.DoesNotExist:
#         logger.error(f"SubIndustry '{sub_industry_name}' not found in the database.")
#         return
#     """
#     for company_data in companies_data:
#         symbol = company_data.get('symbol')
#         company_name = company_data.get('company_name')

#         if symbol and company_name:
#             Company.objects.update_or_create(
#                 subindustry=subindustry,
#                 symbol=symbol,
#                 defaults={'company_name': company_name}
#             )
#     """
#     """
#     for company_data in companies_data:
#         symbol = company_data.get('symbol')
#         company_name = company_data.get('company_name')

#         if symbol and company_name:
#             company, _ = Company.objects.update_or_create(
#                 symbol=symbol,
#                 defaults={'company_name': company_name}
#             )
#             company.subindustry = subindustry
#             company.save()
#     """
