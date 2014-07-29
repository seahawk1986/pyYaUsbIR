#!/usr/bin/python
# -*- encoding:utf-8 -*-
import struct
import bitarray

class Samsung32Decoder:
    start_p_min = 4000
    start_p_max = 5000
    start_s_min = 4000
    start_s_max = 5000
    s_min = 400
    s_max = 700
    l_min = 1500
    l_max = 1800
    
    def __init__(self, output):
        self.ircode = bitarray.bitarray()
        self.state = self.startBitP
        self.start()
        self.repeat = 0
        self.lastcode = None
        self.output = output

    def addEvent(self, t, duration):
        self.state(t, duration)

    def emitBit(self, bit):
        if bit in (0,1):
            self.ircode.append(bit)
        if len(self.ircode) == 32:
            self.addr, check_addr, self.cmd, check_cmd = struct.unpack('BBBB', self.ircode.tobytes())
            if self.addr == check_addr:
                # two identical bytes
                if self.cmd & 0xf == ~check_cmd & 0xf:
                    # complimentary data bytes
                    self.cmd = int('{:08b}'.format(self.cmd)[::-1], 2)
                    self.addr = int('{:08b}'.format(self.addr)[::-1], 2)
                    self.lastcode = self.ircode
                    self.send_code()
            else:
                #print("{0:08b} {1:08b}".format( self.addr, self.cmd))
                #print("{0:08b} {1:08b}".format(self.cmd,  ~inv_cmd & 0xF))
                pass

    def isStartP(self, duration):
        return self.start_p_min < duration < self.start_p_max

    def isStartS(self, duration):
        return self.start_s_min < duration < self.start_s_max

    def isStartR(self, duration):
        return self.start_r_min < duration < self.start_r_max

    def isShort(self, duration):
        return (self.s_min < duration < self.s_max)

    def isLong(self, duration):
        return (self.l_min < duration < self.l_max)

    def start(self):
        #logging.debug(20 * "#", "SAMSUNG START", 20 * "#")
        self.state = self.startBitP

    def startBitP(self, t, duration):
        if t and self.isStartP(duration):
            #print "start Pulse!"
            self.state = self.startBitE

    def startBitE(self, t, duration):
        #logging.debug("startBitE: ", t, duration)
        if not t and self.isStartS(duration):
            #logging.debug("begin Body")
            self.ircode = bitarray.bitarray()
            self.repeat = 0
            self.state = self.startMB
        else:
            #logging.debug("back to start!")
            self.start()

    def startMB(self, t, duration):
        if t and self.isShort(duration):
            #logging.debug("start MBit")
            self.state = self.endMB
        else:
            self.start()
    
    def endMB(self, t, duration):
        #logging.debug("end MBit")
        if not t and self.isShort(duration):
            self.emitBit(0)
            self.state = self.startMB
        elif not t and self.isLong(duration):
            self.state = self.startMB
            self.emitBit(1)
        else:
            self.start()
    
    def repeat_key(self):
        self.repeat += 1
        self.send_code()

    def send_code(self):
        #logging.debug("got code from addr: 0x{0:02x} cmd: 0x{1:02x} repeat: {2:1d}".format(self.addr, self.cmd, self.repeat))
        self.output.output(self.addr, self.repeat, self.cmd, 'samsung')
