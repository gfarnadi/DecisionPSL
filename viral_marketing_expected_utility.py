
# coding: utf-8

# In[1]:

import sqlite3,os,random
import cvxpy
from viral_marketing_sampling import sampling
conn = sqlite3.connect('viral_marketing.db')
c = conn.cursor()


# In[2]:

def make_synthatic_sample(edges, sample_size):
    samples = []
    reachable_size = len(edges)
    for i in range(sample_size):
        sample = []
        for j in range(reachable_size):
            sample.append(random.random())
        samples.append(sample)
    return samples

#samples = make_synthatic_sample(node_size = 5, sample_size=10)
#samples


# In[3]:

def get_samples(edges, sample_size):
    rejection_size = 10
    w1 = 1
    w2 = 1
    rv_list = []
    for e in edges:
         rv_list.append((e[0],e[1]))
    samples = sampling(w1,w2, rv_list , sample_size, rejection_size)
    return samples


# In[4]:

def get_query_result(query):
    result = []
    c.execute(query)
    rows = c.fetchall()
    for row in rows:
        result.append(row)
    return result


# In[5]:

def make_objective(buy, reward):
    objective_function = 0
    for r in reward:
        uid = r[0]
        value = float(r[1])
        objective_function += buy[uid]* value
    return objective_function


# In[6]:

def convert_constraint1(marketed, buy):
    #marketed(u) & user(u) ->buy(u)
    constraint = []
    obj_function = 0.0
    for uid,value in buy.items():
        obj_function+=cvxpy.pos(marketed[uid]-buy[uid])
        constraint.append(cvxpy.pos(marketed[uid]-buy[uid]))
        #constraint.append(marketed[uid]-buy[uid]<=0)
    return constraint,obj_function


# In[7]:

def convert_constraint2(reachable, buy):
    #reachable(u,v) & buy(u) -> buy(v)
    constraint = []
    obj_function = 0.0
    for edge,value in reachable.items():
        u = edge[0]
        v = edge[1]
        obj_function+=cvxpy.pos(cvxpy.pos(float(value)+buy[u]-1.0) - buy[u])
        constraint.append(cvxpy.pos(cvxpy.pos(float(value)+buy[u]-1.0) - buy[u]))
        #constraint.append(float(value)+buy[u]-buy[v]<=1)
    return constraint, obj_function


# In[8]:

def convert_constraint3(marketed, cost, budget):
    #∑ cost(u) * marketed(u) ≤ B
    sum_cost = 0
    for c in cost:
        uid = c[0]
        value = float(c[1])
        sum_cost += value * marketed[uid]
    return [ sum_cost <= budget ]
    


# In[9]:

def convert_fairness_constraint1(sensitive, buy, delta):
    # buy(u) & sensitive(u)
    # buy(u) & ~sensitive(u)
    
    constraint = []
    sum_protected = 0
    sum_unprotected = 0
    for s in sensitive:
        uid = s[0]
        value = float(s[1])
        sum_protected += buy[uid] * value
        sum_unprotected += buy[uid] * (1 - value)
    protected = sum_protected - sum_unprotected
    unprotected = sum_unprotected - sum_protected
    constraint+=[ protected<=delta , unprotected<=delta]
    return constraint 
    
    


# In[10]:

def convert_fairness_constraint2(sensitive, reachable, marketed, delta):
    # marketed(u) & reachable (u,v) & sensitive (v)
    # marketed(u) & reachable (u,v) & ~sensitive (v)
    sum_protected = 0
    sum_unprotected = 0
    constraint = []
    sensitive_dict = dict()
    for s in sensitive:
        uid = s[0]
        value = float(s[1])
        sensitive_dict[uid] = value
    for edge,value in reachable.items():
        u = edge[0]
        v = edge[1]
        if sensitive_dict[v]==1.0:
            sum_protected+= cvxpy.pos(marketed[u]+float(value)-1)
            sum_unprotected += 0
        else:
            sum_protected+= 0
            sum_unprotected += cvxpy.pos(marketed[u]+float(value)-1)
    protected = sum_protected - sum_unprotected
    unprotected = sum_unprotected - sum_protected
    constraint+=[ protected<=delta , unprotected<=delta]
    return constraint
    


