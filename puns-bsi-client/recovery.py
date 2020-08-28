from puns_bsi_client_dinner import *

n_postdemo = 3

send_text('Task B: Starting Testing Phase')
plt.pause(5)
for i in range(n_postdemo):
    send_text(f'Testing Phase \n\n Showing {i+1} of {n_postdemo} task executions')
    command = f'python3.6 /media/homes/demo/puns_demo/src/LTL_specification_MDP_control_MDP/scripts/run_q_learning_agent_as_server_interactive.py demo {i}'
    returnval = os.system(command)


