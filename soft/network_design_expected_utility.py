
# coding: utf-8

# In[3]:

import sqlite3,os,random
import cvxpy
from network_design_sampling import network_sampling
conn = sqlite3.connect('network_design.db')
c = conn.cursor()


# In[4]:

def get_samples(edges, sample_size):
    rejection_size = 10
    w1 = 1
    w2 = 1
    rv_list = []
    for e in edges:
         rv_list.append((e[0],e[1]))
    samples = sampling(w1,w2, rv_list , sample_size, rejection_size)
    return samples


# In[ ]:

def make_optimization(sample_size, budget, delta):
    # present(s,t) -> connected(s,t)
    # ~present(s,t) -> ~connected(s,t)
    # connected(s,t) -> path(s,t)
    # ~connected(s,t) -> ~path(s,t)
    # path(s,t1) & connected(t1,t2) -> path(s,t2)
    # path(s,t1) & ~connected(t1,t2) -> ~path(s,t2)
    # protected(s,t) -> connected(s,t)
    # ~present(s,t) & ~protected(s,t) -> ~connected(s,t)

    
    
    
    
    
    
    
make_optimization(sample_size=20, budget = 2, delta = 0.001)



