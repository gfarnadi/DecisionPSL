
# coding: utf-8

# In[1]:

import sqlite3,os,random
import cvxpy
import pickle
import sys
sys.path.append(os.environ["PROBLOG_HOME"])
import problog
conn = sqlite3.connect('viral_marketing_psl.db')
c = conn.cursor()


# In[2]:

def create_db_from_graph(sample_graph_folder, node_size):
    query = 'DROP TABLE IF EXISTS trusts'
    c.execute(query)
    query = 'DROP TABLE IF EXISTS user'
    c.execute(query)
    query = 'DROP TABLE IF EXISTS cost'
    c.execute(query)
    query = 'DROP TABLE IF EXISTS reward'
    c.execute(query)
    query = 'DROP TABLE IF EXISTS sensitive'
    c.execute(query)
    conn.commit()
    query = ''' CREATE TABLE IF NOT EXISTS trusts
            (person1 string, person2 string, truth real)'''
    c.execute(query)
    query = ''' CREATE TABLE IF NOT EXISTS user
            (person string, truth real)'''
    c.execute(query)
    query = ''' CREATE TABLE IF NOT EXISTS cost
            (person string, truth real)'''
    c.execute(query)
    query = ''' CREATE TABLE IF NOT EXISTS reward
            (person string, truth real)'''
    c.execute(query)
    query = ''' CREATE TABLE IF NOT EXISTS sensitive
            (person string, truth real)'''
    c.execute(query)
    network_data = []
    with open(sample_graph_folder+'trust-'+str(node_size)+'.txt') as f:
        for line in f:
            line = line.strip()
            if not line: continue
            line = line.split('\t')
            network_data.append(tuple(line))
    c.executemany('INSERT INTO trusts VALUES (?, ?, 1.0)', network_data)
    user_data = []
    sensitive_data = []
    with open(sample_graph_folder+'user-'+str(node_size)+'.txt') as f:
        for line in f:
            line = line.strip()
            if not line: continue
            line = line.split('\t')
            user_data.append(tuple(line))
    with open(sample_graph_folder+'sensitive-'+str(node_size)+'.txt') as f:
        for line in f:
            line = line.strip()
            if not line: continue
            line = line.split('\t')
            sensitive_data.append(tuple(line))
    c.executemany('INSERT INTO user VALUES (?, 1.0)', user_data)
    c.executemany('INSERT INTO cost VALUES (?, -2.0)', user_data)
    c.executemany('INSERT INTO reward VALUES (?, 5.0)', user_data)
    c.executemany('INSERT INTO sensitive VALUES (?, ?)', sensitive_data)
    make_reachable()
    conn.commit() 


# In[3]:

def make_reachable():
    query = 'DROP TABLE IF EXISTS reachable'
    c.execute(query)
    conn.commit()
    query = ''' CREATE TABLE IF NOT EXISTS reachable
            (person1 string, person2 string, truth real)'''
    c.execute(query)
    query = 'DROP TABLE IF EXISTS reachableTemp'
    c.execute(query)
    conn.commit()
    query = '''CREATE TABLE reachableTemp AS WITH temp AS
        (SELECT user.person as person1, reward.person as person2
        FROM user 
        CROSS JOIN reward 
        )SELECT * FROM temp'''
    c.execute(query)
    query = '''INSERT INTO reachable (person1, person2) SELECT person1, person2 FROM reachableTemp'''
    c.execute(query)
    conn.commit() 


# In[4]:

def make_objective(buy, reward):
    objective_function = 0
    for r in reward:
        uid = r[0]
        value = float(r[1])
        objective_function += buy[uid]* value
    return objective_function


# In[5]:

def convert_constraint1(marketed, buy, buy_from_marketing, delta):
     #TODO: add buy from marketing
    #marketed(u) & buy_from_marketing(u) ->buy(u)
    #~marketed(u) & buy_from_marketing(u) ->~buy(u)
    constraint = []
    obj_function = 0.0
    for uid,value in buy.items():
        obj_function+=cvxpy.pos(cvxpy.pos(marketed[uid]+buy_from_marketing[uid]-1.0)-buy[uid])
        obj_function+=cvxpy.pos(cvxpy.pos((1-marketed[uid])+buy_from_marketing[uid]-1.0)-(1-buy[uid]))
        constraint.append(delta >= cvxpy.pos(cvxpy.pos(marketed[uid]+buy_from_marketing[uid]-1.0)-buy[uid]))
        constraint.append(delta >= cvxpy.pos(((1-marketed[uid])+buy_from_marketing[uid]-1.0)-(1-buy[uid])))
    return constraint,obj_function


# In[6]:

