from puns_bsi_client_dinner import *
import sys

if __name__ == '__main__':
	
	subject_id = sys.argv[1]
	batch_trial_remote(nQuery=3, n_postdemo = 3, n_demo = 2, trials=1)
	record_subject_data(subject_id,'Batch')