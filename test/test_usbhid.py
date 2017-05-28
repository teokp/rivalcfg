import pytest

import rivalcfg.usbhid


class TestIsDevicePlugged(object):

    def test_not_plugged_mouse(self):
        assert not rivalcfg.usbhid.is_device_plugged(0x1038, 0x0001)

    def test_debug_mouse_plugged(self, monkeypatch):
        monkeypatch.setattr("rivalcfg.debug.DEBUG", True)
        monkeypatch.setenv("RIVALCFG_PROFILE", "1038:0002")
        assert not rivalcfg.usbhid.is_device_plugged(0x1038, 0x0001)
        assert rivalcfg.usbhid.is_device_plugged(0x1038, 0x0002)
