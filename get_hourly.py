import requests
from bs4 import BeautifulSoup

def parse_hourly_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    hourly = []
    for item in soup.select('.accordion-item.hour'):
        hour = item.select_one('.hourly-card-subcontaint .date div')
        temp = item.select_one('.temp.metric')
        realfeel = item.select_one('.real-feel__text')
        phrase = item.select_one('.phrase')
        precip = item.select_one('.precip')
        # Collect all <p> label/value pairs from all .panel blocks in this hour
        details = {}
        for panel in item.select('.panel'):
            for p in panel.select('p'):
                label = p.contents[0].strip() if p.contents else None
                value = p.select_one('.value')
                if label and value:
                    details[label] = value.text.strip()
        # Also collect from all .hourly-content-container .panel blocks
        for content in item.select('.hourly-content-container .panel'):
            for p in content.select('p'):
                label = p.contents[0].strip() if p.contents else None
                value = p.select_one('.value')
                if label and value:
                    details[label] = value.text.strip()
        hourly.append({
            'hour': hour.text.strip() if hour else None,
            'temp': temp.text.strip() if temp else None,
            'realfeel': realfeel.text.strip() if realfeel else None,
            'phrase': phrase.text.strip() if phrase else None,
            'precip': precip.text.strip() if precip else None,
            'details': details
        })
    return hourly

def get_hourly_forecast_by_key(location_key=None, html_path=None):
    """
    If html_path is provided, parse the local HTML file (for testing).
    Otherwise, fetch from AccuWeather using location_key.
    """
    if html_path:
        with open(html_path, encoding='utf-8') as f:
            html = f.read()
        return parse_hourly_html(html)
    if not location_key:
        return []
    url = f"https://www.accuweather.com/vi/vn/any/{location_key}/hourly-weather-forecast/{location_key}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:141.0) Gecko/20100101 Firefox/141.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Referer": "https://www.accuweather.com/",
        "Accept-Language": "vi,en-US;q=0.9,en;q=0.8"
    }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return []
    return parse_hourly_html(response.text)
