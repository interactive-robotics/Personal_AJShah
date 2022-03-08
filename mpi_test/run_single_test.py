#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar  8 13:40:16 2022

@author: ajshah
"""

from mpi4py import MPI
import time

if __name__ == '__main__':
    
    #wait for 20 seconds
    time.sleep(20)
    name = MPI.Get_processor_name()
    print('Hello running on {name}')
    
    