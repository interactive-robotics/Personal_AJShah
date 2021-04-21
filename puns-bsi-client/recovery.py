from puns_bsi_client_dinner import *


nQuery=3 
n_postdemo = 3 
n_demo = 2
trials = 1

n_demo = n_demo + nQuery
demos = []
for i in range(n_demo):
    #send_text(f'Learning Phase: Provide demonstration {i+1} of {n_demo} \n\n Please follow experimenter instructions')
    #returnval = 1
    #while returnval:
    #    command = f'python3.6 /media/homes/demo/puns_demo/src/LTL_specification_MDP_control_MDP/scripts/run_teleop_agent_as_server.py --demo={i+1} --n-demo={n_demo}'
    #    returnval = os.system(command)
    #    if returnval:
    #        'Trying again: Reset the task and reactivate the robot'

    trace = parse_demonstration(i)
    new_demo = {}
    new_demo['trace'] = trace
    new_demo['label'] = True
    demos.append(new_demo)

send_data = create_batch_message([d['trace'] for d in demos])
dist = request_bsi_query(send_data)
specfile = 'Distributions/dist_0.json'
with open(specfile,'w') as file:
    json.dump(dist, file)

#Create MDP from the initial distribution
n_form = len(dist['probs'])
print(f'Initial Batch distributions has {n_form} formulas')
MDP = CreateSmallDinnerMDP(specfile)

display_waiting()
puns_request = create_puns_message(MDP, 'Puns')
#agent = send_puns_request(puns_request)
agent = send_puns_request(puns_request)
print('Final Agent saved')

#send_text('Task C: Starting Testing Phase')
display_questionnaire()
plt.pause(10)
for i in range(n_postdemo):
    #send_text(f'Testing Phase \n\n Showing {i+1} of {n_postdemo} task executions')
    display_eval_slide(i+1, n_postdemo)
    returnval = 1
    while returnval:
        command = f'python3.6 /media/homes/demo/puns_demo/src/LTL_specification_MDP_control_MDP/scripts/run_q_learning_agent_as_server_interactive.py demo {i}'
        returnval = os.system(command)
        if returnval:
            'Trying again: Reset the task and reactivate the robot'


display_post()

