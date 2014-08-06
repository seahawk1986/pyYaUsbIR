#!/usr/bin/python
# -*- encoding:utf-8 -*-
#
# Supports RC6A-32 (mce version)
# TODO: RC6, RC6A-24 bit (apparently no toggle bit), RC6A-20 bit
# 
import bitarray
import logging

class RC6Decoder:
    """ very useful explanation for the state machine: http://www.clearwater.com.au/code/rc5 """
    s_min = 350
    s_max = 600
    l_min = 700
    l_max = 1100
    t_min = 1101
    t_max = 1500
    start_min = 2200
    start_max = 2800
    
    def __init__(self, output):
        self.ircode = bitarray.bitarray()
        self.state = self.midOne
        self.start()
        self.toggleBit = None
        self.last_t = None
        self.repeat = 0
        self.output = output
        self.rc6_header = bitarray.bitarray([1,1,1,1,0])

    def addEvent(self, t, duration):
        if t and self.last_t == t: 
            if self.state == self.startZero:
                self.state(True, 888)
            elif self.state == self.midOne:
                self.state(False, 1800)
            self.start()
        
        self.state(t, duration)
        self.last_t = t

    def emitBit(self, bit):
        self.ircode.append(bit)
        if self.ircode[:5] == self.rc6_header and len(self.ircode) == 37:
            #print("got complete rc-6 code")
            toggleBit = self.ircode[21]
            if toggleBit == self.toggleBit:
                self.repeat += 1
            else:
                self.repeat = 0
            #header = self.ircode[:17].to01()
            address = int(self.ircode[17:21].to01(), 2)
            cmd = int(self.ircode[22:].to01(), 2)
            #print "got code: ", bytestring, "repeat: ", (toggleBit == self.toggleBit), "extended RC5:", extended
            #logging.debug("RC6A - Header: ", "0b"+header, "Address: ", hex(address), "\tCommand: ", hex(cmd), "\trepeat: ", self.repeat, "toggle Bit: ", toggleBit)
            self.output.output(address, self.repeat, cmd, 'RC-6')
            
            #print "raw: 0x%02x%02x" % (address, cmd)
            self.toggleBit = toggleBit
            self.start()

    def isShort(self, duration):
        return self.s_min < duration < self.s_max

    def isLong(self, duration):
        return self.l_min < duration < self.l_max

    def isStartP(self, duration):
        return self.start_min < duration < self.start_max

    def isToggle(self, duration):
        return self.t_min < duration < self.t_max

    def start(self):
        self.state = self.startBitP

    def startBitP(self, t, duration):
        #print "start bit pulse"
        if self.isStartP(duration):
            self.ircode = bitarray.bitarray()
            self.emitBit(1)
            self.state = self.startBitS

    def startBitS(self, t, duration):
        #print "start bit space"
        if self.isLong(duration):
            self.state = self.startOne
        else:
            self.start()

    def startOne(self, t, duration):
        #print "start One"
        if t and self.isShort(duration):
            self.state = self.midOne
            self.emitBit(1)
        else:
            self.start()
    
    def startZero(self, t, duration):
        #print "start Zero"
        if not t and self.isShort(duration):
            self.state = self.midZero
            self.emitBit(0)
        else:
            self.start()
    
    def midOne(self, t, duration):
        #print "mid One"
        if not t and self.isShort(duration):
            self.state = self.startOne
        elif not t and self.isLong(duration):
            self.state = self.midZero
            self.emitBit(0)
        else:
            self.start()

    def midZero(self, t, duration):
        #print "mid Zero: ", t, duration
        if t and self.isShort(duration):
            self.state = self.startZero
            if 7 > len(self.ircode) > 4 and self.ircode[:2].all():
                self.state = self.startToggleZero
                
        elif t and self.isLong(duration):
            self.emitBit(1)
            self.state = self.midOne
        elif t and self.isToggle(duration): # short pulse + long pulse
            self.emitBit(0)
            self.state = self.midToggleZero
        else:
            self.start()

    def startToggleOne(self, t, duration):
        #print "start Toggle One"
        if t and self.isLong(duration):
            #print("next is Zero")
            self.emitBit(1)
            self.state = self.endToggleOne
        elif t and self.isToggle(duration):
            self.emitBit(1)
            self.state = self.endToggleOne

        else:
            self.start()

    def startToggleZero(self, t, duration):
        #print "start Toggle Zero"
        if not t and self.isLong(duration):
            self.emitBit(0)
            self.state = self.midToggleZero
        else:
            self.start()
    
    def midToggleZero(self, t, duration):
        #print "mid ToggleZero"
        if t and self.isToggle(duration):
            self.state = self.midOne
        elif t and self.isLong(duration):
            self.state = self.startOne
        else:
            self.start()

