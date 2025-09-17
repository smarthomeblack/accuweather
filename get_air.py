import requests
from bs4 import BeautifulSoup
import re

def parse_air_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    aqi_cat = soup.select_one('.air-quality-card .category')
    aqi_desc = soup.select_one('.air-quality-card .statement')
    pollutants = {}
    for pol in soup.select('.air-quality-pollutant'):
        qa = pol.get('data-qa', '')
        name = qa.replace('airQualityPollutant', '') if qa else None
        aqi = None
        value = None
        unit = None
        aqi_el = pol.select('h3.column')
        if aqi_el and len(aqi_el) > 0:
            aqi = aqi_el[0].get_text(strip=True)
        pol_text = pol.get_text(separator=' ', strip=True)
        m = re.search(r"([\d.,]+)\s*(µg/m³|mg/m³|ppm|ppb|μg/m³|mg/m3|µg/m3|%)", pol_text)
        if m:
            value = m.group(1)
            unit = m.group(2)
        if name:
            pollutants[name] = {'aqi': aqi, 'value': value, 'unit': unit}
    return {
        'category': aqi_cat.get_text(strip=True) if aqi_cat else None,
        'desc': aqi_desc.get_text(strip=True) if aqi_desc else None,
        'pollutants': pollutants
    }

def get_air_quality_by_key(location_key=None, html_path=None):
    """
    If html_path is provided, parse the local HTML file (for testing).
    Otherwise, fetch from AccuWeather using location_key.
    """
    if html_path:
        with open(html_path, encoding='utf-8') as f:
            html = f.read()
        return parse_air_html(html)
    if not location_key:
        return {'category': None, 'desc': None, 'pollutants': {}}
    url = f"https://www.accuweather.com/vi/vn/any/{location_key}/air-quality-index/{location_key}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:141.0) Gecko/20100101 Firefox/141.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Referer": "https://www.accuweather.com/",
        "Accept-Language": "vi,en-US;q=0.9,en;q=0.8"
    }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return {'category': None, 'desc': None, 'pollutants': {}}
    return parse_air_html(response.text)
