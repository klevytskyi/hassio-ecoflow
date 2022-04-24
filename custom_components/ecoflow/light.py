from typing import Callable

from homeassistant.components.light import (COLOR_MODE_ONOFF, SUPPORT_EFFECT,
                                            LightEntity)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from . import CONF_PRODUCT, DOMAIN, EcoFlowEntity, HassioEcoFlowClient
from .ecoflow.local import has_light, send

_EFFECTS = ["Low", "High", "SOS"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: Callable):
    client: HassioEcoFlowClient = hass.data[DOMAIN][entry.entry_id]
    if has_light(entry.data[CONF_PRODUCT]):
        async_add_entities([
            LedEntity(client),
        ])


class LedEntity(EcoFlowEntity[dict], LightEntity):
    _attr_effect = _EFFECTS[0]
    _attr_effect_list = _EFFECTS
    _attr_supported_color_modes = {COLOR_MODE_ONOFF}
    _attr_supported_features = SUPPORT_EFFECT

    def __init__(self, client: HassioEcoFlowClient):
        super().__init__(client, "pd")
        self._attr_name += " light"

    @property
    def effect(self):
        value = self.coordinator.data.get("light_state", 0)
        if value > 0:
            return _EFFECTS[value - 1]

    @property
    def is_on(self):
        return self.coordinator.data.get("light_state", 0) != 0

    async def async_turn_off(self, **kwargs):
        await self._client.request(send.set_light(self._client.product, 0))
        await self.coordinator.async_request_refresh()

    async def async_turn_on(self, effect: str = None, **kwargs):
        if not effect:
            effect = self.effect or _EFFECTS[0]
        await self._client.request(
            send.set_light(self._client.product, _EFFECTS.index(effect) + 1))
        await self.coordinator.async_request_refresh()