
# coding: utf-8

# In[1]:

import os
import sys
sys.path.append(os.environ["PROBLOG_HOME"])
import problog
from problog.tasks.dtproblog import dtproblog
from problog.program import PrologString
from problog.tasks import sample


# In[2]:

def save_file(path, content):
    try:
        os.remove(path)
    except OSError:
        pass
    with open(path, 'a') as out:
        out.write(content+'\n')


# In[3]:

def read_lines(file_path):
    array = []
    with open(file_path, "r") as ins:
        for line in ins:
            line = line.replace("\n","").replace(" ","")
            if len(line)>0:
                array.append(line)
    return array


# In[4]:

def get_list(edge_path, user_path):
    edges_initial = read_lines(edge_path)
    edges = []
    for e in edges_initial:
        edge = e.split("\t")
        #print(edge)
        if len(edge)>1:
            edges.append((edge[0], edge[1]))    
    users = read_lines(user_path)
    return edges, users


# In[5]:

model_text = ""
for edge in [('e1','e2'), ('e2','e4')]:
         model_text+='trusts_directed(%s,%s).'%(edge[0],edge[1])
         model_text+='\n'
#print(model_text)


# In[6]:

def generate_dtproblog_program(edge_path, user_path, program_path):
    edge_list, user_list = get_list(edge_path, user_path)
    model_text = ""
    for user in user_list:
        model_text+='?::marketed(%s).'%user
        model_text+='\n'
        model_text+='utility(buys(%s), 5).'%user
        model_text+='\n'
        model_text+='utility(marketed(%s), -2).'%user
        model_text+='\n'
        model_text+='person(%s).'%user
        model_text+='\n'
    model_text+="1.0:: trusts_undirected(X,Y) :- trusts_directed(X,Y).\n"
    model_text+="1.0:: trusts_undirected(X,Y) :- trusts_directed(Y,X).\n"
    model_text+="0.4:: trusts(X,Y) :- trusts_undirected(X,Y).\n"
    model_text+="0.3:: trusts(X,Y) :- trusts_undirected(X,Z), trusts(Z,Y).\n"
    model_text+='0.2 :: buy_from_marketing(_).'+'\n'
    model_text+='0.3 :: buy_from_trust(_,_).'+'\n'
    for edge in edge_list:
        model_text+='trusts_directed(%s,%s).'%(edge[0],edge[1])
        model_text+='\n'
    model_text+='buys(X) :-'+'\n'
    model_text+='marketed(X),'+'\n'
    model_text+='buy_from_marketing(X).'+'\n'
    model_text+='buys(X) :-'+'\n'
    model_text+='trusts(X,Y),'+'\n'
    model_text+='buy_from_trust(X,Y),'+'\n'
    model_text+='buys(Y).'+'\n'
    save_file(program_path, model_text)
    return model_text


# In[7]:

def generate_program(node_size):
    sample_graph_path = "../sample_graphs2/"
    trust_file = sample_graph_path+"data/trust-"+str(node_size)+".txt"
    user_file = sample_graph_path+"data/user-"+str(node_size)+".txt"
    program_path = sample_graph_path+"model/dtproblog_model-"+str(node_size)+".txt"
    model_text = generate_dtproblog_program(trust_file, user_file, program_path)
    return model_text


# In[8]:

def run_dtproblog(node_size):
    model_text = generate_program(node_size)
    print(model_text)
    program = PrologString(model_text)
    decisions, score, statistics = dtproblog(program)
    print("++++++++ Program for node size = "+ str(node_size)+"++++++++")
    for name, value in decisions.items():
        print ('%s: %s' % (name, value))


# In[9]:

for node_size in [8,10,12,14,20]:
    generate_program(node_size)
    


# In[ ]:



