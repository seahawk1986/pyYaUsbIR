#!/usr/bin/python
# -*- encoding:utf-8 -*-

class SamsungDecoder:
    """ very useful explanation for the state machine: http://www.clearwater.com.au/code/rc5 """
    start_p_min = 4000
    start_p_max = 5000
    start_s_min = 4000
    start_s_max = 5000
    #start_r_min = 1800
    #start_r_max = 2500
    s_min = 400
    s_max = 700
    l_min = 1500
    l_max = 1800
    #p_repeat = 
    def __init__(self, output):
        self.ircode = []
        self.state = self.startBitP
        self.start()
        self.repeat = 0
        self.extended = False
        self.lastcommand = None
        self.output = output

    def addEvent(self, t, duration):
        self.state(t, duration)

    def emitBit(self, bit):
        if bit in (0,1):
            self.ircode.append(bit)
        if len(self.ircode) == 32:
            addr_lsb = self.ircode[0:3]
            addr_msb = self.ircode[3:7]
            addr_c_lsb = self.ircode[8:11]
            addr_c_msb = self.ircode[12:15]
            self.addr = eval("0b" + 
                             "".join(map(str,addr_msb)) + 
                             "".join(map(str,addr_lsb)) +
                             "".join(map(str,addr_c_msb)) +
                             "".join(map(str,addr_c_lsb))
                             )
            cmd_lsb = self.ircode[16:19]
            cmd_msb = self.ircode[20:23]
            cmd_c_lsb = self.ircode[24:27]
            cmd_c_msb = self.ircode[28:31]
            self.cmd = eval("0b" +
                            "".join(map(str,cmd_msb)) + 
                            "".join(map(str,cmd_lsb)) +
                            "".join(map(str,cmd_c_msb)) +
                            "".join(map(str,cmd_c_lsb)) )
            self.lastcode = self.ircode
            self.send_code()

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
        #print(20 * "#", "SAMSUNG START", 20 * "#")
        self.state = self.startBitP

    def startBitP(self, t, duration):
        if t and self.isStartP(duration):
            #print "start Pulse!"
            self.state = self.startBitE

    def startBitE(self, t, duration):
        #print "startBitE: ", t, duration
        if not t and self.isStartS(duration):
            #print "begin Body"
            self.ircode = []
            self.repeat = 0
            self.state = self.startMB
        else:
            #print "back to start!"
            self.start()

    def startMB(self, t, duration):
        if t and self.isShort(duration):
            #print "start MBit"
            self.state = self.endMB
        else:
            self.start()
    
    def endMB(self, t, duration):
        #print "end MBit"
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
        #print self.lastcode
        print("got code from addr: %s cmd: %s repeat: %s" % (str(bin(self.addr)), str(bin(self.cmd)), self.repeat))
