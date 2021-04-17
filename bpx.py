from bibliopixel.drivers.driver_base import DriverBase
from bibliopixel.drivers.simpixel import SimPixel
from xled.realtime import RealtimeChannel
import xled


class BPX(DriverBase):
    """
    A BiblioPixel driver for the xled driver for Twinkly™ lights.
    """
    def __init__(self, *args, address=None, white_ratio=1, **kwds):
        """
        Args:
            address
                If address is None, discover any LED string.
                Otherwise, address must be a pair of strings representing
                IP address and HW address, or a string containing those
                addresses separated by a /

            white_ratio
                For RGBW LEDs, the white component is the average of the
                RGB components, scaled by `white_ratio` (default 1)

            **kwds:  keywords passed to DriverBase.
        """
        super().__init__(*args, **kwds)
        self.white_ratio = white_ratio

        if not address:
            dd = xled.discover.discover()
            address = dd.ip_address, dd.hw_address,
        elif isinstance(address, str):
            address = address.split('/')
        if len(address) != 2:
            raise ValueError(f'Bad address {address}')

        self.control = xled.ControlInterface(*address)
        self.info = self.control.get_device_info()

        actual_leds = self.info['number_of_led']
        if actual_leds != self.numLEDs:
            raise ValueError(f'Set shape: {actual_leds} in the BP project')

        self.colors_per_led = len(self.info['led_profile'])
        if self.colors_per_led != 3:
            assert self.colors_per_led in 1, 4
            self.buffer = bytearray(self.colors_per_led * num)
        else:
            self.buffer = self._buf
        self.rtc = RealtimeChannel(self.control, 250, 3)
        self.rtc.start_realtime()

    def _compute_packet(self):
        self._render()
        if self.colors_per_led == 3:
            return

        # TODO: use numpy
        for i in range(self.numLEDs):
            color = self._buf[3 * i : 3 * i + 3]
            white = min(255, int(self.use_white * sum(color) / 3))
            if self.colors_per_led == 1:
                self.buffer[i] = white
            else:
                self.buffer[4 * i : 4 * i + 4] = (*color, white)

    def _send_packet(self):
        self.rtc.send_frame(self.buffer)
