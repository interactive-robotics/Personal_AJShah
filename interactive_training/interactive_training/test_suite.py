# -*- coding: utf-8 -*-
"""
Created on Wed Jan 20 12:26:35 2021

@author: AJShah
"""


from query_selection import *
import dill
import numpy as np
from puns import *
import json

if __name__ == '__main__':
    
    with open('sample_agent.pkl','rb') as file:
        sample_agent = dill.load(file)
    
    with open('dist_0.json','r') as file:
        sample_dist = json.load(file)
    
    sample_fsm = SpecificationFSM(sample_dist['support'], sample_dist['probs'])