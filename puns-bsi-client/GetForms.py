# -*- coding: utf-8 -*-
"""
Created on Wed Aug 26 13:08:21 2020

@author: AJShah
"""

import gspread
from oauth2client.service_account import ServiceAccountCredentials
import time

scope = ['https://spreadsheets.google.com/feeds']
cred = ServiceAccountCredentials.from_json_keyfile_name('GSheetsKey.json', scope)
gc = gspread.authorize(cred)

def get_current_record():
    workbook = gc.open_by_url('https://docs.google.com/spreadsheets/d/1-WHaUoXEJ5Ksw6TjscpBtoT7BiZd4kkmRiXDN8rbJQ0/edit?usp=sharing')
    data = workbook.get_worksheet(0)
    return data.get_all_records()

def checkdiff(previous_record, new_record):
    return len(previous_record) != len(new_record)

def get_last_object(new_record):
    
    return new_record[-1]['Object Selection']

def get_latest_object(previous_record):
    flag = True
    while flag:
        #print('Checking for updates')
        new_record = get_current_record()
        
        if checkdiff(previous_record, new_record):
            return (get_last_object(new_record), new_record)
        else:
            time.sleep(2)
            
    

if __name__ == '__main__':
    
    flag = True
    previous_record = get_current_record()
    while flag:
        print('Checking for new response')
        (new_object, new_record) = get_latest_object(previous_record)
        previous_record = new_record
        print(new_object)
        
        if new_object == 'End Task':
            break 
        
        
        
    
    
    