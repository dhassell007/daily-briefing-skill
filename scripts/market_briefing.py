#!/usr/bin/env python3
"""Market Briefing - Gold, Silver, ETFs, Oil, Bonds"""

import urllib.request
import json
import re
import time
from datetime import datetime

API_KEY = '67IWYBPBHFQULB2B'

def fetch_spot_metals():
    """Fetch gold and silver spot prices from JM Bullion."""
    try:
        req = urllib.request.Request(
            'https://www.jmbullion.com/charts/gold-price/',
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        with urllib.request.urlopen(req, timeout=30) as r:
            html = r.read().decode('utf-8')
        
        # Extract prices from data-price attributes
        prices = re.findall(r'data-price="([0-9.]+)"', html)
        
        if len(prices) >= 2:
            gold = float(prices[0])
            silver = float(prices[1])
            ratio = gold / silver
            return {
                'Gold (spot)': {'price': gold},
                'Silver (spot)': {'price': silver},
                'Au/Ag Ratio': {'ratio': ratio}
            }
    except Exception as e:
        print(f'⚠️ Metals fetch error: {e}')
    
    return {}

def fetch_etf(symbol):
    """Fetch ETF quote from Alpha Vantage."""
    try:
        url = f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={API_KEY}'
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read().decode('utf-8'))
        
        quote = data.get('Global Quote', {})
        if quote:
            return {
                'price': float(quote.get('05. price', 0)),
                'change': float(quote.get('09. change', 0)),
                'change_pct': float(quote.get('10. change percent', '0%').rstrip('%'))
            }
    except Exception as e:
        print(f'⚠️ {symbol} fetch error: {e}')
    
    return None

def fetch_commodity(symbol, name):
    """Fetch commodity price from Alpha Vantage."""
    try:
        url = f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={API_KEY}'
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read().decode('utf-8'))
        
        quote = data.get('Global Quote', {})
        if quote:
            return {name: {'price': float(quote.get('05. price', 0))}}
    except Exception as e:
        print(f'⚠️ {name} fetch error: {e}')
    
    return {}

def fetch_treasury(maturity, name):
    """Fetch Treasury yield for a specific maturity."""
    try:
        url = f'https://www.alphavantage.co/query?function=TREASURY_YIELD&interval=daily&maturity={maturity}&apikey={API_KEY}'
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read().decode('utf-8'))
        
        ts = data.get('data', [])
        if ts:
            yield_val = float(ts[0].get('value', 0))
            return {name: {'yield': yield_val}}
    except Exception as e:
        print(f'⚠️ {name} fetch error: {e}')
    
    return {}

def main():
    results = {}
    
    # Fetch spot metals (no API key needed, instant)
    print('Fetching gold/silver...', flush=True)
    results.update(fetch_spot_metals())
    
    # Fetch ETFs (12-second delay between calls for rate limiting)
    for symbol in ['VOO', 'QQQM']:
        print(f'Fetching {symbol}...', flush=True)
        data = fetch_etf(symbol)
        if data:
            results[symbol] = data
        time.sleep(12)  # Alpha Vantage free tier: 5 calls/min
    
    # Fetch oil prices
    print('Fetching WTI crude...', flush=True)
    results.update(fetch_commodity('CL=F', 'WTI Crude'))
    time.sleep(12)
    
    print('Fetching Brent crude...', flush=True)
    results.update(fetch_commodity('BZ=F', 'Brent Crude'))
    time.sleep(12)
    
    # Fetch Treasury yields (2Y, 5Y, 10Y, 30Y)
    treasuries = [
        ('2year', '2Y Treasury'),
        ('5year', '5Y Treasury'),
        ('10year', '10Y Treasury'),
        ('30year', '30Y Treasury')
    ]
    
    for maturity, name in treasuries:
        print(f'Fetching {name}...', flush=True)
        results.update(fetch_treasury(maturity, name))
        time.sleep(12)
    
    # Format output
    now = datetime.now().strftime('%A, %B %-d, %Y — %-I:%M %p %Z')
    lines = [f'📊 **Market Briefing** — {now}\n']
    
    # Display order
    display_order = [
        'Gold (spot)', 'Silver (spot)', 'Au/Ag Ratio',
        'VOO', 'QQQM',
        'WTI Crude', 'Brent Crude',
        '2Y Treasury', '5Y Treasury', '10Y Treasury', '30Y Treasury'
    ]
    
    for name in display_order:
        if name not in results:
            continue
        
        data = results[name]
        
        if 'ratio' in data:
            lines.append(f'• {name}: **{data["ratio"]:.2f}:1**')
        elif 'yield' in data:
            lines.append(f'• {name}: **{data["yield"]:.2f}%**')
        elif 'change' in data:
            # ETFs with change data
            price = data['price']
            change = data['change']
            change_pct = data['change_pct']
            arrow = '🟢' if change >= 0 else '🔴'
            sign = '+' if change >= 0 else ''
            lines.append(f'• {name}: **${price:,.2f}** {arrow} {sign}{change:.2f} ({sign}{change_pct:.2f}%)')
        else:
            # Commodities without change data
            price = data['price']
            lines.append(f'• {name}: **${price:,.2f}**')
    
    print('\n'.join(lines))

if __name__ == '__main__':
    main()
