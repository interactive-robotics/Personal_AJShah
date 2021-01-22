# -*- coding: utf-8 -*-
"""
Created on Tue Oct  6 21:38:41 2020

@author: AJShah
"""

from puns_bsi_client_dinner import *

subject_id = list(range(19))
exclude = [0,5,8,13]

subject_id = [a  for a in subject_id if a not in exclude]

results_path = 'F:\TableSetup_SubjectData'


def create_incremental_batch_dists_subject(subj_id):
    
    demo_path = os.path.join(results_path, f'subject_{subj_id}_Batch', 'demos')
    dist_path = os.path.join(results_path, f'subject_{subj_id}_Batch', 'Distributions')
    
    #send batch bsi requests for 2,3,4 demos
    
    for i in range(3):
        
        demos = []
        
        #first parse the relevant demos
        for demo_id in range(i+2):
            demos.append(parse_demonstration(demo_id, demo_path))
        
        request = create_batch_message(demos)
        dist = request_bsi_query(request)
        distfile = os.path.join(dist_path, f'dist_{i}.json')
        with open(distfile,'w') as file:
            json.dump(dist, file)
            

def create_incremental_batch_dists(subject_ids):
    
    for subj in subject_ids:
        print(f'Running Subject {subj}')
        create_incremental_batch_dists_subject(subj)
        
        
        
    

def rename_dists():
    
    for subj in subject_id:
    
        dist_dir = os.path.join(results_path, f'subject_{subj}_Batch','Distributions')
        old_name = os.path.join(dist_dir, 'dist_0.json')
        new_name = os.path.join(dist_dir, 'dist_3.json')
        
        os.rename(old_name, new_name)

def parse_demonstration(demo_id = 0, path = 'demos'):
    
    
    demofile = os.path.join(path, f'demo_{demo_id}.txt')
    #demofile = f'demos/demo_{demo_id}.txt'

    if os.path.exists(demofile):
        with open(demofile,'r') as file:
            lines = file.readlines()

        state_tuples = [tuple(json.loads(line)) for line in lines]
        cmdp = SmallTableMDP()
        trace_slices = [cmdp.create_observations(t) for t in state_tuples]
        return trace_slices

    else:
        print(f'Record demonstration {demo_id}')
        print('Press Enter when demonstration is recorded')
        input()
        return parse_demonstration(demo_id)
        


    


if __name__ == '__main__':
    
    create_incremental_batch_dists(subject_id)
    
    '''Test 1'''
    # subj_id = 100
    # demo_path = os.path.join(results_path, f'subject_{subj_id}_Batch', 'demos')
    
    # trace = parse_demonstration(0, demo_path)
    
    
    '''Test 2'''
    # subj_id = 1000
    # create_incremental_batch_dists(subj_id)
    