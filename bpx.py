from bibliopixel.drivers.driver_base import DriverBase
from io import BytesIO
import xled


class BPX(DriverBase):
    def __init__(
        self,
        num = 0,
        address = None,
        white_ratio = 1,
        use_socket = False,
        version = 3,
        **kwds
    ):
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
        self.white_ratio = white_ratio
        self.use_socket = use_socket
        self.version = version

        if not address:
            dd = xled.discover.discover()
            address = dd.ip_address, dd.hw_address,

        elif isinstance(address, str):
            address = address.split('/')

        if len(address) != 2:
            raise ValueError(f'Bad address {address}')

        self.control = xled.ControlInterface(*address)
        self.info = self.control.get_device_info()

        self.actual_leds = self.info['number_of_led']
        self.colors_per_led = len(self.info['led_profile'])

        super().__init__(num or self.actual_leds, **kwds)

        assert self.colors_per_led in (1, 3, 4)
        self.buffer = bytearray(self.colors_per_led * self.actual_leds)

    def _compute_packet(self):
        self._render()
        # TODO: use numpy
        if self.colors_per_led == 3:
            if len(self.buffer) >= len(self._buf):
                self.buffer[:len(self._buf)] = self._buf
            else:
                self.buffer[:] = self._buf[:len(self.buffer)]
        else:
            for i in range(min(self.actual_leds, self.numLEDs)):
                color = self._buf[3 * i : 3 * i + 3]
                white = min(255, int(self.use_white * sum(color) / 3))
                if self.colors_per_led == 1:
                    self.buffer[i] = white
                else:
                    self.buffer[4 * i : 4 * i + 4] = (*color, white)

    def _send_packet(self):
        fp = BytesIO(self.buffer)
        if self.use_socket:
            self.control.set_rt_frame_socket(fp, version=self.version)
        else:
            self.control.set_rt_frame_rest(fp)
