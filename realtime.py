"""
xled.realtime
~~~~~~~~~~~~~

Functions to support the realtime mode of the device.
"""

from __future__ import absolute_import

import base64
import math
import socket
from threading import Thread

from xled.control import ControlInterface
from queue import Queue

#: realtime UDP port to send realtime frames to
PORT = 7777


class RealtimeChannel(object):
    """
    Main interface to send realtime frames to device.

    :param control: An activated ControlInterface for the device to control
    :param int nleds: the number of leds in a frame
    :param int bytes_per_led: the number of bytes per led (3 or 4)
    """

    def __init__(self, control, nleds, bytes_per_led):
        self.control = control
        self.nleds = nleds
        self.bytes_per_led = bytes_per_led
        self.queue = Queue()
        self.thread = None

    def start_realtime(self):
        if not self.thread:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.control.set_mode('rt')
            self.thread = Thread(target=self._target, daemon=True)
            self.thread.start()

    def stop(self):
        self.queue.put(None)

    def __del__(self):
        self.stop()

    def _target(self):
        while True:
            data = self.queue.get()
            if not data:
                break
            data_size = self.nleds * self.bytes_per_led
            assert len(data) == data_size
            token = self.control.session.access_token
            for p in _packets(data, self.nleds, token, self.bytes_per_led):
                self.sock.sendto(p, (self.control.host, PORT))

    def send_frame(self, data):
        """
        Sends a realtime frame. Before calling this, start_realtime() must have
        been called.

        :param bytearray data: byte array containing the raw frame data
        :rtype: None
        """
        self.queue.put(data)


def _packets(data, nleds, access_token, bytes_per_led):
    if len(data) < 900 and nleds < 256:
        # Send single frame
        packet = bytearray(b'\x01')
        packet.extend(base64.b64decode(access_token))
        packet.extend(bytes([nleds]))
        packet.extend(data)
        yield packet

    else:
        # Send multi frame
        packet_size = 900 // bytes_per_led
        for i in range(0, math.ceil(len(data) / packet_size)):
            packet_data = data[: (900 // bytes_per_led)]
            data = data[(900 // bytes_per_led) :]
            packet = [
                b'\x03',
                base64.b64decode(access_token),
                b'\x00\x00',
                bytes([i]),
            ]
            packet.append(packet_data)
            yield packets