def convert_constraint2(reachable, buy, buy_from_trust, delta):
     #TODO: add buy from trust
    #reachable(u,v) & buy(u) & buy_from_trust(u,v)-> buy(v)
    #reachable(u,v) & ~buy(u) & buy_from_trust(u,v)-> ~buy(v)
    constraint = []
    obj_function = 0.0
    for edge,value in reachable.items():
        u = edge[0]
        v = edge[1]
        #TODO: fix the value of reachable table to be 1 instead of none
        if (value==True):
            value_num = 1.0
        else:
            value_num = 0.0 
        if (buy_from_trust[edge]==True):
            buy_from_trust_value = 1.0
        else:
            buy_from_trust_value = 0.0
        obj_function+=cvxpy.pos(cvxpy.pos(cvxpy.pos(float(value_num)+buy[u]-1.0)+buy_from_trust_value -1) - buy[v])
        obj_function+=cvxpy.pos(cvxpy.pos(cvxpy.pos(float(value_num)+(1-buy[u])-1.0)+buy_from_trust_value -1) - (1-buy[v]))
        constraint.append(delta >= cvxpy.pos(cvxpy.pos(cvxpy.pos(float(value_num)+buy[u]-1.0)+buy_from_trust_value -1) - buy[v]))
        constraint.append(delta >= cvxpy.pos(cvxpy.pos(cvxpy.pos(float(value_num)+(1-buy[u])-1.0)+buy_from_trust_value -1) - (1-buy[v])))
    return constraint, obj_function


# In[7]:

def convert_constraint3(marketed, cost, budget):
     #TODO: add buy
    #∑ cost(u) * marketed(u) ≤ B
    sum_cost = 0.0
    for c in cost:
        uid = c[0]
        value = float(c[1]) 
        sum_cost += value * marketed[uid]
    return [sum_cost <= budget], sum_cost


# In[8]:

def add_prior(buy):
    #~buy(u)
    sum = 0.0
    for key, value in buy.items(): 
        sum+= (value)
    return sum


# In[9]:

def convert_fairness_constraint1(sensitive, buy, delta):
    # buy(u) & sensitive(u)
    # buy(u) & ~sensitive(u)
    constraint = []
    sum_protected = 0.0
    sum_unprotected = 0.0
    size_protected = 0.0
    size_unprotected = 0.0
    for s in sensitive:
        value = float(s[1])
        if (value==1):
            size_protected +=1.0
        else:
            size_unprotected +=1.0    
    for s in sensitive:
        uid = s[0]
        value = float(s[1])
        sum_protected += buy[uid] * value #* (1/float(size_protected))
        sum_unprotected += buy[uid] * (1 - value) #* (1/float(size_unprotected))
    protected = sum_protected - sum_unprotected
    unprotected = sum_unprotected -  sum_protected
    constraint+=[ protected<=delta , unprotected<=delta]
    return constraint 


# In[10]:

def convert_fairness_constraint2(sensitive, reachable, marketed, delta):
    # marketed(u) & reachable (u,v) & sensitive (v)
    # marketed(u) & reachable (u,v) & ~sensitive (v)
    sum_protected = 0.0
    sum_unprotected = 0.0
    constraint = []
    sensitive_dict = dict()
    size_protected = 0.0
    size_unprotected = 0.0
    for s in sensitive:
        uid = s[0]
        value = float(s[1])
        if (value ==1):
            size_protected += 1.0
        else:
            size_unprotected += 1.0
        sensitive_dict[uid] = value
    for edge,value in reachable.items():
        u = edge[0]
        v = edge[1]
        if float(value) > 0.5:
            if sensitive_dict[v]==1.0:
                sum_protected+= marketed[u] #* (1/float(size_protected))
                #sum_protected+= cvxpy.pos(marketed[u]+float(value)-1)
            else:
                sum_unprotected += marketed[u] #* (1/float(size_unprotected))
                #sum_unprotected += cvxpy.pos(marketed[u]+float(value)-1)
    protected = sum_protected - sum_unprotected
    unprotected = sum_unprotected - sum_protected
    constraint+=[ protected<=delta , unprotected<=delta]
    return constraint
    


# In[11]:

def get_query_result(query):
    result = []
    c.execute(query)
    rows = c.fetchall()
    for row in rows:
        result.append(row)
    return result


# In[12]:

def read_samples(sample_graph_folder, node_size, sample_size):
    pickle_path=sample_graph_folder+"generated_sample_dict-"+str(node_size)+"("+str(sample_size)+")"+".pickle"
    samples= {}   
    with open(pickle_path, 'rb') as handle:
        samples = pickle.load(handle)
    return samples


# In[13]:

def extract_edge(key, string_code):
    edge_str = str(key).replace(string_code, '').replace(')','')
    edges = edge_str.split(',')
    return int(edges[0]),int(edges[1])


# In[14]:

def extract_user_marketing(key):
    user = str(key).replace('buy_from_marketing(', '').replace(')','')
    return int(user)


# In[ ]:

