from __future__ import annotations

import logging
from dataclasses import dataclass

from pyforeca import (
    AirQualityDailyForecast,
    AirQualityForecast,
    CurrentWeather,
    DailyForecast,
    ForecaApiClient,
    ForecaAuthError,
    ForecaError,
    HourlyForecast,
    format_location,
)

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_API_KEY, CONF_LATITUDE, CONF_LONGITUDE
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DAILY_PERIODS, DOMAIN, HOURLY_PERIODS, UPDATE_INTERVAL

_LOGGER = logging.getLogger(__name__)

type ForecaConfigEntry = ConfigEntry[ForecaUpdateCoordinator]


@dataclass(slots=True)
class ForecaWeatherData:
    current: CurrentWeather
    hourly: list[HourlyForecast]
    daily: list[DailyForecast]
    air_quality: AirQualityForecast | None
    air_quality_daily: list[AirQualityDailyForecast]


class ForecaUpdateCoordinator(DataUpdateCoordinator[ForecaWeatherData]):
    config_entry: ForecaConfigEntry

    def __init__(self, hass: HomeAssistant, entry: ForecaConfigEntry) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=UPDATE_INTERVAL,
            config_entry=entry,
        )
        self.client = ForecaApiClient(
            entry.data[CONF_API_KEY], session=async_get_clientsession(hass)
        )
        self.location = format_location(
            lon=entry.data[CONF_LONGITUDE], lat=entry.data[CONF_LATITUDE]
        )

    async def _async_update_data(self) -> ForecaWeatherData:
        try:
            current = await self.client.current(self.location)
            hourly = await self.client.forecast_hourly(
                self.location, periods=HOURLY_PERIODS, dataset="full"
            )
            daily = await self.client.forecast_daily(
                self.location, periods=DAILY_PERIODS, dataset="full"
            )
        except ForecaAuthError as err:
            raise ConfigEntryAuthFailed("API key was rejected") from err
        except ForecaError as err:
            raise UpdateFailed(f"Error communicating with the Foreca API: {err}") from err

        # Air quality is optional: not every location has AQ data, and the
        # weather entity must not go unavailable because of it.
        air_quality: AirQualityForecast | None = None
        air_quality_daily: list[AirQualityDailyForecast] = []
        try:
            aq_forecast = await self.client.air_quality_hourly(
                self.location, periods=1
            )
            air_quality = aq_forecast[0] if aq_forecast else None
            air_quality_daily = await self.client.air_quality_daily(
                self.location, periods=4
            )
        except ForecaAuthError as err:
            raise ConfigEntryAuthFailed("API key was rejected") from err
        except ForecaError as err:
            _LOGGER.warning("Air quality data unavailable: %s", err)

        return ForecaWeatherData(
            current=current,
            hourly=hourly,
            daily=daily,
            air_quality=air_quality,
            air_quality_daily=air_quality_daily,
        )
