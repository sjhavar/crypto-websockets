import asyncio
import aiohttp
import json
from datetime import datetime
from supabase import create_client, Client
import config

# Initialize Supabase client
supabase: Client = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)

async def fetch_quote_async(session, symbol_id):
    """Fetch quote asynchronously"""
    try:
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "v1/getCurrentQuotes",
            "params": [{"symbol_id": symbol_id}]
        }
        
        async with session.post(
            config.QUICKNODE_ENDPOINT,
            json=payload,
            timeout=5
        ) as response:
            data = await response.json()
            
            if 'error' in data:
                raise Exception(data['error']['message'])
            
            return data.get('result')
    
    except Exception as e:
        print(f"❌ Error fetching {symbol_id}: {str(e)}")
        return None

async def collect_all_async():
    """Collect all symbols concurrently"""