from puns_bsi_client_dinner import *
import sys
import dill

if __name__ == '__main__':
	
	subject_id = sys.argv[1]
	Active_run(trials=0)
	record_subject_data(subject_id,'Active')
