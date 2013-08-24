#!/usr/bin/python2
yausbir_commands = {
	"0":29952,
	"1":29965,
	"2":29978,
	"3":29991,
	"4":30004,
	"5":30017,
	"6":30030,
	"7":30043,
	"8":30056,
	"9":30069,
	"10":30082,
	"11":30095,
	"12":30108,
	"13":30121,
	"14":30134,
	"15":30147,
	"16":30160,
	"C_END":30173,
	"C_WATCHDOG":30186,
	"C_OUTPUT":30199,
	"C_INPUT":30212,
	"C_IR":30225,
}

encoded = {}
for command, value in yausbir_commands.items():
    hval = (value/13) | 0x8000
    msb, lsb = divmod(hval, 0x100)
    encoded[command] = [0x01, 0x4E,  msb, lsb ]
    print command, ":\t", encoded[command]
