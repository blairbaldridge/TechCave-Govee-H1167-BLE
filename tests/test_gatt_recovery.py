"""Offline BLE tests for H1167 GATT error recovery."""
from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1] / "custom_components" / "govee_light_ble"


def import_api():
    pkg = types.ModuleType("govee_light_ble")
    pkg.__path__ = [str(ROOT)]
    bleak = types.ModuleType("bleak")
    bleak.BleakClient = object
    retry = types.ModuleType("bleak_retry_connector")
    retry.establish_connection = None
    ha = types.ModuleType("homeassistant")
    ha.__path__ = []
    components = types.ModuleType("homeassistant.components")
    components.__path__ = []
    bluetooth = types.ModuleType("homeassistant.components.bluetooth")
    bluetooth.async_ble_device_from_address = lambda *_args, **_kw: None
    components.bluetooth = bluetooth
    core = types.ModuleType("homeassistant.core")
    core.HomeAssistant = object
    stub = {
        "govee_light_ble": pkg, "bleak": bleak,
        "bleak_retry_connector": retry, "homeassistant": ha,
        "homeassistant.components": components,
        "homeassistant.components.bluetooth": bluetooth,
        "homeassistant.core": core,
    }

    def load(name, path):
        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
        return module

    with patch.dict(sys.modules, stub):
        load("govee_light_ble.const", ROOT / "const.py")
        util = load("govee_light_ble.api_utils", ROOT / "api_utils.py")
        api = load("govee_light_ble.api", ROOT / "api.py")
    return api, util


class Char:
    uuid = "00010203-0405-0607-0809-0a0b0c0d2b11"
    properties = ["write-without-response"]


class NotifyChar:
    uuid = "00010203-0405-0607-0809-0a0b0c0d2b10"
    properties = ["notify"]


class Services:
    def __init__(self, *, missing_write=False):
        self.missing_write = missing_write

    def __iter__(self):
        # The integration enumerates characteristics for diagnostics when
        # service discovery omits a required characteristic.
        characteristics = [NotifyChar()]
        if not self.missing_write:
            characteristics.append(Char())
        return iter([types.SimpleNamespace(characteristics=characteristics)])

    def get_characteristic(self, uuid):
        if uuid.endswith("2b11") and not self.missing_write:
            return Char()
        if uuid.endswith("2b10"):
            return NotifyChar()
        return None


class Client:
    def __init__(self, fail=None, *, missing_write=False):
        self.services = Services(missing_write=missing_write)
        self.is_connected = True
        self.fail = fail
        self.writes = []
        self.disconnects = 0
        self.notifications = 0

    async def start_notify(self, *_args):
        self.notifications += 1
        raise AssertionError("H1167 should not request notifications")

    async def write_gatt_char(self, _char, frame, *, response):
        self.writes.append((frame, response))
        if self.fail:
            raise self.fail

    async def disconnect(self):
        self.disconnects += 1
        self.is_connected = False


