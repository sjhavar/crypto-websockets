# Crypto WebSockets

A Python-based cryptocurrency data collector that supports both REST API and WebSocket connections for real-time market data collection.

## Features

- **REST API Collector**: Synchronous and asynchronous implementations for fetching cryptocurrency data
- **WebSocket Collector**: Real-time data streaming from cryptocurrency exchanges
- **Exchange Support**: Currently supports Coinbase Pro WebSocket feeds
- **Flexible Configuration**: Easy-to-configure system for different exchanges and data types
- **Database Integration**: Supabase integration for data persistence

## Installation

1. Clone the repository:
```bash
git clone https://github.com/sjhavar/crypto-websockets.git
cd crypto-websockets
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
Create a `.env` file in the root directory with your configuration:
```
# Add your environment variables here
```

## Usage

### REST API Collector

Synchronous version:
```python
from collectors.rest_api.collector import collect_data
```

Asynchronous version:
```python
from collectors.rest_api.collector_async import async_collect_data
```

### WebSocket Collector

Run the Coinbase WebSocket collector:
```bash
python collectors/websocket/coinbase_websocket.py
```

Test WebSocket connection:
```bash
python collectors/websocket/test_connection.py
```

### One-time Import

For bulk data import:
```bash
python one_time_import.py
```

## Project Structure

```
crypto-websockets/
├── collectors/
│   ├── rest_api/
│   │   ├── collector.py          # Synchronous REST API collector
│   │   └── collector_async.py    # Asynchronous REST API collector
│   └── websocket/
│       ├── coinbase_websocket.py # Coinbase WebSocket implementation
│       └── test_connection.py    # Connection testing utility
├── config.py                     # Configuration management
├── one_time_import.py           # Bulk import utility
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## Requirements

- Python 3.7+
- See `requirements.txt` for Python package dependencies

## Contributing

Feel free to submit issues and enhancement requests!

## License

[Specify your license here]