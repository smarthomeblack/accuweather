import requests
import re
import json

def parse_health_html(html):
    m = re.search(r"var indexListData\s*=\s*(\[.*?\]);", html, re.DOTALL)
    if not m:
        return []
    try:
        data = json.loads(m.group(1))
    except Exception:
        return []
    result = []
    for item in data:
        result.append({
            'name': item.get('name'),
            'localizedName': item.get('localizedName'),
            'value': item.get('value'),
            'category': item.get('category'),
            'localizedCategory': item.get('localizedCategory'),
            'categoryPhrase': item.get('categoryPhrase'),
            'categoryValue': item.get('categoryValue'),
            'statusColor': item.get('statusColor'),
            'type': item.get('type'),
            'slug': item.get('slug'),
            'indexDate': item.get('indexDate')
        })
    return result

def get_health_activities_by_key(location_key=None, html_path=None):
    """
    If html_path is provided, parse the local HTML file (for testing).
    Otherwise, fetch from AccuWeather using location_key.
    """
    if html_path:
        with open(html_path, encoding='utf-8') as f:
            html = f.read()
        return parse_health_html(html)
    if not location_key:
        return []
    url = f"https://www.accuweather.com/vi/vn/any/{location_key}/health-activities/{location_key}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:141.0) Gecko/20100101 Firefox/141.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Referer": "https://www.accuweather.com/",
        "Accept-Language": "vi,en-US;q=0.9,en;q=0.8"
    }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return []
    return parse_health_html(response.text)

def crawl_all_health_activities_by_key(location_key=None, html_path_dict=None):
    """
    If html_path_dict is provided, it should be a dict {slug: html_path} for testing.
    Otherwise, fetch from AccuWeather using location_key.
    """
    group_slugs = [
        'allergies', 'outdoor', 'travel', 'home-garden', 'pests', 'entertainment'
    ]
    slug_to_group = {
        'allergies': 'allergy_health',
        'outdoor': 'outdoor',
        'travel': 'travel',
        'home-garden': 'home_garden',
        'pests': 'pests',
        'entertainment': 'entertainment',
    }
    groups = {
        'allergy_health': [],
        'outdoor': [],
        'travel': [],
        'home_garden': [],
        'pests': [],
        'entertainment': [],
        'other': []
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:141.0) Gecko/20100101 Firefox/141.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Referer": "https://www.accuweather.com/",
        "Accept-Language": "vi,en-US;q=0.9,en;q=0.8"
    }
    for slug in group_slugs:
        if html_path_dict and slug in html_path_dict:
            with open(html_path_dict[slug], encoding='utf-8') as f:
                html = f.read()
            data = parse_health_html(html)
            group_name = slug_to_group.get(slug, 'other')
            groups[group_name].extend(data)
            continue
        if not location_key:
            continue
        url = f"https://www.accuweather.com/vi/vn/any/{location_key}/{slug}-weather/{location_key}"
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            if resp.status_code != 200:
                continue
            data = parse_health_html(resp.text)
            group_name = slug_to_group.get(slug, 'other')
            groups[group_name].extend(data)
        except Exception as e:
            print(f"Error crawl {slug}: {e}")
    return groups
