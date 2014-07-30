import configparser
import itertools
import os
import socket
import stat
import syslog
#import uinput
from gi.repository import GObject


class Output():

    def __init__(self,socket_path,activeout="lirc",keymap="keymap.txt"):
        self.OutputDevs = {}
        self.keymap = Keymap(keymap)
        #self.add_output_device()
        self.add_output_device(devicename='lirc',devicetype='lirc',socket_path=socket_path, keymap=self.keymap)
        self.active_output = None
        self.set_active_output(activeout)
        syslog.syslog("Lircd Socket is set to %s" %(socket_path))

    def output(self, code, count, cmd, device):
        #logging.debug(" ".join([str(code), str(count), str(cmd), device]))
        if self.active_output != None:
            #print("send key")
            self.active_output.send_key(code, count, cmd, device)

    def set_active_output(self, device):
        if device == 'None' or device == None:
            self.active_output = None
            print("no active output")
        else:
            try:
                self.active_output = self.OutputDevs[device]
                #print(self.active_output)
            except:
                syslog.syslog('No matching device for %s found, setting to None' %(device))
                self.active_output = None

    def add_output_device(self, devicename='lirc', devicetype='lirc', match=['KEY_'], socket_path='/var/run/lirc/lircd.ya', keymap=None):
        self.OutputDevs[devicename] = OutputDev(devicename,devicetype,match,socket_path, keymap=self.keymap)
        #print('test2')

class OutputDev():
  
    def __init__(self, devicename='lirc', devicetype='lirc', match=['KEY_','BTN_','REL_'],
                                                       socket_path='/var/run/lirc/lircd.ya', keymap=None):    
        self.devicetype = devicetype    
        self.keymap = keymap
        #if devicetype == 'uinput':
        #    self.events = self.select_capabilities(match)
        #    self.device = uinput.Device(self.events, devicename)
        if devicetype == 'lirc':
            self.device = self.create_lircd_socket(socket_path)
            self.conns = []

    """def select_capabilities(self,match):
        keys = []
        items = dir(uinput)
        for item in itertools.product(match,items):
            if item[1].startswith(item[0]):
                keys.append(eval('uinput.%s'%(item[1])))
        return keys"""

    def create_lircd_socket(self, socket_path):
        try:
            os.remove(socket_path)
        except OSError:
            pass
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(socket_path)
        sock.listen(5)
        os.chmod(socket_path, 0o777)
        GObject.io_add_watch(sock, GObject.IO_IN, self.listener)
        print("created Lirc-Socket %s"%(socket_path))
        return sock

    def listener(self, sock, *args):
        conn, a = sock.accept()
        self.conns.append(conn)
        print("Connected to %s" %(conn))
        return True


    def send_key(self, code, count, cmd, device):
        if self.devicetype == 'uinput':
            self.device.emit(eval('uinput.%s'%(cmd)),1)
            self.device.emit(eval('uinput.%s'%(cmd)),0)
        if self.devicetype == 'lirc' and len(self.conns) > 0:
            for conn in self.conns:
                #print("write to lircd socket")
                try:
                    #print("send code")
                    #line = " ".join([str(code), str(count), str(cmd), device])
                    keyname = self.keymap.get_keyname(cmd, code, device)
                    line = "{0:02x} {1:02x} {2} {4}_{3}\n".format(cmd, count, keyname, code, device)
                    #line = "%s\n" % line
                    line = line.encode('utf-8')
                    conn.send(line)
                except Exception as e: # garbage collection for lost clients - any better idea?
                    print(e)
                    print("cannot write to connection %s, removing client connection"%(conn))
                    conn.close()
                    self.conns.pop(self.conns.index(conn))

class Keymap:
    def __init__(self, keymap):
       print("reading keymap %s" % keymap)
       self.parser = configparser.SafeConfigParser(delimiters=(" ","\t"))
       self.parser.optionxform = str
       self.remotes = {}
       with open(keymap, 'r', encoding='utf-8') as f:
            self.parser.readfp(f)
       for remote in self.parser.keys():
            key_dict = {}
            for code, keyname in  self.parser[remote].items():
                #key_dict[eval(code)] = keyname
                key_dict[int(code, 16)] = keyname
            self.remotes[remote] = key_dict
             

    def get_keyname(self, cmd, address, decoder):
        #logging.debug("{0}_{1}".format(decoder, address),"{0:#02x}".format(cmd))
        try:
            return self.remotes["{0}_{1}".format(decoder, address)][cmd]
        except Exception as e:
            pass
            #print(e)
            
            
