from Auto_Eval_Active import *
import dill
import sys

if __name__ == '__main__':

    directory = sys.argv[1]

    #Read the run config
    with open(os.path.join(directory, 'run_config.pkl'), 'rb') as file:
        args = dill.load(file)
    args = args['args']
    run_args = args[3]

    run_data = run_meta_selection_trials(directory, **run_args)

    #Save the run information
    with open(os.path.join(directory, 'meta_selection.pkl'),'wb') as file:
        dill.dump(run_data, file)
