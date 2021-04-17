# -*- coding: utf-8 -*-

"""
xled.realtime
~~~~~~~~~~~~~

Functions to support the realtime mode of the device.
"""

from __future__ import absolute_import

import base64
import math
import socket

from xled.control import ControlInterface

#: UDP port to send realtime frames to
REALTIME_UDP_PORT_NUMBER = 7777


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

    def start_realtime(self):
        self.control.set_mode('rt')

    def send_frame(self, data):
        """
        Sends a realtime frame. Before calling this, start_realtime() must have
        been called.

        :param bytearray data: byte array containing the raw frame data
        :rtype: None
        """
        data_size = self.nleds*self.bytes_per_led
        assert len(data) == data_size
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            access_token = self.control.session.access_token
            for packet in _packets(data, self.nleds, access_token):
                sock.sendto(packet, (self.control.host, REALTIME_UDP_PORT_NUMBER))


def _packets(data, nleds, access_token):
    if len(data) < 900 and nleds < 256:
        # Send single frame
        packet = bytearray(b'\x01')
        packet.extend(base64.b64decode(access_token))
        packet.extend(bytes([nleds]))
        packet.extend(data)
        yield packet

    else:
        # Send multi frame
        packet_size = 900//self.bytes_per_led
        for i in range(0, math.ceil(len(data)/packet_size)):
            packet_data = data[:(900//self.bytes_per_led)]
            data = data[(900//self.bytes_per_led):]
            packet = [ b'\x03', base64.b64decode(access_token),
                b'\x00\x00', bytes([i])]
            packet.append(packet_data)
            yield packets
