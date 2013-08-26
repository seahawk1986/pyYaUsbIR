#!/usr/bin/python2
# -*- coding:utf-8 -*-
from __future__ import division
import itertools


class RC5Encoder:
    s_len = 67  #884 * 6 / 79
    l_len = 136 #1800 * 6 / 79
    frequency = 0x4F # = 79  = 3 * 10^6 / 38000 kHz
    pause = 900000 # wait 90 ms between repeats (under 100 ms should be fine)

    def __init__(self):
        self.last_bytestring = None
        self.toggleBit = 1
        self.ircommand = []
        pass

    def send_hexcode(self, code):
        bitcmd = [1] # Start Bit, always 1
        addr, cmd = divmod(code, 0x100)
        print hex(addr), hex(cmd)
        print bin(addr), bin(cmd)
        print addr, cmd
        if code & 0x40 == 0x40: # 2nd Start Bit, 0 for RC5X, 1 for RC5
          print "extended"
          bitcmd.append(0)
          cmd -= 0x40
        else:
          print "classic"
          bitcmd.append(1)
        bitcmd.append(1)#self.toggleBit ^ 1) # Toggle Bit - change after releasing the key
        self.toggleBit = 1 #self.toggleBit ^ 1
        print "{0:05b}".format(addr) # 5 address Bits
        for i in "{0:05b}".format(addr):
          bitcmd.append(int(i))
        print "{0:06b}".format(cmd)
        for i in "{0:06b}".format(cmd): # 6 command bits
          bitcmd.append(int(i))
        #print "".join(map(str,bitcmd))
        sendcmd = self.prepareSend(bitcmd)
        return sendcmd

    def prepareSend(self, bitcmd):
        elements = []
        n = 0
        print bitcmd
        for bit in bitcmd:
            if n+1 >= len(bitcmd):
                print bit, n, "last"
                if bit == 0:
                    continue
                elements.append(self.s_len)
                continue
            if n == 0 and bitcmd[n+1] == bit and bit == 1:
                 print "start encoding"
                 elements.extend([self.s_len, self.s_len])
            elif n == 0 and bitcmd[n+1] != bit:
                 print "start encoding"
                 elements.append(self.l_len)
            elif bitcmd[n+1] == bit:
                print "%s to %s" % (bit, bitcmd[n+1])
                elements.extend([self.s_len, self.s_len])
            elif bitcmd[n+1] != bit:
                print "%s to %s" % (bit, bitcmd[n+1])
                elements.append(self.l_len)
            else:
                print "this should not happen %s to %s" % (bit, bitcmd[n+1])
            n +=1
            
        #pack ir data into 64 byte packages
        #first byte is always 0x01
        #second byte is send frequency: 0x4F = 79  = 3 * 10^6 / 38000 kHz

        a = [0x01,self.frequency]
        result = []
        for irtype, byte in zip(elements, itertools.cycle([128,0])):
            a.extend([byte, irtype])
            if len(a) == 64:
                result.append(a)
                a = [0x01,self.frequency]
        if len(a) > 2:
            result.extend(a)
        print result
        return result



    def send_bytestring(self, bytestring):
        for n in range(2, len(bytestring)):
            #print n, bytestring[n]
            self.ircommand.extend(self.addBit(n, bytestring))
        #print self.ircommand
        result = self.prepare()
        return result

    def addBit(self, n, bytestring):
        elements = []
        if n + 1 >= len(bytestring):
            return [self.s_len]
        if bytestring[n-1] == "b" and bytestring[n+1] == "1":
            print "begin Encoding"
            elements.extend([self.s_len,self.s_len])
        elif bytestring[n-1] == "b" and bytestring[n+1] == "0":
            elements.append(self.l_len)
        elif bytestring[n+1] == bytestring[n]:
            elements.extend([self.s_len, self.s_len])
        else:
            elements.append(self.l_len)

        return elements
    
    def prepare(self):
        a = [0x01,self.frequency]
        result = []
        for irtype, byte in zip(self.ircommand, itertools.cycle([128,0])):
            a.extend([byte, irtype])
            if len(a) == 64:
                result.append(a)
                a = [0x01,self.frequency]
        if len(a) > 2:
            result.extend(a)
        #print result
        return result
if __name__ == '__main__':
    encoder = RC5Encoder()
    encoder.send_bytestring("0b11111110100101")
    #print encoder.ircommand
