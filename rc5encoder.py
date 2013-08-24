#!/usr/bin/python2
# -*- coding:utf-8 -*-
from __future__ import division
import itertools


class RC5Encoder:
    s_len = 67  #884 * 6 / 79
    l_len = 136 #1800 * 6 / 79
    frequency = 0x4F # = 79  = 3 * 10^6 / 38000 kHz

    def __init__(self):
        self.last_bytestring = None
        self.toggleBit = 1
        self.ircommand = []
        pass

    def send_bytestring(self, bytestring):
        for n in range(2, len(bytestring)):
            #print n, bytestring[n]
            self.ircommand.extend(self.addBit(n, bytestring))
        print self.ircommand
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
        """if bytestring[n-1] == "0":
            if bytestring[n] == "1":
                elements.append(self.l_len)
            elif bytestring[n] == "0":
                elements.extend([self.s_len, self.s_len])
        elif bytestring[n-1] == "1":
            if bytestring[n] == "1":
                elements.extend([self.s_len, self.s_len])
            elif bytestring[n] == "0":
                elements.append(self.l_len)"""
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
        print result
        return result
if __name__ == '__main__':
    encoder = RC5Encoder()
    encoder.send_bytestring("0b11111110100101")
    #print encoder.ircommand
