#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 13 19:34:02 2019

@author: ajshah
"""

import socket
import matplotlib.pyplot as plt
import time

TEXT_HOST = 'localhost'
TEXT_PORT = 20000

fig = plt.gcf()
fig.set_size_inches(10,5)
fig.clear()
ax = plt.axes()
ax.get_xaxis().set_visible(False)
ax.get_yaxis().set_visible(False)
plt.box(False)

def show_text(text):
    ax.clear()
    plt.text(0.5, 0.5, text, fontsize = 32, verticalalignment = 'center', 
             horizontalalignment = 'center', wrap = True )
    plt.show()
    plt.pause(0.01)
    
def listen_server():
    while True: 
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
                s.bind((TEXT_HOST,TEXT_PORT))
                s.listen()
                
                print('Waiting for Text')
                conn,addr = s.accept()
                raw_data = b''
                while True:
                    newdata = conn.recv(4096)
                    raw_data += newdata
                    #print(newdata[-4::])
                    if not newdata: break
                rec_data = raw_data.decode()
                
                show_text(rec_data)

if __name__=='__main__':
    
    listen_server()
    