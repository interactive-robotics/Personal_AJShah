from puns_bsi_client_dinner import *
import sys
from IPython import embed
import socket
import re, argparse
import rospy


server_address_start_end = ('localhost', 20002)

if __name__ == '__main__':
    rospy.init_node('Meta_Demo', anonymous=True)
    # Make sure sim time is working
    while not rospy.Time.now():
        pass

    subject_id = sys.argv[1]
    #active_trial_remote(nQuery=3, n_postdemo = 3, n_demo = 2)
    # Meta_demo(n_demo = 3, n_query = 1, n_postdemo = 1)
    #record_subject_data(subject_id,'Lab_Demo')

    # 220817: Based on Shen and Ankit's email about <question about puns> (see https://github.com/interactive-robotics/Personal_AJShah/blob/museum_demo/meta_client/failed_demos_for_debug/220817/notes.txt):
    Active_demo(n_demo = 3, n_query = 1, n_postdemo = 1)

    # In run_q_learning_agent_as_server_interactive.py, we send 1 to run_interactive_demo.py to start it. In Meta_Demo.py, we send 2 to run_interactive_demo.py to end it.
    sock_end = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print('[sock_end] Connecting to %s port %s' % server_address_start_end)
    sock_end.connect(server_address_start_end)
    try:
        ending_str = '#2#' # 2 means ending; 1 means starting.
        print('[sock_end] Sending "%s"' % ending_str)
        sock_end.sendall(str.encode(ending_str))

        response = ""
        while True:
            data = sock_end.recv(16)
            # print('[sock_end] Received "%s"' % data)
            response += data.decode("utf-8")
            if response == ending_str:
                break
    finally:
        print("[sock_end] closing socket")
        sock_end.close()