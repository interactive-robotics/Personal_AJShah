#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar  8 13:18:51 2022

@author: ajshah
"""
from mpi4py import MPI
from mpi4py.futures import MPIPoolExecutor
import sys
import os
import time

def print_hello(rank, size, name):
  msg = "Hello World! I am process {0} of {1} on {2}.\n"
  sys.stdout.write(msg.format(rank, size, name))
  
def test_mpi_executor(n_cores = 48):
    commands = [f'python run_single_test.py {i}' for i in range(n_cores)]
    print(commands)
    with MPIPoolExecutor(max_workers = n_cores) as executor:
        retvals = executor.map(os.system, commands)
    retvals = list(retvals)
    return retvals

def mpi_test():
    size = MPI.COMM_WORLD.Get_size()
    rank = MPI.COMM_WORLD.Get_rank()
    name = MPI.Get_processor_name()
    print_hello(rank, size, name)
    

if __name__ == "__main__":
    
    
    mpi_test()
    
    '''
    start = time.time()
    n_cores = 32
    commands = [f'python run_single_test.py {i}' for i in range(n_cores)]
    print(commands)
    with MPIPoolExecutor(max_workers = n_cores) as executor:
        retvals = executor.map(os.system, commands)
    retvals = list(retvals)
    #return retvals
    end = time.time()
    print('Time elapsed: ', end-start)
    '''