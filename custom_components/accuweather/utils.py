"""Utility functions for AccuWeather integration."""
from __future__ import annotations

import asyncio
import logging
import re
from typing import Any

import aiohttp
from bs4 import BeautifulSoup

from .const import AUTOCOMPLETE_URL, BASE_URL, CONDITION_MAP, CONDITION_MAP_VI

_LOGGER = logging.getLogger(__name__)


def get_headers() -> dict[str, str]:
    """Get default headers for requests."""
    return {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:141.0) Gecko/20100101 Firefox/141.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Referer": "https://www.accuweather.com/",
        "Accept-Language": "vi,en-US;q=0.9,en;q=0.8"
    }


async def get_location_keys(session: aiohttp.ClientSession, query: str) -> list[tuple[str, str, str]]:
    """Get location keys from AccuWeather."""
    params = {
        "query": query,
        "language": "vi"
    }
    headers = get_headers()
    headers["Accept"] = "application/json, text/javascript, */*; q=0.01"
    
    try:
        async with session.get(AUTOCOMPLETE_URL, params=params, headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                if data and isinstance(data, list):
                    results = []
                    for item in data:
                        key = item.get("key")
                        name = item.get("localizedName") 
                        long_name = item.get("longName")
                        if key and name:
                            results.append((key, name, long_name))
                    return results
    except Exception as e:
        _LOGGER.error("Error getting location keys: %s", e)
    
    return []


def extract_numeric_value(text: str) -> float | None:
    """Extract numeric value from text."""
    if not text:
        return None
    
    # Remove special characters and get numbers
    match = re.search(r"([\d.,]+)", str(text).replace("°", "").replace("%", ""))
    if match:
        try:
            return float(match.group(1).replace(",", "."))
        except ValueError:
            pass
    return None


def extract_wind_info(wind_text: str) -> tuple[float | None, str | None]:
    """Extract wind speed and direction from text."""
    if not wind_text:
        return None, None
    
    # Extract speed (km/h, m/s, etc)
    speed_match = re.search(r"([\d.,]+)\s*(km/h|m/s|mph)", wind_text)
    speed = None
    if speed_match:
        try:
            speed = float(speed_match.group(1).replace(",", "."))
        except ValueError:
            pass
    
    # Extract direction
    direction_match = re.search(r"([NSEW]{1,3}|[BTĐN]{1,3})", wind_text)
    direction = direction_match.group(1) if direction_match else None
    
    return speed, direction


def convert_temp_to_numeric(temp_text: str) -> float | None:
    """Convert temperature text to numeric value."""
    if not temp_text:
        return None
    
    # Extract number from temperature string  
    match = re.search(r"(-?[\d.,]+)", str(temp_text))
    if match:
        try:
            return float(match.group(1).replace(",", "."))
        except ValueError:
            pass
    return None


def map_condition_to_ha(condition: str) -> str:
    """Map AccuWeather condition to Home Assistant condition."""
    if not condition:
        return "unknown"
    
    condition_lower = condition.lower().strip()
    
    # Try Vietnamese mapping first
    for vi_condition, ha_condition in CONDITION_MAP_VI.items():
        if vi_condition in condition_lower:
            return ha_condition
    
    # Try English mapping
    for en_condition, ha_condition in CONDITION_MAP.items():
        if en_condition in condition_lower:
            return ha_condition
    
    # Default fallback
    if "mưa" in condition_lower or "rain" in condition_lower:
        return "rainy"
    elif "mây" in condition_lower or "cloud" in condition_lower:
        return "cloudy"
    elif "nắng" in condition_lower or "sun" in condition_lower:
        return "sunny"
    elif "gió" in condition_lower or "wind" in condition_lower:
        return "windy"
    
    return "unknown"


async def parse_weather_html(html: str) -> dict[str, Any] | None:
    """Parse current weather HTML (converted from get_weather.py)."""
    try:
        soup = BeautifulSoup(html, 'html.parser')
        card = soup.select_one('.current-weather-card')
        if not card:
            return None
        
        # Time
        time_element = card.select_one('.card-header .sub')
        time_val = time_element.text.strip() if time_element else None
        
        # Temperature
        temp_element = card.select_one('.display-temp')
        temp_val = temp_element.text.strip() if temp_element else None
        temp_numeric = convert_temp_to_numeric(temp_val) if temp_val else None
        
        # Weather phrase/condition
        phrase_element = card.select_one('.phrase')
        phrase_val = phrase_element.text.strip() if phrase_element else None
        condition = map_condition_to_ha(phrase_val)
        
        # RealFeel
        realfeel = realfeel_shade = None
        extra = card.select_one('.current-weather-extra')
        if extra:
            realfeel_divs = extra.find_all('div')
            if len(realfeel_divs) > 0:
                realfeel = realfeel_divs[0].get_text(strip=True)
            if len(realfeel_divs) > 1:
                realfeel_shade = realfeel_divs[1].get_text(strip=True)
        
        # Details
        details = {}
        for item in card.select('.current-weather-details .detail-item'):
            label = item.select_one('div:nth-child(1)')
            value = item.select_one('div:nth-child(2)')
            if label and value:
                details[label.text.strip()] = value.text.strip()
        
        return {
            'time': time_val,
            'temperature': temp_numeric,
            'temperature_unit': '°C',
            'condition': condition,
            'phrase': phrase_val,
            'realfeel': realfeel,
            'realfeel_shade': realfeel_shade,
            'humidity': extract_numeric_value(details.get('Độ ẩm')),
            'pressure': extract_numeric_value(details.get('Khí áp')),
            'wind_speed': extract_wind_info(details.get('Gió', ''))[0],
            'wind_bearing': extract_wind_info(details.get('Gió', ''))[1],
            'visibility': extract_numeric_value(details.get('Tầm nhìn')),
            'cloud_coverage': extract_numeric_value(details.get('Mật độ mây')),
            'uv_index': extract_numeric_value(details.get('Chỉ số UV tối đa')),
            'details': details
        }
    except Exception as e:
        _LOGGER.error("Error parsing weather HTML: %s", e)
        return None


async def get_current_weather(session: aiohttp.ClientSession, location_key: str) -> dict[str, Any] | None:
    """Get current weather data (converted from get_weather.py)."""
    url = f"{BASE_URL}/vi/vn/any/{location_key}/current-weather/{location_key}"
    headers = get_headers()
    
    try:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                html = await response.text()
                return await parse_weather_html(html)
    except Exception as e:
        _LOGGER.error("Error getting current weather: %s", e)
    
    return None


async def parse_daily_html(html: str) -> list[dict[str, Any]]:
    """Parse daily forecast HTML (converted from get_daily.py)."""
    try:
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
                        precip_val = extract_numeric_value(t.strip())
                        break
            
            phrase = content.select_one('.phrase')
            phrase_val = phrase.get_text(strip=True) if phrase else None
            condition = map_condition_to_ha(phrase_val)
            
            # Extract high/low temp
            high = low = None
            temp = card.select_one('.temp')
            if temp:
                high_span = temp.select_one('.high')
                low_span = temp.select_one('.low')
                high = convert_temp_to_numeric(high_span.get_text(strip=True)) if high_span else None
                low = convert_temp_to_numeric(low_span.get_text(strip=True)) if low_span else None
            
            # Extract all details from panels
            details = {}
            for panel in content.select('.panels .left, .panels .right'):
                for p in panel.select('p.panel-item'):
                    label = p.contents[0].strip() if p.contents else None
                    value = p.select_one('.value')
                    if label and value:
                        details[label] = value.text.strip()
            
            daily.append({
                'datetime': date,
                'condition': condition,
                'phrase': phrase_val,
                'native_temperature': high,
                'native_templow': low,
                'precipitation_probability': precip_val,
                'humidity': extract_numeric_value(details.get('Độ ẩm')),
                'wind_speed': extract_wind_info(details.get('Gió', ''))[0],
                'wind_bearing': extract_wind_info(details.get('Gió', ''))[1],
                'uv_index': extract_numeric_value(details.get('Chỉ số UV tối đa')),
                'realfeel': extract_numeric_value(details.get('RealFeel®')),
                'realfeel_shade': extract_numeric_value(details.get('RealFeel Shade™')),
                'details': details
            })
        return daily
    except Exception as e:
        _LOGGER.error("Error parsing daily HTML: %s", e)
        return []


async def get_daily_forecast(session: aiohttp.ClientSession, location_key: str) -> list[dict[str, Any]]:
    """Get daily forecast data (converted from get_daily.py)."""
    url = f"{BASE_URL}/vi/vn/any/{location_key}/daily-weather-forecast/{location_key}"
    headers = get_headers()
    
    try:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                html = await response.text()
                return await parse_daily_html(html)
    except Exception as e:
        _LOGGER.error("Error getting daily forecast: %s", e)
    
    return []


async def parse_hourly_html(html: str) -> list[dict[str, Any]]:
    """Parse hourly forecast HTML (converted from get_hourly.py)."""
    try:
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
            
            phrase_val = phrase.text.strip() if phrase else None
            condition = map_condition_to_ha(phrase_val)
            
            hourly.append({
                'datetime': hour.text.strip() if hour else None,
                'native_temperature': convert_temp_to_numeric(temp.text.strip()) if temp else None,
                'condition': condition,
                'phrase': phrase_val,
                'native_apparent_temperature': convert_temp_to_numeric(realfeel.text.strip()) if realfeel else None,
                'precipitation_probability': extract_numeric_value(precip.text.strip()) if precip else None,
                'humidity': extract_numeric_value(details.get('Độ ẩm')),
                'wind_speed': extract_wind_info(details.get('Gió', ''))[0],
                'wind_bearing': extract_wind_info(details.get('Gió', ''))[1],
                'cloud_coverage': extract_numeric_value(details.get('Mật độ mây')),
                'uv_index': extract_numeric_value(details.get('Chỉ số UV tối đa')),
                'visibility': extract_numeric_value(details.get('Tầm nhìn')),
                'details': details
            })
        return hourly
    except Exception as e:
        _LOGGER.error("Error parsing hourly HTML: %s", e)
        return []


async def get_hourly_forecast(session: aiohttp.ClientSession, location_key: str) -> list[dict[str, Any]]:
    """Get hourly forecast data (converted from get_hourly.py)."""
    url = f"{BASE_URL}/vi/vn/any/{location_key}/hourly-weather-forecast/{location_key}"
    headers = get_headers()
    
    try:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                html = await response.text()
                return await parse_hourly_html(html)
    except Exception as e:
        _LOGGER.error("Error getting hourly forecast: %s", e)
    
    return []


async def parse_air_html(html: str) -> dict[str, Any]:
    """Parse air quality HTML (converted from get_air.py)."""
    try:
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
                aqi = extract_numeric_value(aqi_el[0].get_text(strip=True))
            
            pol_text = pol.get_text(separator=' ', strip=True)
            m = re.search(r"([\d.,]+)\s*(µg/m³|mg/m³|ppm|ppb|μg/m³|mg/m3|µg/m3|%)", pol_text)
            if m:
                value = float(m.group(1).replace(",", "."))
                unit = m.group(2)
            
            if name:
                pollutants[name] = {'aqi': aqi, 'value': value, 'unit': unit}
        
        return {
            'category': aqi_cat.get_text(strip=True) if aqi_cat else None,
            'description': aqi_desc.get_text(strip=True) if aqi_desc else None,
            'pollutants': pollutants
        }
    except Exception as e:
        _LOGGER.error("Error parsing air quality HTML: %s", e)
        return {'category': None, 'description': None, 'pollutants': {}}


async def get_air_quality(session: aiohttp.ClientSession, location_key: str) -> dict[str, Any]:
    """Get air quality data (converted from get_air.py)."""
    url = f"{BASE_URL}/vi/vn/any/{location_key}/air-quality-index/{location_key}"
    headers = get_headers()
    
    try:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                html = await response.text()
                return await parse_air_html(html)
    except Exception as e:
        _LOGGER.error("Error getting air quality: %s", e)
    
    return {'category': None, 'description': None, 'pollutants': {}}


async def parse_health_html(html: str) -> list[dict[str, Any]]:
    """Parse health activities HTML (converted from get_all_health.py)."""
    try:
        # Extract JavaScript data
        m = re.search(r"var indexListData\s*=\s*(\[.*?\]);", html, re.DOTALL)
        if not m:
            return []
        
        import json
        data = json.loads(m.group(1))
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
                'indexDate': item.get('indexDate'),
                'lifestyleCategory': item.get('lifestyleCategory')
            })
        return result
    except Exception as e:
        _LOGGER.error("Error parsing health HTML: %s", e)
        return []


