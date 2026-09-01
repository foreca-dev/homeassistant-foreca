# Foreca integration for Home Assistant

Weather integration backed by the [Foreca Weather API](https://developer.foreca.com).
Provides a `weather` entity with current conditions plus daily (10-day) and hourly
(48-hour) forecasts.

Get an API key by creating a free account at
[developer.foreca.com](https://developer.foreca.com) — the Freemium plan
(2,000 requests/day) covers this integration's usage (~150 requests/day) many
times over.

This repository is the development home for the integration targeted at
inclusion in [Home Assistant Core](https://github.com/home-assistant/core)
(`homeassistant/components/foreca/`). The `custom_components/foreca/` layout
lets it run as-is in a development Home Assistant instance.

## Development

```bash
python3.13 -m venv .venv
.venv/bin/pip install homeassistant pytest-homeassistant-custom-component -e ../pyforeca
.venv/bin/pytest
.venv/bin/hass -c config   # config/custom_components symlinks to ./custom_components
```
