# This is a python3 port for the ros script on robbie-yuri

import math, copy, argparse, os, yaml, sys, time
from catkin.find_in_workspaces import find_in_workspaces
import socket, re
import rospy

server_address_observation = ('localhost', 10000)
server_address_action = ('localhost',10001)
server_address_start_end = ('localhost', 10002)
num_steps = 1

DEBUG = False

class runInteractiveDemoNoRobot():
    def __init__(self):
        # 1. Constants
        self.GLASS = "glass"
        self.CUP = "cup"
        self.BOWL = "bowl"
        self.FORK = "fork"
        self.SPOON = "spoon"
        self.KNIFE = "knife"
        self.BIG_PLATE = "big_plate"
        self.SMALL_PLATE = "small_plate"
        self.TAG_TABLEPLACING = "tag_tablePlacing"

        # 2. Task information
        self.objId_2_objName = {
            0: "DinnerPlate",
            1: "SmallPlate",
            2: "Bowl",
            3: "Knife",
            4: "Fork",
            5: "Spoon",
            6: "Mug",
            7: "Glass"
        }

        self.objName_2_obj = {
            "DinnerPlate": self.BIG_PLATE,
            "SmallPlate": self.SMALL_PLATE,
            "Bowl": self.BOWL,
            "Knife": self.KNIFE,
            "Fork": self.FORK,
            "Spoon": self.SPOON,
            "Mug": self.CUP,
            "Glass": self.GLASS
        }

        # 3. Create a TCP/IP server to receive the action
        # of the control MDP from the specification MDP.
        self.sock_action = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Bind the socket to the port
        print('Starting up on %s port %s' % server_address_observation)
        self.sock_action.bind(server_address_action)
        # Listen for incoming connections
        self.sock_action.listen(1)

    def check_connection(self):
        """Shake hand with server"""
        self.send_control_state([-1])
        while True:
            tmp = self.receive_control_action()
            if tmp == -2:
                break

    def run(self):
        self.num_objs = len(self.objId_2_objName)
        self.num_steps = num_steps
        self.cur_state = tuple([0] * self.num_objs)

        # 0. Send a dummy message to initiate specification MDP.
        self.send_control_state(self.cur_state)

        while True:
            # 1. Receive the action from specification MDP.
            control_action = self.receive_control_action()
            if DEBUG:
                print("Received control_action=" + str(control_action))

            if control_action == -1:
                if DEBUG:
                    print("Terminate")
                break

            # 2. Execute.
            cur_state_tmp = copy.deepcopy(list(self.cur_state))
            # If this task has already been finished,
            # return the current state.
            obj = self.objName_2_obj[self.objId_2_objName[control_action]]
            debug_msg = ""
            if self.cur_state[control_action] >= self.num_steps:
                if DEBUG:
                    print("obj=", obj, "is already finished.")
                debug_msg = "repetition"
            else:
                if DEBUG:
                    print("obj=", obj, "is not finished yet.")
                cur_state_tmp[control_action] = 1
                debug_msg = "success"
            self.cur_state = tuple(cur_state_tmp)

            # 3. Send the new control state back to
            # the specification MDP.
            self.send_control_state(self.cur_state)
            if DEBUG:
                print("Sent self.cur_state=" + str(self.cur_state))

    def close_sock(self):
        self.sock_action.close()

    def send_control_state(self, control_state):
        # Create a TCP/IP client to send the observation
        sock_observation = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # print '[send_control_state] Connecting to %s port %s'\
        # % server_address_observation
        sock_observation.connect(server_address_observation)
        try:
            control_state_str = ','.join([str(x) for x in control_state])
            control_state_str = "#" + control_state_str + "#"
            # print '[send_control_state] Sending "%s"' % control_state_str
            sock_observation.sendall(str.encode(control_state_str))

            response = ""
            while True:
                data = sock_observation.recv(16)
                # print '[send_control_state] Received "%s"' % data
                #print(data)
                #print(data.decode('utf-8'))
                response += data.decode('utf-8')
                if response == control_state_str:
                    break
        finally:
            # print "[send_control_state] closing socket"
            sock_observation.close()

    def receive_control_action(self):
        control_action = []

        # Wait for a connection
        # print '[receive_control_action] Waiting for a connection'
        connection, client_address = self.sock_action.accept()
        try:
            # print '[receive_control_action] Connection from', client_address

            # We need to concatenate the series of messages and
            # remove the b from "b'string'".
            response = ""

            # Receive the data in small chunks and retransmit it
            while True:
                data = connection.recv(16)
                # print '[receive_control_action] Received "%s"' % data
                if data:
                    response += data.decode('utf-8')
                    # print '[receive_control_action] Sending data back to the client'
                    connection.sendall(data)
                else:
                    # print '[receive_control_action] No more data from', client_address
                    break

            # print "[receive_control_action] response=[" + str(response) + "]"
            assert (response[0] == "#" and response[-1] == "#")
            control_action_result = re.search("#(.*)#", response)
            control_action_str = control_action_result.group(1)
            control_action = int(control_action_str)
        finally:
            # print "[receive_control_action] Clean up the connection"
            connection.close()
        return control_action


def receive_starting_ending_signal():
    # In run_q_learning_agent_as_server_interactive.py, we send 1 to run_interactive_demo.py to start it. In Meta_Demo.py, we send 2 to run_interactive_demo.py to end it.
    sock_start_end = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print('Starting up on %s port %s' % server_address_start_end)
    # https://stackoverflow.com/questions/7354476/python-socket-object-accept-time-out
    sock_start_end.settimeout(1200) 
    # Bind the socket to the port
    sock_start_end.bind(server_address_start_end)
    # Listen for incoming connections
    sock_start_end.listen(1)
    
    signal = None

    # Wait for a connection
    print('[receive_starting_ending_signal] Waiting for a connection')
    connection, client_address = sock_start_end.accept()
    try:
        print('[receive_starting_ending_signal] Connection from', client_address)
        # We need to concatenate the series of messages and
        # remove the b from "b'string'".
        response = ""

        # Receive the data in small chunks and retransmit it
        while True:
            data = connection.recv(16)
            print('[receive_starting_ending_signal] Received "%s"' % data)
            if data:
                response += data.decode("utf-8")
                print('[receive_starting_ending_signal] Sending data back to the client: ' + response)
                connection.sendall(data)
            else:
                print('[receive_starting_ending_signal] No more data from', client_address)
                break

        print("[receive_starting_ending_signal] response=[" + str(response) + "]")
        assert (response[0] == "#" and response[-1] == "#")
        result = re.search("#(.*)#", response)
        signal_str = result.group(1)
        signal = int(signal_str)
    finally:
        print("[receive_starting_ending_signal] Clean up the connection")
        connection.close()
        sock_start_end.close()
    return signal

if __name__ == "__main__":
    # https://github.com/shenlirobot/table_setup/blob/museum/scripts/run_interactive_demo.py
    count = 0
    while not rospy.is_shutdown():
        rospy.logwarn("\n\n\nWaiting for starting signal")
        starting_ending_signal = receive_starting_ending_signal()
        rospy.logwarn("Received starting_ending_signal=" + str(starting_ending_signal))
        assert starting_ending_signal in [1,2]
        if starting_ending_signal == 2:
            break

        d = runInteractiveDemoNoRobot()
        d.run()
        d.close_sock()

        print("\nDone")
    print("ALL DONE!")