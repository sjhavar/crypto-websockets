import json
import requests
import time
import signal
import sys
from datetime import datetime
from supabase import create_client, Client
import config

# Initialize Supabase client
supabase: Client = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)

# Statistics tracking
stats = {
    'total_collections': 0,
    'successful': 0,
    'failed': 0,
    'start_time': datetime.now()
}

# Flag for graceful shutdown
running = True

def signal_handler(sig, frame):
    """Handle Ctrl+C for graceful shutdown"""
    global running
    print('\n\n🛑 Shutting down gracefully...')
    running = False
    print_stats()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def fetch_quote(symbol_id):
    """Fetch current quote from QuickNode"""
    try:
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "v1/getCurrentQuotes",
            "params": [{"symbol_id": symbol_id}]
        }
        
        response = requests.post(
            config.QUICKNODE_ENDPOINT,
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=5
        )
        
        data = response.json()
        
        if 'error' in data:
            raise Exception(data['error']['message'])
        
        return data.get('result')
    
    except Exception as e:
        print(f"❌ Error fetching {symbol_id}: {str(e)}")
        return None

def save_quote(symbol, data):
    """Save quote data to Supabase"""
    global stats
    
    try:
        # Prepare quote data
        quote_data = {
            'symbol': symbol,
            'exchange': 'COINBASE',
            'symbol_id': data['symbol_id'],
            'bid_price': data['bid_price'],
            'bid_size': data['bid_size'],
            'ask_price': data['ask_price'],
            'ask_size': data['ask_size'],
            'time_exchange': data['time_exchange'],
            'time_coinapi': data['time_coinapi']
        }
        
        # Insert into quotes table
        supabase.table('quotes').insert(quote_data).execute()
        
        # If there's a last trade, save it
        if 'last_trade' in data and data['last_trade']:
            trade_data = {
                'symbol': symbol,
                'exchange': 'COINBASE',
                'trade_uuid': data['last_trade'].get('uuid'),
                'price': data['last_trade']['price'],
                'size': data['last_trade']['size'],
                'taker_side': data['last_trade'].get('taker_side'),
                'time_exchange': data['last_trade']['time_exchange'],
                'time_coinapi': data['last_trade']['time_coinapi']
            }
            
            try:
                supabase.table('trades').insert(trade_data).execute()
            except Exception as e:
                if 'duplicate' not in str(e).lower():
                    print(f"⚠️ Trade error: {str(e)[:50]}")
        
        # Calculate and display price info
        mid_price = (data['bid_price'] + data['ask_price']) / 2
        spread = data['ask_price'] - data['bid_price']
        
        print(f"✅ {symbol}: ${mid_price:,.2f} | Spread: ${spread:.2f} | {datetime.now().strftime('%H:%M:%S')}")
        stats['successful'] += 1
        return True
    
    except Exception as e:
        print(f"❌ Save error for {symbol}: {str(e)[:50]}")
        stats['failed'] += 1
        return False

def collect_all_prices():
    """Collect data for all symbols"""
    global stats
    stats['total_collections'] += 1
    
    print(f"\n📊 Collection #{stats['total_collections']} at {datetime.now().strftime('%H:%M:%S')}")
    
    for item in config.SYMBOLS:
        data = fetch_quote(item['id'])
        if data:
            save_quote(item['symbol'], data)
        
        # Small delay between symbols to avoid rate limits
        time.sleep(0.1)

def print_stats():
    """Print collection statistics"""
    runtime = datetime.now() - stats['start_time']
    hours = int(runtime.total_seconds() // 3600)
    minutes = int((runtime.total_seconds() % 3600) // 60)
    seconds = int(runtime.total_seconds() % 60)
    
    total_attempts = stats['successful'] + stats['failed']
    success_rate = (stats['successful'] / total_attempts * 100) if total_attempts > 0 else 0
    
    print('\n📈 Statistics:')
    print(f"Runtime: {hours}h {minutes}m {seconds}s")
    print(f"Collections: {stats['total_collections']}")
    print(f"Successful saves: {stats['successful']}")
    print(f"Failed saves: {stats['failed']}")
    print(f"Success rate: {success_rate:.1f}%")

def main():
    """Main execution loop"""
    print('🚀 Starting continuous data collector')
    print(f"📍 Collecting data every {config.COLLECTION_INTERVAL} seconds")
    print(f"📊 Symbols: {', '.join([s['symbol'] for s in config.SYMBOLS])}")
    print('Press Ctrl+C to stop\n')
    
    # Run immediately
    collect_all_prices()
    
    # Statistics timer
    last_stats_time = time.time()
    
    # Main loop
    while running:
        # Wait for the interval
        time.sleep(config.COLLECTION_INTERVAL)
        
        if running:
            collect_all_prices()
        
        # Print stats every 5 minutes
        if time.time() - last_stats_time > 300:
            print_stats()
            last_stats_time = time.time()

if __name__ == "__main__":
    main()