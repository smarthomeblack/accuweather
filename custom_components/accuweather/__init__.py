"""AccuWeather custom component for Home Assistant."""
from __future__ import annotations

import logging

import aiohttp
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import DOMAIN, CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL
from .coordinator import AccuWeatherDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.WEATHER, Platform.SENSOR]

# Singleton session per location_key to avoid cross-contamination of cookies/connections
_sessions: dict[str, aiohttp.ClientSession] = {}


async def _get_accuweather_session(
    hass: HomeAssistant, location_key: str
) -> aiohttp.ClientSession:
    """Get or create a dedicated aiohttp session for a location.

    Each location gets its own session so that connection issues for one
    location do not affect others, and to allow per-session tuning.
    """
    if location_key in _sessions:
        return _sessions[location_key]

    connector = aiohttp.TCPConnector(
        limit=20,               # max concurrent connections per session
        limit_per_host=10,      # max connections to the same host
        ttl_dns_cache=300,      # cache DNS for 5 minutes
        enable_cleanup_closed=True,
        force_close=False,      # reuse connections when possible
        keepalive_timeout=30,   # keep connections alive for 30s
    )
    session = aiohttp.ClientSession(
        connector=connector,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/123.0.0.0 Safari/537.36"
            ),
            "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
        },
    )
    _sessions[location_key] = session
    _LOGGER.debug("Created dedicated session for location %s", location_key)
    return session


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up AccuWeather from a config entry."""
    _LOGGER.debug("Setting up AccuWeather integration")

    location_key = entry.data["location_key"]
    location_name = entry.data["location_name"]
    update_interval = entry.data.get(CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL)

    session = await _get_accuweather_session(hass, location_key)
    coordinator = AccuWeatherDataUpdateCoordinator(
        hass, session, location_key, location_name, entry, update_interval
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
    
    return unload_ok
