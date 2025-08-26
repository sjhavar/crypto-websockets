import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
QUICKNODE_ENDPOINT = os.getenv('QUICKNODE_ENDPOINT')
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_ANON_KEY')
COLLECTION_INTERVAL = int(os.getenv('COLLECTION_INTERVAL', 10))

# Symbols to track
SYMBOLS = [
    {'symbol': 'BTC', 'id': 'COINBASE_SPOT_BTC_USD'},
    {'symbol': 'ETH', 'id': 'COINBASE_SPOT_ETH_USD'},
    {'symbol': 'SOL', 'id': 'COINBASE_SPOT_SOL_USD'}
]

# Validate configuration
if not all([QUICKNODE_ENDPOINT, SUPABASE_URL, SUPABASE_KEY]):
    print("❌ Missing required environment variables!")
    print("Please check your .env file")
    sys.exit(1)

# Remove trailing slash from endpoint if present
QUICKNODE_ENDPOINT = QUICKNODE_ENDPOINT.rstrip('/')