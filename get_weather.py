import requests
from bs4 import BeautifulSoup

def parse_weather_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    card = soup.select_one('.current-weather-card')
    if not card:
        return None
    # Thời gian cập nhật
    time = card.select_one('.card-header .sub')
    time_val = time.text.strip() if time else None
    # Nhiệt độ
    temp = card.select_one('.display-temp')
    temp_val = temp.text.strip() if temp else None
    # Mô tả
    phrase = card.select_one('.phrase')
    phrase_val = phrase.text.strip() if phrase else None
    # RealFeel và RealFeel Shade
    realfeel = realfeel_shade = None
    extra = card.select_one('.current-weather-extra')
    if extra:
        realfeel_divs = extra.find_all('div')
        if len(realfeel_divs) > 0:
            realfeel = realfeel_divs[0].get_text(strip=True)
        if len(realfeel_divs) > 1:
            realfeel_shade = realfeel_divs[1].get_text(strip=True)
    # Các chi tiết
    details = {}
    for item in card.select('.current-weather-details .detail-item'):
        label = item.select_one('div:nth-child(1)')
        value = item.select_one('div:nth-child(2)')
        if label and value:
            details[label.text.strip()] = value.text.strip()
    # Trả về dict đầy đủ
    return {
        'time': time_val,
        'temp': temp_val,
        'phrase': phrase_val,
        'realfeel': realfeel,
        'realfeel_shade': realfeel_shade,
        'details': details
    }

def get_weather_by_key(location_key=None, html_path=None):
    """
    If html_path is provided, parse the local HTML file (for testing).
    Otherwise, fetch from AccuWeather using location_key.
    """
    if html_path:
        with open(html_path, encoding='utf-8') as f:
            html = f.read()
        return parse_weather_html(html)
    if not location_key:
        return None
    url = f"https://www.accuweather.com/vi/vn/any/{location_key}/current-weather/{location_key}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:141.0) Gecko/20100101 Firefox/141.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Referer": "https://www.accuweather.com/",
        "Accept-Language": "vi,en-US;q=0.9,en;q=0.8"
    }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return None
    return parse_weather_html(response.text)
