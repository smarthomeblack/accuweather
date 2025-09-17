"""Sensor platform for AccuWeather integration."""
from __future__ import annotations

import logging
import re
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    UnitOfLength,
    UnitOfPressure,
    UnitOfSpeed,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import AccuWeatherDataUpdateCoordinator
from .device import get_device_info

_LOGGER = logging.getLogger(__name__)


SENSOR_TYPES: tuple[SensorEntityDescription, ...] = (
    # Basic weather sensors
    SensorEntityDescription(
        key="realfeel_temperature",
        name="RealFeel Temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    SensorEntityDescription(
        key="humidity",
        name="Humidity",
        device_class=SensorDeviceClass.HUMIDITY,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=PERCENTAGE,
    ),
    SensorEntityDescription(
        key="pressure",
        name="Pressure",
        device_class=SensorDeviceClass.PRESSURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfPressure.HPA,
    ),
    SensorEntityDescription(
        key="wind_speed",
        name="Wind Speed",
        device_class=SensorDeviceClass.WIND_SPEED,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfSpeed.KILOMETERS_PER_HOUR,
    ),
    SensorEntityDescription(
        key="wind_bearing",
        name="Wind Bearing",
        icon="mdi:compass",
    ),
    SensorEntityDescription(
        key="wind_gust",
        name="Wind Gust",
        device_class=SensorDeviceClass.WIND_SPEED,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfSpeed.KILOMETERS_PER_HOUR,
    ),
    SensorEntityDescription(
        key="visibility",
        name="Visibility",
        device_class=SensorDeviceClass.DISTANCE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfLength.KILOMETERS,
    ),
    SensorEntityDescription(
        key="cloud_coverage",
        name="Cloud Coverage",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=PERCENTAGE,
    ),
    SensorEntityDescription(
        key="uv_index",
        name="UV Index",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="dew_point",
        name="Dew Point",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    # Air quality sensors
    SensorEntityDescription(
        key="pm25",
        name="PM2.5",
        device_class=SensorDeviceClass.PM25,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="µg/m³",
    ),
    SensorEntityDescription(
        key="pm10",
        name="PM10",
        device_class=SensorDeviceClass.PM10,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="µg/m³",
    ),
    SensorEntityDescription(
        key="ozone",
        name="Ozone",
        device_class=SensorDeviceClass.OZONE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="µg/m³",
    ),
    SensorEntityDescription(
        key="nitrogen_dioxide",
        name="Nitrogen Dioxide",
        device_class=SensorDeviceClass.NITROGEN_DIOXIDE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="µg/m³",
    ),
    SensorEntityDescription(
        key="sulfur_dioxide",
        name="Sulfur Dioxide",
        device_class=SensorDeviceClass.SULPHUR_DIOXIDE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="µg/m³",
    ),
    SensorEntityDescription(
        key="carbon_monoxide",
        name="Carbon Monoxide",
        device_class=SensorDeviceClass.CO,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="ppm",
    ),
    SensorEntityDescription(
        key="cloud_ceiling",
        name="Cloud Ceiling",
        device_class=SensorDeviceClass.DISTANCE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfLength.METERS,
    ),
    # MinuteCast sensor
    SensorEntityDescription(
        key="minutecast",
        name="MinuteCast Precipitation",
        icon="mdi:radar",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up AccuWeather sensor entities."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    
    entities = []
    
    # Add static sensor types
    for description in SENSOR_TYPES:
        entities.append(AccuWeatherSensorEntity(coordinator, description))
    
    # Add dynamic health activity sensors
    if coordinator.data and "health_activities" in coordinator.data:
        health_data = coordinator.data["health_activities"]
        
        for group_name, activities in health_data.items():
            for activity in activities:
                activity_name = activity.get("name")
                activity_slug = activity.get("slug")
                if activity_name and activity_slug:
                    # Create sensor description for this health activity
                    health_desc = SensorEntityDescription(
                        key=f"health_{activity_slug.replace('-', '_')}",
                        name=activity_name,
                        icon=get_health_icon(activity_slug),
                    )
                    entities.append(AccuWeatherHealthSensorEntity(coordinator, health_desc, activity))
    
    async_add_entities(entities, False)


def get_health_icon(slug: str) -> str:
    """Get icon for health activity based on slug."""
    icon_map = {
        "asthma": "mdi:lungs",
        "arthritis": "mdi:bone",
        "migraine": "mdi:head-outline", 
        "dust-dander": "mdi:air-filter",
        "common-cold": "mdi:account-alert",
        "flu": "mdi:account-alert",
        "sinus": "mdi:head-outline",
        "running": "mdi:run",
        "hiking": "mdi:hiking",
        "biking": "mdi:bike",
        "golf": "mdi:golf",
        "sun-sand": "mdi:pool",
        "astronomy": "mdi:telescope",
        "fishing": "mdi:fish",
        "air-travel": "mdi:airplane",
        "driving": "mdi:car",
        "lawn-mowing": "mdi:grass",
        "composting": "mdi:compost",
        "mosquito-activity": "mdi:bug",
        "indoor-pests": "mdi:home-variant",
        "outdoor-pests": "mdi:bug-outline",
        "outdoor-entertaining": "mdi:party-popper",
    }
    return icon_map.get(slug, "mdi:information")


class AccuWeatherSensorEntity(CoordinatorEntity[AccuWeatherDataUpdateCoordinator], SensorEntity):
    """Implementation of AccuWeather sensor entity."""

    def __init__(
        self,
        coordinator: AccuWeatherDataUpdateCoordinator,
        description: SensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_name = f"AccuWeather {coordinator.location_name} {description.name}"
        self._attr_unique_id = f"accuweather_{coordinator.location_key}_{description.key}"
        self._attr_device_info = get_device_info(coordinator.location_key, coordinator.location_name)

    @property
    def native_value(self) -> Any:
        """Return the state of the sensor."""
        if not self.coordinator.data:
            return None
        
        key = self.entity_description.key
        
        # Current weather sensors
        if "current" in self.coordinator.data:
            current = self.coordinator.data["current"]
            details = current.get("details", {})
            
            if key == "realfeel_temperature":
                realfeel = current.get("realfeel")
                if realfeel:
                    match = re.search(r"(-?\d+)", str(realfeel))
                    if match:
                        return float(match.group(1))
                return current.get("temperature")
                
            elif key == "humidity":
                return current.get("humidity")
            elif key == "pressure":
                return current.get("pressure")
            elif key == "wind_speed":
                return current.get("wind_speed")
            elif key == "wind_bearing":
                bearing = current.get("wind_bearing")
                # Convert Vietnamese direction to English
                direction_map = {
                    "B": "N", "BĐB": "NNE", "ĐB": "NE", "ĐĐB": "ENE",
                    "Đ": "E", "ĐĐN": "ESE", "ĐN": "SE", "NĐN": "SSE",
                    "N": "S", "NTN": "SSW", "TN": "SW", "TTN": "WSW",
                    "T": "W", "TTB": "WNW", "TB": "NW", "BTB": "NNW"
                }
                return direction_map.get(bearing, bearing) if bearing else None
            elif key == "visibility":
                return current.get("visibility")
            elif key == "cloud_coverage":
                return current.get("cloud_coverage")
            elif key == "uv_index":
                return current.get("uv_index")
            elif key == "dew_point":
                dew_val = details.get("Điểm sương")
                if dew_val:
                    match = re.search(r"(-?\d+)", str(dew_val))
                    if match:
                        return float(match.group(1))
                return None
            elif key == "wind_gust":
                gust_val = details.get("Gió giật mạnh") or details.get("Gió giật")
                if gust_val:
                    match = re.search(r"(\d+)", str(gust_val))
                    if match:
                        return float(match.group(1))
                return None
            elif key == "cloud_ceiling":
                ceiling_val = details.get("Trần mây")
                if ceiling_val:
                    match = re.search(r"(\d+)", str(ceiling_val))
                    if match:
                        return float(match.group(1))
                return None
        
        # Air quality sensors
        if "air_quality" in self.coordinator.data:
            air_data = self.coordinator.data["air_quality"]
            
            # Individual pollutants
            pollutants = air_data.get("pollutants", {})
            pollutant_map = {
                "pm25": "PM2_5",
                "pm10": "PM10",
                "ozone": "O3",
                "nitrogen_dioxide": "NO2",
                "sulfur_dioxide": "SO2",
                "carbon_monoxide": "CO"
            }
            
            if key in pollutant_map and pollutant_map[key] in pollutants:
                pollutant_data = pollutants[pollutant_map[key]]
                value = pollutant_data.get("value")
                if value:
                    try:
                        float_value = float(value)
                        # Convert CO from µg/m³ to ppm for HA compatibility
                        if key == "carbon_monoxide":
                            return round(float_value * 0.00087, 2)  # µg/m³ to ppm conversion for CO
                        return float_value
                    except (ValueError, TypeError):
                        return None
        
        # MinuteCast sensor
        if key == "minutecast" and "minutecast" in self.coordinator.data:
            minutecast_data = self.coordinator.data["minutecast"]
            return minutecast_data.get("summary", "Không có dữ liệu MinuteCast")
        
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes."""
        if not self.coordinator.data:
            return {}
        
        attrs = {
            "location_key": self.coordinator.location_key,
        }
        
        # Add current weather update time
        if "current" in self.coordinator.data:
            current = self.coordinator.data["current"]
            attrs["last_update"] = current.get("time")
        
        # Add air quality details
        if "air_quality" in self.coordinator.data and self.entity_description.key.startswith(("pm25", "pm10", "ozone", "nitrogen", "sulfur", "carbon")):
            air_data = self.coordinator.data["air_quality"]
            attrs.update({
                "description": air_data.get("desc"),
                "category": air_data.get("category"),
            })
            
            # Add specific pollutant details
            pollutants = air_data.get("pollutants", {})
            pollutant_map = {
                "pm25": "PM2_5",
                "pm10": "PM10",
                "ozone": "O3",
                "nitrogen_dioxide": "NO2",
                "sulfur_dioxide": "SO2",
                "carbon_monoxide": "CO"
            }
            
            if self.entity_description.key in pollutant_map and pollutant_map[self.entity_description.key] in pollutants:
                pollutant_data = pollutants[pollutant_map[self.entity_description.key]]
                attrs.update({
                    "aqi": pollutant_data.get("aqi"),
                    "unit": pollutant_data.get("unit"),
                })
                
                # For CO, add original unit info since we converted it
                if self.entity_description.key == "carbon_monoxide":
                    attrs["original_unit"] = pollutant_data.get("unit", "µg/m³")
                    attrs["original_value"] = pollutant_data.get("value")
        
        # Add MinuteCast details
        if self.entity_description.key == "minutecast" and "minutecast" in self.coordinator.data:
            minutecast_data = self.coordinator.data["minutecast"]
            attrs.update({
                "current_temperature": minutecast_data.get("current_temperature"),
                "current_condition": minutecast_data.get("current_condition"),
                "realfeel": minutecast_data.get("realfeel"),
                "current_time": minutecast_data.get("current_time"),
                "forecast_type": minutecast_data.get("forecast_type"),
            })
        
        return attrs


class AccuWeatherHealthSensorEntity(CoordinatorEntity[AccuWeatherDataUpdateCoordinator], SensorEntity):
    """Implementation of AccuWeather health activity sensor entity."""

    def __init__(
        self,
        coordinator: AccuWeatherDataUpdateCoordinator,
        description: SensorEntityDescription,
        activity_data: dict[str, Any],
    ) -> None:
        """Initialize the health sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._activity_data = activity_data
        self._attr_name = f"AccuWeather {coordinator.location_name} {description.name}"
        self._attr_unique_id = f"accuweather_{coordinator.location_key}_{description.key}"
        self._attr_device_info = get_device_info(coordinator.location_key, coordinator.location_name)

    @property
    def native_value(self) -> Any:
        """Return the state of the sensor."""
        if not self.coordinator.data or "health_activities" not in self.coordinator.data:
            return None
        
        health_data = self.coordinator.data["health_activities"]
        activity_slug = self._activity_data.get("slug")
        
        # Find current activity data
        for group_activities in health_data.values():
            for activity in group_activities:
                if activity.get("slug") == activity_slug:
                    # Return localized category instead of raw value
                    return activity.get("localizedCategory", activity.get("category", "Không rõ"))
        
        return "Không rõ"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes."""
        if not self.coordinator.data or "health_activities" not in self.coordinator.data:
            return {}
        
        health_data = self.coordinator.data["health_activities"]
        activity_slug = self._activity_data.get("slug")
        
        # Find current activity data
        for group_activities in health_data.values():
            for activity in group_activities:
                if activity.get("slug") == activity_slug:
                    return {
                        "location_key": self.coordinator.location_key,
                        "raw_value": activity.get("value"),
                        "category_value": activity.get("categoryValue"),
                        "phrase": activity.get("categoryPhrase"),
                        "status_color": activity.get("statusColor"),
                        "localized_name": activity.get("localizedName"),
                        "index_date": activity.get("indexDate"),
                    }
        
        return {"location_key": self.coordinator.location_key}
