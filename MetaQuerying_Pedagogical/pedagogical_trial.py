from Auto_Eval_Active import *
import dill
import sys

if __name__ == '__main__':

    directory = sys.argv[1]
    arg_id = sys.argv[2]
    arg_id = int(arg_id)

    #Read the run config
    with open(os.path.join(directory, '..', 'run_config.pkl'), 'rb') as file:
        args = dill.load(file)
    args = args['args']
    run_args = args[arg_id]

    run_data = run_pedagogical_trials(directory, **run_args)

    #Save the run information
    with open(os.path.join(directory, '..', f'condition_{arg_id}.pkl'),'wb') as file:
        dill.dump(run_data, file)
