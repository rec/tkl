from bibliopixel.drivers.driver_base import DriverBase
import xled


class BPX(DriverBase):
    """
    A BiblioPixel driver for the xled driver for Twinkly™ lights.
    """

    def __init__(
        self, use_white=False, ip_address=None, hw_address=None, **kwds
    ):
        """
        Args:
            num:  number of LEDs on the Twinkly.

            use_white:
                False means three colors.
                True means four colors, with white at the average of RGB.
                A number means four colors, but scale the white level.
                Scaling beyond 1 is possible but can result in clipping.

            **kwds:  keywords passed to DriverBase.
        """
        dd = xled.discover.discover()
        self.control = xled.ControlInterface(
            ip_address or dd.ip_address, hw_address or dd.hw_address,
        )
        self.control.set_mode("rt")

        numLEDs = self.control.get_device_info()["number_of_led"]

        super().__init__(numLEDs, **kwds)

        assert self.use_white >= 0
        self.use_white = use_white
        self.rgbw = use_white is not False and bytearray(4 * numLEDs)

    def _send_packet(self):
        # Called on each BiblioPixel update
        self.control.set_rt_message(self._buffer())
        # xled.control.ControlInterface.set_rt_message() doesn't exist yet!

    def _buffer(self):
        # Returns a bytearray looking like this:
        #    RGBRGBRGB... if use_white is False
        #    RGBWRGBWRGBW... if use_white is True, or any number

        if self.rgbw:
            for i in range(self.numLEDs):
                color = self._buf[3 * i : 3 * i + 3]
                white = min(255, int(self.use_white * sum(color) / 3))
                self.rgbw[4 * i : 4 * i + 4] = (*color, white)

        return self.rgbw or self._buf
