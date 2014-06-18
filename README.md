pyYaUsbIR
=========

an userspace driver for yaUsbIR written in python

requires:
---------
 * python3
 * python-dbus
 * python-gi
 * pyhton-uinput: https://github.com/tuomasjjrasanen/python-uinput
 * pyusb: https://github.com/walac/pyusb

TODO:
 * remove massive debug output
 * allow to set socket as start argument
 * cleanup code and optimize for python3
 * allow lirc output for samsung codes
 * learning mode
 * optional uinput key generation via uinput
 * configuration file to (de)activate decoders
 * control daemon via dbus
 * Learning mode
 * additional decoders and encoders (?)
