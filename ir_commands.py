#!/usr/bin/python2
import datetime


class yaUsbIR_Control:
    ircmd = {
    "1" : [1, 78, '0x137', '0x1'],
    "0" : [1, 78, '0x137', '0x0'],
    "3" : [1, 78, '0x137', '0x3'],
    "2" : [1, 78, '0x137', '0x2'],
    "5" : [1, 78, '0x137', '0x5'],
    "4" : [1, 78, '0x137', '0x4'],
    "7" : [1, 78, '0x137', '0x7'],
    "6" : [1, 78, '0x137', '0x6'],
    "9" : [1, 78, '0x137', '0x9'],
    "8" : [1, 78, '0x137', '0x8'],
    "11" : [1, 78, '0x137', '0x11'],
    "10" : [1, 78, '0x137', '0x10'],
    "13" : [1, 78, '0x137', '0x13'],
    "12" : [1, 78, '0x137', '0x12'],
    "14" : [1, 78, '0x137', '0x14'],
    "15" : [1, 78, '0x137', '0x15'],
    "16" : [1, 78, '0x137', '0x16'],
    "C_END" : [1, 78, '0x137', '0x17'],
    "C_WATCHDOG" : [1, 78, '0x137', '0x18'],
    "C_OUTPUT" : [1, 78, '0x137', '0x19'],
    "C_INPUT" : [1, 78, '0x137', '0x20'],
    "C_IR" : [1, 78, '0x137', '0x21'],
    }
    
    def ___init__(self):
        pass

    def cmd_learn_power_from_ir(self):
        commands = ["C_IR", "1", "1", "0", "C_END"]
        return [ircmd[i] for i in commands]

    def cmd_learn_power_from_code(self):
        commands = ["C_IR", "1", "1", "1", "C_END"]
        return [ircmd[i] for i in commands]

    def cmd_delete_power_code(self):
        commands = ["C_IR", "1", "2", "C_END"]
        return [ircmd[i] for i in commands]

    def cmd_learn_key_from_ir(self, n):
       """learn ir command in slot n from a ir source"""
        if 0 < int(n) < 9:
            commands = ["C_IR", "2", str(n), "0", "C_END"]
            return [ircmd[i] for i in commands]
        else:
            "print n is not between 1 and 8"
            return []

    def cmd_learn_key_from_code(self, n):
       """learn ir command in slot n by sending the raw data to the yaUsbIR"""
        if 0 < int(n) < 9:
            commands = ["C_IR", "2", str(n), "1", "C_END"]
            return [ircmd[i] for i in commands]
        else:
            "print n is not between 1 and 8"
            return []

    def cmd_set_send_key_on_release(self, n):
       """send ir command in slot n on key release"""
        if 0 < int(n) < 9:
            commands = ["C_IR", "3", str(n), "C_END"]
            return [ircmd[i] for i in commands]
        else:
            "print n is not between 1 and 8"
            return []

    def cmd_set_send_key_on_press(self, n):
       """send ir command in slot n on key press"""
        if 0 < int(n) < 9:
            commands = ["C_IR", "4", str(n), "C_END"]
            return [ircmd[i] for i in commands]
        else:
            "print n is not between 1 and 8"
            return []

    def cmd_delete_mem_on_press(self, n):
       """delete ir command saved to slot n"""
        if 0 < int(n) < 9:
            commands = ["C_IR", "5", str(n), "C_END"]
            return [ircmd[i] for i in commands]
        else:
            "print n is not between 1 and 8"
            return []

    def cmd_set_repeat_key(self, n, repeats):
        """set how often an ir command saved to slot n should be repeated"""
        if 0 < int(n) < 9 and 0 < int(repeats) < 17:
            commands = ["C_IR", "6", str(n), str(repeats), "C_END"]
            return [ircmd[i] for i in commands]
        else:
            "print n is not between 1 and 8"
            return []

    def cmd_reset_yaUsbIR(self):
        """reset yaUsbIR to factory default settings"""
        commands = ["C_IR", "7", "C_END"]
        return [ircmd[i] for i in commands]

    def cmd_set_led_off(self):
        """disable red signal led"""
        commands = ["C_IR", "8", "0", "C_END"]
        return [ircmd[i] for i in commands]

    def cmd_set_led_on(self):
        """enable red signal led"""
        commands = ["C_IR", "8", "1", "C_END"]
        return [ircmd[i] for i in commands]

    def cmd_stop_watchdog(self):
        """deactivate the watchdog feature"""
	commands = ["C_WATCHDOG", "0", "C_END"]
        return [ircmd[i] for i in commands]

    def cmd_trigger_watchdog(self, timedelta=10):
        """set watchdog timeout as integer or float in seconds (default: 10 s, max 99.9 s)"""
        if delta <= 99.9:
            delta = datetime.timedelta(seconds=timedelta)
            10s = delta.seconds // 10
            s = delta.seconds % 10
            ms = delta.milliseconds
            commands = ["C_WATCHDOG", "1", "%s" % 10s, "%s" % s , "%s" % ms, "C_END"]
            return [ircmd[i] for i in commands]

    def cmd_set_watchdog_poweroff_timeout(self, timedelta=5):
        """set time needed for poweroff when pressing the power button (default: 5 s, max 99.9 s)"""
        if delta <= 99.9:
            delta = datetime.timedelta(seconds=timedelta)
            10s = delta.seconds // 10
            s = delta.seconds % 10
            ms = delta.milliseconds
            commands = ["C_WATCHDOG", "2", "%s" % 10s, "%s" % s , "%s" % ms, "C_END"]
            return [ircmd[i] for i in commands]

    def cmd_set_watchdog_timeout_after_poweroff(self, timedelta=10):
        """set time needed after poweroff using the power button (default: 5 s, max 99.9 s)"""
        if delta <= 99.9:
            delta = datetime.timedelta(seconds=timedelta)
            10s = delta.seconds // 10
            s = delta.seconds % 10
            ms = delta.milliseconds
            commands = ["C_WATCHDOG", "2", "%s" % 10s, "%s" % s , "%s" % ms, "C_END"]
            return [ircmd[i] for i in commands]

    def cmd_set_watchdog_timeout_poweron(self, timedelta=10):
        """set time needed to power on pc using the power button (default: 800 ms, max 99.9 s)"""
        if delta <= 99.9:
            delta = datetime.timedelta(seconds=timedelta)
            10s = delta.seconds // 10
            s = delta.seconds % 10
            ms = delta.milliseconds
            commands = ["C_WATCHDOG", "2", "%s" % 10s, "%s" % s , "%s" % ms, "C_END"]
            return [ircmd[i] for i in commands]

    def cmd_set_input_single_mode(self):
        """set inputs to singe key mode (genereates rc5 codes, address = 0xf8, command 0x00 to 0x07)"""
        commands = ["C_INPUT", "0", "0", "C_END"]
        return [ircmd[i] for i in commands]

    def cmd_set_input_matrix_mode(self):
        """set inputs to key matrix mode (genereates rc5 codes, address = 0xf8, command 0x00 to 0x0F)"""
        commands = ["C_INPUT", "0", "1", "C_END"]
        return [ircmd[i] for i in commands]

    def cmd_set_input_level_mode(self, n):
        """set input n to pegel mode (generates rc5 codes on request (cmd_get_input_pegel), address = 0xf8, command 0x010 to 0x1F, if command % 2 == 0: input is low)"""
        if 0 < int(n) < 9:
            commands = ["C_INPUT", "1", "%s" % str(n), "C_END"]
            return [ircmd[i] for i in commands]

    def cmd_set_input_key_repeat(self, n):
        """set key repeat in ms (max: 900 ms)"""
        if 0 < int(n) < 9:
            commands = ["C_INPUT", "2", "%s" % str(n), "C_END"]
            return [ircmd[i] for i in commands]


    def cmd_get_input_level(self, n):
        """get level on input n as rc5 code address = 0xf8, command 0x010 to 0x1F, if command % 2 == 0: input is low)"""
        if 0 < int(n) < 9:
            commands = ["C_INPUT", "3", "%s" % str(n), "C_END"]
            return [ircmd[i] for i in commands]

    def cmd_set_output_low(self, n):
        "set output n to low (GND)"
        if 0 < int(n) <5:
            commands = ["C_OUTPUT", "%s" % str(n), "0", "C_END"]

    def cmd_set_output_high(self, n):
        "set output n to high (open collector)"
        if 0 < int(n) <5:
            commands = ["C_OUTPUT", "%s" % str(n), "1", "C_END"]

