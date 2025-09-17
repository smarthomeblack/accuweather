"""Config flow for AccuWeather integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.config_entries import ConfigEntry

from .const import (
    DOMAIN, 
    CONF_LOCATION_KEY, 
    CONF_LOCATION_NAME,
    CONF_UPDATE_INTERVAL,
    DEFAULT_UPDATE_INTERVAL,
    MIN_UPDATE_INTERVAL,
    MAX_UPDATE_INTERVAL
)
from .utils import get_location_keys

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required("location"): str,
    }
)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for AccuWeather."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize config flow."""
        self._locations: list[tuple[str, str, str]] = []
        self._selected_location_key: str = ""
        self._selected_location_name: str = ""

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        
        if user_input is not None:
            try:
                session = async_get_clientsession(self.hass)
                location_query = user_input["location"]
                
                # Get location keys from AccuWeather
                self._locations = await get_location_keys(session, location_query)
                
                if not self._locations:
                    errors["base"] = "no_locations"
                else:
                    # Always show selection step, even with 1 result for confirmation
                    return await self.async_step_select_location()
                    
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )

    async def async_step_select_location(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle location selection step."""
        if user_input is not None:
            selected_location = user_input["location_choice"]
            
            # Find selected location and store for next step
            for location_key, location_name, long_name in self._locations:
                if f"{location_key}|{location_name}" == selected_location:
                    self._selected_location_key = location_key
                    self._selected_location_name = location_name
                    
                    # Move to update interval configuration
                    return await self.async_step_update_interval()
            
            return self.async_abort(reason="invalid_selection")
        
        # Create options for location selection
        location_options = {}
        for location_key, location_name, long_name in self._locations:
            display_name = f"{location_name} ({long_name})" if long_name else location_name
            location_options[f"{location_key}|{location_name}"] = display_name
        
        data_schema = vol.Schema({
            vol.Required("location_choice"): vol.In(location_options)
        })
        
        return self.async_show_form(
            step_id="select_location",
            data_schema=data_schema,
            description_placeholders={"location_count": str(len(self._locations))}
        )

    async def async_step_update_interval(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle update interval configuration step."""
        if user_input is not None:
            update_interval = user_input.get("update_interval", DEFAULT_UPDATE_INTERVAL)
            
            # Check if already configured
            await self.async_set_unique_id(self._selected_location_key)
            self._abort_if_unique_id_configured()
            
            return self.async_create_entry(
                title=self._selected_location_name,
                data={
                    CONF_LOCATION_KEY: self._selected_location_key,
                    CONF_LOCATION_NAME: self._selected_location_name,
                    CONF_UPDATE_INTERVAL: update_interval,
                }
            )
        
        # Show update interval configuration form
        data_schema = vol.Schema({
            vol.Optional(
                "update_interval", 
                default=DEFAULT_UPDATE_INTERVAL
            ): vol.All(vol.Coerce(int), vol.Range(min=MIN_UPDATE_INTERVAL, max=MAX_UPDATE_INTERVAL))
        })
        
        return self.async_show_form(
            step_id="update_interval",
            data_schema=data_schema,
            description_placeholders={
                "location_name": self._selected_location_name,
                "default_interval": str(DEFAULT_UPDATE_INTERVAL // 60),
                "min_interval": str(MIN_UPDATE_INTERVAL // 60),
                "max_interval": str(MAX_UPDATE_INTERVAL // 60),
            }
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        """Create the options flow."""
        return OptionsFlow(config_entry)


class OptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for AccuWeather."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            # Update the config entry data with new update interval
            new_data = dict(self.config_entry.data)
            new_data[CONF_UPDATE_INTERVAL] = user_input.get("update_interval", DEFAULT_UPDATE_INTERVAL)
            
            self.hass.config_entries.async_update_entry(
                self.config_entry, data=new_data
            )
            
            # Reload the entry to apply new update interval
            await self.hass.config_entries.async_reload(self.config_entry.entry_id)
            
            return self.async_create_entry(title="", data={})

        current_interval = self.config_entry.data.get(CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL)
        
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Optional(
                    "update_interval", 
                    default=current_interval
                ): vol.All(vol.Coerce(int), vol.Range(min=MIN_UPDATE_INTERVAL, max=MAX_UPDATE_INTERVAL))
            }),
            description_placeholders={
                "current_interval": str(current_interval // 60),
                "min_interval": str(MIN_UPDATE_INTERVAL // 60),
                "max_interval": str(MAX_UPDATE_INTERVAL // 60),
            }
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidLocation(HomeAssistantError):
    """Error to indicate there is invalid location."""
