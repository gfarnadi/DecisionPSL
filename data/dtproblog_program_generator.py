
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
        
    text +="0.4:: trusts(X,Y) :- trusts_directed(Y,X).\n"
    text +="0.4:: trusts(X,Y) :- trusts_directed(X,Y).\n"
    text +="0.3:: trusts(X,Y) :- trusts_directed(X,Z), trusts(Z,Y).\n"
    
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

    
#    save_file(text,program_path)


# In[6]:

#for person in ('angelika', 'guy', 'bernd', 'kurt', 'theo',
#               'martijn', 'laura','ingo'):
#    print('?::marketed(%s).'%person)
#     print('utility(buys(%s), 5).'%person)
#     print('utility(marketed(%s), -2).'%person)


# In[7]:


def solve_dtProblog():
    model= '''
    % Decisions
    ?::marketed(angelika).
    ?::marketed(guy).
    ?::marketed(bernd).
    ?::marketed(kurt).
    ?::marketed(theo).
    ?::marketed(martijn).
    ?::marketed(laura).
    ?::marketed(ingo).
 
    utility(buys(angelika), 5).
    utility(marketed(angelika), -2).
    utility(buys(guy), 5).
    utility(marketed(guy), -2).
    utility(buys(bernd), 5).
    utility(marketed(bernd), -2).
    utility(buys(kurt), 5).
    utility(marketed(kurt), -2).
    utility(buys(theo), 5).
    utility(marketed(theo), -2).
    utility(buys(martijn), 5).
    utility(marketed(martijn), -2).
    utility(buys(laura), 5).
    utility(marketed(laura), -2).
    utility(buys(ingo), 5).
    utility(marketed(ingo), -2).

    % Probabilistic facts
    0.2 :: buy_from_marketing(_).
    0.3 :: buy_from_trust(_,_).

    % Background knowledge
    person(bernd).
    person(ingo).
    person(theo).
    person(angelika).
    person(guy).
    person(martijn).
    person(laura).
    person(kurt).

    trusts(X,Y) :- trusts_directed(X,Y).
    trusts(X,Y) :- trusts_directed(Y,X).

    trusts_directed(bernd,ingo).
    trusts_directed(ingo,theo).
    trusts_directed(theo,angelika).
    trusts_directed(bernd,martijn).
    trusts_directed(ingo,martijn).
    trusts_directed(martijn,guy).
    trusts_directed(guy,theo).
    trusts_directed(guy,angelika).
    trusts_directed(laura,ingo).
    trusts_directed(laura,theo).
    trusts_directed(laura,guy).
    trusts_directed(laura,martijn).
    trusts_directed(kurt,bernd).

    buys(X) :-
         marketed(X),
         buy_from_marketing(X).
    buys(X) :-
         trusts(X,Y),
         buy_from_trust(X,Y),
         buys(Y).
'''
    program = PrologString(model)
    decisions, score, statistics = dtproblog(program)

    for name, value in decisions.items():
        print ('%s: %s' % (name, value))


# In[8]:

#%%time
#solve_dtProblog()


# In[9]:

#4.2 / (2**7)


# In[10]:

#for x in (10, 12, 14):
#    t = 0.0328125 * (2**x)
#    print(x, t)


# In[11]:

def solve_dtProblog():
    model= '''
    0.3::rain.
    0.5::wind.
    ?::umbrella.
    ?::raincoat.

    broken_umbrella :- umbrella, rain, wind.
    dry :- rain, raincoat.
    dry :- rain, umbrella, not broken_umbrella.
    dry :- not(rain).

    utility(broken_umbrella, -40).
    utility(raincoat, -20).
    utility(umbrella, -2).
    utility(dry, 60).
'''
    program = PrologString(model)
    decisions, score, statistics = dtproblog(program)

    for name, value in decisions.items():
        print ('%s: %s' % (name, value))
        
#solve_dtProblog()


# In[12]:

from problog.program import PrologString
from problog import get_evaluatable
from problog.program import PrologFile
from problog.formula import LogicFormula
from problog.sdd_formula import SDD
from problog.cnf_formula import CNF

def solve():
    model= '''
    % Decisions
    0.1::marketed(guy).
    0.2::marketed(bernd).
    0.5::marketed(ingo).
    0.3::marketed(theo).

    % Probabilistic facts
    0.2 :: buy_from_marketing(_).
    0.3 :: buy_from_trust(_,_).

    % Background knowledge
    person(bernd).
    person(ingo).
    person(theo).
    person(angelika).
    person(guy).
    person(martijn).
    person(laura).
    person(kurt).

    trusts(X,Y) :- trusts_directed(X,Y).
    trusts(X,Y) :- trusts_directed(Y,X).

    trusts_directed(bernd,ingo).
    trusts_directed(ingo,theo).
    trusts_directed(theo,angelika).
    trusts_directed(bernd,martijn).
    trusts_directed(ingo,martijn).
    trusts_directed(martijn,guy).
    trusts_directed(guy,theo).
    trusts_directed(guy,angelika).
    trusts_directed(laura,ingo).
    trusts_directed(laura,theo).
    trusts_directed(laura,guy).
    trusts_directed(laura,martijn).
    trusts_directed(kurt,bernd).

    buys(X) :-
         marketed(X),
         buy_from_marketing(X).
    buys(X) :-
         trusts(X,Y),
         buy_from_trust(X,Y),
         buys(Y).
         
    query(buys(kurt)).
'''
    
    program = PrologString(model)
    formula = LogicFormula.create_from(program)
    sdd = SDD.create_from(formula)
    return sdd.evaluate()

#%timeit solve()


# In[13]:

model_text = ""
for user in ['u1', 'u2']:
    model_text+='?::marketed(%s).'%user
    model_text+='\n'
    model_text+='utility(buys(%s), 5).'%user
    model_text+='\n'
    model_text+='utility(marketed(%s), -2).'%user
    model_text+='\n'
#print(model_text)
    


# In[14]:

model_text = ""
for edge in [('e1','e2'), ('e2','e4')]:
         model_text+='trusts_directed(%s,%s).'%(edge[0],edge[1])
         model_text+='\n'
#print(model_text)


# In[19]:

def generate_probog_program(edge_path, user_path, program_path):
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
    model_text+="0.4:: trusts(X,Y) :- trusts_directed(Y,X).\n"
    model_text+="0.4:: trusts(X,Y) :- trusts_directed(X,Y).\n"
    model_text+="0.3:: trusts(X,Y) :- trusts_directed(X,Z), trusts(Z,Y).\n"
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


# In[20]:

def generate_program(node_size):
    sample_graph_path = "../sample_graphs2/"
    trust_file = sample_graph_path+"data/trust-"+str(node_size)+".txt"
    user_file = sample_graph_path+"data/user-"+str(node_size)+".txt"
    program_path = sample_graph_path+"model/dtproblog_model-"+str(node_size)+".txt"
    model_text = generate_probog_program(trust_file, user_file, program_path)
    return model_text


# In[21]:

def run_dtproblog(node_size):
    model_text = generate_program(node_size)
    print(model_text)
    program = PrologString(model_text)
    decisions, score, statistics = dtproblog(program)
    print("++++++++ Program for node size = "+ str(node_size)+"++++++++")
    for name, value in decisions.items():
        print ('%s: %s' % (name, value))


# In[22]:

for node_size in [8,10,12,14,20]:
    generate_program(node_size)
    


# In[ ]:



