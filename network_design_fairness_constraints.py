
# coding: utf-8

# In[1]:

import sqlite3,os,random
conn = sqlite3.connect('network_design.db')
c = conn.cursor()


# In[2]:

def test_query(query):
    c.execute(query)
    rows = c.fetchall()
    for row in rows:
        print(row)


# In[3]:

def ground_fairness_constraints():
    # path(s, c) & large(c) & large(s)
    
     #ground constraint 1
    
    print('\nFairness-Constraint1\n%s'%('='*10))
    
    query = 'DROP TABLE IF EXISTS fairnesstemp1'
    c.execute(query)
    conn.commit()
    
    query = '''
    CREATE TABLE fairnesstemp1
    AS
    WITH temp1 AS
    (
    SELECT path.node1, path.node2, 
    path.truth as t1, large.truth as t2
    FROM 
    path
    INNER JOIN 
    large
    ON path.node1 = large.node 
    )
    SELECT * from temp1
    '''
    
    test_query(query)
    
    
    query = 'DROP TABLE IF EXISTS fairness1'
    c.execute(query)
    conn.commit()
    
    query = '''
    CREATE TABLE fairness1
    AS
    WITH temp1 AS
    (
    SELECT fairnesstemp1.node1, fairnesstemp1.node2, 
    fairnesstemp1.t1 as t1, fairnesstemp1.t2 as t2, large.truth as t3
    FROM 
    fairnesstemp1
    INNER JOIN 
    large
    ON fairnesstemp1.node2 = large.node
    )
    SELECT * from temp1
    '''
    
    test_query(query)
    
    
    query = '''
    SELECT * from fairness1
    '''
    test_query(query)
    
    print('\nFairness1-info\n%s'%('='*10))
    
    query = '''
    PRAGMA table_info(fairness1);
    '''
    test_query(query)
    conn.close()
    
    
ground_fairness_constraints()

