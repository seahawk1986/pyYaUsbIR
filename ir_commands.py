#!/usr/bin/python2
import datetime
import dbus
import dbus.service
from dbus.mainloop.glib import DBusGMainLoop
dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
import time

class yaUsbIR_Control(dbus.service.Object):
    ircmd = {
        "0" : [1, 78, 137, 0],
        "1" : [1, 78, 137, 1],
        "2" : [1, 78, 137, 2],
        "3" : [1, 78, 137, 3],
        "4" : [1, 78, 137, 4],
        "5" : [1, 78, 137, 5],
        "6" : [1, 78, 137, 6],
        "7" : [1, 78, 137, 7],
        "8" : [1, 78, 137, 8],
        "9" : [1, 78, 137, 9],
        "10" : [1, 78, 137, 10],
        "11" : [1, 78, 137, 11],
        "12" : [1, 78, 137, 12],
        "13" : [1, 78, 137, 13],
        "14" : [1, 78, 137, 14],
        "15" : [1, 78, 137, 15],
        "16" : [1, 78, 137, 16],
        "C_END" : [1, 78, 137, 17],
        "C_WATCHDOG" : [1, 78, 137, 18],
        "C_OUTPUT" : [1, 78, 137, 19],
        "C_INPUT" : [1, 78, 137, 20],
        "C_IR" : [1, 78, 137, 21],
        }
    
    pause = [1, 78, 9, 80]

    def __init__(self, device):
        self.endpoint_w = device[0][(0,0)][1]
        self.set_led_off()
        self.bus = dbus.SystemBus()
        bus_name = dbus.service.BusName('org.yausbir.control', bus=self.bus)
        dbus.service.Object.__init__(self, bus_name, '/cmd')


    def send_cmd(self, commands):
        cmd = [self.ircmd[i] for i in commands]
        try:
            for c in cmd:
                self.endpoint_w.write(c)
            return True
        except Exception as e:
            print(e)
            return False

    @dbus.service.method('org.yausbir.control', out_signature='b')
    def learn_power_from_ir(self):
        commands = ["C_IR", "1", "1", "0", "C_END"]
        return self.send_cmd(commands)

    @dbus.service.method('org.yausbir.control', out_signature='b')
    def learn_power_from_code(self):
        commands = ["C_IR", "1", "1", "1", "C_END"]
        return self.send_cmd([self.ircmd[i] for i in commands])

    @dbus.service.method('org.yausbir.control', out_signature='b')
    def delete_power_code(self):
        commands = ["C_IR", "1", "2", "C_END"]
        return self.send_cmd(commands)

    @dbus.service.method('org.yausbir.control', in_signature='i', out_signature='b')
    def learn_key_from_ir(self, n):
        """learn ir command in slot n from a ir source"""
        if 0 < int(n) < 9:
            commands = ["C_IR", "2", str(n), "0", "C_END"]
            return self.send_cmd(commands)
        else:
            "print n is not between 1 and 8"
            return []

    @dbus.service.method('org.yausbir.control', in_signature='i', out_signature='b')
    def learn_key_from_code(self, n):
        """learn ir command in slot n by sending the raw data to the yaUsbIR"""
        if 0 < int(n) < 9:
            commands = ["C_IR", "2", str(n), "1", "C_END"]
            return self.send_cmd(commands)
        else:
            "print n is not between 1 and 8"
            return []

    @dbus.service.method('org.yausbir.control', in_signature='i', out_signature='b')
    def set_send_key_on_release(self, n):
        """send ir command in slot n on key release"""
        if 0 < int(n) < 9:
            commands = ["C_IR", "3", str(n), "C_END"]
            return self.send_cmd(commands)
        else:
            "print n is not between 1 and 8"
            return []

    @dbus.service.method('org.yausbir.control', in_signature='i', out_signature='b')
    def set_send_key_on_press(self, n):
        """send ir command in slot n on key press"""
        if 0 < int(n) < 9:
            commands = ["C_IR", "4", str(n), "C_END"]
            return self.send_cmd(commands)
        else:
            "print n is not between 1 and 8"
            return []

    @dbus.service.method('org.yausbir.control', in_signature='i', out_signature='b')
    def delete_mem_on_press(self, n):
        """delete ir command saved to slot n"""
        if 0 < int(n) < 9:
            commands = ["C_IR", "5", str(n), "C_END"]
            return self.send_cmd(commands)
        else:
            "print n is not between 1 and 8"
            return []

    @dbus.service.method('org.yausbir.control', in_signature='ii', out_signature='b')
    def set_repeat_key(self, n, repeats):
        """set how often an ir command saved to slot n should be repeated"""
        if 0 < int(n) < 9 and 0 < int(repeats) < 17:
            commands = ["C_IR", "6", str(n), str(repeats), "C_END"]
            return self.send_cmd(commands)
        else:
            "print n is not between 1 and 8"
            return []

    @dbus.service.method('org.yausbir.control', out_signature='b')
    def reset_yaUsbIR(self):
        """reset yaUsbIR to factory default settings"""
        commands = ["C_IR", "7", "C_END"]
        return self.send_cmd(commands)

    @dbus.service.method('org.yausbir.control', out_signature='b')
    def set_led_off(self):
        """disable red signal led"""
        commands = ["C_IR", "8", "0", "C_END"]
        self.led_off = True
        return self.send_cmd(commands)

    @dbus.service.method('org.yausbir.control', out_signature='b')
    def set_led_on(self):
        """enable red signal led"""
        commands = ["C_IR", "8", "1", "C_END"]
        self.led_off = False
        return self.send_cmd(commands)

    @dbus.service.method('org.yausbir.control', out_signature='b')
    def stop_watchdog(self):
        """deactivate the watchdog feature"""
        commands = ["C_WATCHDOG", "0", "C_END"]
        return self.send_cmd(commands)

    @dbus.service.method('org.yausbir.control', in_signature='i', out_signature='b')
    def trigger_watchdog(self, timedelta=10):
        """set watchdog timeout as integer or float in seconds (default: 10 s, max 99.9 s)"""
        if delta <= 99.9:
            delta = datetime.timedelta(seconds=timedelta)
            tens = delta.seconds // 10
            s = delta.seconds % 10
            ms = delta.milliseconds
            commands = ["C_WATCHDOG", "1", "%s" % tens, "%s" % s , "%s" % ms, "C_END"]
            return self.send_cmd(commands)

    @dbus.service.method('org.yausbir.control', in_signature='i', out_signature='b')
    def set_watchdog_poweroff_timeout(self, timedelta=5):
        """set time needed for poweroff when pressing the power button (default: 5 s, max 99.9 s)"""
        if delta <= 99.9:
            delta = datetime.timedelta(seconds=timedelta)
            tens = delta.seconds // 10
            s = delta.seconds % 10
            ms = delta.milliseconds
            commands = ["C_WATCHDOG", "2", "%s" % tens, "%s" % s , "%s" % ms, "C_END"]
            return self.send_cmd(commands)

    @dbus.service.method('org.yausbir.control', in_signature='i', out_signature='b')
    def set_watchdog_timeout_after_poweroff(self, timedelta=10):
        """set time needed after poweroff using the power button (default: 5 s, max 99.9 s)"""
        if delta <= 99.9:
            delta = datetime.timedelta(seconds=timedelta)
            tens = delta.seconds // 10
            s = delta.seconds % 10
            ms = delta.milliseconds
            commands = ["C_WATCHDOG", "2", "%s" % tens, "%s" % s , "%s" % ms, "C_END"]
            return self.send_cmd(commands)

    @dbus.service.method('org.yausbir.control', in_signature='i', out_signature='b')
    def set_watchdog_timeout_poweron(self, timedelta=10):
        """set time needed to power on pc using the power button (default: 800 ms, max 99.9 s)"""
        if delta <= 99.9:
            delta = datetime.timedelta(seconds=timedelta)
            tens = delta.seconds // 10
            s = delta.seconds % 10
            ms = delta.milliseconds
            commands = ["C_WATCHDOG", "2", "%s" % tens, "%s" % s , "%s" % ms, "C_END"]
            return self.send_cmd(commands)

    @dbus.service.method('org.yausbir.control', out_signature='b')
    def set_input_single_mode(self):
        """set inputs to singe key mode (generates rc5 codes, address = 0xf8, command 0x00 to 0x07)"""
        commands = ["C_INPUT", "0", "0", "C_END"]
        return self.send_cmd(commands)

    @dbus.service.method('org.yausbir.control', out_signature='b')
    def set_input_matrix_mode(self):
        """set inputs to key matrix mode (generates rc5 codes, address = 0xf8, command 0x00 to 0x0F)"""
        commands = ["C_INPUT", "0", "1", "C_END"]
        return self.send_cmd(commands)

    @dbus.service.method('org.yausbir.control', in_signature='i', out_signature='b')
    def set_input_level_mode(self, n):
        """set input n to pegel mode (generates rc5 codes on request (get_input_pegel), address = 0xf8, command 0x010 to 0x1F, if command % 2 == 0: input is low)"""
        if 0 < int(n) < 9:
            commands = ["C_INPUT", "1", "%s" % str(n), "C_END"]
            return self.send_cmd(commands)

    @dbus.service.method('org.yausbir.control', in_signature='i', out_signature='b')
    def set_input_key_repeat(self, n):
        """set key repeat in ms (max: 900 ms)"""
        if 0 < int(n) < 9:
            commands = ["C_INPUT", "2", "%s" % str(n), "C_END"]
            return self.send_cmd(commands)

    @dbus.service.method('org.yausbir.control', in_signature='i', out_signature='b')
    def get_input_level(self, n):
        """get level on input n as rc5 code address = 0xf8, command 0x010 to 0x1F, if command % 2 == 0: input is low)"""
        try:
            if 0 < int(n) < 9:
                commands = ["C_INPUT", "3", str(n), "C_END"]
                return self.send_cmd(commands)
            else:
                return False
        except Exception as e:
            print(e)
    
    @dbus.service.method('org.yausbir.control', in_signature='i', out_signature='b')
    def set_output_low(self, n):
        "set output n to low (GND)"
        if 0 < int(n) < 5:
            commands = ["C_OUTPUT", str(n), "0", "C_END"]
            return self.send_cmd(commands)

    @dbus.service.method('org.yausbir.control', in_signature='i', out_signature='b')
    def set_output_high(self, n):
        "set output n to high (open collector)"
        if 0 < int(n) <5:
            commands = ["C_OUTPUT", str(n), "1", "C_END"]
            return self.send_cmd(commands)
