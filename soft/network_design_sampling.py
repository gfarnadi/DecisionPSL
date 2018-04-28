
# coding: utf-8

# In[1]:

import numpy as np
import pandas as pd
import sqlite3,os,random,cvxpy,math
from viral_marketing_sampling import get_acceptance_rate, sample_from_distribution, initialize_variables
conn = sqlite3.connect('network_design.db')
c = conn.cursor()


# In[2]:

def get_query_result(query):
    result = []
    c.execute(query)
    rows = c.fetchall()
    for row in rows:
        result.append(row)
    return result


# In[3]:

def prob_distribution_function_network_design(w1,w2):
    # ~presents(a,b)
    # ~edge(a,b)->~presents(a,b)
    # edge(s,t1) & edge(t1,t2) & ~presents(t1,t2) -> ~presents(s,t1)
    # edge(s,t1) & edge(s,t2) & ~present(s,t2) -> ~presents(s,t1)
    
    prob_distribution = 0
    
    query1 = '''
    SELECT * from rule1
    '''
    query2 = '''
    SELECT * from rule2
    '''
    query3 = '''
    SELECT * from presents
    '''
    
    #print('\nRule1\n%s'%('='*10))
    rule1 = get_query_result(query1)
    #print(rule1)
    
    #print('\nRule2\n%s'%('='*10))
    rule2 = get_query_result(query2)
    #print(rule2)
    
    #print('\nPresents\n%s'%('='*10))
    presents = get_query_result(query3)
    #print(presents)
    
    vid_dict = dict()
    #print(len(reachables))
    
    i = 0 
    for r in presents:
        vid_dict [(r[0],r[1])] = cvxpy.Variable()
        i+=1
    #print (len(vid_dict))
    
    
    for r in rule1:
        if r[3]==None:
            present = vid_dict [(r[0],r[1])]
        else:
            present = float(r[3])
        prob_distribution+=w1 * cvxpy.pos(present - float(r[2]))
        
    for r in rule2:
        if r[3]==None:
            present1 = vid_dict [(r[0],r[1])]
        else:
            reachable1 = float(r[3])
        if r[5]==None:
            present2 = vid_dict [(r[0],r[2])]
        else:
            present2 = float(r[5])
        prob_distribution+=w2 * cvxpy.pos(cvxpy.pos(present1 + float(r[4])-1.0) - present2)
        
    return prob_distribution, vid_dict


# In[4]:

def network_sampling(w1, w2, rv_list, sample_size, rejection_size):
    rv_size = len(rv_list)
    #print(rv_size)
    initial_sample = initialize_variables(rv_size)
    sample = []
    sample.append(initial_sample)
    prob_distribution, vid_dict = prob_distribution_function_network_design(w1,w2)
    i=0
    while len(sample)<sample_size+rejection_size+1:
        previous_state = sample[-1]
        #print(len(previous_state))
        current_state = sample_from_distribution(previous_state, rv_size)
        acceptace = get_acceptance_rate(prob_distribution, vid_dict, current_state, previous_state)
        if (acceptace>=1):
            previous_state = current_state
            sample.append(previous_state)
            i+=1
        else:
            ran = random.random()
            if ran < acceptace:
                previous_state = current_state
                sample.append(previous_state)
                i+=1                   
    return sample    


# In[ ]:




# In[ ]:



