
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

def ground_distribution():
    # ~reachable(a,b)
    #trusts(a,b)->reachable(a,b)
    #reachable(a,b) & trusts(b,c) -> reachable(a,c)
    
    print('\nTrusts\n%s'%('='*10))
    
    query = '''
    SELECT * from trusts
    '''
    test_query(query)
    
    #Ground rule 1:
    
    print('\nReachable\n%s'%('='*10))
    query = 'DROP TABLE IF EXISTS reachable'
    c.execute(query)
    conn.commit()
    query = ''' CREATE TABLE IF NOT EXISTS reachable
            (person1 string, person2 string, truth real)'''
    c.execute(query)
    
    
    query = '''INSERT INTO reachable (person1, person2) SELECT person1, person2 FROM trusts 
    '''
    c.execute(query)
    
    query = '''
    SELECT * from reachable
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
    SELECT reachable.person1, reachable.person2, 
    trusts.truth as t1, reachable.truth as t2
    FROM 
    reachable  
    INNER JOIN 
    trusts
    ON reachable.person1 = trusts.person1 AND reachable.person2 = trusts.person2
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
    
    #Ground rule 2:
    print('\nRule2\n%s'%('='*10))
    
    query = 'DROP TABLE IF EXISTS temprule2'
    c.execute(query)
    conn.commit()
    
    
    query = ''' 
    CREATE TABLE temprule2
    AS
    WITH RECURSIVE transitive_closure AS
    (SELECT person1, person2 FROM Reachable
      UNION 
      SELECT tc.person1, trusts.person2 FROM trusts
        JOIN transitive_closure AS tc
      ON (trusts.person1 = tc.person2 AND tc.person1 <> trusts.person2)
    )
    SELECT * FROM transitive_closure
    '''
    test_query(query)
    
    query = '''
    SELECT * from temprule2
    '''
    test_query(query)
    
    print('\nTemprule2-info\n%s'%('='*10))
    
    query = '''
    PRAGMA table_info(temprule2);
    '''
    test_query(query)
    
    print('\nReachable-updated\n%s'%('='*10))
    
    query = '''INSERT INTO reachable (person1, person2) SELECT person1, person2 FROM temprule2 
    '''
    c.execute(query)
    
    query = '''
    SELECT * from reachable
    '''
    test_query(query)
    
    
    
    query = 'DROP TABLE IF EXISTS rule2'
    c.execute(query)
    conn.commit()
    
    query = '''
    CREATE TABLE rule2
    AS
    WITH temp2 AS
    (SELECT r1.person1 as person1, r1.person2 as person2, r2.person2 as person3,
    r1.truth as t1, r2.truth as t2, r3.truth as t3
    FROM Reachable aS r1, trusts as r2, Reachable aS r3
      WHERE
      r1.person1 = r3.person1 AND
      r1.person2 = r2.person1 AND
      r2. person2 = r3.person2
    )
    SELECT * FROM temp2
    '''
    
    print('\nRule2\n%s'%('='*10))
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


# In[ ]:



