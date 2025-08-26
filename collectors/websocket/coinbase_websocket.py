"""
Coinbase WebSocket Connection - Step 1: Basic Implementation
This script establishes a connection to Coinbase WebSocket and receives real-time market data.
"""

import asyncio
import websockets
import json
import signal
import sys
from datetime import datetime
from typing import Dict, Optional

# Configuration
COINBASE_WS_URL = "wss://ws-feed.exchange.coinbase.com"
SYMBOLS = ["BTC-USD", "ETH-USD", "SOL-USD"]

# Global flag for graceful shutdown
running = True

def signal_handler(sig, frame):
    """Handle Ctrl+C for graceful shutdown"""
    global running
    print('\n🛑 Shutting down gracefully...')
    running = False

signal.signal(signal.SIGINT, signal_handler)

class CoinbaseWebSocket:
    """Basic Coinbase WebSocket client"""
    
    def __init__(self, symbols: list):
        """
        Initialize the WebSocket client
        
        Args:
            symbols: List of trading pairs (e.g., ['BTC-USD', 'ETH-USD'])
        """
        self.url = COINBASE_WS_URL
        self.symbols = symbols
        self.ws = None
        
        # Statistics
        self.message_count = 0
        self.message_types = {}
        self.last_prices = {}
        self.start_time = datetime.now()
        
    async def connect(self):
        """Establish WebSocket connection"""
        try:
            print(f"🔌 Connecting to Coinbase WebSocket...")
            self.ws = await websockets.connect(self.url)
            print(f"✅ Connected to {self.url}")
            return True
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False
    
    async def subscribe(self):
        """Subscribe to ticker and matches channels for specified symbols"""
        if not self.ws:
            print("❌ No WebSocket connection")
            return False
        
        # Subscribe to both ticker (quotes) and matches (trades)
        subscribe_message = {
            "type": "subscribe",
            "product_ids": self.symbols,
            "channels": [
                "ticker",   # Real-time best bid/ask
                "matches",  # Real-time trades
                "heartbeat" # Connection health
            ]
        }
        
        try:
            await self.ws.send(json.dumps(subscribe_message))
            print(f"📊 Subscribing to: {', '.join(self.symbols)}")
            print(f"📡 Channels: ticker, matches, heartbeat")
            return True
        except Exception as e:
            print(f"❌ Subscription failed: {e}")
            return False
    
    async def handle_message(self, message: str):
        """Process incoming WebSocket messages"""
        try:
            data = json.loads(message)
            msg_type = data.get('type')
            
            # Track message types
            self.message_count += 1
            self.message_types[msg_type] = self.message_types.get(msg_type, 0) + 1
            
            # Handle different message types
            if msg_type == 'ticker':
                await self.handle_ticker(data)
            elif msg_type == 'match' or msg_type == 'last_match':
                await self.handle_match(data)
            elif msg_type == 'heartbeat':
                # Heartbeat messages - just count them
                pass
            elif msg_type == 'subscriptions':
                print("✅ Subscription confirmed:")
                print(f"   Channels: {data.get('channels', [])}")
            elif msg_type == 'error':
                print(f"❌ Error from Coinbase: {data.get('message', 'Unknown error')}")
            
        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse message: {e}")
        except Exception as e:
            print(f"❌ Error handling message: {e}")
    
    async def handle_ticker(self, data: Dict):
        """Handle ticker updates (quotes)"""
        symbol = data.get('product_id')
        bid = float(data.get('best_bid', 0))
        ask = float(data.get('best_ask', 0))
        last_price = float(data.get('price', 0))
        timestamp = data.get('time')
        
        # Store last price for display
        self.last_prices[symbol] = {
            'bid': bid,
            'ask': ask,
            'last': last_price,
            'spread': ask - bid if bid and ask else 0,
            'mid': (bid + ask) / 2 if bid and ask else 0,
            'time': timestamp
        }
        
        # Print every 10th ticker update to avoid spam
        if self.message_types.get('ticker', 0) % 10 == 0:
            spread_bps = (ask - bid) / bid * 10000 if bid > 0 else 0
            print(f"📈 {symbol}: Bid: ${bid:,.2f} | Ask: ${ask:,.2f} | "
                  f"Spread: ${ask-bid:.2f} ({spread_bps:.1f} bps) | "
                  f"Mid: ${self.last_prices[symbol]['mid']:,.2f}")
    
    async def handle_match(self, data: Dict):
        """Handle match updates (trades)"""
        symbol = data.get('product_id')
        price = float(data.get('price', 0))
        size = float(data.get('size', 0))
        side = data.get('side')
        trade_id = data.get('trade_id')
        timestamp = data.get('time')
        
        # Calculate trade value
        trade_value = price * size
        
        # Print significant trades (>$10,000)
        if trade_value > 10000:
            emoji = "🟢" if side == 'buy' else "🔴"
            print(f"{emoji} {symbol} Trade: {side.upper()} {size:.4f} @ ${price:,.2f} "
                  f"(${trade_value:,.0f}) - ID: {trade_id}")
    
    async def receive_messages(self):
        """Main loop to receive and process messages"""
        global running
        
        while running and self.ws:
            try:
                # Set timeout to allow checking the running flag
                message = await asyncio.wait_for(
                    self.ws.recv(), 
                    timeout=1.0
                )
                await self.handle_message(message)
                
            except asyncio.TimeoutError:
                # Timeout is normal, just check if we should continue
                continue
            except websockets.exceptions.ConnectionClosed:
                print("📡 WebSocket connection closed")
                break
            except Exception as e:
                print(f"❌ Error receiving message: {e}")
                break
    
    def print_statistics(self):
        """Print connection statistics"""
        runtime = datetime.now() - self.start_time
        
        print("\n" + "="*50)
        print("📊 Connection Statistics:")
        print(f"⏱️  Runtime: {runtime}")
        print(f"📨 Total messages: {self.message_count:,}")
        
        if self.message_count > 0:
            print(f"\n📈 Message breakdown:")
            for msg_type, count in sorted(self.message_types.items(), 
                                         key=lambda x: x[1], reverse=True):
                percentage = (count / self.message_count) * 100
                print(f"   {msg_type}: {count:,} ({percentage:.1f}%)")
        
        if self.last_prices:
            print(f"\n💰 Last prices:")
            for symbol, prices in self.last_prices.items():
                print(f"   {symbol}: ${prices['mid']:,.2f} "
                      f"(Bid: ${prices['bid']:,.2f}, Ask: ${prices['ask']:,.2f})")
        
        if runtime.total_seconds() > 0:
            msg_rate = self.message_count / runtime.total_seconds()
            print(f"\n⚡ Message rate: {msg_rate:.1f} msgs/sec")
        
        print("="*50)
    
    async def disconnect(self):
        """Close WebSocket connection"""
        if self.ws:
            await self.ws.close()
            print("🔌 Disconnected from Coinbase")
    
    async def run(self):
        """Main execution flow"""
        # Connect
        if not await 
        self.connect():
            return
        
        # Subscribe
        if not await self.subscribe():
            await self.disconnect()
            return
        
        print("\n🚀 Receiving real-time data... (Press Ctrl+C to stop)\n")
        
        # Receive messages
        await self.receive_messages()
        
        # Clean up
        await self.disconnect()
        self.print_statistics()

async def main():
    """Entry point"""
    print("="*50)
    print("🚀 Coinbase WebSocket Client - Basic Version")
    print(f"📊 Symbols: {', '.join(SYMBOLS)}")
    print("="*50 + "\n")
    
    # Create and run WebSocket client
    client = CoinbaseWebSocket(SYMBOLS)
    await client.run()
    
    print("\n✅ Program ended successfully")

if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())