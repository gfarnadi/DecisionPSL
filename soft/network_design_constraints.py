
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

def ground_constraints():
    #presents(a,b)->connected(a,b)
    #connected(a,b) -> path(a,b)
    #path(a,b) & connected(b,c) -> path(a,c)
    #protected(a,b)->connected(a,b)
    #present(a,b) & protected(a,b) -> connected(a,b)
    
    print('\nPresents\n%s'%('='*10))
    
    query = '''
    SELECT * from presents
    '''
    test_query(query)
    
    #Ground constraint 1:
    
    print('\nConnected\n%s'%('='*10))
    query = 'DROP TABLE IF EXISTS connected'
    c.execute(query)
    conn.commit()
    query = ''' CREATE TABLE IF NOT EXISTS connected
            (node1 string, node2 string, truth real)'''
    c.execute(query)
    
    
    query = '''INSERT INTO connected (node1, node2) SELECT node1, node2 FROM presents 
    '''
    c.execute(query)
    
    query = '''
    SELECT * from connected
    '''
    test_query(query)
    
    print('\nConstraint1\n%s'%('='*10))
    query = 'DROP TABLE IF EXISTS constraint1'
    c.execute(query)
    conn.commit()
    
    query = '''
    CREATE TABLE constraint1
    AS
    WITH temp1 AS
    (
    SELECT presents.node1, presents.node2, 
    presents.truth as t1, connected.truth as t2
    FROM 
    connected
    INNER JOIN 
    presents
    ON connected.node1 = presents.node1 AND connected.node2 = presents.node2
    )
    SELECT * from temp1
    '''
    
    test_query(query)
    
    query = '''
    SELECT * from constraint1
    '''
    test_query(query)
    
    print('\nConstraint1-info\n%s'%('='*10))
    
    query = '''
    PRAGMA table_info(constraint1);
    '''
    test_query(query)
    
    #Ground constraint 2:
    
    print('\nConstraint2\n%s'%('='*10))
    
    query = 'DROP TABLE IF EXISTS path'
    c.execute(query)
    conn.commit()
    query = ''' CREATE TABLE IF NOT EXISTS path
            (node1 string, node2 string, truth real)'''
    c.execute(query)
    
    
    query = '''INSERT INTO path (node1, node2) SELECT node1, node2 FROM connected 
    '''
    c.execute(query)
    
    query = '''
    SELECT * from path
    '''
    test_query(query)
    
    
    query = 'DROP TABLE IF EXISTS constraint2'
    c.execute(query)
    conn.commit()
    
    query = '''
    CREATE TABLE constraint2
    AS
    WITH temp1 AS
    (
    SELECT connected.node1, connected.node2, 
    connected.truth as t1, path.truth as t2
    FROM 
    connected
    INNER JOIN 
    path
    ON connected.node1 = path.node1 AND connected.node2 = path.node2
    )
    SELECT * from temp1
    '''
    
    test_query(query)
    
    query = '''
    SELECT * from constraint2
    '''
    test_query(query)
    
    print('\nConstraint2-info\n%s'%('='*10))
    
    query = '''
    PRAGMA table_info(constraint2);
    '''
    test_query(query)
    

    query = 'DROP TABLE IF EXISTS tempconstraint2'
    c.execute(query)
    conn.commit()
    
    
    query = ''' 
    CREATE TABLE tempconstraint2
    AS
    WITH RECURSIVE transitive_closure AS
    (SELECT node1, node2 FROM path
      UNION 
      SELECT tc.node1, connected.node2 FROM connected
        JOIN transitive_closure AS tc
      ON (connected.node1 = tc.node2 AND tc.node1 <> connected.node2)
    )
    SELECT * FROM transitive_closure
    '''
    test_query(query)
    
    query = '''
    SELECT * from tempconstraint2
    '''
    test_query(query)
    
    print('\nTempconstraint2-info\n%s'%('='*10))
    
    query = '''
    PRAGMA table_info(tempconstraint2);
    '''
    test_query(query)
    
    print('\nPath-updated\n%s'%('='*10))
    
    query = '''INSERT INTO path (node1, node2) SELECT node1, node2 FROM tempconstraint2 
    '''
    c.execute(query)
    
    query = '''
    SELECT * from path
    '''
    test_query(query)
    
    
    #Ground constraint 3:
    
    query = 'DROP TABLE IF EXISTS constraint3'
    c.execute(query)
    conn.commit()
    
    query = '''
    CREATE TABLE constraint3
    AS
    WITH temp2 AS
    (SELECT r1.node1 as node2, r1.node2 as node2, r2.node2 as node3,
    r1.truth as t1, r2.truth as t2, r3.truth as t3
    FROM path aS r1, connected as r2, path aS r3
      WHERE
      r1.node1 = r3.node1 AND
      r1.node2 = r2.node1 AND
      r2. node2 = r3.node2
    )
    SELECT * FROM temp2
    '''
    
    print('\nConstraint3\n%s'%('='*10))
    test_query(query)
    
    query = '''
    SELECT * from constraint3
    '''
    test_query(query)
    
    print('\nConstraint3-info\n%s'%('='*10))
    
    query = '''
    PRAGMA table_info(constraint3);
    '''
    test_query(query)
    
    
    
    
    #Ground constraint 4:
    
    print('\nProtected\n%s'%('='*10))
    query = 'DROP TABLE IF EXISTS protected'
    c.execute(query)
    conn.commit()
    query = ''' CREATE TABLE IF NOT EXISTS protected
            (node1 string, node2 string, truth real)'''
    c.execute(query)
    
    
    query = '''INSERT INTO protected (node1, node2) SELECT node1, node2 FROM connected 
    '''
    c.execute(query)
    
    query = '''
    SELECT * from protected
    '''
    test_query(query)
    
    print('\nConstraint4\n%s'%('='*10))
    query = 'DROP TABLE IF EXISTS constraint4'
    c.execute(query)
    conn.commit()
    
    query = '''
    CREATE TABLE constraint4
    AS
    WITH temp1 AS
    (
    SELECT connected.node1, connected.node2, 
    connected.truth as t1, protected.truth as t2
    FROM 
    connected
    INNER JOIN 
    protected
    ON connected.node1 = protected.node1 AND connected.node2 = protected.node2
    )
    SELECT * from temp1
    '''
    
    test_query(query)
    
    query = '''
    SELECT * from constraint4
    '''
    test_query(query)
    
    print('\nConstraint4-info\n%s'%('='*10))
    
    query = '''
    PRAGMA table_info(constraint4);
    '''
    test_query(query)
    
    #Ground constraint 5:
    
    print('\nTempconstraint5\n%s'%('='*10))
    
    
    
    query = 'DROP TABLE IF EXISTS tempconstraint5'
    c.execute(query)
    conn.commit()
    
    query = '''
    CREATE TABLE tempconstraint5
    AS
    WITH temp1 AS
    (
    SELECT presents.node1, presents.node2, 
    presents.truth as t1, protected.truth as t2
    FROM 
    presents
    INNER JOIN 
    protected
    ON presents.node1 = protected.node1 AND presents.node2 = protected.node2
    ) 
    SELECT * FROM temp1
    '''
    
    test_query(query)
    
    query = '''
    SELECT * from tempconstraint5
    '''
    test_query(query)
    
    
    print('\nConstraint5\n%s'%('='*10))
    
    
    query = 'DROP TABLE IF EXISTS constraint5'
    c.execute(query)
    conn.commit()
    
    query = '''
    CREATE TABLE constraint5
    AS
    WITH temp2 AS(
    SELECT tempconstraint5.node1, tempconstraint5.node2, 
    tempconstraint5.t1 as t1, tempconstraint5.t2 as t2, connected.truth as t3
    FROM 
    tempconstraint5
    INNER JOIN 
    connected
    ON connected.node1 = tempconstraint5.node1 AND connected.node2 = tempconstraint5.node2
    )
    SELECT * FROM temp2
    '''
    
    test_query(query)
    
    query = '''
    SELECT * from constraint5
    '''
    test_query(query)
    
    print('\nConstraint5-info\n%s'%('='*10))
    
    query = '''
    PRAGMA table_info(constraint5);
    '''
    test_query(query)
    
    
    conn.close()

ground_constraints()






