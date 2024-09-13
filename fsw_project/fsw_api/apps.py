from django.apps import AppConfig


class FswApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'fsw_api'
    """
    def ready(self):
        import logging
        from .models import Company, Subsector, SubIndustry, CompanyPerformance
        from .api_integrations.subsectors import update_subsectors_in_db
        from .api_integrations.industries import update_industries_in_db
        from .api_integrations.subindustries import update_subindustries_in_db
        from .api_integrations.companies_by_index import update_companies_by_index
        from .api_integrations.companies_by_subsector import update_companies_by_subsector
        from .api_integrations.companies_by_subindustry import update_companies_by_subindustry
        from .api_integrations.company_performance_since_ipo import update_company_performance
        import time
        ## import another needed module later

        logger = logging.getLogger(__name__)
     
        # Fetch and update data for subsectors
        update_subsectors_in_db()
        time.sleep(5)

        # Fetch and update data for industries
        update_industries_in_db()
        time.sleep(5)

        # Fetch and update data for subindustries
        update_subindustries_in_db()
        time.sleep(5)

        # Fetch and update companies_by_index
        indexes = ['ftse', 'idx30', 'idxbumn20', 'idxesgl', 'idxg30', 'idxhidiv20', 'idxq30', 'idxv30', 'jii70', 'kompas100', 'lq45', 'sminfra18', 'srikehati']
        for index in indexes:
            logger.info(f"Fetching and updating data for index {index}")
            update_companies_by_index(index_name=index)
            time.sleep(5)

        # Fetch and update companies_by_subsector
        subsectors = Subsector.objects.all()
        for subsector in subsectors:
            logger.info(f"Fetching and updating data for {subsector.name} subsector")
            update_companies_by_subsector(subsector_name=subsector.name)
            time.sleep(5)

        # Fetch and update companies_by_subindustry
        subindustries = SubIndustry.objects.all()
        for subindustry in subindustries:
            logger.info(f"Fetching and updating data for {subindustry.name} subindustry")
            update_companies_by_subindustry(sub_industry_name=subindustry.name)
            time.sleep(5)
        
        # Fetch and update company_performance_since ipo
        companies = Company.objects.all()
        for company in companies:
            logger.info(f"Fetching and updating data for {company.symbol} symbol")
            update_company_performance(company.symbol)
        
    """

        


        
