from unittest.mock import MagicMock

from pyforeca import ForecaError
from homeassistant.const import CONF_API_KEY, CONF_LATITUDE, CONF_LONGITUDE, STATE_UNAVAILABLE
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.foreca.const import DOMAIN


async def _setup(hass: HomeAssistant) -> MockConfigEntry:
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Helsinki",
        unique_id="60.1700-24.9400",
        data={CONF_API_KEY: "test-key", CONF_LATITUDE: 60.17, CONF_LONGITUDE: 24.94},
    )
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    return entry


async def test_air_quality_sensors(hass: HomeAssistant, mock_client: MagicMock) -> None:
    await _setup(hass)

    aqi = hass.states.get("sensor.helsinki_air_quality_index")
    assert aqi is not None
    assert aqi.state == "23"
    assert aqi.attributes["attribution"] == "Data provided by Foreca"

    pollutant = hass.states.get("sensor.helsinki_dominant_pollutant")
    assert pollutant is not None
    assert pollutant.state == "Ozone"


async def test_daily_aqi_sensors(hass: HomeAssistant, mock_client: MagicMock) -> None:
    await _setup(hass)
    for day, expected in ((1, "34"), (2, "35"), (3, "31")):
        state = hass.states.get(f"sensor.helsinki_air_quality_index_day_{day}")
        assert state is not None, f"day {day} sensor missing"
        assert state.state == expected


async def test_subindex_sensors_disabled_by_default(
    hass: HomeAssistant, mock_client: MagicMock
) -> None:
    await _setup(hass)
    registry = er.async_get(hass)
    for key in ("aqi_o3", "aqi_pm2p5", "aqi_co", "aqi_no2", "aqi_so2", "aqi_pm10"):
        entries = [
            entry
            for entry in registry.entities.values()
            if entry.unique_id.endswith(f"-{key}")
        ]
        assert len(entries) == 1
        assert entries[0].disabled_by is er.RegistryEntryDisabler.INTEGRATION


async def test_weather_survives_air_quality_failure(
    hass: HomeAssistant, mock_client: MagicMock
) -> None:
    mock_client.air_quality_hourly.side_effect = ForecaError("no AQ here")
    await _setup(hass)

    weather = hass.states.get("weather.helsinki")
    assert weather is not None
    assert weather.state == "partlycloudy"

    aqi = hass.states.get("sensor.helsinki_air_quality_index")
    assert aqi is not None
    assert aqi.state == STATE_UNAVAILABLE

    day1 = hass.states.get("sensor.helsinki_air_quality_index_day_1")
    assert day1 is not None
    assert day1.state == STATE_UNAVAILABLE
