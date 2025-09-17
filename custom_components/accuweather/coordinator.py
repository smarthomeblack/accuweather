"""DataUpdateCoordinator for AccuWeather."""
from __future__ import annotations

import asyncio
from datetime import timedelta
import logging
from typing import Any

import aiohttp

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, DEFAULT_UPDATE_INTERVAL
from .utils import get_current_weather, get_daily_forecast, get_hourly_forecast, get_air_quality, crawl_all_health_activities, get_minutecast_data

_LOGGER = logging.getLogger(__name__)


class AccuWeatherDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching AccuWeather data."""

    def __init__(
        self,
        hass: HomeAssistant,
        session: aiohttp.ClientSession,
        location_key: str,
        location_name: str,
        update_interval: int = DEFAULT_UPDATE_INTERVAL,
    ) -> None:
        """Initialize."""
        self.location_key = location_key
        self.location_name = location_name
        self.session = session
        
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=update_interval),
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Update data via library."""
        try:
            # Get all data concurrently
            current_weather, daily_forecast, hourly_forecast, air_quality, health_activities, minutecast = await asyncio.gather(
                get_current_weather(self.session, self.location_key),
                get_daily_forecast(self.session, self.location_key),
                get_hourly_forecast(self.session, self.location_key),
                get_air_quality(self.session, self.location_key),
                crawl_all_health_activities(self.session, self.location_key),
                get_minutecast_data(self.session, self.location_key),
                return_exceptions=True
            )
            
            # Handle exceptions from gather
            if isinstance(current_weather, Exception):
                _LOGGER.error("Error getting current weather: %s", current_weather)
                current_weather = None
            
            if isinstance(daily_forecast, Exception):
                _LOGGER.error("Error getting daily forecast: %s", daily_forecast)
                daily_forecast = []
            
            if isinstance(hourly_forecast, Exception):
                _LOGGER.error("Error getting hourly forecast: %s", hourly_forecast)
                hourly_forecast = []
                
            if isinstance(air_quality, Exception):
                _LOGGER.error("Error getting air quality: %s", air_quality)
                air_quality = {'category': None, 'description': None, 'pollutants': {}}
            
            if isinstance(health_activities, Exception):
                _LOGGER.error("Error getting health activities: %s", health_activities)
                health_activities = {}
            
            if isinstance(minutecast, Exception):
                _LOGGER.error("Error getting MinuteCast data: %s", minutecast)
                minutecast = None
            
            if not current_weather:
                raise UpdateFailed("Failed to get current weather data")
            
            return {
                "current": current_weather,
                "daily_forecast": daily_forecast or [],
                "hourly_forecast": hourly_forecast or [],
                "air_quality": air_quality or {'category': None, 'description': None, 'pollutants': {}},
                "health_activities": health_activities or {},
                "minutecast": minutecast,
                "location_key": self.location_key,
                "location_name": self.location_name,
            }
            
        except Exception as exception:
            raise UpdateFailed(f"Error communicating with API: {exception}") from exception
