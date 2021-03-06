#!/usr/bin/python
# -*- encoding:utf-8 -*-

class NECDecoder:
    """ very useful explanation for the state machine: http://www.clearwater.com.au/code/rc5 """
    start_p_min = 8000
    start_p_max = 10000
    start_s_min = 4000
    start_s_max = 5000
    start_r_min = 1800
    start_r_max = 2500
    s_min = 444
    s_max = 888
    l_min = 1334
    l_max = 2000
    #p_repeat = 
    def __init__(self, output):
        self.ircode = []
        self.state = self.startBitP
        self.start()
        self.repeat = 0
        self.extended = False
        self.lastcommand = None
        self.lastcode = None
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
            for lsb, lsb_c, msb, msb_c in zip(addr_lsb, addr_c_lsb, addr_msb, addr_c_msb):
                if lsb is not lsb_c and msb is not msb_c:
                    self.extended = False
                else:
                    self.extended = True
                    break
            if self.extended:
                self.addr = eval("0b" + 
                                 "".join(map(str,addr_c_msb)) + "".join(map(str,addr_c_lsb)) +
                                 "".join(map(str,addr_msb)) + "".join(map(str,addr_lsb)) # Address low
                                )
            else:
                self.addr = eval("0b" + "".join(map(str,addr_msb)) + "".join(map(str,addr_lsb)) )
            cmd_lsb = self.ircode[16:20]
            cmd_msb = self.ircode[20:24]
            cmd_c_lsb = self.ircode[24:28]
            cmd_c_msb = self.ircode[28:32]
            for lsb, lsb_c, msb, msb_c in zip(cmd_lsb, cmd_c_lsb, cmd_msb, cmd_c_msb):
                if lsb is not lsb_c and msb is not msb_c:
                    cmd = True
                else:
                    print("control bits do not match!")
                    cmd = False
                    break
            if cmd:
                self.cmd = eval("0b" + "".join(map(str,cmd_msb)) + "".join(map(str,cmd_lsb)) )
                self.lastcode = self.ircode
                self.send_code()
            else:
                self.lastcode = None
                self.ircode = []

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
        #print(20 * "#", "NEC START", 20 * "#")
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
        elif not t and self.isStartR(duration) and self.lastcode:
            #print "repeat!"
            self.repeat_key()
            self.state = self.startBitP
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
            self.emitBit(1)
            self.state = self.startMB
        else:
            self.start()
    
    def repeat_key(self):
        self.repeat += 1
        self.send_code()

    def send_code(self):
        #print self.lastcode
        print("got code from addr: %s cmd: %s repeat: %s" % (str(hex(self.addr)), str(hex(self.cmd)), self.repeat))
        self.output.output(self.addr, self.repeat, self.cmd, 'NEC')
