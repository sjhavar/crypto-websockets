"""
Quick test script to verify Coinbase WebSocket connection
Run this first to make sure everything is working!
"""

import asyncio
import websockets
import json

async def quick_test():
    """Quick connection test - receives just a few messages"""
    
    print("🧪 Testing Coinbase WebSocket Connection...\n")
    
    url = "wss://ws-feed.exchange.coinbase.com"
    
    try:
        # Connect
        print("1️⃣ Connecting to Coinbase...")
        ws = await websockets.connect(url)
        print("   ✅ Connected!\n")
        
        # Subscribe to BTC-USD ticker only (simplest test)
        print("2️⃣ Subscribing to BTC-USD ticker...")
        subscribe = {
            "type": "subscribe",
            "product_ids": ["BTC-USD"],
            "channels": ["ticker"]
        }
        await ws.send(json.dumps(subscribe))
        print("   ✅ Subscription sent!\n")
        
        # Receive and print 5 messages
        print("3️⃣ Receiving messages...")
        for i in range(5):
            message = await ws.recv()
            data = json.loads(message)
            
            msg_type = data.get('type')
            
            if msg_type == 'subscriptions':
                print(f"   ✅ Subscription confirmed!")
                print(f"      Channels: {data.get('channels', [])}")
            elif msg_type == 'ticker':
                price = data.get('price', 'N/A')
                bid = data.get('best_bid', 'N/A')
                ask = data.get('best_ask', 'N/A')
                print(f"   📈 BTC-USD: Price=${price}, Bid=${bid}, Ask=${ask}")
            else:
                print(f"   📨 Received: {msg_type}")
        
        # Close connection
        await ws.close()
        print("\n✅ Test completed successfully!")
        print("   Your connection to Coinbase WebSocket is working!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        print("\nPossible issues:")
        print("  - Check your internet connection")
        print("  - Coinbase might be down (check status.coinbase.com)")
        print("  - Firewall might be blocking WebSocket connections")

if __name__ == "__main__":
    asyncio.run(quick_test())