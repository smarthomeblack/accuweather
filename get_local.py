import requests

def get_location_keys(query=None, html_path=None):
    """
    If html_path is provided, return empty list (for testing placeholder).
    Otherwise, fetch from AccuWeather using query.
    """
    if html_path:
        return []
    if not query:
        return []
    url = "https://www.accuweather.com/web-api/autocomplete"
    params = {
        "query": query,
        "language": "vi"
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:141.0) Gecko/20100101 Firefox/141.0",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Referer": "https://www.accuweather.com/",
        "Accept-Language": "vi,en-US;q=0.9,en;q=0.8"
    }
    response = requests.get(url, params=params, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if data and isinstance(data, list):
            results = []
            for item in data:
                key = item.get("key")
                name = item.get("localizedName")
                long_name = item.get("longName")
                if key and name:
                    results.append((key, name, long_name))
            return results
        else:
            return []
    else:
        return []
