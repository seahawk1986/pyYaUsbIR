#!/usr/bin/env python3
#from __future__ import division
#from __future__ import print_function
import dbus
import errno
import logging
from optparse import OptionParser
import sys
import usb.core
import usb.control
from gi.repository import GObject
from dbus.mainloop.glib import DBusGMainLoop
dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
from ir_commands import yaUsbIR_Control
from output import Output, OutputDev

logging.basicConfig(level=logging.DEBUG)

class yaUsbIR():
    ID_VENDOR = 0x10c4
    ID_PRODUCT = 0x876c
    ID_VENDOR_ID = str(ID_VENDOR)
    ID_MODEL_ID = str(ID_PRODUCT)

    def __init__(self, options):
        self.decoders = []
        self.protocols = options.protocol.split()
        self.output = Output(options.socket, 'lirc', options.keymap)
        self.load_decoder()
        logging.info("enabled protocols: %s", self.protocols)
        self.device = None
        self.yausbir_send = None
        self.retry_delay = 1000  # 1 s
        if self.connect_device():
            self.reconnect = GObject.timeout_add(self.retry_delay, self.connect_device)
    
    def connect_device(self):
        if not self.device:
            self.device = usb.core.find(idVendor=self.ID_VENDOR, idProduct=self.ID_PRODUCT)
            if self.device is None:
                logging.error("no device found, retry in {} s".format(self.retry_delay / 1000))
                return True
            elif self.device.is_kernel_driver_active(0):
                try:
                    self.device.detach_kernel_driver(0)
                    logging.debug("detached kernel driver successfully")
                except usb.core.USBError as e:
                    logging.error("Could not detach Kernel driver: %s" % str(e))
                    return True
            try:
                self.device.set_configuration()
                self.device.reset()
                self.endpoint = self.device[0][(0,0)][0]
                if self.yausbir_send:
                    self.yausbir_send.device = self.device
                    self.yausbir_send.set_endpoint_w()
                else:
                    self.yausbir_send = yaUsbIR_Control(self.device)
                self.yausbir_send.device = self.device
                self.read = GObject.idle_add(self.read_data)
                logging.info("connection to yaUsbIR established, ready.")
                return False
            except usb.core.USBError as e:
                logging.error(e)
        return True

    def read_data(self):
        try:
            data = self.device.read(self.endpoint.bEndpointAddress, self.endpoint.wMaxPacketSize)
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
                    for decoder in self.decoders:
                        decoder.addEvent(t, duration)
    
        except usb.core.USBError as e:
            if e.errno != 110:  # ingore timeout errors when reading from device
                logging.error(e)
                self.device = None
                self.reconnect = GObject.timeout_add(self.retry_delay,
                                                     self.connect_device)
                return False
        return True

    def load_decoder(self):
        if  "RC-5" in self.protocols:
            from rc5decoder import RC5Decoder
            rc5decoder = RC5Decoder(self.output)
            self.decoders.append(rc5decoder)
        if "RC-6" in self.protocols:
            from rc6decoder import RC6Decoder
            rc6decoder = RC6Decoder(self.output)
            self.decoders.append(rc6decoder)
        if "NEC" in self.protocols:
            from necdecoder import NECDecoder
            necdecoder = NECDecoder(self.output)
            self.decoders.append(necdecoder)
        if "SAMSUNG" in self.protocols:
            from samsungdecoder import Samsung32Decoder
            samsungdecoder = Samsung32Decoder(self.output)
            self.decoders.append(samsungdecoder)


if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("-s", "--socket", dest = "socket", default="/var/run/lirc/lircd.ya")
    parser.add_option("-k", "--keymap", dest="keymap", default="keymap.txt", metavar = "KEYMAP")
    parser.add_option("-p", "--protocol", dest="protocol", default="RC-5 RC-6 NEC SAMSUNG", metavar = "\"RC-5 RC-6 NEC SAMSUNG\"")

    (options, args) = parser.parse_args()
    yausbir_reciever = yaUsbIR(options)
    
    #output.add_output_device(devicename='lirc', devicetype='lirc', match=['KEY_'], socket_path='/var/run/lird')

    loop = GObject.MainLoop()
    loop.run()
    
