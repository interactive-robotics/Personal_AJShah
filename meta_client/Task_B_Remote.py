from puns_bsi_client_dinner import *
import sys

if __name__ == '__main__':
	
	subject_id = sys.argv[1]
	#active_trial_remote(nQuery=3, n_postdemo = 3, n_demo = 2)
	Batch_run(trials=0)
	record_subject_data(subject_id,'Demo')
