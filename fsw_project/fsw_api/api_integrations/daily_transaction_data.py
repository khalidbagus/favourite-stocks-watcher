import requests
from django.conf import settings
from ..models import Index, IndexDailyTransaction
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

API_URL = "https://api.sectors.app/v1/index-daily/{index_code}/"

def fetch_index_daily_transactions(index_code, start_date=None, end_date=None):
    headers = {
        "Authorization": f"Bearer {settings.SECTORS_API_KEY}"
    }

    params = {}
    if start_date:
        params["start"] = start_date
    if end_date:
        params["end"] = end_date

    response = requests.get(API_URL.format(index_code=index_code), headers=headers, params=params)
    
    try:
        response.raise_for_status()
    except requests.HTTPError as e:
        logger.error(f"Error fetching index daily transactions: {e}")
        return []

    return response.json()

def update_index_daily_transactions(index_code, start_date=None, end_date=None):
    data = fetch_index_daily_transactions(index_code, start_date, end_date)

    for transaction in data:
        date = datetime.strptime(transaction['date'], "%Y-%m-%d").date()
        closing_price = transaction['price']
        
        index, created = Index.objects.get_or_create(name=index_code)
        
        IndexDailyTransaction.objects.update_or_create(
            index=index,
            date=date,
            defaults={
                'closing_price': closing_price
            }
        )
