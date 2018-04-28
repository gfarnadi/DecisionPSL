
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

def ground_fairness_constraints():
    # buy(u) & sensitive(u)
    # buy(u) & ~sensitive(u)
    
    # marketed(u) & reachable (u,v) & sensitive (v)
    # marketed(u) & reachable (u,v) & ~sensitive (v)
    
    #ground constraint 1
    
    print('\nFairness-Constraint1\n%s'%('='*10))
    query = 'DROP TABLE IF EXISTS fairness1'
    c.execute(query)
    conn.commit()
    
    query = ''' CREATE TABLE IF NOT EXISTS fairness1
            (person string, t1 real, t2 real)'''
    c.execute(query)
    
    
    query = '''INSERT INTO fairness1 (person, t2) SELECT person, truth FROM sensitive 
    '''
    c.execute(query)
    
    query = '''
    SELECT * from fairness1
    '''
    test_query(query)
    
    print('\nFairness1-info\n%s'%('='*10))
    
    query = '''
    PRAGMA table_info(fairness1);
    '''
    test_query(query)
    
    
    print('\nFairness-Constraint2\n%s'%('='*10))
    query = 'DROP TABLE IF EXISTS fairness2'
    c.execute(query)
    conn.commit()
    
    query = ''' CREATE TABLE IF NOT EXISTS fairness2
            (person1 string, person2 string, t1 real, t2 real, t3 real)'''
    c.execute(query)
    
    
    query = '''INSERT INTO fairness2 (person1, person2, t2) SELECT person1, person2, truth FROM reachable 
    '''
    c.execute(query)
    
    query = '''
    SELECT * from fairness2
    '''
    test_query(query)
    
    print('\nFairness2-info\n%s'%('='*10))
    
    query = '''
    PRAGMA table_info(fairness2);
    '''
    test_query(query)
    
    
    conn.close()

ground_fairness_constraints()


# In[ ]:



