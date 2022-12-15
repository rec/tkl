import xled


def control():
    dd = xled.discover.discover()
    return xled.ControlInterface(dd.ip_address, dd.hw_address)
