from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from pyforeca import AirQualityForecast

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTRIBUTION, DOMAIN
from .coordinator import ForecaConfigEntry, ForecaUpdateCoordinator


@dataclass(frozen=True, kw_only=True)
class ForecaSensorDescription(SensorEntityDescription):
    value_fn: Callable[[AirQualityForecast], float | str | None]


SENSORS: tuple[ForecaSensorDescription, ...] = (
    ForecaSensorDescription(
        key="aqi",
        device_class=SensorDeviceClass.AQI,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda aq: aq.aqi,
    ),
    ForecaSensorDescription(
        key="dominant_pollutant",
        translation_key="dominant_pollutant",
        value_fn=lambda aq: aq.pollutant,
    ),
    ForecaSensorDescription(
        key="aqi_co",
        translation_key="aqi_co",
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
        value_fn=lambda aq: aq.aqi_co,
    ),
    ForecaSensorDescription(
        key="aqi_no2",
        translation_key="aqi_no2",
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
        value_fn=lambda aq: aq.aqi_no2,
    ),
    ForecaSensorDescription(
        key="aqi_o3",
        translation_key="aqi_o3",
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
        value_fn=lambda aq: aq.aqi_o3,
    ),
    ForecaSensorDescription(
        key="aqi_so2",
        translation_key="aqi_so2",
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
        value_fn=lambda aq: aq.aqi_so2,
    ),
    ForecaSensorDescription(
        key="aqi_pm10",
        translation_key="aqi_pm10",
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
        value_fn=lambda aq: aq.aqi_pm10,
    ),
    ForecaSensorDescription(
        key="aqi_pm2p5",
        translation_key="aqi_pm2p5",
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
        value_fn=lambda aq: aq.aqi_pm2p5,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ForecaConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    coordinator = entry.runtime_data
    async_add_entities(
        ForecaAirQualitySensor(coordinator, entry, description)
        for description in SENSORS
    )


class ForecaAirQualitySensor(
    CoordinatorEntity[ForecaUpdateCoordinator], SensorEntity
):
    entity_description: ForecaSensorDescription
    _attr_attribution = ATTRIBUTION
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: ForecaUpdateCoordinator,
        entry: ForecaConfigEntry,
        description: ForecaSensorDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}-{description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=entry.title,
            manufacturer="Foreca",
            entry_type=DeviceEntryType.SERVICE,
        )

    @property
    def available(self) -> bool:
        return super().available and self.coordinator.data.air_quality is not None

    @property
    def native_value(self) -> float | str | None:
        if (air_quality := self.coordinator.data.air_quality) is None:
            return None
        return self.entity_description.value_fn(air_quality)