def group_health_activities(items: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    """Group health activities by category (converted from run_weather.py)."""
    groups = {
        'allergy_health': [],
        'outdoor': [],
        'travel': [],
        'home_garden': [],
        'pests': [],
        'allergy_other': [],
        'entertainment': [],
        'other': []
    }
    
    for item in items:
        slug = (item.get('slug') or '').lower()
        cat = item.get('lifestyleCategory')
        t = item.get('type')
        
        if cat == 1 or slug in ['asthma','flu','sinus','migraine','arthritis','common-cold'] or t in [21, 23, 25, 26, 27, 30, 18]:
            groups['allergy_health'].append(item)
        elif cat == 2 or slug in ['running','hiking','biking','golf','sun-sand','astronomy','fishing']:
            groups['outdoor'].append(item)
        elif cat == 3 or slug in ['driving','air-travel']:
            groups['travel'].append(item)
        elif cat == 4 or slug in ['lawn-mowing','composting']:
            groups['home_garden'].append(item)
        elif cat == 5 or 'pest' in slug or 'mosquito' in slug:
            groups['pests'].append(item)
        elif slug in ['dust-dander','pollen']:
            groups['allergy_other'].append(item)
        elif slug in ['outdoor-entertaining','entertainment']:
            groups['entertainment'].append(item)
        else:
            groups['other'].append(item)
    
    return groups


async def crawl_all_health_activities(session: aiohttp.ClientSession, location_key: str) -> dict[str, list[dict[str, Any]]]:
    """Crawl all health activities by category (converted from get_all_health.py)."""
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
    
    headers = get_headers()
    
    for slug in group_slugs:
        try:
            url = f"{BASE_URL}/vi/vn/any/{location_key}/{slug}-weather/{location_key}"
            async with session.get(url, headers=headers, timeout=10) as response:
                if response.status == 200:
                    html = await response.text()
                    data = await parse_health_html(html)
                    group_name = slug_to_group.get(slug, 'other')
                    groups[group_name].extend(data)
        except Exception as e:
            _LOGGER.error("Error crawling health data for %s: %s", slug, e)
    
    return groups


async def get_minutecast_data(session: aiohttp.ClientSession, location_key: str) -> dict[str, Any] | None:
    """Get MinuteCast data (minute-by-minute precipitation forecast)."""
    url = f"{BASE_URL}/vi/vn/any/{location_key}/minute-weather-forecast/{location_key}"
    headers = get_headers()
    
    try:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                html = await response.text()
                return await parse_minutecast_html(html)
    except Exception as e:
        _LOGGER.error("Error getting MinuteCast data: %s", e)
    
    return None


async def parse_minutecast_html(html: str) -> dict[str, Any]:
    """Parse MinuteCast HTML to extract precipitation forecast."""
    try:
        soup = BeautifulSoup(html, 'html.parser')
        
        # Find MinuteCast summary - the main precipitation forecast text
        summary = None
        summary_selectors = [
            '.minute-cast-chart .summary',
            '.minute-cast-chart',
            '.minutecast-summary',
            '.chart-summary'
        ]
        
        for selector in summary_selectors:
            summary_element = soup.select_one(selector)
            if summary_element:
                summary = summary_element.get_text(strip=True)
                if summary:  # Only break if we actually got text
                    break
        
        # Extract current weather info from the page
        current_temp = None
        current_condition = None  
        realfeel = None
        current_time = None
        
        # Look for current weather section
        current_weather_selectors = [
            '.current-weather',
            '.minute-cast-current', 
            '.current-conditions'
        ]
        
        current_section = None
        for selector in current_weather_selectors:
            current_section = soup.select_one(selector)
            if current_section:
                break
        
        if current_section:
            # Extract temperature from current weather section
            temp_element = current_section.select_one('.temp, .temperature')
            if temp_element:
                temp_text = temp_element.get_text(strip=True)
                temp_match = re.search(r'(\d+)°', temp_text)
                if temp_match:
                    current_temp = int(temp_match.group(1))
            
            # Extract condition from current weather section
            condition_element = current_section.select_one('.phrase, .condition, .weather-phrase')
            if condition_element:
                current_condition = condition_element.get_text(strip=True)
            
            # Extract RealFeel from current weather section
            realfeel_element = current_section.select_one('.realfeel, .real-feel')
            if realfeel_element:
                realfeel_text = realfeel_element.get_text(strip=True)
                realfeel_match = re.search(r'(\d+)°', realfeel_text)
                if realfeel_match:
                    realfeel = int(realfeel_match.group(1))
            
            # Extract time from current weather section
            time_element = current_section.select_one('.time, .current-time')
            if time_element:
                current_time = time_element.get_text(strip=True)
        
        # Fallback: search in full page text if current section not found
        if not current_temp or not realfeel or not current_time or not current_condition:
            body_text = soup.get_text()
            
            # Try to extract condition from JSON data in the page (HTML encoded)
            if not current_condition:
                # Look for pattern: \&quot;Phrase\&quot;:\&quot;Some text\&quot;
                phrase_match = re.search(r'\\&quot;Phrase\\&quot;:\\&quot;([^\\]+)\\&quot;', html)
                if phrase_match:
                    current_condition = phrase_match.group(1)
            
            # Temperature fallback
            if not current_temp:
                temp_match = re.search(r'(\d+)°\s*C', body_text)
                if temp_match:
                    current_temp = int(temp_match.group(1))
            
            # RealFeel fallback  
            if not realfeel:
                realfeel_match = re.search(r'RealFeel®?\s*(\d+)°', body_text)
                if realfeel_match:
                    realfeel = int(realfeel_match.group(1))
            
            # Time fallback
            if not current_time:
                time_match = re.search(r'\d{2}:\d{2}', body_text)
                if time_match:
                    current_time = time_match.group(0)
        
        return {
            'summary': summary or 'Không có dữ liệu MinuteCast',
            'current_temperature': current_temp,
            'current_condition': current_condition,
            'realfeel': realfeel,
            'current_time': current_time,
            'forecast_type': 'minutecast'
        }
        
    except Exception as e:
        _LOGGER.error("Error parsing MinuteCast HTML: %s", e)
        return {
            'summary': 'Lỗi phân tích dữ liệu MinuteCast',
            'current_temperature': None,
            'current_condition': None,
            'realfeel': None,
            'current_time': None,
            'forecast_type': 'minutecast'
        }
