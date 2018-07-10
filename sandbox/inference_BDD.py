
# coding: utf-8

# In[1]:

import tempfile, subprocess, os, sys
from collections import namedtuple

BddNode = namedtuple('BDDNode', ['id', 'varid', 'hi', 'lo'])
Variable = namedtuple('Variable', ['id', 'pweight', 'nweight', 'is_decision'])
BDD = namedtuple('BDD', ['bdd_nodes', 'bdd_vars', 'roots', 'max_vars'])


# In[48]:

def read_bdd(filename):
    with open(filename) as f:
        nn, nv = map(int, f.readline().strip().split())
        bdd_vars = [Variable(i, 1.0, 1.0, False) for i in range(nv)]
        roots = set(map(int, f.readline().strip().split()))
        bdd_nodes = [None] * nn
        for i in range(nn):
            varid, lo, hi = map(int, f.readline().strip().split())
            bdd_nodes[i] = BddNode(i, varid, hi, lo)

        weights = list(map(float, f.readline().strip().split()))
        for i in range(nv):
            bdd_vars[i] = bdd_vars[i]._replace(pweight=weights[2*i],
                                               nweight=weights[2*i + 1])

        max_vars = set(map(int, f.readline().strip().split()))
        for v in max_vars:
            bdd_vars[v] = bdd_vars[v]._replace(is_decision=True)

    return BDD(bdd_nodes, bdd_vars, roots, max_vars)


# In[49]:

filename = "./data/toy1.txt"
BDD_sample  = read_bdd(filename)
BDD_sample.bdd_nodes


# In[58]:

def run_inference(bdd):
    inference_value = 0.0
    dynamic_value_holder ={}
    for root in bdd.roots:
        bdd_node = find_node(root, bdd)
        inference_value+=get_inference_value(bdd_node, bdd, dynamic_value_holder)
    return inference_value

def find_node(root, bdd):
    for node in bdd.bdd_nodes:
        if node.id == root:
            return node
        
def find_variable(variable, bdd):
    for var in bdd.bdd_vars:
        if var.id == variable:
            return var

def get_inference_value(bdd_node, bdd, dynamic_value_holder):
    if bdd_node in dynamic_value_holder.keys():
        return dynamic_value_holder[bdd_node]
    else:
        inference_result = 0.0
        variable = find_variable(bdd_node.varid,bdd)
        if bdd_node.hi == -2:
            if bdd_node.lo == -2:
                dynamic_value_holder[bdd_node] = 1.0 * variable.pweight + 1.0 * (1-variable.pweight)
                return dynamic_value_holder[bdd_node]
            elif bdd_node.lo == -1:
                dynamic_value_holder[bdd_node] = 1.0 * variable.pweight
                return dynamic_value_holder[bdd_node]
            elif bdd_node.lo>-1:
                return 1.0 * variable.pweight + get_inference_value(find_node(bdd_node.lo,bdd),bdd, dynamic_value_holder) * (1-variable.pweight)
            else:
                 pass
        elif bdd_node.hi == -1:
            if bdd_node.lo == -2:
                dynamic_value_holder[bdd_node] = 1.0 * (1-variable.pweight)
                return dynamic_value_holder[bdd_node] 
            elif bdd_node.lo == -1:
                dynamic_value_holder[bdd_node] = 0.0
                return dynamic_value_holder[bdd_node]
            elif bdd_node.lo>-1:
                return get_inference_value(find_node(bdd_node.lo,bdd),bdd, dynamic_value_holder) * (1-variable.pweight)
            else:
                pass
        elif bdd_node.hi>-1:
            if bdd_node.lo == -2:
                return get_inference_value(find_node(bdd_node.hi,bdd),bdd, dynamic_value_holder) * variable.pweight + 1.0 * (1-variable.pweight)
            elif bdd_node.lo == -1:
                return get_inference_value(find_node(bdd_node.hi,bdd),bdd, dynamic_value_holder) * variable.pweight 
            elif bdd_node.lo > -1:
                return get_inference_value(find_node(bdd_node.hi,bdd),bdd, dynamic_value_holder) * variable.pweight + get_inference_value(find_node(bdd_node.lo,bdd),bdd, dynamic_value_holder) * (1-variable.pweight)
        else:
            pass


# In[59]:

run_inference(BDD_sample)


# In[ ]:



