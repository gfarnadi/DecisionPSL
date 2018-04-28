
# coding: utf-8

# In[14]:

import numpy as np
import pandas as pd
import sqlite3,os,random,cvxpy,math
from viral_marketing_sampling import prob_distribution_function
conn = sqlite3.connect('viral_marketing.db')
c = conn.cursor()


# In[30]:

def get_query_result(query):
    result = []
    c.execute(query)
    rows = c.fetchall()
    for row in rows:
        result.append(row)
    return result


# In[62]:

def k_MAP(k, delta, w1, w2):
    prob_distribution, vid_dict = prob_distribution_function(w1,w2)
    # make the range constraints [0,1]
    # make the constraints
    constraints = []
    for var, value in vid_dict.items():
        constraints += [0 <= value, value <= 1]
    query = '''SELECT * from reachable'''
    reachables = get_query_result(query)
    i=0
    while i<k:
        print('\nIteration\n%s'%('='*10))
        print(i)
        # Solve the problem
        objective = cvxpy.Minimize(prob_distribution)
        problem = cvxpy.Problem(objective, constraints)
        final_result = problem.solve()
        #print('\nProbability distribution\n%s'%('='*10))
        #print(prob_distribution)
        print('\nFunction Value\n%s'%('='*10))
        print(problem.value)
        # Process the results
        result = dict()
        for r in reachables:
            vid = (r[0],r[1])
            result[vid] = vid_dict[vid].value
        for var, value in vid_dict.items():
            optimal1 = float(result[var]+delta)
            optimal2 = float(result[var]-delta)
            #print("optimal1"+str(optimal1))
            #print("optimal2"+str(optimal2))
            constraints += [optimal1 < value, value < optimal2]
            
        #print ('\nConstraintss\n%s'%('='*10))
        #print(constraints)
        print('\nReachable results\n%s'%('='*10))
        print(result)
        i+=1
    


# In[63]:

def test_k_MAP():
    k = 5
    w1 = 1
    w2 = 1
    delta = 0.00000001
    k_MAP(k, delta, w1, w2)
    
test_k_MAP()


# In[ ]:



