from __future__ import division
import sys
import usb.core
import usb.control

from rc5decoder import RC5Decoder

ID_VENDOR = 0x10c4
ID_PRODUCT = 0x876c
device = usb.core.find(idVendor=ID_VENDOR, idProduct=ID_PRODUCT)
if device is None:
    sys.exit("Could not find yaUsbIr")
if device.is_kernel_driver_active(0):
    try:
        device.detach_kernel_driver(0)
    except usb.core.USBError as e:
        sys.exit("Could not detach Kernel driver: %s" % str(e))

try:
    device.set_configuration()
    device.reset()
except usb.core.USBError as e:
    sys.exit("Could not set configuration: %s" % str(e))

endpoint = device[0][(0,0)][0]
code = []

decoder = RC5Decoder()
while True:
    try:
        data = device.read(endpoint.bEndpointAddress, endpoint.wMaxPacketSize)
        irdata = 0
        last = 0
        for n in range(2, len(data), 2):
            if data[0] == 1:
                result = (int(data[n]) & 0x7F) << 8
                result = result | data[n + 1]
                if data[n] & 0x80 == 0x80:
                    t = True
                else: 
                    t = False
                duation = data[1] * result
                if data[n] is 0 and data[n+1] is 0:
                    break
                print("%s %s us - raw: 0x%02x%02x" % (t, duration, data[n], data[n+1]))
                decoder.addEvent(t, duration)

    except usb.core.USBError as e:
        #print(e.args)
        pass

    
