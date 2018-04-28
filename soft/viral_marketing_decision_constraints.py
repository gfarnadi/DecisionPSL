
# coding: utf-8

# In[1]:

import sqlite3,os,random
conn = sqlite3.connect('viral_marketing.db')
c = conn.cursor()


# In[2]:

def test_query(query):
    c.execute(query)
    rows = c.fetchall()
    for row in rows:
        print(row)
        


# In[3]:

def ground_constraints():
    #marketed(u) & user(u) ->buy(u)
    #reachable(u,v) & buy(u) -> buy(v)
    #∑ cost(u) * marketed(u) ≤ B
    print('\nUser\n%s'%('='*10))
    
    query = '''
    SELECT * from user
    '''
    test_query(query)
    
    #ground constraint 1
    
    print('\nConstraint1\n%s'%('='*10))
    query = 'DROP TABLE IF EXISTS constraint1'
    c.execute(query)
    conn.commit()
    
    query = ''' CREATE TABLE IF NOT EXISTS constraint1
            (person string, t1 real, t2 real, t3 real)'''
    c.execute(query)
    
    
    query = '''INSERT INTO constraint1 (person, t2) SELECT person, truth FROM user 
    '''
    c.execute(query)
    
    query = '''
    SELECT * from constraint1
    '''
    test_query(query)
    
    print('\nConstraint1-info\n%s'%('='*10))
    
    query = '''
    PRAGMA table_info(constraint1);
    '''
    test_query(query)
    
    
    print('\nConstraint2\n%s'%('='*10))
    query = 'DROP TABLE IF EXISTS constraint2'
    c.execute(query)
    conn.commit()
    
    query = ''' CREATE TABLE IF NOT EXISTS constraint2
            (person1 string, person2 string, t1 real, t2 real, t3 real)'''
    c.execute(query)
    
    
    query = '''INSERT INTO constraint2 (person1, person2, t1) SELECT person1, person2, truth FROM reachable
    '''
    c.execute(query)
    
    query = '''
    SELECT * from constraint2
    '''
    test_query(query)
    
    print('\nConstraint2-info\n%s'%('='*10))
    
    query = '''
    PRAGMA table_info(constraint2);
    '''
    test_query(query)
    
    
    print('\nConstraint3\n%s'%('='*10))
    query = 'DROP TABLE IF EXISTS constraint3'
    c.execute(query)
    conn.commit()
    
    query = ''' CREATE TABLE IF NOT EXISTS constraint3
            (person string, truth real, cost real)'''
    c.execute(query)
    
    query = '''INSERT INTO constraint3 (person, cost) SELECT person, truth FROM cost
    '''
    c.execute(query)
    
    query = '''
    SELECT * from constraint3
    '''
    test_query(query)
    
    print('\nConstraint3-info\n%s'%('='*10))
    
    query = '''
    PRAGMA table_info(constraint2);
    '''
    test_query(query)
    conn.close()
    
    
ground_constraints()    
    
    


# In[ ]:



