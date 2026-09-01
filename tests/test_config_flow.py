from unittest.mock import MagicMock

from pyforeca import ForecaAuthError, ForecaConnectionError
from homeassistant.config_entries import SOURCE_USER
from homeassistant.const import CONF_API_KEY, CONF_LATITUDE, CONF_LONGITUDE
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.foreca.const import DOMAIN

USER_INPUT = {
    CONF_API_KEY: "test-key",
    "location": {CONF_LATITUDE: 60.17, CONF_LONGITUDE: 24.94},
}


async def test_full_flow(hass: HomeAssistant, mock_client: MagicMock) -> None:
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {}

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], USER_INPUT
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == "Helsinki"
    assert result["data"] == {
        CONF_API_KEY: "test-key",
        CONF_LATITUDE: 60.17,
        CONF_LONGITUDE: 24.94,
    }


async def test_invalid_auth(hass: HomeAssistant, mock_client: MagicMock) -> None:
    mock_client.location_info.side_effect = ForecaAuthError
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], USER_INPUT
    )
    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "invalid_auth"}

    mock_client.location_info.side_effect = None
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], USER_INPUT
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY


async def test_cannot_connect(hass: HomeAssistant, mock_client: MagicMock) -> None:
    mock_client.location_info.side_effect = ForecaConnectionError
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], USER_INPUT
    )
    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "cannot_connect"}


async def test_unknown_error(hass: HomeAssistant, mock_client: MagicMock) -> None:
    mock_client.location_info.side_effect = ValueError
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], USER_INPUT
    )
    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "unknown"}


async def test_duplicate_aborts(hass: HomeAssistant, mock_client: MagicMock) -> None:
    MockConfigEntry(
        domain=DOMAIN,
        unique_id="60.1700-24.9400",
        data={CONF_API_KEY: "k", CONF_LATITUDE: 60.17, CONF_LONGITUDE: 24.94},
    ).add_to_hass(hass)
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], USER_INPUT
    )
    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"
