'''
Created on 21.10.2017

@author: rustr
'''

from __future__ import print_function

import time
import struct
import sys, os

# set the paths to find library
file_dir = os.path.dirname( __file__)
parent_dir = os.path.abspath(os.path.join(file_dir, ".."))
parent_parent_dir = os.path.abspath(os.path.join(parent_dir, ".."))
parent_parent_parent_dir = os.path.abspath(os.path.join(parent_parent_dir, ".."))
sys.path.append(file_dir)
sys.path.append(parent_dir)
sys.path.append(parent_parent_dir)
sys.path.append(parent_parent_parent_dir)

from base_client import BaseClient
from ur_online_control_py3.communication.msg_identifiers import *

class URClient(BaseClient):
    
    def __init__(self, host = '127.0.0.1', port = 30003): 
        super(URClient, self).__init__("UR", host, port)
        self.ghenv = None
    
    def stdout(self, msg):
        print(msg)
    
    def send_command_received(self, counter):
        self._send(MSG_COMMAND_RECEIVED, counter)
            
    def send_command_executed(self, counter):
        self._send(MSG_COMMAND_EXECUTED, counter)
        
    def _format_other_messages(self, msg_id, msg = None):
        if msg_id == MSG_COMMAND_RECEIVED or msg_id == MSG_COMMAND_EXECUTED:
            msg_snd_len = 4 + 4
            params = [msg_snd_len, msg_id, msg]
            buf = struct.pack(self.byteorder + "3i", *params)
            return buf
    
    def _process_other_messages(self, msg_len, msg_id, raw_msg):
        if msg_id == MSG_COMMAND:
            
            """
            msg_length = rcv[1]
            msg_id = rcv[2]
            if msg_id == MSG_COMMAND:
            rcv2 = socket_read_binary_integer(2)
            msg_command_id = rcv2[1]
            command_counter = rcv2[2]
            
            msg_float_tuple = struct.unpack_from(self.byteorder + str((msg_len-4)/4) + "f", raw_msg)
            """
            self.stdout("Received MSG_COMMAND")
            msg = struct.unpack_from(self.byteorder + "%ii" % int((msg_len-4)/4), raw_msg)
            cmd_id = msg[0]
            counter = msg[1]
            print(counter)
            self.send_command_received(counter)
            time.sleep(0.5)
            self.send_command_executed(counter)
        else:
            self.stdout("Message identifier unknown: %d, message: %s" % (msg_id, raw_msg))

                
if __name__ == "__main__":
    #server_address = "192.168.10.111"
    server_address = "192.168.10.111"
    
    server_port = 30003
    client = URClient(server_address, server_port)
    success = client.connect_to_server() 
    print(success) 
    if success:  
        client.start()
    print("running")
    #client.send(MSG_FLOAT_LIST, [1.2, 3.6, 4, 6, 7])
    #client.send(MSG_INT, 1)
    #client.send(MSG_FLOAT_LIST, [1.2, 3.6, 4, 6, 7])
    