from Auto_Eval_Active import *
import dill
import sys

if __name__ == '__main__':

    directory = sys.argv[1]

    #Read the run config
    with open(os.path.join(directory, 'run_config.pkl'), 'rb') as file:
        args = dill.load(file)
    args = args['args']
    run_args = args[2]

    run_data = run_batch_trial(**run_args)

    #Save the run information
    with open(os.path.join(directory, 'batch.pkl'),'wb') as file:
        dill.dump(run_data, file)
