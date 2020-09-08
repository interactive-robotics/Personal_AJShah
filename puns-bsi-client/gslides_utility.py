# -*- coding: utf-8 -*-
"""
Created on Thu Sep  3 10:30:35 2020

@author: AJShah
"""

import pickle
import os.path
from googleapiclient.discovery import build
from google.oauth2 import service_account
from google.auth.transport.requests import Request

SCOPES = ['https://www.googleapis.com/auth/presentations']

SAMPLE_PID = '1rOk9sLMrMHZUxQnJlGN0VntimIeIvWH93r1fmVAoMdE'
DISPLAY_PID = '1LSwaOUx2PQSgX8Ad-aSi_CToBl41W5M9zVzf8J6IyYE'

# Preload the slides library



def generate_services():
    cred_file = 'GSheetsKey.json'
    creds = service_account.Credentials.from_service_account_file('GSheetsKey.json', scopes = SCOPES)
    service = build('slides','v1', credentials = creds)
    
    return service

def display_slide(slide):
    a=1

service = generate_services()
slides = service.presentations().get(presentationId = DISPLAY_PID).execute()['slides']

slide_idx = {}
slide_idx['welcome'] = 1
slide_idx['demo_intro'] = 2
slide_idx['demo_ready'] = 3
slide_idx['demo_waiting'] = 4
slide_idx['query_waiting'] = 5
slide_idx['query_assessment'] = 6
slide_idx['query_confirmation'] = 7
slide_idx['eval'] = 8
slide_idx['questionnaire'] = 9


def display_welcome():
    display_slide(slide_idx['welcome'])

def display_trial_demo_intro():
    update_trial_demo()
    idx = slide_idx['demo_intro']
    display_slide(idx)

def display_trial_demo_ready():
    update_trial_demo()
    idx = slide_idx['demo_ready']
    display_slide(idx)

def display_trial_demo_waiting(action):
    update_trial_demo()
    update_action_slide(action)
    idx = slide_idx['demo_waiting']
    display_slide(idx)

def display_demo_intro(demo, nDemo):
    idx = slide_idx['demo_intro']
    update_demo_slide(demo, nDemo, idx)
    display_slide(idx)

def display_demo_ready(demo, nDemo):
    idx = slide_idx['demo_ready']
    update_demo_slide(demo, nDemo, idx)
    display_slide(idx)
    

def display_demo_waiting(demo, nDemo, action):
    idx = slide_idx['demo_waiting']
    update_demo_slide(demo, nDemo, idx)
    update_action_slide(action)
    display_slide(idx)

def display_query_waiting():
    display_slide(slide_idx['query_waiting'])

def display_query_assessment():
    display_slide(slide_idx['query_assessment'])

def display_query_confirmation(label):
    idx = slide_idx['query_confirmation']
    update_assessment_slide(label)
    display_slide(idx)

def display_eval_slide(demo, nPostDemo):
    idx = slide_idx['eval']
    update_eval_slide(demo, nPostDemo)
    display_slide(idx)
    
def display_questionnaire():
    idx = slide_idx['questionnaire']
    display_slide(idx)

def update_trial_demo():
    idx = [slide_idx['demo_intro'], slide_idx['demo_ready'], slide_idx['demo_waiting']]

    for i in idx:
        slide = slides[i]
        title_object_id = slide['pageElements'][0]['objectId']
        request = []

        request.append({
            'deleteText':{
            'objectId': title_object_id,
            'textRange': {'type': 'ALL'}
            }
            })

        request.append({
            'insertText':{
            'objectId': title_object_id,
            'text': f'Trial Demonstration'}
            })
        response = service.presentations().batchUpdate(presentationId=DISPLAY_PID, body = {'requests': request}).execute()

    

def update_demo_slide( demo, nDemo, idx=1):
    
    slide = slides[idx]
    title_obj_id = slide['pageElements'][0]['objectId']
    request = []
    request.append({
        'deleteText':{
            'objectId': title_obj_id,
            'textRange': {'type': 'ALL'}
            }
        })
    
    request.append({
        'insertText':{
            'objectId': title_obj_id,
            'text': f'Learning Phase: Demo {demo} of {nDemo}'}
        })
    
    response = service.presentations().batchUpdate(presentationId=DISPLAY_PID, body = {'requests': request}).execute()
    return response

def update_action_slide(action):
    slide = slides[4]
    text_obj_id = slide['pageElements'][1]['objectId']
    
    request = []
    
    request.append({
        'deleteText':{
            'objectId': text_obj_id,
            'textRange': {'type': 'ALL'}
            }
        })
    
    request.append({
        'insertText':{
            'objectId': text_obj_id,
            'text': f'Please wait for the robot to complete the action: {action}'}
        })
    response = service.presentations().batchUpdate(presentationId=DISPLAY_PID, body = {'requests': request}).execute()

def update_assessment_slide(label):
    slide = slides[slide_idx['query_confirmation']]
    text_object_id = slide['pageElements'][1]['objectId']
    
    request = []
    
    request.append({
        'deleteText': {
            'objectId': text_object_id,
            'textRange': {'startIndex':0, 'type': 'FROM_START_INDEX'}
            }
        })
    
    request.append({
        'insertText':{
            'objectId': text_object_id,
            'text':f'Your assessment was: {label}'}
        })
    
    response = service.presentations().batchUpdate(presentationId = DISPLAY_PID, body = {'requests': request}).execute()
    
def update_eval_slide(idx, nPostDemo):
    slide = slides[slide_idx['eval']]
    text_object_id = slide['pageElements'][1]['objectId']
    
    request  = []
    
    request.append({
        'deleteText': {
            'objectId': text_object_id,
            'textRange': {'startIndex': 0, 'type': 'FROM_START_INDEX'}
            }
        })
    
    request.append({
        'insertText':{
            'objectId': text_object_id,
            'text': f'The Robot is ready to perform {idx} of {nPostDemo} demonstrations '
            }
        })
        
    response = service.presentations().batchUpdate(presentationId = DISPLAY_PID, body = {'requests': request}).execute()
    
def display_slide(slide_idx):
    
    curr_slides = service.presentations().get(presentationId=DISPLAY_PID).execute()['slides']
    curr_display_slide_id = curr_slides[0]['objectId']
    new_display_slide_id = curr_slides[slide_idx]['objectId']
    copied_id = 'copy' + new_display_slide_id
    
    #Copy the new display slide
    request = []
    
    
    
    request.append({
        'duplicateObject': {
            'objectId': new_display_slide_id,
            'objectIds':{new_display_slide_id: copied_id} 
            }})
    #response = service.presentations().batchUpdate(presentationId=DISPLAY_PID, body = {'requests': request}).execute()
    #print(response)
    #repositions the new slide
    request.append({
        'updateSlidesPosition':{
            'slideObjectIds': copied_id,
            'insertionIndex': 1}
            })
    response = service.presentations().batchUpdate(presentationId=DISPLAY_PID, body = {'requests': request}).execute()
    
    request = [{
        'deleteObject':{
            'objectId': curr_display_slide_id}
        }]
    
    response = service.presentations().batchUpdate(presentationId=DISPLAY_PID, body = {'requests': request}).execute()
    #Delete the old display slide


