from Auto_Eval_Active import *
import dill

if __name__ == '__main__':

    #Read the run config
    with open('Run_Config/run_config.pkl', 'rb') as file:
        args = dill.load(file)
    args = args['args']
    run_args = args[2]

    run_data = run_batch_trial(**run_args)

    #Save the run information
    with open('Run_config/batch.pkl','wb') as file:
        dill.dump(run_data)
