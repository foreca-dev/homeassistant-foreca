from unittest.mock import MagicMock

from homeassistant.components.weather import (
    ATTR_CONDITION_CLEAR_NIGHT,
    ATTR_CONDITION_CLOUDY,
    ATTR_CONDITION_FOG,
    ATTR_CONDITION_LIGHTNING_RAINY,
    ATTR_CONDITION_PARTLYCLOUDY,
    ATTR_CONDITION_POURING,
    ATTR_CONDITION_RAINY,
    ATTR_CONDITION_SNOWY,
    ATTR_CONDITION_SNOWY_RAINY,
    ATTR_CONDITION_SUNNY,
    DOMAIN as WEATHER_DOMAIN,
    SERVICE_GET_FORECASTS,
)
from homeassistant.const import CONF_API_KEY, CONF_LATITUDE, CONF_LONGITUDE
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.foreca.const import DOMAIN, symbol_to_condition

ENTITY_ID = "weather.helsinki"


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


async def test_weather_state(hass: HomeAssistant, mock_client: MagicMock) -> None:
    await _setup(hass)
    state = hass.states.get(ENTITY_ID)
    assert state is not None
    assert state.state == ATTR_CONDITION_PARTLYCLOUDY
    assert state.attributes["temperature"] == 17.4
    assert state.attributes["humidity"] == 62
    assert state.attributes["pressure"] == 1013.2
    assert state.attributes["wind_bearing"] == 210
    assert state.attributes["attribution"] == "Data provided by Foreca"


async def test_forecasts(hass: HomeAssistant, mock_client: MagicMock) -> None:
    await _setup(hass)
    response = await hass.services.async_call(
        WEATHER_DOMAIN,
        SERVICE_GET_FORECASTS,
        {"entity_id": ENTITY_ID, "type": "daily"},
        blocking=True,
        return_response=True,
    )
    daily = response[ENTITY_ID]["forecast"]
    assert len(daily) == 1
    assert daily[0]["datetime"] == "2026-09-02"
    assert daily[0]["temperature"] == 18.0
    assert daily[0]["templow"] == 9.0
    assert daily[0]["condition"] == ATTR_CONDITION_RAINY

    response = await hass.services.async_call(
        WEATHER_DOMAIN,
        SERVICE_GET_FORECASTS,
        {"entity_id": ENTITY_ID, "type": "hourly"},
        blocking=True,
        return_response=True,
    )
    hourly = response[ENTITY_ID]["forecast"]
    assert len(hourly) == 1
    assert hourly[0]["condition"] == ATTR_CONDITION_PARTLYCLOUDY


def test_symbol_to_condition() -> None:
    assert symbol_to_condition("d000") == ATTR_CONDITION_SUNNY
    assert symbol_to_condition("n000") == ATTR_CONDITION_CLEAR_NIGHT
    assert symbol_to_condition("n100") == ATTR_CONDITION_CLEAR_NIGHT
    assert symbol_to_condition("d200") == ATTR_CONDITION_PARTLYCLOUDY
    assert symbol_to_condition("d300") == ATTR_CONDITION_PARTLYCLOUDY
    assert symbol_to_condition("d400") == ATTR_CONDITION_CLOUDY
    assert symbol_to_condition("d500") == ATTR_CONDITION_PARTLYCLOUDY
    assert symbol_to_condition("d600") == ATTR_CONDITION_FOG
    assert symbol_to_condition("n600") == ATTR_CONDITION_FOG
    assert symbol_to_condition("d210") == ATTR_CONDITION_RAINY
    assert symbol_to_condition("d320") == ATTR_CONDITION_RAINY
    assert symbol_to_condition("d430") == ATTR_CONDITION_POURING
    assert symbol_to_condition("d211") == ATTR_CONDITION_SNOWY_RAINY
    assert symbol_to_condition("d212") == ATTR_CONDITION_SNOWY
    assert symbol_to_condition("d422") == ATTR_CONDITION_SNOWY
    assert symbol_to_condition("d240") == ATTR_CONDITION_LIGHTNING_RAINY
    assert symbol_to_condition("d440") == ATTR_CONDITION_LIGHTNING_RAINY
    assert symbol_to_condition("d442") == ATTR_CONDITION_SNOWY
    assert symbol_to_condition(None) is None
    assert symbol_to_condition("bogus") is None