def run_optimization(sample_graph_folder, sample_size, node_size, budget, delta):
    create_db_from_graph(sample_graph_folder+'data/', node_size)
    samples = read_samples(sample_graph_folder+'sample/', node_size, sample_size)

    query_cost = '''
    SELECT * from cost
    '''
    query_reward = '''
    SELECT * from reward
    '''
    query_sensitive = '''
    SELECT * from sensitive
    '''
    query_users = '''
    SELECT * from user
    '''
    query_reachable = '''
    SELECT * from reachable
    '''
    query_trusts = '''
    SELECT * from trusts
    '''
    print('\nUsers\n%s'%('='*10))
    users = get_query_result(query_users)
    print(users)
    print('\nCost\n%s'%('='*10))
    cost = get_query_result(query_cost)
    print(cost)
    print('\nReward\n%s'%('='*10))
    reward = get_query_result(query_reward)
    print(reward)
    print('\nSensitive\n%s'%('='*10))
    sensitive = get_query_result(query_sensitive)
    print(sensitive)
    print('\nTrusts\n%s'%('='*10))
    trusts = get_query_result(query_trusts)
    print(trusts)
    print('\nReachable\n%s'%('='*10))
    edges = get_query_result(query_reachable)
    print(edges)
    
    var_dict = dict()
    
    
    # make decision variable for marketed
    marketed = dict()
    for user in users:
        uid = user[0]
        variable = cvxpy.Variable()
        marketed[uid] = variable
        var_dict[('marketed', uid)] = variable
    
    buys = []
    reachables = []
    buy_from_trusts= []
    buy_from_marketings = []
    for i in range(sample_size):
        # make random variable for buy
        buy = dict()
        for user in users:
            uid = user[0]
            variable = cvxpy.Variable()
            buy[uid] = variable
            var_dict[('buy', i, uid)] = variable
        buys.append(buy)
        #use samples for reachable
        reachable = dict()
        buy_from_trust = dict()
        buy_from_marketing = dict()
        for key in samples.keys():
            if str(key).startswith('trusts('):
                e1,e2 = extract_edge(key, string_code = 'trusts(')
                edge = (e1,e2)
                reachable[edge] = samples[key][i]
            elif str(key).startswith('buy_from_trust('):
                e1,e2 = extract_edge(key, string_code = 'buy_from_trust(' )
                edge = (e1,e2)
                buy_from_trust[edge] = samples[key][i]
                
            elif str(key).startswith('buy_from_marketing('):
                marketed_user = extract_user_marketing(key)
                buy_from_marketing[marketed_user] = samples[key][i]
            else:
                pass
        reachables.append(reachable)
        buy_from_trusts.append(buy_from_trust)
        buy_from_marketings.append(buy_from_marketing)
    
    objective_function = 0.0
    # make the optimization problem 
    for i in range (sample_size):
        objective_function += make_objective(buys[i], reward)
    
    objective_function = objective_function* (1/float(sample_size))
    #print(objective_function)
    # make the constraints
    constraints = []
    
    function_constraint_3, obj_3 = convert_constraint3(marketed, cost, budget)
    objective_function+=obj_3
    #constraints+= function_constraint_3   
    
    for i in range (sample_size):
        function_constraint_1,obj_1 = convert_constraint1(marketed, buys[i], buy_from_marketings[i], delta)
        #constraints+=function_constraint_1
        objective_function+=(1-obj_1)* (1/2*float(sample_size))
        function_constraint_2, obj_2 = convert_constraint2(reachables[i], buys[i], buy_from_trusts[i], delta)
        #constraints+=function_constraint_2
        objective_function+=(1-obj_2)* (1/2*float(sample_size))
        objective_function+= add_prior(buys[i])* (1/float(sample_size))
        
        ########################################
        # make the fairness constraints
        fairness_constraint1 = convert_fairness_constraint1(sensitive, buys[i], delta)
        #constraints+=fairness_constraint1
        fairness_constraint2 = convert_fairness_constraint2(sensitive, reachable, marketed, delta)
        #constraints+=fairness_constraint2
       
    # make the range constraints [0,1]
    for var, value in var_dict.items():
        constraints += [0 <= value, value <= 1]
    
    #print('\nObjective_function\n%s'%('='*10))
    #print(objective_function)
    
    #print('\nConstraints\n%s'%('='*10))
    #print(constraints)
    

    # Solve the problem
    #print('\nobjective_function\n%s'%('='*10))
    #print(objective_function)
    #print('\nConstraints\n%s'%('='*10))
    #print(constraints)
    objective = cvxpy.Maximize(objective_function)
    problem = cvxpy.Problem(objective, constraints)
    final_result = problem.solve()
    
    
    # Process the results
    marketed_result = dict()
    for user in users:
        uid = user[0]
        vid = ('marketed', uid)
        marketed_result[uid] = var_dict[vid].value
        
    
    print('\nMarketed results\n%s'%('='*10))
    print(marketed_result)
    
    buyer_result = dict()
    for user in users:
        buyer_value = 0.0
        for i in range (sample_size):
            uid = user[0]
            vid = ('buy', i, uid)
            buyer_value+=var_dict[vid].value
        buyer_result[uid] = buyer_value* (1/float(sample_size))
    
    print('\nBuyer results\n%s'%('='*10))
    print(buyer_result)
    
    print('\nStatus of optimization\n%s'%('='*10))
    print(problem.status)
    
    print('\nOptimal value\n%s'%('='*10))
    print(problem.value)


# In[ ]:

sample_graph_folder = '../sample_graphs2/'
run_optimization(sample_graph_folder, sample_size = 1000, node_size = 8, budget = 4, delta = 0.001)


# In[ ]:




# In[ ]:



