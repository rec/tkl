import struct, webbrowser
from bibliopixel.driver.server_driver import ServerDriver
# from bibliopixel.main import args


class BPX(ServerDriver):
    """
    A BiblioPixel driver for the xled driver for Twinkly™ lights.
    """

    def __init__(self, num=32, port=1337, **kwds):
        """
        Args:
            num:  number of LEDs on the Twinkly.
            port:  the port on which the BPX lights is running.
            **kwds:  keywords passed to DriverBase.
        """
        super().__init__(num, address=port, **kwds)

    def _send_packet(self):
        if not self.server:
            raise ValueError(
                'Tried to send a packet before Layout.start() was called')
        self.server.update(pixels=self._buf)
