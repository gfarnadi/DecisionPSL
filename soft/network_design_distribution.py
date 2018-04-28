
# coding: utf-8

# In[2]:

import sqlite3,os,random
conn = sqlite3.connect('network_design.db')
c = conn.cursor()


# In[3]:

def test_query(query):
    c.execute(query)
    rows = c.fetchall()
    for row in rows:
        print(row)


# In[4]:

def ground_distribution1():
    # ~presents(a,b)
    # ~edge(a,b)->~presents(a,b)
    
    print('\nEdges\n%s'%('='*10))
    
    query = '''
    SELECT * from edges
    '''
    test_query(query)
    
    #Ground rule 1:
    
    print('\nPresents\n%s'%('='*10))
    query = 'DROP TABLE IF EXISTS presents'
    c.execute(query)
    conn.commit()
    query = ''' CREATE TABLE IF NOT EXISTS presents
            (node1 string, node2 string, truth real)'''
    c.execute(query)
    
    
    query = '''INSERT INTO presents (node1, node2) SELECT node1, node2 FROM edges 
    '''
    c.execute(query)
    
    query = '''
    SELECT * from presents
    '''
    test_query(query)
    
    print('\nRule1\n%s'%('='*10))
    query = 'DROP TABLE IF EXISTS rule1'
    c.execute(query)
    conn.commit()
    
    query = '''
    CREATE TABLE rule1
    AS
    WITH temp1 AS
    (
    SELECT presents.node1, presents.node2, 
    edges.truth as t1, presents.truth as t2
    FROM 
    presents
    INNER JOIN 
    edges
    ON presents.node1 = edges.node1 AND presents.node2 = edges.node2
    )
    SELECT * from temp1
    '''
    
    test_query(query)
    
    query = '''
    SELECT * from rule1
    '''
    test_query(query)
    
    print('\nRule1-info\n%s'%('='*10))
    
    query = '''
    PRAGMA table_info(rule1);
    '''
    test_query(query)
     
ground_distribution1()


# In[5]:

def ground_distribution2():    
    
     #Ground rule 2:
    print('\nRule2\n%s'%('='*10))
    query = 'DROP TABLE IF EXISTS rule2'
    c.execute(query)
    conn.commit()

    query = '''
    CREATE TABLE rule2
    AS
    WITH temp1 AS
    (
    SELECT presents.node1, presents.node2, 
    edges.truth as t1, presents.truth as t2
    FROM 
    presents
    INNER JOIN 
    edges
    ON presents.node1 = edges.node1 AND presents.node2 = edges.node2
    )
    SELECT * from temp1
    '''
    
    test_query(query)
    
    query = '''
    SELECT * from rule2
    '''
    test_query(query)
    
    print('\nRule2-info\n%s'%('='*10))
    
    query = '''
    PRAGMA table_info(rule2);
    '''
    test_query(query)
    
ground_distribution2()


# In[27]:

def ground_distribution3():     
    # edge(s,t1) & edge(t1,t2) & ~presents(t1,t2) -> ~presents(s,t1)
    # edge(s,t1) & edge(s,t2) & ~present(s,t2) -> ~presents(s,t1)
    #Ground rule 3:
    
    print('\nRule3\n%s'%('='*10))
    query = 'DROP TABLE IF EXISTS temprule13'
    c.execute(query)
    conn.commit()
    
    query = '''
    CREATE TABLE temprule13
    AS
    WITH temp1 AS
    (
    SELECT edges.node1 as node1, edges.node2 as node2, presents.node2 as node3, 
    edges.truth as t1, presents.truth as t2
    FROM 
    presents
    INNER JOIN 
    edges
    ON presents.node1 = edges.node2 
    )
    SELECT * from temp1
    '''
    
    test_query(query)
    
    
    print('\nTemprule13-info\n%s'%('='*10))
    
    query = '''
    PRAGMA table_info(temprule13);
    '''
    test_query(query)
    
    
    query = 'DROP TABLE IF EXISTS temprule23'
    c.execute(query)
    conn.commit()
    
    query = '''
    CREATE TABLE temprule23
    AS
    WITH temp1 AS
    (
    SELECT edges.node1 as node1, edges.node2 as node2, presents.node2 as node3, 
    edges.truth as t1, presents.truth as t2
    FROM 
    presents
    INNER JOIN 
    edges
    ON presents.node2 = edges.node1 
    )
    SELECT * from temp1
    '''
    
    test_query(query)
    
    print('\nTemprule23-info\n%s'%('='*10))
    
    query = '''
    PRAGMA table_info(temprule23);
    '''
    test_query(query)
     
    query = 'DROP TABLE IF EXISTS rule3'
    c.execute(query)
    conn.commit()
    
    query = '''
    CREATE TABLE rule3
    AS
    WITH temp1 AS
    (
    SELECT temprule13.node1 as node1 as temprule13.node2 as node2, temprule13.node3 as node3, 
    temprule13.t1 as t1, temprule23.t1 as t2, temprule13.t2 as t3, temprule23.t2 as t4
    FROM 
    temprule13
    INNER JOIN 
    temprule23
    ON temprule13.node1 = temprule23.node3 AND 
    temprule13.node2 = temprule23.node1 AND 
    temprule13.node3 = temprule23.node2
    )
    SELECT * from temp1
    '''
    test_query(query)
    
    query = '''
    SELECT * from rule3
    '''
    test_query(query)
    
    print('\nRule3-info\n%s'%('='*10))
    
    query = '''
    PRAGMA table_info(rule3);
    '''
    test_query(query)
    
    conn.close() 
    
ground_distribution3()


# In[ ]:




# In[ ]:



