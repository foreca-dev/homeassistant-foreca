from collections.abc import Generator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pyforeca import (
    AirQualityForecast,
    CurrentWeather,
    DailyForecast,
    HourlyForecast,
    Location,
)

pytest_plugins = "pytest_homeassistant_custom_component"


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations: None) -> None:
    """Enable loading custom integrations in all tests."""


CURRENT = CurrentWeather(
    time="2026-09-01T17:00+03:00",
    symbol="d200",
    symbol_phrase="partly cloudy",
    temperature=17.4,
    feels_like_temp=16.9,
    rel_humidity=62,
    dew_point=10.1,
    wind_speed=4.2,
    wind_dir=210,
    wind_gust=8.0,
    precip_prob=5,
    cloudiness=40,
    uv_index=2,
    pressure=1013.2,
    visibility=20000,
)

HOURLY = [
    HourlyForecast(
        time="2026-09-01T18:00+03:00",
        symbol="d300",
        temperature=16.0,
        feels_like_temp=15.2,
        wind_speed=3.9,
        wind_gust=7.1,
        wind_dir=200,
        precip_prob=10,
        precip_accum=0.0,
        rel_humidity=70,
        cloudiness=60,
    )
]

DAILY = [
    DailyForecast(
        date="2026-09-02",
        symbol="d310",
        max_temp=18.0,
        min_temp=9.0,
        precip_accum=1.2,
        precip_prob=40,
        max_wind_speed=6.0,
        max_wind_gust=11.0,
        wind_dir=225,
        uv_index=3,
    )
]

AIR_QUALITY = AirQualityForecast(
    time="2026-09-01T18:00+03:00",
    pollutant="Ozone",
    pollutant_phrase="Ozone",
    aqi=23,
    aqi_co=2,
    aqi_no2=5,
    aqi_o3=23,
    aqi_so2=1,
    aqi_pm10=8,
    aqi_pm2p5=11,
)

LOCATION = Location(
    id=100658225,
    name="Helsinki",
    country="Finland",
    timezone="Europe/Helsinki",
    lon=24.94,
    lat=60.17,
)


@pytest.fixture
def mock_client() -> Generator[MagicMock]:
    with (
        patch(
            "custom_components.foreca.config_flow.ForecaApiClient", autospec=True
        ) as flow_client_cls,
        patch(
            "custom_components.foreca.coordinator.ForecaApiClient",
            new=flow_client_cls,
        ),
    ):
        client = flow_client_cls.return_value
        client.location_info = AsyncMock(return_value=LOCATION)
        client.current = AsyncMock(return_value=CURRENT)
        client.forecast_hourly = AsyncMock(return_value=HOURLY)
        client.forecast_daily = AsyncMock(return_value=DAILY)
        client.air_quality_hourly = AsyncMock(return_value=[AIR_QUALITY])
        yield client
