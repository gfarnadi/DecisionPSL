
# coding: utf-8

# In[1]:

import numpy as np
import pandas as pd
import sqlite3,os,random,cvxpy,math
conn = sqlite3.connect('viral_marketing.db')
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

def get_prob_distribution(w1,w2, state):
    #trusts(a,b)->reachable(a,b)
    #reachable(a,b) & trusts(b,c) -> reachable(a,c)
    
    #print(state)
    #print(len(state))
    prob_distribution = 0
    
    query1 = '''
    SELECT * from rule1
    '''
    query2 = '''
    SELECT * from rule2
    '''
    query3 = '''
    SELECT * from reachable
    '''
    
    #print('\nRule1\n%s'%('='*10))
    rule1 = get_query_result(query1)
    #print(rule1)
    
    #print('\nRule2\n%s'%('='*10))
    rule2 = get_query_result(query2)
    #print(rule2)
    
    #print('\nReachables\n%s'%('='*10))
    reachables = get_query_result(query3)
    #print(reachables)
    
    vid_dict = dict()
    #print(len(reachables))
    
    i = 0 
    for r in reachables:
        vid_dict [(r[0],r[1])] = state[i]
        i+=1
    #print (len(vid_dict))
    
    
    for r in rule1:
        if r[3]==None:
            reachable = vid_dict [(r[0],r[1])]
        else:
            reachable = float(r[3])
        prob_distribution+=w1 * cvxpy.pos(reachable - float(r[2]))
        
    for r in rule2:
        if r[3]==None:
            reachable1 = vid_dict [(r[0],r[1])]
        else:
            reachable1 = float(r[3])
        if r[5]==None:
            reachable2 = vid_dict [(r[0],r[2])]
        else:
            reachable2 = float(r[5])
        prob_distribution+=w2 * cvxpy.pos(cvxpy.pos(reachable1 + float(r[4])-1.0) - reachable2)
        
        obj = cvxpy.Minimize(prob_distribution)
        prob = cvxpy.Problem(obj, [])
        result = prob.solve()
        
    return result


# In[4]:

def prob_distribution_function(w1,w2):
    #trusts(a,b)->reachable(a,b)
    #reachable(a,b) & trusts(b,c) -> reachable(a,c)
    
    #print(state)
    #print(len(state))
    prob_distribution = 0
    
    query1 = '''
    SELECT * from rule1
    '''
    query2 = '''
    SELECT * from rule2
    '''
    query3 = '''
    SELECT * from reachable
    '''
    
    #print('\nRule1\n%s'%('='*10))
    rule1 = get_query_result(query1)
    #print(rule1)
    
    #print('\nRule2\n%s'%('='*10))
    rule2 = get_query_result(query2)
    #print(rule2)
    
    #print('\nReachables\n%s'%('='*10))
    reachables = get_query_result(query3)
    #print(reachables)
    
    vid_dict = dict()
    #print(len(reachables))
    
    i = 0 
    for r in reachables:
        vid_dict [(r[0],r[1])] = cvxpy.Variable()
        i+=1
    #print (len(vid_dict))
    
    
    for r in rule1:
        if r[3]==None:
            reachable = vid_dict [(r[0],r[1])]
        else:
            reachable = float(r[3])
        prob_distribution+=w1 * cvxpy.pos(reachable - float(r[2]))
        
    for r in rule2:
        if r[3]==None:
            reachable1 = vid_dict [(r[0],r[1])]
        else:
            reachable1 = float(r[3])
        if r[5]==None:
            reachable2 = vid_dict [(r[0],r[2])]
        else:
            reachable2 = float(r[5])
        prob_distribution+=w2 * cvxpy.pos(cvxpy.pos(reachable1 + float(r[4])-1.0) - reachable2)
        
    return prob_distribution, vid_dict


# In[5]:

def get_value_of_prob_distribution(prob_distribution, vid_dict, state):
    value = 0.0
    i = 0
    for key,value in vid_dict.items():
        vid_dict[key].value = state[i]
        i+=1
    return prob_distribution.value
    


# In[6]:

def initialize_variables(rv_size):
    initial_sample = []
    for i in range(rv_size):  
        v = random.random()
        initial_sample.append(v)
    return initial_sample 


# In[7]:

def calculate_mean(previous_state):
    n = len(previous_state)
    mean_matrix=[]
    state = []
    for j in range(n):
        state.append(1.0)
    mean_matrix.append(state)
    for i in range(n):
        state = []
        for j in range(n):
            if i==j:
                state.append(previous_state[j]-1.0)
            else:
                state.append(previous_state[j])
        mean_matrix.append(state)
    b=[1.0]
    for i in range(n):
        b.append(0.0)
    solution = np.linalg.lstsq(mean_matrix, b)[0]
    return solution


# In[8]:

def sample_from_distribution(previous_state, rv_size):
    state = calculate_mean(previous_state)
    current_state  =  np.random.dirichlet(state, 1)
    return current_state[0]


# In[9]:

def get_acceptance_rate(prob_distribution, vid_dict, current_state, previous_state):
    #accept =  min(1, get_value(w1, w2, current_state)/ get_value(w1, w2, previous_state))
    accept = min(1, get_value_of_prob_distribution(prob_distribution, vid_dict, current_state) 
                 / get_value_of_prob_distribution(prob_distribution, vid_dict, previous_state))
    return accept


# In[10]:

def get_value(w1, w2, state):
    value = get_prob_distribution(w1, w2, state)
    return value


# In[11]:

def sampling(w1, w2, rv_list, sample_size, rejection_size):
    rv_size = len(rv_list)
    #print(rv_size)
    initial_sample = initialize_variables(rv_size)
    sample = []
    sample.append(initial_sample)
    prob_distribution, vid_dict = prob_distribution_function(w1,w2)
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

#samples = sampling(1 , 1 , ['r1','r2','r3'], 10, 10)
#print(samples)


# In[ ]:



