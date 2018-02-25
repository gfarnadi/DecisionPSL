
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
    #Buy(u)∧Sensitive(u)
    
    #ground constraint 1
    
    print('\nConstraint1\n%s'%('='*10))
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
    conn.close()

ground_fairness_constraints()

