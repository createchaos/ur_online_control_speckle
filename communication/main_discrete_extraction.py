'''
Created on 10.11.2018

@author: kathrind
'''
from __future__ import print_function
import time
import sys
import os

# set the paths to find library
file_dir = os.path.dirname( __file__)
parent_dir = os.path.abspath(os.path.join(file_dir, ".."))
#uronline_control = os.path.abspath(os.path.join(parent_dir, "fosterws2018")
sys.path.append(file_dir)
sys.path.append(parent_dir)

for path in sys.path:
    print(path)

import ur_online_control.communication.container as container
from ur_online_control.communication.server import Server
from ur_online_control.communication.client_wrapper import ClientWrapper
from ur_online_control.communication.formatting import format_commands
from helpers import send_cmd_place_sand

if len(sys.argv) > 1:
    server_address = sys.argv[1]
    server_port = int(sys.argv[2])
    ur_ip = sys.argv[3]
    print(sys.argv)
else:
    #server_address = "192.168.10.12"
    server_address = "127.0.0.1"
    server_port = 30003
    #ur_ip = "192.168.10.11"
    ur_ip = "127.0.0.1"


def main():

    # start the server
    server = Server(server_address, server_port)
    server.start()
    server.client_ips.update({"UR": ur_ip})

    # create client wrappers, that wrap the underlying communication to the sockets
    gh = ClientWrapper("GH")
    ur = ClientWrapper("UR")

    # wait for the clients to be connected
    gh.wait_for_connected()
    ur.wait_for_connected()
    
    number_of_completed_poses = 0

    # now enter fabrication loop
    while True: # and ur and gh connected

        # 1. let gh control if we should continue
        continue_fabrication = gh.wait_for_int()
        print("continue_fabrication: %i" % continue_fabrication)
        if not continue_fabrication:
            break

        # 2. set the tool tcp
        tool_pose = gh.wait_for_float_list() # client.send(MSG_FLOAT_LIST, tool_pose)
        print("2: set tool TCP")
        ur.send_command_tcp(tool_pose)

        # 3. receive command length
        len_command = gh.wait_for_int()
        print("We received %i the command length." % len_command)

        # 4. receive commands flattened, and format according to the sent length
        commands_flattened = gh.wait_for_float_list()
        commands = format_commands(commands_flattened, len_command)
        print("We received %i commands." % len(commands))
        
        # 5. receive safety commands flattened, and format according to the sent length
        savety_commands_flattened = gh.wait_for_float_list()
        savety_commands = format_commands(savety_commands_flattened, len_command)
        
        print("savety_commands_flattened: %s" % str(savety_commands_flattened))
        
        for i, cmd in enumerate(commands):
            
            x, y, z, ax, ay, az, acceleration, speed, io_value = cmd

            ur.send_command_digital_out(0, int(io_value)) # set DO to the received value
            print("set io: %i" % int(io_value))
            time.sleep(0.3)
                  
            ur.send_command_movel([x, y, z, ax, ay, az], a=acceleration, v=speed)
            ur.wait_for_ready()

            number_of_completed_poses += 1
            current_pose_joint = ur.wait_for_current_pose_joint()
            
            if i == len(commands) - 1: # send savety commands
                for cmd in savety_commands:
                    x, y, z, ax, ay, az, acceleration, speed, io_value = cmd    
                    ur.send_command_movel([x, y, z, ax, ay, az], a=acceleration, v=speed)
                ur.wait_for_ready()

            # send a command to gh to trigger the component  
            gh.send_float_list(current_pose_joint)
            
            # update wait time 
            wait_time = gh.wait_for_float_list()[0]
            time.sleep(wait_time)

            # check if the routine is paused
            pause = gh.wait_for_int()
            print("pause: %i" % pause)
            if pause:
                stop_pause = gh.wait_for_int()
            
            print("number of completed robot poses: %i" % number_of_completed_poses)
            print("wait_time in between poses: %f" % wait_time)
                    
        
        print("============================================================")
        """
        ur.wait_for_ready()
        # wait for sensor value
        digital_in = ur.wait_for_digital_in(number)
        current_pose_joint = ur.wait_for_current_pose_joint()
        current_pose_cartesian = ur.get_current_pose_cartesian()
        # send further to gh
        gh.send_float_list(digital_in)
        gh.send_float_list(current_pose_joint)
        gh.send_float_list(current_pose_cartesian)
        """
    ur.quit()
    gh.quit()
    server.close()

    print("Please press a key to terminate the program.")
    junk = sys.stdin.readline()
    print("Done.")

if __name__ == "__main__":
    main()