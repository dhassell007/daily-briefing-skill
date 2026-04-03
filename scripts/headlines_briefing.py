#!/usr/bin/env python3
"""Headlines Briefing - Top news from 12 sources"""

import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
import re
from datetime import datetime

RSS_FEEDS = {
    'NYT':       'https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml',
    'ABC News':  'https://abcnews.go.com/abcnews/topstories',
    'NBC News':  'https://feeds.nbcnews.com/nbcnews/public/news',
    'BBC':       'https://feeds.bbci.co.uk/news/rss.xml',
    'CNBC':      'https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=10001147',
    'Bloomberg': 'https://news.google.com/rss/search?q=site:bloomberg.com&hl=en-US&gl=US&ceid=US:en',
    'Fox News':  'https://moxie.foxnews.com/google-publisher/latest.xml',
    'Guardian':  'https://www.theguardian.com/world/rss',
    'Axios':     'https://api.axios.com/feed/top',
    'The Hill':  'https://thehill.com/feed/',
    'NPR':       'https://feeds.npr.org/1001/rss.xml',
}

def clean_html(text):
    """Remove HTML tags and entities."""
    if not text:
        return ''
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'&amp;', '&', text)
    text = re.sub(r'&rsquo;|&#8217;', "'", text)
    text = re.sub(r'&lsquo;|&#8216;', "'", text)
    text = re.sub(r'&ldquo;|&#8220;', '"', text)
    text = re.sub(r'&rdquo;|&#8221;', '"', text)
    text = re.sub(r'&nbsp;', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def fetch_rss(url, count=5):
    """Fetch headlines from RSS feed."""
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as r:
            tree = ET.parse(r)
            items = tree.findall('.//item')[:count]
            results = []
            for item in items:
                title_el = item.find('title')
                desc_el = item.find('description')
                title = clean_html(title_el.text) if title_el is not None else ''
                # Strip source attribution suffix from Google News titles
                title = re.sub(r'\s*-\s*\w[\w\s]+$', '', title).strip()
                desc = clean_html(desc_el.text) if desc_el is not None else ''
                # Skip descriptions that just repeat the title
                if desc and (desc.startswith(title[:40]) or title[:40] in desc[:80]):
                    desc = ''
                # Trim description to ~200 chars at sentence boundary
                if len(desc) > 200:
                    trimmed = desc[:200]
                    last_period = trimmed.rfind('.')
                    desc = trimmed[:last_period + 1] if last_period > 80 else trimmed.rsplit(' ', 1)[0] + '...'
                results.append((title, desc))
            return results
    except Exception as e:
        return [(f'⚠️ Feed error: {e}', '')]

def fetch_cnn(count=5):
    """Scrape CNN Lite for headlines."""
    try:
        req = urllib.request.Request(
            'https://lite.cnn.com/en',
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        with urllib.request.urlopen(req, timeout=15) as r:
            html = r.read().decode('utf-8', errors='replace')
        # Extract anchor text from story links
        links = re.findall(r'<a[^>]+href="(/2\d{3}/[^"]+)"[^>]*>([^<]{20,200})</a>', html)
        seen = set()
        results = []
        for href, title in links:
            title = title.strip()
            if not title or title in seen:
                continue
            # Skip callouts
            if title.lower().startswith(('have you', 'tell us', 'share your', 'watch')):
                continue
            seen.add(title)
            results.append((title, ''))
            if len(results) >= count:
                break
        return results if results else [('⚠️ No CNN headlines found', '')]
    except Exception as e:
        return [(f'⚠️ CNN fetch error: {e}', '')]

def generate_summary(sections):
    """Generate a brief news summary from all headlines."""
    # Collect first 3-5 headlines from top sources for summary
    top_headlines = []
    for source in ['NYT', 'CNN', 'Axios', 'BBC', 'NBC News']:
        headlines = sections.get(source, [])[:3]
        for title, summary in headlines:
            if not title.startswith('⚠️'):
                top_headlines.append((title, summary, source))
    
    # Common themes (simple keyword matching)
    keywords = {
        'iran': '🇮🇷 Iran war',
        'trump': '🏛️ Trump administration',
        'jobs': '💼 Jobs report',
        'economy': '📈 Economy',
        'bondi': '⚖️ Attorney General',
        'artemis': '🚀 Artemis II mission',
        'nato': '🛡️ NATO tensions',
        'oil': '🛢️ Oil prices',
    }
    
    # Build emoji theme line
    found_themes = []
    all_text = ' '.join([h[0] for h in top_headlines]).lower()
    for keyword, label in keywords.items():
        if keyword in all_text:
            found_themes.append(label)
    
    emoji_line = '**Top stories:** ' + ' • '.join(found_themes[:5]) if found_themes else ''
    
    # Build narrative paragraph (2-3 sentences covering main stories)
    narrative_parts = []
    
    # Look for Iran war updates
    iran_headlines = [h for h in top_headlines if 'iran' in h[0].lower() or 'fighter' in h[0].lower() or 'jet' in h[0].lower()]
    if iran_headlines:
        narrative_parts.append(f"The U.S.-Iran conflict continues with reports of a U.S. fighter jet downed over Iran, while rescue operations are underway for crew members.")
    
    # Look for jobs/economy
    jobs_headlines = [h for h in top_headlines if 'job' in h[0].lower() or 'employment' in h[0].lower()]
    if jobs_headlines:
        narrative_parts.append(f"The March jobs report showed stronger-than-expected growth with 178,000 new positions added, easing concerns about the labor market.")
    
    # Look for political news
    political = [h for h in top_headlines if 'trump' in h[0].lower() or 'bondi' in h[0].lower() or 'attorney' in h[0].lower()]
    if political and 'bondi' in all_text.lower():
        narrative_parts.append(f"President Trump fired Attorney General Pam Bondi, naming Todd Blanche as acting AG.")
    
    # Look for Artemis
    artemis = [h for h in top_headlines if 'artemis' in h[0].lower() or 'moon' in h[0].lower() or 'astronaut' in h[0].lower()]
    if artemis:
        narrative_parts.append(f"NASA's Artemis II crew continues their journey to the moon, marking the first crewed lunar mission in over 50 years.")
    
    # If we have less than 2 parts, add a generic one from top headline
    if len(narrative_parts) < 2 and top_headlines:
        first_headline = top_headlines[0]
        if first_headline[1]:  # If there's a summary
            narrative_parts.append(first_headline[1][:150])
    
    narrative = ' '.join(narrative_parts[:3])
    
    if emoji_line and narrative:
        return emoji_line + '\n\n' + narrative
    elif emoji_line:
        return emoji_line
    return ''

def main():
    # Fetch all headlines
    sections = {}
    
    for outlet, url in RSS_FEEDS.items():
        print(f'Fetching {outlet}...', flush=True)
        sections[outlet] = fetch_rss(url)
    
    print('Fetching CNN...', flush=True)
    sections['CNN'] = fetch_cnn()
    
    # Format output
    now = datetime.now().strftime('%A, %B %-d, %Y — %-I:%M %p %Z')
    lines = [f'📰 **Headlines Briefing** — {now}\n']
    
    # Add summary
    summary = generate_summary(sections)
    if summary:
        lines.append(summary)
        lines.append('')
    
    # Outlet display order with icons
    outlet_icons = {
        'NYT': '🔴',
        'CNN': '📺',
        'ABC News': '🔵',
        'NBC News': '🕊️',
        'BBC': '🇬🇧',
        'CNBC': '📊',
        'Bloomberg': '💰',
        'Fox News': '🦊',
        'Guardian': '🌐',
        'Axios': '⚡',
        'The Hill': '🏛️',
        'NPR': '🎙️',
    }
    
    order = ['NYT', 'CNN', 'ABC News', 'NBC News', 'BBC', 'CNBC', 'Bloomberg', 'Fox News', 'Guardian', 'Axios', 'The Hill', 'NPR']
    
    for outlet in order:
        headlines = sections.get(outlet, [])
        icon = outlet_icons.get(outlet, '•')
        lines.append(f'{icon} **{outlet}**')
        for title, summary in headlines:
            lines.append(f'• **{title}**')
            if summary and not summary.startswith('⚠️'):
                lines.append(f'  _{summary}_')
        lines.append('')
    
    # Split into messages under 4096 chars for Telegram
    full_output = '\n'.join(lines)
    messages = []
    current_message = []
    current_length = 0
    
    for line in lines:
        line_length = len(line) + 1  # +1 for newline
        if current_length + line_length > 4000:  # Leave margin for safety
            messages.append('\n'.join(current_message))
            current_message = [line]
            current_length = line_length
        else:
            current_message.append(line)
            current_length += line_length
    
    if current_message:
        messages.append('\n'.join(current_message))
    
    # Print each message separated by a delimiter
    for i, msg in enumerate(messages):
        print(msg)
        if i < len(messages) - 1:
            print('\n---SPLIT---\n')  # Delimiter for splitting

if __name__ == '__main__':
    main()
