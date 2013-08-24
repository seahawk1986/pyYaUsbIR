#!/usr/bin/python
# -*- encoding:utf-8 -*-
import ctypes

class RC5Decoder:
    """ very useful explanation for the state machine: http://www.clearwater.com.au/code/rc5 """
    s_min = 444
    s_max = 1333
    l_min = 1334
    l_max = 5000
    def __init__(self):
        self.ircode = ctypes.c_ushort(0)
        self.state = self.midOne
        self.start()
        self.toggleBit = None
        self.last_t = None
        self.repeat = 0

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
        if bit in (0,1):
            if self.ircode.value > 0:
                self.ircode.value = self.ircode.value << 1
            self.ircode.value += bit
        if self.ircode.value > 8192:
            bytestring = str(bin(self.ircode.value))
            print bytestring
            toggleBit = bytestring[4]
            if toggleBit == self.toggleBit:
                self.repeat += 1
            else:
                self.repeat = 0
            if bytestring[3] == "1":
                extended = False
            else:
                extended = True
            #print "got code: ", bytestring, "repeat: ", (toggleBit == self.toggleBit), "extended RC5:", extended
            print "extended RC5: ", extended, "\trepeat: ", self.repeat, "\tAddress: ", hex(int(bytestring[5:9],2)), "\tCommand: ", hex(int(bytestring[10:],2))
            self.toggleBit = toggleBit
            self.ircode.value = 0

    def isShort(self, duration):
        a = (self.s_min < duration < self.s_max)
        return (self.s_min < duration < self.s_max)

    def isLong(self, duration):
        a = (self.l_min < duration < self.l_max)
        return (self.l_min < duration < self.l_max)

    def start(self):
        self.ircode.value = 0
	self.state = self.midOne
	self.emitBit(1)

    def startOne(self, t, duration):
        if not t and self.isShort(duration):
            self.state = self.midOne
            self.emitBit(1)
        else:
            self.start()
    
    def startZero(self, t, duration):
        if t and self.isShort(duration):
            self.state = self.midZero
            self.emitBit(0)
        else:
            self.start()
    
    def midOne(self, t, duration):
        if t and self.isShort(duration):
            self.state = self.startOne
        elif t and self.isLong(duration):
            self.state = self.midZero
            self.emitBit(0)
        else:
            self.start()

    def midZero(self, t, duration):
        if not t and self.isShort(duration):
            self.state = self.startZero
        elif not t and self.isLong(duration):
            self.state = self.midOne
            self.emitBit(1)
        else:
            self.start()

    
