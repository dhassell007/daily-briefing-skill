---
name: daily-briefing
description: Generate automated daily market briefings with precious metals spot prices, ETF quotes, Treasury yields, and curated news headlines. Ideal for scheduling via cron or on-demand reporting.
---

# Daily Briefing

## Overview

Fetch and format a comprehensive daily briefing combining:
- **Precious metals** (Gold & Silver spot prices + ratio) - scraped from JM Bullion
- **ETF quotes** (customizable portfolio) - via Alpha Vantage API
- **Treasury yields** (2Y, 10Y, 30Y) - placeholder for now
- **News headlines** from major outlets (NYT, WSJ, BBC, NPR, CNBC, Reuters, Guardian, NBC) - via RSS

Perfect for automated morning/afternoon briefings delivered to Telegram, email, or anywhere you need market awareness.

## Quick Start

### 1. Install Dependencies

```bash
cd ~/.openclaw/workspace/daily-briefing
pip3 install -r requirements.txt
```

The skill requires: `requests`, `pyyaml`

### 2. Configure

```bash
# Copy example files
cp config.example.yaml config.yaml
cp .env.example .env

# Edit config.yaml to choose:
# - Which ETFs to track
# - Which news sources to include
# - How many headlines per source

# Edit .env to add your Alpha Vantage API key
# Get free key at: https://www.alphavantage.co/support/#api-key
```

### 3. Run

```bash
# One-time manual run
./scripts/fetch-briefing.py

# Or use OpenClaw cron scheduling (see Automation section)
```

## Configuration

### `config.yaml`

Customize what's included in your briefing:

```yaml
markets:
  # Precious metals (always included, no API key needed)
  metals:
    - gold
    - silver
  
  # ETFs to track (requires Alpha Vantage API)
  etfs:
    - SPY    # S&P 500
    - QQQ    # Nasdaq-100
    - VOO    # Vanguard S&P 500
    - QQQM   # Nasdaq-100 (lower cost)
  
  # Treasury yields
  bonds:
    - 2Y
    - 10Y
    - 30Y

news:
  sources:
    - NYT       # New York Times
    - WSJ       # Wall Street Journal
    - CNBC      # CNBC
    - Reuters   # Reuters
  
  max_headlines: 5  # Headlines per source
```

### `.env`

Add your Alpha Vantage API key:

```bash
ALPHA_VANTAGE_API_KEY=your_key_here
```

**Get a free key:** https://www.alphavantage.co/support/#api-key

The free tier allows 5 API calls/minute. The script auto-delays 12 seconds between ETF lookups to stay within limits.

## Output Format

Example briefing:

```
📊 DAILY BRIEFING
==================================================

💰 MARKETS
--------------------------------------------------

🥇 Gold: $3,095.00/oz
🥈 Silver: $33.50/oz
📈 Gold/Silver Ratio: 92.39:1

📈 VOO: $524.32 (+2.15, +0.41%)
📉 QQQM: $198.87 (-1.23, -0.61%)

📉 Treasury Yields:
   2Y: N/A
   10Y: N/A
   30Y: N/A

📰 HEADLINES
--------------------------------------------------

**NYT**
  • Breaking: Major climate summit begins in Geneva
  • Tech stocks surge on AI breakthrough
  • Fed signals possible rate cut in June
  ...

--------------------------------------------------
Updated: 2026-04-02 09:00 AM MST
```

## Automation

### Schedule via OpenClaw Cron

Create scheduled briefings delivered to Telegram, email, or any OpenClaw-connected channel:

```bash
# Morning briefing (9 AM ET)
/cron add "0 9 * * *" "Run daily morning briefing" --channel telegram --timezone America/New_York --script ~/.openclaw/workspace/daily-briefing/scripts/fetch-briefing.py

# Afternoon briefing (3:30 PM ET, market close)
/cron add "30 15 * * 1-5" "Run daily afternoon briefing" --channel telegram --timezone America/New_York --script ~/.openclaw/workspace/daily-briefing/scripts/fetch-briefing.py
```

### Direct Cron (Unix/Linux/Mac)

```bash
# Edit crontab
crontab -e

# Add line for 9 AM daily:
0 9 * * * /path/to/daily-briefing/scripts/fetch-briefing.py | telegram-send --stdin
```

## Data Sources

| Component | Source | Rate Limit | API Key Required |
|-----------|--------|------------|------------------|
| Gold/Silver | JM Bullion (scraping) | Reasonable use | ❌ No |
| ETFs | Alpha Vantage API | 5 calls/min (free) | ✅ Yes |
| Bonds | Placeholder (TODO) | N/A | N/A |
| Headlines | RSS feeds | Reasonable use | ❌ No |

## Extending

### Add More ETFs

Edit `config.yaml`:

```yaml
markets:
  etfs:
    - SPY
    - QQQ
    - GLD    # Gold ETF
    - SLV    # Silver ETF
    - TLT    # 20+ Year Treasury Bond
```

### Add More News Sources

The script supports any RSS feed. Edit `scripts/fetch-briefing.py` to add feeds:

```python
feeds = {
    'NYT': 'https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml',
    'YourSource': 'https://example.com/rss.xml'
}
```

Then add `'YourSource'` to `config.yaml`.

### Change Output Format

The `format_briefing()` function in `scripts/fetch-briefing.py` controls formatting. Customize as needed - add emojis, change layouts, reorder sections, etc.

## Troubleshooting

**"No Alpha Vantage API key found"**
- Add your key to `.env` or set `ALPHA_VANTAGE_API_KEY` environment variable

**"Error fetching ETF"**
- Check your API key is valid
- Verify symbol is correct (use ticker symbols like `VOO`, not fund names)
- Free tier has 5 calls/min limit - script auto-delays 12 seconds between calls

**Missing gold/silver prices**
- JM Bullion site may have changed - check network connectivity
- Script scrapes HTML, so site redesigns may break parser

**No headlines from a source**
- RSS feed may be down or changed
- Check network connectivity
- Some sources block automated access - rotate user agents if needed

## License

MIT - Use freely, modify as needed, share with friends! 🦞

---

**Created by:** The Claw  
**For:** David Hassell & friends who want smarter morning briefings  
**Repo:** https://github.com/your-username/daily-briefing-skill
