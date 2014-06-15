import sys
import time
import usb.core
import usb.control

from rc5encoder import RC5Encoder
from rc5decoder import RC5Decoder
from sonyencoder import SonyEncoder

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

endpoint = device[0][(0,0)][1]

#encoder = RC5Encoder()
encoder = SonyEncoder()
#command = encoder.send_hexcode(0x1e17)
#endpoint.write(command)

command = encoder.send_hexcode(0x70,12)
#for i in command:
#  print(hex(i))
endpoint.write(command)
#time.sleep(sleep_int)
#endpoint.write(command)
#time.sleep(sleep_int)
#endpoint.write(command)
#command = encoder.send_bytestring("0b11111110010110")
#print(command)
#endpoint.write(command)
#endpointr.read(endpointr.bEndpointAddress, endpointr.wMaxPacketSize)
#command = [0x01, 0x4E, 0x89, 0x15, 0x89, 0x08, 0x89, 0x00, 0x89, 0x11]#
"""command = [0x01, 0x4E, 0x89, 0x15 ]
endpoint.write(command, timeout=50)
command = [0x01, 0x4E, 0x89, 0x08 ]
endpoint.write(command, timeout=50)
command = [0x01, 0x4E, 0x89, 0x01 ]
endpoint.write(command, timeout=50)
command = [0x01, 0x4E, 0x89, 0x11]"""

#print(command)
#endpoint.write(command, timeout=50)

#time.sleep(2)
#command = [0x01, 0x4F, 0x89, 0x15, 0x89, 0x08, 0x89, 0x01, 0x89, 0x11]
#endpoint.write(command)
