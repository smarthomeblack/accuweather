"""Device information for AccuWeather integration."""
from __future__ import annotations

from homeassistant.helpers.entity import DeviceInfo

from .const import DOMAIN


def get_device_info(location_key: str, location_name: str) -> DeviceInfo:
    """Get device info for AccuWeather location."""
    return DeviceInfo(
        identifiers={(DOMAIN, location_key)},
        name=f"AccuWeather {location_name}",
        manufacturer="smarthomeblack",
        model="AccuWeather",
        sw_version="2025.9.19",
        configuration_url=f"https://www.accuweather.com/vi/search-locations?query={location_name}",
        entry_type="service",
    )
