
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

def ground_distribution():
    # ~presents(a,b)
    # ~edge(a,b)->~presents(a,b)
    # edge(s,t1) & edge(t1,t2) & ~presents(t1,t2) -> ~presents(s,t1)
    # edge(s,t1) & edge(s,t2) & ~present(s,t2) -> ~presents(s,t1)
    
    
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
    conn.close()

ground_distribution()

