from __future__ import annotations

from pyforeca import DailyForecast, HourlyForecast

from homeassistant.components.weather import (
    Forecast,
    SingleCoordinatorWeatherEntity,
    WeatherEntityFeature,
)
from homeassistant.const import (
    UnitOfLength,
    UnitOfPrecipitationDepth,
    UnitOfPressure,
    UnitOfSpeed,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import ATTRIBUTION, DOMAIN, symbol_to_condition
from .coordinator import ForecaConfigEntry, ForecaUpdateCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ForecaConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    async_add_entities([ForecaWeather(entry.runtime_data, entry)])


def _daily_to_forecast(day: DailyForecast) -> Forecast:
    return Forecast(
        datetime=day.date or "",
        condition=symbol_to_condition(day.symbol),
        native_temperature=day.max_temp,
        native_templow=day.min_temp,
        native_precipitation=day.precip_accum,
        precipitation_probability=day.precip_prob,
        native_wind_speed=day.max_wind_speed,
        native_wind_gust_speed=day.max_wind_gust,
        wind_bearing=day.wind_dir,
        uv_index=day.uv_index,
    )


def _hourly_to_forecast(hour: HourlyForecast) -> Forecast:
    return Forecast(
        datetime=hour.time or "",
        condition=symbol_to_condition(hour.symbol),
        native_temperature=hour.temperature,
        native_apparent_temperature=hour.feels_like_temp,
        native_precipitation=hour.precip_accum,
        precipitation_probability=hour.precip_prob,
        native_wind_speed=hour.wind_speed,
        native_wind_gust_speed=hour.wind_gust,
        wind_bearing=hour.wind_dir,
        humidity=hour.rel_humidity,
        cloud_coverage=hour.cloudiness,
        uv_index=hour.uv_index,
    )


class ForecaWeather(SingleCoordinatorWeatherEntity[ForecaUpdateCoordinator]):
    _attr_attribution = ATTRIBUTION
    _attr_has_entity_name = True
    _attr_name = None
    _attr_native_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_native_pressure_unit = UnitOfPressure.HPA
    _attr_native_wind_speed_unit = UnitOfSpeed.METERS_PER_SECOND
    _attr_native_precipitation_unit = UnitOfPrecipitationDepth.MILLIMETERS
    _attr_native_visibility_unit = UnitOfLength.METERS
    _attr_supported_features = (
        WeatherEntityFeature.FORECAST_DAILY | WeatherEntityFeature.FORECAST_HOURLY
    )

    def __init__(
        self, coordinator: ForecaUpdateCoordinator, entry: ForecaConfigEntry
    ) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = entry.entry_id
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=entry.title,
            manufacturer="Foreca",
            entry_type=DeviceEntryType.SERVICE,
        )

    @property
    def condition(self) -> str | None:
        return symbol_to_condition(self.coordinator.data.current.symbol)

    @property
    def native_temperature(self) -> float | None:
        return self.coordinator.data.current.temperature

    @property
    def native_apparent_temperature(self) -> float | None:
        return self.coordinator.data.current.feels_like_temp

    @property
    def native_dew_point(self) -> float | None:
        return self.coordinator.data.current.dew_point

    @property
    def humidity(self) -> float | None:
        return self.coordinator.data.current.rel_humidity

    @property
    def native_pressure(self) -> float | None:
        return self.coordinator.data.current.pressure

    @property
    def native_wind_speed(self) -> float | None:
        return self.coordinator.data.current.wind_speed

    @property
    def native_wind_gust_speed(self) -> float | None:
        return self.coordinator.data.current.wind_gust

    @property
    def wind_bearing(self) -> float | None:
        return self.coordinator.data.current.wind_dir

    @property
    def native_visibility(self) -> float | None:
        return self.coordinator.data.current.visibility

    @property
    def cloud_coverage(self) -> float | None:
        return self.coordinator.data.current.cloudiness

    @property
    def uv_index(self) -> float | None:
        return self.coordinator.data.current.uv_index

    @callback
    def _async_forecast_daily(self) -> list[Forecast] | None:
        return [_daily_to_forecast(day) for day in self.coordinator.data.daily]

    @callback
    def _async_forecast_hourly(self) -> list[Forecast] | None:
        return [_hourly_to_forecast(hour) for hour in self.coordinator.data.hourly]
