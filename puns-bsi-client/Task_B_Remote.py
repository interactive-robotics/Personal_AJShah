from puns_bsi_client_dinner import *
import sys

if __name__ == '__main__':
	
	subject_id = sys.argv[1]
	random_trial_remote(nQuery=1, n_postdemo = 1, n_demo = 2)
	record_subject_data(subject_id,'Random')