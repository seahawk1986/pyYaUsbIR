#!/usr/bin/python
# -*- encoding:utf-8 -*-
#
# Supports RC6A-32 (mce version)
# TODO: RC6A-24 bit (apparently no toggle bit), RC6A-20 bit
# 


import bitarray

class RC6Decoder():
    base = 444
    s_min = int(base * 0.7)
    s_max = int(base * 1.3)
    l_min = int(base * 1.4)
    l_max = int(base * 2.6)
    t_min = int(base * 2.7)
    t_max = int(base * 3.3)
    u_min = int(base * 5)
    u_max = int(base * 7)
    t1 = (s_min, s_max)
    t2 = (l_min, l_max)
    t3 = (t_min, t_max)
    t6 = (u_min, u_max)

    def __init__(self, output):
        self.reset()
        self.output = output
        self.repeat = 0
        self.toggleBit = None
        self.rc6_6A_32_header = bitarray.bitarray([1,1,1,0])
        self.rc6_philips_header = bitarray.bitarray([1,0,0])

    def addEvent(self, t, duration):
        """type t (pulse = True, space = False), duration of event"""
        #print(t, duration)
        self.state(t, duration)

    def add_bit(self, bit):
        self.ircode.append(bit)
        #print(self.ircode[:3], self.rc6_philips_header)
        if len(self.ircode) == 21 and self.ircode[:3] == self.rc6_philips_header:
            toggleBit = self.ircode[4]
            if toggleBit == self.toggleBit:
                self.repeat += 1
            else:
                self.repeat = 0
            mode = self.ircode[1:4].to01()
            header = self.ircode[:4]
            address = int(self.ircode[5:13].to01(), 2)
            cmd = int(self.ircode[13:].to01(), 2)
            self.output.output(address, self.repeat, cmd, 'RC-6')
            self.toggleBit = toggleBit
            self.reset()

        elif len(self.ircode) == 37 and self.ircode[:4] == self.rc6_6A_32_header:
            toggleBit = self.ircode[-16]
            if toggleBit == self.toggleBit:
                self.repeat += 1
            else:
                self.repeat = 0
            
            mode = self.ircode[1:4].to01()
            address = int(self.ircode[4:-16].to01(), 2)
            cmd = int(self.ircode[-15:].to01(), 2)
            self.output.output(address, self.repeat, cmd, 'RC-6-6A-32')
            self.toggleBit = toggleBit
            self.reset()

    def check_duration(self, d, duration):
        if d[0] < duration < d[1]:
            return True

    def reset(self):
        self.ircode = bitarray.bitarray()
        self.state = self.start

    def start(self, t, duration):
        """pulse for start bit (self.t * 6)"""
        if t and self.check_duration(self.t6, duration):
            self.state = self.end_start
            return
        self.reset()

    def end_start(self, t, duration):
        """end of start bit (self.t * 2)"""
        if not t: 
            if self.check_duration(self.t2, duration):
                self.state = self.start_one
                return
            elif self.check_duration(self.t3, duration):
                self.state = self.mid_zero
                return
        self.reset()

    def start_one(self, t, duration):
        """start of 1 (short (self.t) or trailing bit (t * 2))"""
        if t:
            if self.check_duration(self.t1, duration):
                self.add_bit(1)
                self.state = self.end_one
                return
            elif self.check_duration(self.t2, duration):
                self.add_bit(1)
                self.state = self.mid_trailing_one
                return
        self.reset()

    def end_one(self, t, duration):
        """end of 1 (short (self.t) eventually with begin a zero (t * 2 or t * 3)"""
        if not t:
            if self.check_duration(self.t1, duration):
                self.state = self.start_one
                return
            elif self.check_duration(self.t2, duration):
                self.state = self.mid_zero
                return
            elif self.check_duration(self.t3, duration):
                self.state = self.mid-trailing_zero
                return
        self.reset()

    def start_zero(self, t, duration):
        if not t:
            if self.check_duration(self.t1, duration):
                self.state = self.mid_zero
                return
            elif self.check_duration(self.t2, duration):
                self.state = self.mid_trailing_zero
                return
        self.reset()

    def mid_zero(self, t, duration):
        if t:
            if self.check_duration(self.t1, duration):
                self.add_bit(0)
                self.state = self.start_zero
                return
            elif self.check_duration(self.t2, duration):
                self.add_bit(0)
                self.add_bit(1)
                self.state = self.end_one
                return
            elif self.check_duration(self.t3, duration):
                self.add_bit(0)
                self.add_bit(1)
                self.state = self.mid_trailing_one
                return
        self.reset()

    def mid_trailing_zero(self, t, duration):
        if t:
            if self.check_duration(self.t2, duration):
                self.add_bit(0)
                self.state = self.start_zero
                return
            elif self.check_duration(self.t3, duration):
                self.add_bit(0)
                self.add_bit(1)
                self.state = self.end_one
                return
        self.reset()

    def mid_trailing_one(self, t, duration):
        if not t:
            if self.check_duration(self.t2, duration):
                self.state = self.start_one
                return
            elif self.check_duration(self.t3, duration):
                self.state = self.mid_zero
                return
        self.reset()

