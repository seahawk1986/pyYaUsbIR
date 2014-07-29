#!/usr/bin/env python3
#from __future__ import division
#from __future__ import print_function
#import dbus
import logging
from optparse import OptionParser
import sys
import usb.core
import usb.control
from gi.repository import GObject
#from dbus.mainloop.glib import DBusGMainLoop
#dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

from output import Output, OutputDev


def read_data():
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
                duration = data[1] * result
                if data[n] is 0 and data[n+1] is 0:
                    break
                #print("%s %s us - raw: 0x%02x%02x" % (t, duration, data[n], data[n+1]))
                if t: typ = "pulse"
                else: typ = "space"
                #print(typ, duration)
                if "RC-6" in protocols:
                    rc6decoder.addEvent(t, duration)
                if "NEC" in protocols:
                    necdecoder.addEvent(t, duration)
                if "SAMSUNG" in protocols:
                    samsungdecoder.addEvent(t, duration)
                if "RC-5" in protocols:
                    rc5decoder.addEvent(t, duration)

    except usb.core.USBError as e:
        #print(e.args)
        pass
    return True

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("-s", "--socket", dest = "socket", default="/var/run/lirc/lircd.ya")
    parser.add_option("-k", "--keymap", dest="keymap", default="keymap.txt", metavar = "KEYMAP")
    parser.add_option("-p", "--protocoll", dest="protocol", default="RC-5 RC-6 NEC SAMSUNG", metavar = "\"RC-5 RC-6 NEC SAMSUNG\"")

    (options, args) = parser.parse_args()
    protocols = options.protocol.split()
    print("enabled protocols:", protocols)

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
    
    output = Output(options.socket, 'lirc', options.keymap)
    #output.add_output_device(devicename='lirc', devicetype='lirc', match=['KEY_'], socket_path='/var/run/lird')
    if  "RC-5" in protocols:
        from rc5decoder import RC5Decoder
        rc5decoder = RC5Decoder(output)
    if "RC-6" in protocols:
        from rc6decoder import RC6Decoder
        rc6decoder = RC6Decoder(output)
    if "NEC" in protocols:
        from necdecoder import NECDecoder
        necdecoder = NECDecoder(output)
    if "SAMSUNG" in protocols:
        from samsungdecoder import Samsung32Decoder
        samsungdecoder = Samsung32Decoder(output)

    loop = GObject.MainLoop()
    a = GObject.idle_add(read_data)
    loop.run()
    
