"""Constants for AccuWeather integration."""

DOMAIN = "accuweather"

# Config flow
CONF_LOCATION_KEY = "location_key"
CONF_LOCATION_NAME = "location_name"
CONF_UPDATE_INTERVAL = "update_interval"

# Update intervals
DEFAULT_UPDATE_INTERVAL = 600  # 10 minutes
MIN_UPDATE_INTERVAL = 300     # 5 minutes
MAX_UPDATE_INTERVAL = 3600    # 60 minutes

# API URLs
BASE_URL = "https://www.accuweather.com"
AUTOCOMPLETE_URL = f"{BASE_URL}/web-api/autocomplete"

# Weather conditions mapping to Home Assistant
CONDITION_MAP = {
    "sunny": "sunny",
    "clear": "sunny", 
    "mostly sunny": "sunny",
    "partly sunny": "partlycloudy",
    "intermittent clouds": "partlycloudy",
    "hazy sunshine": "partlycloudy",
    "mostly cloudy": "cloudy",
    "cloudy": "cloudy",
    "overcast": "cloudy",
    "fog": "fog",
    "showers": "rainy",
    "mostly cloudy w/ showers": "rainy", 
    "partly sunny w/ showers": "rainy",
    "t-storms": "lightning-rainy",
    "mostly cloudy w/ t-storms": "lightning-rainy",
    "partly sunny w/ t-storms": "lightning-rainy",
    "rain": "rainy",
    "flurries": "snowy",
    "mostly cloudy w/ flurries": "snowy",
    "partly sunny w/ flurries": "snowy",
    "snow": "snowy",
    "mostly cloudy w/ snow": "snowy",
    "ice": "snowy",
    "sleet": "snowy",
    "freezing rain": "snowy",
    "rain and snow": "snowy-rainy",
    "hot": "sunny",
    "cold": "sunny",
    "windy": "windy",
    "clear night": "clear-night",
    "mostly clear": "clear-night",
    "partly cloudy": "partlycloudy",
    "intermittent clouds night": "partlycloudy",
    "hazy moonlight": "partlycloudy",
    "mostly cloudy night": "cloudy",
    "partly cloudy w/ showers": "rainy",
    "mostly cloudy w/ showers night": "rainy",
    "partly cloudy w/ t-storms": "lightning-rainy",
    "mostly cloudy w/ t-storms night": "lightning-rainy",
    "partly cloudy w/ flurries": "snowy",
    "mostly cloudy w/ flurries night": "snowy",
    "rain and snow mixed": "snowy-rainy"
}

# Vietnamese condition mapping (updated based on real data)
CONDITION_MAP_VI = {
    "nắng": "sunny",
    "quang đãng": "sunny",
    "nắng nhiều": "sunny",
    "nắng nhẹ": "sunny", 
    "ít mây": "partlycloudy",
    "có mây": "partlycloudy",
    "mây rải rác": "partlycloudy",
    "mây và nắng": "partlycloudy",
    "nắng sau đó có ít mây": "partlycloudy",
    "mây ngày càng nhiều": "cloudy",
    "nhiều mây": "cloudy",
    "u ám": "cloudy",
    "âm u": "cloudy",
    "sương mù": "fog",
    "mưa rào": "rainy",
    "mưa": "rainy",
    "mưa nhẹ": "rainy",
    "mưa vừa": "rainy", 
    "mưa to": "pouring",
    "đôi lúc có mưa": "rainy",
    "khả năng có mưa": "rainy",
    "một vài cơn mưa rào": "rainy",
    "một chút mưa": "rainy",
    "cơn mưa rào hoặc mưa dông": "lightning-rainy",
    "dông": "lightning",
    "sấm sét": "lightning-rainy",
    "mưa dông": "lightning-rainy",
    "một vài cơn mưa rão và mưa dông": "lightning-rainy",
    "mưa dông ở một số phần trong khu vực": "lightning-rainy",
    "một vài cơn mưa dông": "lightning-rainy",
    "có thể có mưa rào hoặc mưa dông": "lightning-rainy",
    "tuyết": "snowy",
    "mưa tuyết": "snowy-rainy",
    "gió": "windy",
    "đêm quang đãng": "clear-night"
}
