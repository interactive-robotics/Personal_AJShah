# This is a python3 port for the ros script on robbie-yuri

import math, copy, argparse, os, yaml, sys, time
from catkin.find_in_workspaces import find_in_workspaces
import socket, re
from tqdm import tqdm

server_address_observation = ('localhost', 10000)
server_address_action = ('localhost',10001)
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

    def run(self, log_file_path):
        self.num_objs = len(self.objId_2_objName)
        self.num_steps = num_steps
        self.cur_state = tuple([0] * self.num_objs)

        #log_file_path = log_file_path + time.strftime("%y%m%d_%H%M%S",
                                                      time.localtime())

        # 0. Send a dummy message to initiate specification MDP.
        self.send_control_state(self.cur_state)

        time_log = []

        while True:
            # 1. Receive the action from specification MDP.
            control_action = self.receive_control_action()
            if DEBUG:
                print("Received control_action=" + str(control_action))

            time_log_iteration = {}
            if log_file_path != "":
                time_log_iteration[
                    "cur_state_before_executing_control_action"] = list(
                        self.cur_state)
                time_log_iteration["control_action"] = control_action
                if control_action != -1:
                    time_log_iteration["object_name"] = self.objId_2_objName[
                        control_action]

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

            if log_file_path != "":
                time_log_iteration["debug_msg"] = debug_msg
                time_log.append(time_log_iteration)
                #with open(log_file_path + ".yaml", 'w') as outfile:
                #    yaml.dump(time_log, outfile, default_flow_style=False)

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


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Pickup and Place multiple objects while "\
                "interacting with a specification MDP")

    parser.add_argument(
        "-fn",
        dest="log_file_name",
        default="",
        type=str,
        help="log_file_name")
    parser.add_argument(
        "-itr",
        dest="num_iteration",
        default=1,
        type=int,
        help="num_iteration")

    args = parser.parse_args()
    num_iteration = int(args.num_iteration)
    assert (num_iteration > 0)
    #log_file_name = args.log_file_name
    #log_path = find_in_workspaces(
    #    search_dirs=['share'],
    #    project="table_setup",
    #    path='logs',
    #    first_match_only=True)[0]
    log_file_path = 'log.txt'
    print("log_file_path=", log_file_path)

    d = runInteractiveDemoNoRobot()
    for i in tqdm(range(num_iteration)):
        #print('checking connection')
        #d.check_connection()
        #print('connection verified')
        d.run(log_file_path=log_file_path + "_" + str(i) + "_")
    d.close_sock()

    print("\nDone")
