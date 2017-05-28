from io import BytesIO

import usb.core
import usb.util

from . import debug


_BREQUEST_SET_REPORT = 0x09


def is_device_plugged(vendor_id, product_id):
    """Returns True if the given HID device is plugged to the computer.

    Arguments:
    vendor_id -- the mouse vendor id (e.g. 0x1038)
    product_id -- the mouse product id (e.g. 0x1710)
    """
    if debug.DEBUG:
        mouse_id = debug.get_debug_profile()
        if mouse_id:
            return mouse_id.vendor_id == vendor_id and mouse_id.product_id == product_id
    return usb.core.find(idVendor=vendor_id, idProduct=product_id) is not None


class HidDevice(object):

    """Manupulate HID devices."""

    def __init__(self, vendor_id, product_id, interface_number):
        """Constructor.

        Arguments:
        vendor_id -- the mouse vendor id (e.g. 0x1038)
        product_id -- the mouse product id (e.g. 0x1710)
        interface_number -- the interface number
        """
        self.vendor_id = vendor_id
        self.product_id = product_id
        self.interface_number = interface_number
        self.device = None

    def open(self):
        """Opens and returns the USB device. Raise IOError if the device is not
        available.
        """
        # Dry run
        if debug.DEBUG and debug.DRY and is_device_plugged(self.vendor_id, self.product_id):
            self.device = BytesIO()  # Moke the device
            return

        self.device = usb.core.find(
                idVendor=self.vendor_id,
                idProduct=self.product_id
                )

        if not self.device:
            raise IOError("Unable to find the requested device: %04X:%04X" % (
                self.vendor_id, self.product_id))

        if self.device.is_kernel_driver_active(self.interface_number):
            self.device.detach_kernel_driver(self.interface_number)

        usb.util.claim_interface(self.device, self.interface_number)

    def set_report(self, data, wValue=0x0000):
        """Send a "SET_REPORT" request to the device with given parts dand data.

        Arguments:
        data -- the data fragment to write to the device

        Keywork arguments:
        wValue -- the wValue part of the request (Report Type and Report ID, default=0x0000)
        """

        # Fake device
        if type(self.device) is BytesIO:
            self.device.write(data)
            return

        bmRequestType = usb.util.build_request_type(
                usb.util.CTRL_OUT,
                usb.util.CTRL_TYPE_CLASS,
                usb.util.CTRL_RECIPIENT_INTERFACE)

        wIndex = self.interface_number

        self.device.ctrl_transfer(bmRequestType, _BREQUEST_SET_REPORT,
                wValue, wIndex, data)

    def close(self):
        """Close the device."""

        # Fake device
        if type(self.device) is BytesIO:
            self.device.close()
            return

        usb.util.release_interface(self.device, self.interface_number)
        self.device.attach_kernel_driver(self.interface_number)

