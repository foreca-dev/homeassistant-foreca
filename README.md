# Foreca integration for Home Assistant

[![CI](https://github.com/foreca-dev/homeassistant-foreca/actions/workflows/ci.yml/badge.svg)](https://github.com/foreca-dev/homeassistant-foreca/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

Weather integration for [Home Assistant](https://www.home-assistant.io) backed by
the [Foreca Weather API](https://developer.foreca.com).

One weather entity and 32 sensors:

- `weather` entity with current conditions, a 10-day daily forecast and a 48-hour
  hourly forecast
- Precipitation nowcast: when precipitation starts within the next hour, and the
  average and total expected over that hour
- Measurements from the nearest reporting weather station: temperature, humidity,
  and — disabled by default — pressure, wind speed, wind gust speed and snow depth
- Today's outlook: thunderstorm probability, precipitation intensity and type,
  solar radiation now and for the day, snow depth, snow accumulation, sunshine
  duration and Foreca's own forecast confidence
- Air quality: general AQI, dominant pollutant, daily AQI for the next three days,
  and per-pollutant sub-indices (disabled by default)
- Plan usage: requests made today and this month, so you can watch your quota

Air quality follows the US EPA air quality index. The values come from atmospheric
composition models, blended with measurements from air quality monitoring stations
where one is close by: near a station the first hours lean on the measurements and
then fade into the model. Further from any station, the values are model output alone.

## Getting an API key

Create a free account at [developer.foreca.com](https://developer.foreca.com),
pick the Freemium plan, verify your email and copy the key from **My API**. The
integration polls every 30 minutes, eight requests per poll for one location, so
about 384 requests per day. That is well inside the Freemium plan's 2,000 requests
per day; the count doubles for a second location, and the limit allows about five.

The Freemium plan is free for non-commercial use — hobbyist, student, and research
projects — and is provided without an SLA or support. Commercial use, a larger quota, or the
rest of Foreca's weather products need a
[paid plan](https://business.foreca.com/weather-api/pricing).

## Status

This is the development home for the integration on its way into
[Home Assistant Core](https://github.com/home-assistant/core)
(`homeassistant/components/foreca/`). The `custom_components/foreca/` layout
lets it run as-is in a development Home Assistant instance in the meantime. The
API client lives in [pyforeca](https://github.com/foreca-dev/pyforeca).

The component here is kept in step with the version prepared for Core; the two
differ only in packaging. This repository will be archived once the Core
integration is merged.

## Development

```bash
python3.13 -m venv .venv
.venv/bin/pip install homeassistant pytest-homeassistant-custom-component -e ../pyforeca
.venv/bin/pytest

# Run a development Home Assistant instance against this component
mkdir -p config/custom_components
ln -sfn ../../custom_components config/custom_components/foreca
.venv/bin/hass -c config
```

Maintained by [Foreca](https://business.foreca.com) in the
[foreca-dev](https://github.com/foreca-dev) organization. Released under the
[MIT License](LICENSE).
