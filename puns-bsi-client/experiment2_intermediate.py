# -*- coding: utf-8 -*-
"""
Created on Wed Oct  7 11:02:53 2020

@author: AJShah
"""

from puns_bsi_client_dinner import *


results_path = 'C:/Users/AJShah/Google Drive/Remote Interactive Robot Training/TableSetup_SubjectData'
discard = set([1])

def create_incremental_batch_dists():
    
    subject_dirs = os.listdir(results_path)
    
    for folder in subject_dirs:
        
        if folder.split('_')[0] == 'subject':
            if int(folder.split('_')[1]) not in discard :
                if folder.split('_')[2] == 'Batch':
                    
                    subj_id = int(folder.split('_')[1])
                    create_incremental_batch_dists_subject(subj_id)
                    
    

def get_task_assignments():
    
    task1 = []
    for i in range(10):
        
        base = 3*(2*i+1)
        task1.extend([base-1, base, base+1])
    
    task1 = set(task1)
    
    task2 = []
    for i in range(10):
        j = i+1
        base = 6*j
        task2.extend([base-1, base, base+1])
    task2 = set(task2)
    
    return task1, task2



def rename_dists():
    
    subject_dirs = os.listdir(results_path)
    
    for folder in subject_dirs:
        
        #verify that it is subject data
        if folder.split('_')[0] == 'subject':
            #Check if the subject was excluded
            if int(folder.split('_')[1]) not in discard:
                #Check for batch protocol:
                if folder.split('_')[2] == 'Batch':
                    
                    oldname = os.path.join(results_path,folder,'Distributions','dist_0.json')
                    newname = os.path.join(results_path,folder,'Distributions','dist_3.json')
                    os.rename(oldname, newname)

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
    
if __name__ == '__main__':
    create_incremental_batch_dists()