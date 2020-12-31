from bibliopixel.drivers.driver_base import DriverBase


class BPX(ServerDriver):
    """
    A BiblioPixel driver for the xled driver for Twinkly™ lights.
    """

    def __init__(self, num=32, use_white=False, xled_params_here=None, **kwds):
        """
        Args:
            num:  number of LEDs on the Twinkly.

            use_white:
                False means three colors.
                True means four colors, with white at the average of RGB.
                A number means four colors, but scale the white level.
                Scaling beyond 1 is possible but can result in clipping.

            to_xled: placeholder

            **kwds:  keywords passed to DriverBase.
        """
        super().__init__(num, xled_params=None, **kwds)

        assert self.use_white >= 0
        self.use_white = use_white
        self.white_bytes = use_white is not False and bytearray(4 * n)

        # TODO: Initialize connection with xled here using xled_params

    def _send_packet(self):
        if self.white_bytes:
            buffer = self.white_bytes

            for i in range(self.numLEDs):
                color = self._buf[3 * i: 3 * i + 3]
                white = min(255, int(self.use_white * sum(color) / 3))
                buffer[4 * i : 4 * i + 4] = (*color, white)
        else:
            buffer = self._buf

        # `buffer` is a bytearray looking like this:
        #    RGBRGBRGB... if use_white is False
        #    RGBWRGBWRGBW... if use_white is True, or any number

        # TODO: send `buffer` as an update to xled here!
