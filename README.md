# Foreca integration for Home Assistant

[![CI](https://github.com/foreca-dev/homeassistant-foreca/actions/workflows/ci.yml/badge.svg)](https://github.com/foreca-dev/homeassistant-foreca/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

Weather integration for [Home Assistant](https://www.home-assistant.io) backed by
the [Foreca Weather API](https://developer.foreca.com).

- `weather` entity with current conditions, a 10-day daily forecast and a 48-hour
  hourly forecast
- Air-quality sensors: general AQI, dominant pollutant, per-pollutant sub-indices
  (disabled by default), and daily AQI for the next three days

Air-quality values are the model's estimate for the current hour or day, not a
monitoring-station measurement.

## Getting an API key

Create a free account at [developer.foreca.com](https://developer.foreca.com),
pick the Freemium plan, verify your email and copy the key from **My API**. The
integration polls every 30 minutes (five requests per poll, about 240 per day),
well inside the Freemium plan's 2,000 requests per day.

## Status

This is the development home for the integration on its way into
[Home Assistant Core](https://github.com/home-assistant/core)
(`homeassistant/components/foreca/`). The `custom_components/foreca/` layout
lets it run as-is in a development Home Assistant instance in the meantime. The
API client lives in [pyforeca](https://github.com/foreca-dev/pyforeca).

## Development

```bash
python3.13 -m venv .venv
.venv/bin/pip install homeassistant pytest-homeassistant-custom-component -e ../pyforeca
.venv/bin/pytest
.venv/bin/hass -c config   # config/custom_components symlinks to ./custom_components
```

Maintained by [Foreca](https://business.foreca.com) in the
[foreca-dev](https://github.com/foreca-dev) organization. Released under the
[MIT License](LICENSE).
