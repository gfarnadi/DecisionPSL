
# coding: utf-8

# In[1]:

import networkx, os, random


# In[2]:

def save_file(path, content):
    try:
        os.remove(path)
    except OSError:
        pass
    with open(path, 'a') as out:
        out.write(content+'\n')


# In[3]:

n = 10
m = 6
p = 0.2
graph = networkx.powerlaw_cluster_graph(n, m, p, seed=None)
#for edge in graph.edges():
#    print(edge)
#for node in list(graph):
#    print(node)


# In[4]:

def create_synthetic_viral_marketing(n,m,p):
    graph = networkx.powerlaw_cluster_graph(n, m, p, seed=None)
    return graph

def make_db_from_graph(graph, edge_file, node_file, sensitive_file):
    edge_text= ''
    node_text = ''
    sensitive_text = ''
    for edge in graph.edges():
        edge_txt = str(edge).replace("(","").replace(")","").replace(",", "\t") 
        edge_text+=edge_txt+'\n'
    for node in list(graph):
        node_text+=str(node)+'\n'
        sensivity = random.choice('01')
        sensitive_text+=str(node)+'\t'+sensivity+'\n'
    save_file(edge_file, edge_text)    
    save_file(node_file, node_text)
    save_file(sensitive_file, sensitive_text) 

def making_synthetic_viral_marketing_data(n, m, p, edge_file, node_file, sensitive_file):
    graph = create_synthetic_viral_marketing(n,m,p)
    make_db_from_graph(graph, edge_file, node_file, sensitive_file)
    


# In[5]:

n = 10
m = 6
p = 0.3
edge_file = "./trust.txt"
node_file = "./user.txt"
sensitive_file = "./sensitive.txt"
#generate_synthetic_viral_marketing(n,m,p, edge_file, node_file, sensitive_file)


# In[6]:

def making_epinion_data(epinion_file, edge_file, node_file, sensitive_file):
    graph=networkx.read_edgelist(epinion_file, nodetype=str)
    make_db_from_graph(graph, edge_file, node_file, sensitive_file)


# In[7]:

def get_epinion_info(epinion_file):
    graph=networkx.read_edgelist(epinion_file, nodetype=str)
    print(networkx.density(graph))
    average = networkx.degree(graph)
    mean = 0.0
    n=0.0
    print(len(average.items()))
    print(len(graph.edges()))
    for key,value in average.items():
        n+=1.0
        mean+=value
    print(mean/n)


# In[8]:

epinion_file = "./soc-Epinions1.txt"
get_epinion_info(epinion_file)


# In[13]:

n = 20
m = 6
p = 0.3
edge_file = "../sample_graphs2/data/trust-20.txt"
node_file = "../sample_graphs2/data/user-20.txt"
sensitive_file = "../sample_graphs2/data/sensitive-20.txt"
making_synthetic_viral_marketing_data(n, m, p, edge_file, node_file, sensitive_file)


# In[ ]:



