#!/usr/bin/env python3
"""
Daily Briefing - Fetch markets and headlines
Combines precious metals, ETFs, bonds, and news headlines into one report
"""

import os
import sys
import json
import time
import requests
from datetime import datetime
from pathlib import Path
import yaml

# Get script directory
SCRIPT_DIR = Path(__file__).parent
SKILL_DIR = SCRIPT_DIR.parent

def load_config():
    """Load configuration from config.yaml"""
    config_path = SKILL_DIR / "config.yaml"
    if not config_path.exists():
        config_path = SKILL_DIR / "config.example.yaml"
    
    with open(config_path) as f:
        return yaml.safe_load(f)

def load_env():
    """Load environment variables from .env file"""
    env_path = SKILL_DIR / ".env"
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value

def fetch_metals():
    """Fetch gold and silver spot prices from JM Bullion"""
    try:
        response = requests.get(
            'https://www.jmbullion.com/charts/gold-price/',
            headers={'User-Agent': 'Mozilla/5.0'},
            timeout=30
        )
        response.raise_for_status()
        
        # Extract prices using regex
        import re
        prices = re.findall(r'data-price="([0-9.]+)"', response.text)[:2]
        
        if len(prices) >= 2:
            gold = float(prices[0])
            silver = float(prices[1])
            ratio = gold / silver if silver > 0 else 0
            
            return {
                'gold': gold,
                'silver': silver,
                'ratio': round(ratio, 2)
            }
    except Exception as e:
        print(f"Error fetching metals: {e}", file=sys.stderr)
    
    return None

def fetch_etf(symbol, api_key, delay=12):
    """Fetch ETF quote from Alpha Vantage"""
    try:
        time.sleep(delay)  # Rate limiting
        
        url = 'https://www.alphavantage.co/query'
        params = {
            'function': 'GLOBAL_QUOTE',
            'symbol': symbol,
            'apikey': api_key
        }
        
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        if 'Global Quote' in data and data['Global Quote']:
            quote = data['Global Quote']
            return {
                'symbol': symbol,
                'price': float(quote.get('05. price', 0)),
                'change': float(quote.get('09. change', 0)),
                'change_percent': quote.get('10. change percent', '0%').rstrip('%')
            }
    except Exception as e:
        print(f"Error fetching {symbol}: {e}", file=sys.stderr)
    
    return None

def fetch_treasury_yields():
    """Fetch Treasury yields - placeholder for now"""
    # TODO: Find reliable source for Treasury yields
    # For now, return placeholder data
    return {
        '2Y': 'N/A',
        '5Y': 'N/A',
        '10Y': 'N/A',
        '30Y': 'N/A'
    }

def fetch_headlines(sources, max_per_source=5):
    """Fetch headlines from news sources using RSS feeds"""
    headlines = {}
    
    # RSS feed URLs for each source
    feeds = {
        'NYT': 'https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml',
        'WSJ': 'https://feeds.a.dj.com/rss/RSSWorldNews.xml',
        'BBC': 'http://feeds.bbci.co.uk/news/rss.xml',
        'NPR': 'https://feeds.npr.org/1001/rss.xml',
        'CNBC': 'https://www.cnbc.com/id/100003114/device/rss/rss.html',
        'Reuters': 'https://www.reutersagency.com/feed/?taxonomy=best-topics&post_type=best',
        'Guardian': 'https://www.theguardian.com/world/rss',
        'NBC': 'https://feeds.nbcnews.com/nbcnews/public/news'
    }
    
    for source in sources:
        if source not in feeds:
            continue
            
        try:
            response = requests.get(feeds[source], timeout=10)
            response.raise_for_status()
            
            # Parse RSS feed
            import xml.etree.ElementTree as ET
            root = ET.fromstring(response.content)
            
            items = []
            for item in root.findall('.//item')[:max_per_source]:
                title = item.find('title')
                if title is not None and title.text:
                    items.append(title.text.strip())
            
            if items:
                headlines[source] = items
                
        except Exception as e:
            print(f"Error fetching {source} headlines: {e}", file=sys.stderr)
    
    return headlines

def format_briefing(data):
    """Format all data into a readable briefing"""
    lines = []
    lines.append("📊 DAILY BRIEFING")
    lines.append("=" * 50)
    lines.append("")
    
    # Markets section
    lines.append("💰 MARKETS")
    lines.append("-" * 50)
    lines.append("")
    
    # Metals
    if data.get('metals'):
        m = data['metals']
        lines.append(f"🥇 Gold: ${m['gold']:,.2f}/oz")
        lines.append(f"🥈 Silver: ${m['silver']:,.2f}/oz")
        lines.append(f"📈 Gold/Silver Ratio: {m['ratio']}:1")
        lines.append("")
    
    # ETFs
    if data.get('etfs'):
        for etf in data['etfs']:
            change_symbol = "📈" if etf['change'] >= 0 else "📉"
            lines.append(
                f"{change_symbol} {etf['symbol']}: ${etf['price']:.2f} "
                f"({etf['change']:+.2f}, {etf['change_percent']:+}%)"
            )
        lines.append("")
    
    # Bonds
    if data.get('bonds'):
        lines.append("📉 Treasury Yields:")
        for period, yield_val in data['bonds'].items():
            lines.append(f"   {period}: {yield_val}")
        lines.append("")
    
    # Headlines section
    if data.get('headlines'):
        lines.append("📰 HEADLINES")
        lines.append("-" * 50)
        lines.append("")
        
        for source, items in data['headlines'].items():
            lines.append(f"**{source}**")
            for item in items:
                lines.append(f"  • {item}")
            lines.append("")
    
    # Footer
    lines.append("-" * 50)
    lines.append(f"Updated: {datetime.now().strftime('%Y-%m-%d %I:%M %p %Z')}")
    
    return "\n".join(lines)

def main():
    """Main execution"""
    # Load configuration
    load_env()
    config = load_config()
    
    # Get API key
    api_key = os.environ.get('ALPHA_VANTAGE_API_KEY')
    if not api_key and config.get('api', {}).get('alpha_vantage', {}).get('key'):
        api_key = config['api']['alpha_vantage']['key']
    
    if not api_key:
        print("Warning: No Alpha Vantage API key found. ETF data will be skipped.", file=sys.stderr)
        print("Set ALPHA_VANTAGE_API_KEY environment variable or add to config.yaml", file=sys.stderr)
    
    # Collect all data
    data = {}
    
    # Fetch metals
    print("Fetching precious metals prices...", file=sys.stderr)
    data['metals'] = fetch_metals()
    
    # Fetch ETFs
    if api_key and config.get('markets', {}).get('etfs'):
        data['etfs'] = []
        delay = config.get('api', {}).get('alpha_vantage', {}).get('rate_limit_delay', 12)
        
        for symbol in config['markets']['etfs']:
            print(f"Fetching {symbol}...", file=sys.stderr)
            etf_data = fetch_etf(symbol, api_key, delay)
            if etf_data:
                data['etfs'].append(etf_data)
    
    # Fetch bond yields
    if config.get('markets', {}).get('bonds'):
        print("Fetching Treasury yields...", file=sys.stderr)
        all_yields = fetch_treasury_yields()
        data['bonds'] = {k: all_yields.get(k, 'N/A') for k in config['markets']['bonds']}
    
    # Fetch headlines
    if config.get('news', {}).get('sources'):
        print("Fetching headlines...", file=sys.stderr)
        max_headlines = config.get('news', {}).get('max_headlines', 5)
        data['headlines'] = fetch_headlines(config['news']['sources'], max_headlines)
    
    # Format and output
    briefing = format_briefing(data)
    print(briefing)
    
    # Also output as JSON for programmatic use
    json_output = {
        'timestamp': datetime.now().isoformat(),
        'data': data,
        'formatted': briefing
    }
    
    json_file = SKILL_DIR / 'last-briefing.json'
    with open(json_file, 'w') as f:
        json.dump(json_output, f, indent=2)

if __name__ == '__main__':
    main()
