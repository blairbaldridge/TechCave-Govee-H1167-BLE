"""Exercise first-run wizard logic with tiny HA/voluptuous test doubles.

Tests the app-facing choices, not Home Assistant's own form renderer.
"""

import asyncio
import importlib.util
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1] / 'custom_components/govee_light_ble'


def load_flow():
    ads = []
    async def fake_active_scan(hass, duration=None):
        return None

    class FakeInfo:
        def __init__(self, address, name):
            self.address = address
            self.name = name

    class FakeFlow:
        def __init_subclass__(cls, **kwargs):
            return super().__init_subclass__()
        async def async_set_unique_id(self, value):
            self.unique_id = value
        def _async_current_entries(self):
            return getattr(self, 'entries', [])
        def _abort_if_unique_id_configured(self):
            if self.unique_id in [x.unique_id for x in self._async_current_entries()]:
                raise RuntimeError('already_configured')
        def async_create_entry(self, **kwargs):
            return {'type': 'create_entry', **kwargs}
        def async_abort(self, **kwargs):
            return {'type': 'abort', **kwargs}
        def async_show_form(self, **kwargs):
            return {'type': 'form', **kwargs}

    def mod(name, **attrs):
        obj = types.ModuleType(name)
        obj.__dict__.update(attrs)
        return obj
    vol = mod('voluptuous', Required=lambda x, **kw:x, Optional=lambda x, **kw:x, In=lambda x:x, Schema=lambda x:x)
    bluetooth = mod('homeassistant.components.bluetooth',
        BluetoothServiceInfoBleak=FakeInfo,
        async_discovered_service_info=lambda hass, connectable=True: ads,
        async_request_active_scan=fake_active_scan)
    mods = {
        'voluptuous': vol,
        'homeassistant': mod('homeassistant'),
        'homeassistant.components': mod('homeassistant.components', bluetooth=bluetooth),
        'homeassistant.components.bluetooth': bluetooth,
        'homeassistant.config_entries': mod('homeassistant.config_entries', ConfigFlow=FakeFlow),
        'homeassistant.const': mod('homeassistant.const', CONF_ADDRESS='address', CONF_NAME='name'),
        'govee_light_ble': mod('govee_light_ble', __path__=[str(ROOT)]),
        'govee_light_ble.const': mod('govee_light_ble.const', DOMAIN='govee_light_ble'),
    }
    with patch.dict(sys.modules, mods):
        spec = importlib.util.spec_from_file_location('govee_light_ble.discovery', ROOT/'discovery.py')
        discovery = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(discovery)
        with patch.dict(sys.modules, {'govee_light_ble.discovery': discovery}):
            spec = importlib.util.spec_from_file_location('govee_light_ble.config_flow', ROOT/'config_flow.py')
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
    return module.GoveeConfigFlow, FakeInfo, ads


class TestSetupFlow(unittest.TestCase):
    def new_flow(self):
        klass, info, ads = load_flow()
        obj = klass()
        obj.hass = object()
        obj.context = {}
        obj.entries = []
        return obj, info, ads

    def test_discovered_dropdown_filters_other_devices_and_configured(self):
        obj, info, ads = self.new_flow()
        ads.extend([info('AA:00:00:00:00:11', 'Govee_H1167_LIVING'),
                    info('AA:00:00:00:00:22', 'Govee_H617C'),
                    info('AA:00:00:00:00:33', 'GVH1167_BEDROOM')])
        obj.entries = [types.SimpleNamespace(unique_id='AA:00:00:00:00:33', data={})]
        found = obj._discovered_devices()
        self.assertEqual(list(found), ['AA:00:00:00:00:11'])
        first = asyncio.run(obj.async_step_user())
        self.assertEqual(first['step_id'], 'user')
        self.assertIn('AA:00:00:00:00:11', first['data_schema']['address'])
        made = asyncio.run(obj.async_step_user({'address': 'AA:00:00:00:00:11'}))
        self.assertEqual(made['data']['model'], 'H1167')
        self.assertEqual(made['data']['address'], 'AA:00:00:00:00:11')

    def test_no_scan_manual_entry_validates_address(self):
        obj, _, _ = self.new_flow()
        page = asyncio.run(obj.async_step_user({'address': '__manual__'}))
        self.assertEqual(page['step_id'], 'manual')
        bad = asyncio.run(obj.async_step_manual({'address':'123', 'name':''}))
        self.assertEqual(bad['errors'], {'address':'invalid_address'})
        good = asyncio.run(obj.async_step_manual({'address':'aa-bb-cc-dd-ee-ff','name':''}))
        self.assertEqual(good['data']['address'], 'AA:BB:CC:DD:EE:FF')
        self.assertEqual(good['data']['model'], 'H1167')

    def test_auto_discovery_requires_h1167_and_confirm(self):
        obj, info, _ = self.new_flow()
        reject = asyncio.run(obj.async_step_bluetooth(info('AA:00:00:00:00:11','Govee_H617A')))
        self.assertEqual(reject['reason'], 'not_h1167')
        confirm = asyncio.run(obj.async_step_bluetooth(info('AA:00:00:00:00:12','Govee_H1167_9876')))
        self.assertEqual(confirm['step_id'], 'bluetooth_confirm')
        created = asyncio.run(obj.async_step_bluetooth_confirm({}))
        self.assertEqual(created['data']['address'], 'AA:00:00:00:00:12')


if __name__ == '__main__':
    unittest.main()
