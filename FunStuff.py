# -*- coding: utf-8 -*-
"""
Created on Wed Mar 10 11:54:15 2021

@author: AJShah
"""

def string_iterator(string):
    for i in range(len(string)):
        yield string[i]
    yield True

def find_including_substring(str1, str2):
    
    reverse_candidate_ends = [i for (i,c) in enumerate(str1) if c == str2[-1]]
    
    reverse_candidates = [str1[0:c+1] for c in reverse_candidate_ends]
    candidates = []
    for ci in reverse_candidates:
        candidate_starts = [i for (i,c) in enumerate(str1) if c == str2[0]]
        candidates.extend([ci[c::] for c in candidate_starts])
    
    max_len = max([len(c) for c in candidates])
    verifiers = [string_iterator(str2) for c in candidates]
    verified = [False]*len(candidates)
    ver_chars = [next(verifiers[i]) for i in range(len(candidates))]
    for i in range(max_len):
        
        for (j,c) in enumerate(candidates):
            if not verified[j]:
                if len(c) > i:
                    if c[i] == ver_chars[j]:
                        ver_chars[j] = next(verifiers[j])
                        if ver_chars[j] == True: 
                            verified[j] = True
                            break
    
    verified_candidates = [c for (c,v) in zip(candidates, verified) if v]
    return verified_candidates
        
    
    #return candidates
    
    
    
    
    
if __name__ == '__main__':
    str1 = 'basdaslasdasdadadashasld;,ma;sld,m;asldbaslasdaasdh'
    str2 = 'blah'