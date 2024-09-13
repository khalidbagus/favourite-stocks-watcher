import requests
from django.conf import settings
from ..models import IDXMarketCap
import logging

logger = logging.getLogger(__name__)

API_URL = "https://api.sectors.app/v1/idx-total/"

def fetch_idx_market_cap_data(start=None, end=None):
    headers = {
        "Authorization": f"Bearer {settings.SECTORS_API_KEY}"
    }
    params = {
        "start": start,
        "end": end,
    }
    
    try:
        response = requests.get(API_URL, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching IDX market cap data: {e}")
        return []

def update_idx_market_cap_in_db(start=None, end=None):
    market_cap_data = fetch_idx_market_cap_data(start=start, end=end)
    
    for item in market_cap_data:
        date = item.get('date')
        idx_total_market_cap = item.get('idx_total_market_cap')
        
        if date and idx_total_market_cap:
            IDXMarketCap.objects.update_or_create(
                date=date,
                defaults={'idx_total_market_cap': idx_total_market_cap}
            )