# In[11]:

def make_optimization(sample_size, budget, delta):
    #marketed(u) & user(u) ->buy(u)
    #reachable(u,v) & buy(u) -> buy(v)
    #∑ cost(u) * marketed(u) ≤ B
    
    
    query1 = '''
    SELECT * from constraint1
    '''
    query2 = '''
    SELECT * from constraint2
    '''
    query3 = '''
    SELECT * from constraint3
    '''
    query_users = '''
    SELECT * from user
    '''
    query_reachable = '''
    SELECT * from reachable
    '''
    query_cost = '''
    SELECT * from cost
    '''
    query_reward = '''
    SELECT * from reward
    '''
    
    query_sensitive = '''
    SELECT * from sensitive
    '''
    
    print('\nConstraint1\n%s'%('='*10))
    constraint1 = get_query_result(query1)
    print(constraint1)
    print('\nConstraint2\n%s'%('='*10))
    constraint2 = get_query_result(query2)
    print(constraint2)
    print('\nConstraint3\n%s'%('='*10))
    constraint3 = get_query_result(query3)
    print(constraint3)
    print('\nUsers\n%s'%('='*10))
    users = get_query_result(query_users)
    print(users)
    print('\nReachable\n%s'%('='*10))
    edges = get_query_result(query_reachable)
    print(edges)
    print('\nCost\n%s'%('='*10))
    cost = get_query_result(query_cost)
    print(cost)
    print('\nReward\n%s'%('='*10))
    reward = get_query_result(query_reward)
    print(reward)
    print('\nSensitive\n%s'%('='*10))
    sensitive = get_query_result(query_sensitive)
    print(sensitive)
    
    var_dict = dict()
    
    #samples = make_synthatic_sample(edges, sample_size)
    samples = get_samples(edges, sample_size)
    
    # make decision variable for marketed
    marketed = dict()
    for user in users:
        uid = user[0]
        variable = cvxpy.Variable()
        marketed[uid] = variable
        var_dict[('marketed', uid)] = variable
    
    buys = []
    reachables = []
    
    
    for i in range(sample_size):
        sample = samples[i]
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
        x = 0
        for item in edges:
            edge = tuple((item[0],item[1]))
            reachable[edge] = sample[x]
            x+=1
        reachables.append(reachable)
     
    # make the optimization problem 
    for i in range (sample_size):
        objective_function += make_objective(buys[i], reward)
    
    # make the constraints
    constraints = []
    function_constraint_3 = convert_constraint3(marketed, cost, budget)
    constraints+= function_constraint_3
    for i in range (sample_size):
        function_constraint_1,obj_1 = convert_constraint1(marketed, buys[i])
        constraints+=function_constraint_1
        #objective_function+=1-obj_1
        function_constraint_2, obj_2 = convert_constraint2(reachables[i], buys[i])
        constraints+=function_constraint_2
        #objective_function+=1-obj_2
    # make the fairness constraints
    for i in range (sample_size):
        fairness_constraint1 = convert_fairness_constraint1(sensitive, buys[i], delta)
        constraints+=fairness_constraint1
        #fairness_constraint2 = convert_fairness_constraint2(sensitive, reachable, marketed, delta)
        #constraints+=fairness_constraint2
        
    # make the range constraints [0,1]
    for var, value in var_dict.items():
        constraints += [0 <= value, value <= 1]
    
    
    
    #print('\nObjective_function\n%s'%('='*10))
    #print(objective_function)
    
    #print('\nConstraints\n%s'%('='*10))
    #print(constraints)
    

    # Solve the problem
    objective = cvxpy.Maximize(objective_function)
    problem = cvxpy.Problem(objective, constraints)
    final_result = problem.solve()
    
    
    # Process the results
    result = dict()
    for user in users:
        uid = user[0]
        vid = ('marketed', uid)
        result[uid] = var_dict[vid].value
    
    
    print('\nMarketed results\n%s'%('='*10))
    print(result)
    
    print('\nStatus of optimization\n%s'%('='*10))
    print(problem.status)
    
    print('\nOptimal value\n%s'%('='*10))
    print(problem.value)
    
    
make_optimization(sample_size=10, budget = 2, delta = 0.001)




# In[ ]:



