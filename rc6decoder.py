#!/usr/bin/python
# -*- encoding:utf-8 -*-
#
# Supports RC6A-32 (mce version)
# TODO: RC6, RC6A-24 bit (apparently no toggle bit), RC6A-20 bit
# 
import bitarray
import struct

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
    
    #p_repeat = 
    def __init__(self, output):
        self.ircode = bitarray.bitarray()
        self.state = self.midOne
        self.start()
        self.toggleBit = None
        self.last_t = None
        self.repeat = 0
        self.output = output

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
        #print("got bit:", bit)
        self.ircode.append(bit)
        #print(self.ircode.to01())
        #print(len(self.ircode))
        #print(self.ircode[:5].tolist())
        #print str(bin(self.ircode.value))[4:7]
        #if str(bin(self.ircode.value))[4:7] == "000":
        #print(self.ircode[4:7])
        #if self.ircode[4:7].tolist() == [0,0,0]:
        #    print(len(self.ircode))
        #    print("RC6 protocol")
        #elif str(bin(self.ircode.value))[4:7] == "110" and self.ircode.value >= 0b1100000000000000000000000000000000000:
        if self.ircode[:5].tolist() == [1,1,1,1,0] and len(self.ircode) == 37:
            #print("got complete rc-6 code")
            #print len(str(bin(self.ircode.value))[2:])
            #print(len(self.ircode))
            bytestring = self.ircode.to01()
            #print bytestring
            #print(bytestring[:17], bytestring[17:21], bytestring[21], bytestring[22:])
            header = bytestring[:17]
            addr = bytestring[17:21]
            toggleBit = bytestring[21]
            #print "Toggle-Bit: ", toggleBit
            if toggleBit == self.toggleBit:
                self.repeat += 1
            else:
                self.repeat = 0
            #print "HEADER: ", bytestring[2:4]
            address = eval("0b"+ addr)
            cmdstr = bytestring[22:]
            cmd = eval("0b" + cmdstr)
            #print "got code: ", bytestring, "repeat: ", (toggleBit == self.toggleBit), "extended RC5:", extended
            print("RC6A - Header: ", "0b"+header, "Address: ", hex(address), "\tCommand: ", hex(cmd), "\trepeat: ", self.repeat, "toggle Bit: ", toggleBit)
            self.output.output(address, self.repeat, cmd, 'RC-6')
            
            #print "raw: 0x%02x%02x" % (address, cmd)
            self.toggleBit = toggleBit
            #self.ircode.value = 0
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
        #print(20 * "#", "RC-6 START", 20 * "#")
        self.state = self.startBitP
        #self.emitBit(1)

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
            if 0b110000 > eval("0b%s" % self.ircode.to01()) > 0b11000:
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
            print("next is Zero")
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

