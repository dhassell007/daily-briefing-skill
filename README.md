# 📊 Daily Briefing - AgentSkill

**Automated market briefings combining precious metals, ETFs, bonds, and curated news headlines.**

Perfect for morning/afternoon market updates delivered to Telegram, email, or anywhere you need awareness without doomscrolling.

## What's Included

✅ **Precious Metals** - Gold & Silver spot prices + ratio (scraped from JM Bullion, no API needed)  
✅ **ETF Quotes** - Track your portfolio (VOO, QQQ, SPY, etc.) via Alpha Vantage  
✅ **Treasury Yields** - 2Y, 10Y, 30Y bonds (placeholder for now)  
✅ **News Headlines** - NYT, WSJ, BBC, NPR, CNBC, Reuters, Guardian, NBC (via RSS)  
✅ **Customizable** - Choose which ETFs, sources, and headline counts  
✅ **Schedulable** - Run via OpenClaw cron or system cron for automated delivery

## Quick Start

```bash
# 1. Clone or install via ClawHub
clawhub install daily-briefing

# 2. Navigate to skill directory
cd ~/.openclaw/workspace/daily-briefing

# 3. Install dependencies
pip3 install -r requirements.txt

# 4. Configure
cp config.example.yaml config.yaml
cp .env.example .env

# Edit config.yaml to choose your ETFs and news sources
# Edit .env to add your Alpha Vantage API key (free at https://www.alphavantage.co)

# 5. Test run
./scripts/fetch-briefing.py

# 6. Schedule it (via OpenClaw)
/cron add "0 9 * * *" "Morning briefing" --channel telegram --script ~/.openclaw/workspace/daily-briefing/scripts/fetch-briefing.py
```

## Example Output

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

📰 HEADLINES
--------------------------------------------------

**NYT**
  • Breaking: Major climate summit begins in Geneva
  • Tech stocks surge on AI breakthrough
  
**CNBC**
  • S&P 500 hits new all-time high
  • Fed signals possible rate cut
  
--------------------------------------------------
Updated: 2026-04-02 09:00 AM MST
```

## Configuration

### Choose Your ETFs

Edit `config.yaml`:

```yaml
markets:
  etfs:
    - VOO    # Vanguard S&P 500
    - QQQM   # Invesco Nasdaq-100
    - GLD    # Gold ETF
    - TLT    # Long-term Treasury
```

### Choose Your News Sources

```yaml
news:
  sources:
    - NYT       # New York Times
    - WSJ       # Wall Street Journal
    - CNBC      # CNBC
    - Reuters   # Reuters
  
  max_headlines: 5  # Per source
```

### Add Your API Key

Get a free Alpha Vantage key: https://www.alphavantage.co/support/#api-key

Add to `.env`:
```bash
ALPHA_VANTAGE_API_KEY=your_key_here
```

## Scheduling

### OpenClaw Cron (Recommended)

```bash
# Morning briefing at 9 AM ET
/cron add "0 9 * * *" "Morning briefing" \
  --channel telegram \
  --timezone America/New_York \
  --script ~/.openclaw/workspace/daily-briefing/scripts/fetch-briefing.py

# Afternoon briefing at 3:30 PM ET (market close), weekdays only
/cron add "30 15 * * 1-5" "Afternoon briefing" \
  --channel telegram \
  --timezone America/New_York \
  --script ~/.openclaw/workspace/daily-briefing/scripts/fetch-briefing.py
```

### System Cron

```bash
crontab -e

# Add:
0 9 * * * /path/to/daily-briefing/scripts/fetch-briefing.py | telegram-send --stdin
```

## Requirements

- **Python 3.7+**
- **Dependencies:** `requests`, `pyyaml` (see `requirements.txt`)
- **Alpha Vantage API key** (free tier: 5 calls/min, 500/day)

## Data Sources

| Component | Source | API Key? |
|-----------|--------|----------|
| Gold/Silver | JM Bullion (scraping) | ❌ No |
| ETFs | Alpha Vantage | ✅ Yes (free) |
| Bonds | Placeholder (TODO) | N/A |
| Headlines | RSS feeds | ❌ No |

## Customization

- **Add more ETFs** - Edit `config.yaml`
- **Change news sources** - Add RSS feeds to `scripts/fetch-briefing.py`
- **Adjust formatting** - Edit `format_briefing()` function
- **Add oil prices** - Integrate commodity API of choice
- **Add crypto** - Use CoinGecko or similar API

## Use Cases

✅ Morning market awareness without opening 10 tabs  
✅ Pre-market briefing before trading  
✅ Afternoon recap after market close  
✅ Weekend catch-up (headlines only, markets closed)  
✅ Shared briefings for family/friends/team  

## License

MIT - Use freely, modify as needed, share with friends!

---

**Created by:** The Claw 🦞  
**For:** Anyone who wants smarter briefings without the noise  
**Repo:** https://github.com/your-username/daily-briefing-skill  
**Skill Directory:** Compatible with ClawHub - install with `clawhub install daily-briefing`
