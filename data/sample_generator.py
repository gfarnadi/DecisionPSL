
# coding: utf-8

# In[1]:

import os
import sys
sys.path.append(os.environ["PROBLOG_HOME"])
import problog
from problog.tasks import sample
from problog.program import PrologString


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

def get_samples(modeltext, sample_size):
    model = PrologString(modeltext)
    result = sample.sample(model, n=sample_size, format='dict')
    return result   


# In[6]:

def test_model(modeltext):
    result = get_samples(modeltext, sample_size=3)
    for i in result:
        print(i)


# In[7]:

def generate_model_text(sample_graph_path,node_size):
    model_text = ""
    model = """
1.0:: trusts_undirected(X,Y) :- trusts_directed(X,Y).
1.0:: trusts_undirected(X,Y) :- trusts_directed(Y,X).
0.4:: trusts(X,Y) :- trusts_undirected(X,Y).
0.3:: trusts(X,Y) :- trusts_undirected(X,Z), trusts(Z,Y).
0.2:: buy_from_marketing(_).
0.3:: buy_from_trust(_,_).
    """
    trust_file = sample_graph_path+"data/trust-"+str(node_size)+".txt"
    user_file = sample_graph_path+"data/user-"+str(node_size)+".txt"
    trusts, users = get_list(trust_file,user_file)
    for trust in trusts:
        model_text+="trusts_directed("+trust[0]+","+trust[1]+")."+'\n'
    model_text+=model+'\n'
    query_text = ""
    for user1 in users:
        for user2 in users:
            if user1!= user2:
                query_text+="query(trusts("+user1+","+user2+"))."+'\n'
                query_text+="query(buy_from_trust("+user1+","+user2+"))."+'\n'
    for user in users:
        query_text+="query(buy_from_marketing("+user+"))."+'\n'
    model_text+= query_text+"\n" 
    model_path = sample_graph_path+"model/"+"problog_model-"+str(node_size)+".txt"
    save_file(model_path, model_text)
    return model_text


# In[8]:

import pickle
def save_to_pickle(dict_to_save, path_to_save):
    with open(path_to_save, 'wb') as handle:
        pickle.dump(dict_to_save, handle, protocol=pickle.HIGHEST_PROTOCOL)
        
def read_pickle(pickle_path):
    b= {}
    with open(pickle_path, 'rb') as handle:
        b = pickle.load(handle)
    return b


# In[9]:

def make_dictionary (sample_result):
    dict_to_save = {}
    for sample_dict in sample_result:
        for item in sample_dict.keys():
            if item in dict_to_save.keys():
                samples_of_item = dict_to_save[item]
                samples_of_item.append(sample_dict[item])
                dict_to_save[item] = samples_of_item
            else:
                dict_to_save[item] = [sample_dict[item]]
    return dict_to_save


# In[ ]:

def save_samples(sample_graph_path, node_size, sample_size):
    model_text = generate_model_text(sample_graph_path,node_size)
    result = get_samples(model_text, sample_size)
    path_to_save = sample_graph_path+"sample/generated_sample_dict-"+str(node_size)+"("+str(sample_size)+")"+".pickle"
    dict_to_save = make_dictionary (result)
    save_to_pickle(dict_to_save, path_to_save)


# In[ ]:

sample_graph_path = "../sample_graphs2/"
for node_size in [8,10,12,14,20]:
    save_samples(sample_graph_path, node_size, sample_size = 1000)


# In[ ]:

#sample_graph_path = "../sample_graphs2/"
#pickle_path = sample_graph_path+"sample/generated_sample_dict-"+str(8)+"("+str(1000)+")"+".pickle"
#test_dict = read_pickle(pickle_path)


# In[ ]:

#test_dict


# In[ ]:



