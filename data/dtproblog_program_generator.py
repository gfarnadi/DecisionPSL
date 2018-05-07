
# coding: utf-8

# In[1]:

import os


# In[2]:

def save_file(path, content):
    try:
        os.remove(path)
    except OSError:
        pass
    with open(path, 'a') as out:
        out.write(content+'\n')


# In[4]:

def read_lines(file_path):
    array = []
    with open(file_path, "r") as ins:
        for line in ins:
            array.append(line)
    return array


# In[5]:

def get_list(edge_path, user_path):
    edges_initial = read_lines(edge_path)
    edges = []
    for e in edges_initial:
        edge = e.split("\t")
        edges.append[edge]    
    users = read_lines(user_path)
    return edges, users


# In[6]:

def generate_dtproblog_program(edge_path, user_path, program_path):
    edge_list, user_list = get_list(edge_path, user_path)
    text = "% Decisions\n"
    text +="? :: marketed(P) :- person(P).\n\n"
    text +="% Utility attributes\n"
    text +="buys(P) => 5 :- person(P).\n"
    text +="marketed(P) => -2 :- person(P).\n"
    text +="% Probabilistic facts\n"
    text +="0.2 :: buy_from_marketing(_).\n"
    text +="0.3 :: buy_from_trust(_,_).\n"
    text +="% Background knowledge'\n"
    for user in user_list:
        text+= "person("+str(user)+").\n"
        
    text +=" trusts(X,Y) :- trusts_directed(X,Y).\n"
    text +="trusts(X,Y) :- trusts_directed(Y,X).\n"
    
    for edge in edge_list:
        text+= "trusts_directed("+str(edge[0])+","+str(edge[1])+").\n" 
       
    text +="buys(X) :- buys(X,[X]).\n"
    text +="buys(X, _) :-\n"
    text +="    marketed(X),\n"
    text +="    buy_from_marketing(X).\n"
    text +="buys(X, Visited) :-\n"
    text +="    trusts(X,Y),\n"
    text +="    buy_from_trust(X,Y),\n"
    text +="    absent(Y,Visited),\n"
    text +="    buys(Y, [Y|Visited]).\n"
    text +="absent(_,[]).\n"
    text +="absent(X,[Y|Z]):-X \= Y, absent(X,Z).\n"

    
    save_file(text,program_path)


# In[ ]:



