#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar  8 13:40:16 2022

@author: ajshah
"""

from mpi4py import MPI
import time
import sys

if __name__ == '__main__':
    
    i = sys.argv[1]
    with open(f'file{i}.txt','w') as file:
        f.write('Here')
    print('Starting wait time')
    time.sleep(120)
    name = MPI.Get_processor_name()
    print('Hello running on {name}')
    
    
