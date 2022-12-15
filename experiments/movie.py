import xled, random
from xled import realtime
import time


def frame():
    return bytes(random.randint(0, 255) for i in range(750))


dd = xled.discover.discover()
control = xled.ControlInterface(dd.ip_address, dd.hw_address)
rtc = realtime.RealtimeChannel(control, 250, 3)
rtc.start_realtime()

BLACK = bytes(750 * [0])
FRAMES = [frame(), frame(), frame(), frame(), frame(), BLACK, BLACK]

for i in range(0, 255):
    rtc.send_frame(FRAMES[i % len(FRAMES)])
    time.sleep(0.05)

rtc.send_frame(BLACK)
