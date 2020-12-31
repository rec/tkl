from bibliopixel.drivers.driver_base import DriverBase


class BPX(ServerDriver):
    """
    A BiblioPixel driver for the xled driver for Twinkly™ lights.
    """

    def __init__(self, num=32, xled_params_here=None, **kwds):
        """
        Args:
            num:  number of LEDs on the Twinkly.

            four_color:
                False means three colors.
                True means four colors, with white at the average of RGB.
                A number means four colors, but scale the white level.
                Scaling beyond 1 is possible but can result in clipping.

            to_xled: placeholder

            **kwds:  keywords passed to DriverBase.
        """
        super().__init__(num, four_color=0, xled_params=None, **kwds)

        assert self.four_color >= 0
        self.four_color = four_color
        self.four_color_bytes = four_color is not False and bytearray(4 * n)

        # TODO: Initialize connection with xled here using xled_params

    def _send_packet(self):
        if self.four_color_bytes:
            buffer = self.four_color_bytes

            for i in range(self.numLEDs):
                color = self._buf[3 * i: 3 * i + 3]
                white = min(255, int(self.four_color * sum(color) / 3))
                buffer[4 * i : 4 * i + 4] = (*color, white)
        else:
            buffer = self._buf

        # `buffer` is a bytearray looking like this:
        #    RGBRGBRGB... if four_color is False
        #    RGBWRGBWRGBW... if four_color is True, or any number

        # TODO: send `buffer` as an update to xled here!
