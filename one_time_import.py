import json
import requests
from datetime import datetime
from supabase import create_client, Client
import config

# Initialize Supabase client
supabase: Client = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)

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
        result = supabase.table('quotes').insert(quote_data).execute()
        
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
                    print(f"⚠️ Trade insert error for {symbol}: {str(e)}")
        
        # Calculate and display price info
        mid_price = (data['bid_price'] + data['ask_price']) / 2
        spread = data['ask_price'] - data['bid_price']
        
        print(f"✅ {symbol} saved - Price: ${mid_price:,.2f} | Spread: ${spread:.2f}")
        return True
    
    except Exception as e:
        print(f"❌ Error saving {symbol}: {str(e)}")
        return False

def run_one_time_import():
    """Run one-time import for all symbols"""
    print("🚀 Starting one-time import...\n")
    
    successful = []
    failed = []
    
    for item in config.SYMBOLS:
        print(f"📊 Fetching {item['symbol']}...")
        
        # Fetch data from QuickNode
        data = fetch_quote(item['id'])
        
        if data:
            # Save to Supabase
            if save_quote(item['symbol'], data):
                successful.append(item['symbol'])
            else:
                failed.append(item['symbol'])
        else:
            failed.append(item['symbol'])
    
    # Print summary
    print("\n📈 Import Summary:")
    print(f"✅ Successful: {', '.join(successful) if successful else 'None'}")
    print(f"❌ Failed: {', '.join(failed) if failed else 'None'}")
    
    # Verify data in database
    try:
        result = supabase.table('quotes').select('symbol', count='exact').execute()
        print(f"\n📊 Total records in database: {result.count}")
    except:
        pass

if __name__ == "__main__":
    run_one_time_import()
    print("\n✨ One-time import complete!")