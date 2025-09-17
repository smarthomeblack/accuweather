import requests
from bs4 import BeautifulSoup

def parse_daily_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    daily = []
    for wrapper in soup.select('.daily-wrapper'):
        card = wrapper.select_one('.daily-forecast-card')
        content = wrapper.select_one('.half-day-card-content')
        if not card or not content:
            continue
        # Extract date from two <span> inside <h2 class="date">
        date = None
        date_h2 = card.select_one('.info h2.date')
        if date_h2:
            spans = date_h2.find_all('span')
            if len(spans) >= 2:
                date = f"{spans[0].get_text(strip=True)} {spans[1].get_text(strip=True)}"
        # Fallback: try .date as before
        if not date:
            date_tag = card.select_one('.date')
            date = date_tag.get_text(strip=True) if date_tag else None
        precip = card.select_one('.precip')
        precip_val = None
        if precip:
            # Only get the text node, ignore SVG
            for t in precip.contents:
                if isinstance(t, str) and t.strip():
                    precip_val = t.strip()
                    break
        phrase = content.select_one('.phrase')
        phrase_val = phrase.get_text(strip=True) if phrase else None
        # Extract high/low temp
        high = low = None
        temp = card.select_one('.temp')
        if temp:
            high_span = temp.select_one('.high')
            low_span = temp.select_one('.low')
            high = high_span.get_text(strip=True) if high_span else None
            low = low_span.get_text(strip=True) if low_span else None
        # Extract all details from panels
        details = {}
        for panel in content.select('.panels .left, .panels .right'):
            for p in panel.select('p.panel-item'):
                label = p.contents[0].strip() if p.contents else None
                value = p.select_one('.value')
                if label and value:
                    details[label] = value.text.strip()
        daily.append({
            'date': date,
            'precip': precip_val,
            'phrase': phrase_val,
            'high': high,
            'low': low,
            'details': details
        })
    return daily

def get_daily_forecast_by_key(location_key=None, html_path=None):
    """
    If html_path is provided, parse the local HTML file (for testing).
    Otherwise, fetch from AccuWeather using location_key.
    """
    if html_path:
        with open(html_path, encoding='utf-8') as f:
            html = f.read()
        return parse_daily_html(html)
    if not location_key:
        return []
    url = f"https://www.accuweather.com/vi/vn/any/{location_key}/daily-weather-forecast/{location_key}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:141.0) Gecko/20100101 Firefox/141.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Referer": "https://www.accuweather.com/",
        "Accept-Language": "vi,en-US;q=0.9,en;q=0.8"
    }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return []
    return parse_daily_html(response.text)