class TestGATTRecovery(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.module, utils = import_api()
        self.frame = utils.generate_frame(0x33, 0x01, bytes([1]))
        self.module.bluetooth.async_ble_device_from_address = (
            lambda *_args, **_kw: types.SimpleNamespace(name="Govee H1167")
        )
        self.clients = []
        self.calls = []

        async def connect(_cls, device, name, *, max_attempts):
            self.calls.append((device, name, max_attempts))
            return self.clients[len(self.calls) - 1]

        self.module.establish_connection = connect
        self.api = self.module.GoveeAPI(
            object(), "AB:CD:EF:01:02:03", lambda: None, write_only=True
        )

    async def test_no_notification_or_unobservable_poll(self):
        self.clients = [Client()]
        await self.api.request_state(power_only=True)
        self.assertEqual(self.calls, [])
        await self.api.set_h1167_mode(self.frame)
        self.assertEqual(len(self.calls), 1)
        self.assertEqual(self.clients[0].notifications, 0)
        self.assertEqual(self.clients[0].writes, [(self.frame, False)])

    async def test_service_discovery_failure_reconnects(self):
        self.clients = [
            Client(fail=RuntimeError("Service Discovery has not been performed yet")),
            Client(),
        ]
        with patch.object(self.module.asyncio, "sleep", return_value=None):
            await self.api.set_h1167_mode(self.frame)
        self.assertEqual(len(self.calls), 2)
        self.assertEqual(self.clients[0].disconnects, 1)
        self.assertEqual(self.clients[1].writes, [(self.frame, False)])

    async def test_unknown_object_reconnects(self):
        self.clients = [
            Client(fail=RuntimeError(
                '[org.freedesktop.DBus.Error.UnknownObject] Method "WriteValue" does not exist'
            )),
            Client(),
        ]
        with patch.object(self.module.asyncio, "sleep", return_value=None):
            await self.api.set_h1167_mode(self.frame)
        self.assertEqual(len(self.calls), 2)

    async def test_missing_write_characteristic_recovers_on_second_discovery(self):
        self.clients = [Client(missing_write=True), Client()]
        with self.assertLogs("govee_light_ble.api", level="INFO") as captured:
            with patch.object(self.module.asyncio, "sleep", return_value=None) as delay:
                await self.api.set_h1167_mode(self.frame)

        self.assertEqual(len(self.calls), 2)
        delay.assert_awaited_once_with(0.4)
        self.assertEqual(self.clients[0].disconnects, 1)
        self.assertEqual(self.clients[0].writes, [])
        self.assertEqual(self.clients[1].writes, [(self.frame, False)])
        self.assertEqual(self.clients[1].notifications, 0)
        logs = "\n".join(captured.output)
        self.assertIn("initial GATT discovery is missing", logs)
        self.assertIn("service rediscovery succeeded", logs)
        self.assertIn("command completed after one automatic reconnect", logs)

    async def test_missing_write_characteristic_fails_after_one_retry(self):
        self.clients = [Client(missing_write=True), Client(missing_write=True)]
        with self.assertLogs("govee_light_ble.api", level="WARNING") as captured:
            with patch.object(self.module.asyncio, "sleep", return_value=None):
                with self.assertRaisesRegex(
                    ConnectionError, "required WRITE characteristic"
                ):
                    await self.api.set_h1167_mode(self.frame)

        self.assertEqual(len(self.calls), 2)
        self.assertEqual([c.disconnects for c in self.clients], [1, 1])
        self.assertEqual([c.writes for c in self.clients], [[], []])
        self.assertIn("command failed after one automatic reconnect", "\n".join(captured.output))

    async def test_other_devices_do_not_retry_missing_write_characteristic(self):
        # Retry policy is deliberately limited to H1167/write-only devices.
        self.api.write_only = False
        self.clients = [Client(missing_write=True)]
        with self.assertRaisesRegex(ConnectionError, "required WRITE characteristic"):
            await self.api.set_h1167_mode(self.frame)
        self.assertEqual(len(self.calls), 1)
        self.assertEqual(self.clients[0].disconnects, 1)

    async def test_unrelated_error_not_retried(self):
        self.clients = [Client(fail=RuntimeError("unexpected failure"))]
        with self.assertRaisesRegex(RuntimeError, "unexpected failure"):
            await self.api.set_h1167_mode(self.frame)
        self.assertEqual(len(self.calls), 1)
        self.assertEqual(self.clients[0].disconnects, 1)

    async def test_retry_is_limited_to_one_reconnect(self):
        self.clients = [
            Client(fail=RuntimeError("Service Discovery has not been performed yet")),
            Client(fail=RuntimeError("Service Discovery has not been performed yet")),
        ]
        with patch.object(self.module.asyncio, "sleep", return_value=None):
            with self.assertRaisesRegex(RuntimeError, "Service Discovery"):
                await self.api.set_h1167_mode(self.frame)
        self.assertEqual(len(self.calls), 2)
        self.assertEqual(self.clients[1].disconnects, 1)
