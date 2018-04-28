
# coding: utf-8

# In[1]:

import sqlite3,os,random
conn = sqlite3.connect('network_design.db')
c = conn.cursor()


# In[2]:

def save_file(path, content):
    try:
        os.remove(path)
    except OSError:
        pass
    with open(path, 'a') as out:
        out.write(content+'\n')


# In[3]:

def make_synthetic_network(node_size, edge_size):
    edges= []
    text_edges = ''
    text_nodes= ''
    text_sensitive = ''
    for i in range(node_size):
        node = 'c'+str(i)
        text_nodes+=node+'\n'
        sensivity = random.choice('01')
        text_sensitive+=node+'\t'+sensivity+'\n'
    save_file('./city.txt',text_nodes)
    save_file('./large.txt',text_sensitive)
    for i in range(edge_size):
        source = random.randint(0,node_size-1)
        target = random.randint(0,node_size-1)
        edge = 'c'+str(source)+'\t'+'c'+str(target)
        trial = 0
        while (target == source or edge in edges) and (trial<node_size-1):
            target = random.randint(0,node_size-1)
            edge = 'c'+str(source)+'\t'+'c'+str(target)
            trial+=1
        if (trial<node_size-1):
            edges.append(edge)
            text_edges+=edge+'\n'
    save_file('./edges.txt',text_edges)
    
make_synthetic_network(node_size = 5, edge_size = 8)


# In[4]:

def create_db():
    query = 'DROP TABLE IF EXISTS edges'
    c.execute(query)
    query = 'DROP TABLE IF EXISTS city'
    c.execute(query)
    query = 'DROP TABLE IF EXISTS cost'
    c.execute(query)
    query = 'DROP TABLE IF EXISTS large'
    c.execute(query)
    conn.commit()
    query = ''' CREATE TABLE IF NOT EXISTS edges
            (node1 string, node2 string, truth real)'''
    c.execute(query)
    query = ''' CREATE TABLE IF NOT EXISTS city
            (node string, truth real)'''
    c.execute(query)
    query = ''' CREATE TABLE IF NOT EXISTS cost
            (node1 string, node2 string, truth real)'''
    c.execute(query)
    query = ''' CREATE TABLE IF NOT EXISTS large
            (node string, truth real)'''
    c.execute(query)
    network_data = []
    with open('./edges.txt') as f:
        for line in f:
            line = line.strip()
            if not line: continue
            line = line.split('\t')
            network_data.append(tuple(line))
    c.executemany('INSERT INTO edges VALUES (?, ?, 1.0)', network_data)
    city_data = []
    sensitive_data = []
    with open('./city.txt') as f:
        for line in f:
            line = line.strip()
            if not line: continue
            line = line.split('\t')
            city_data.append(tuple(line))
    with open('./large.txt') as f:
        for line in f:
            line = line.strip()
            if not line: continue
            line = line.split('\t')
            sensitive_data.append(tuple(line))
    c.executemany('INSERT INTO city VALUES (?, 1.0)', city_data)
    c.executemany('INSERT INTO cost VALUES (?, ?, 1.0)', network_data)
    c.executemany('INSERT INTO large VALUES (?, ?)', sensitive_data)
    conn.commit()
    
create_db()


# In[5]:

def test_db():
    print('\nEdges\n%s'%('='*10))
    c.execute('SELECT * FROM edges')
    rows = c.fetchall()
    for row in rows:
        print(row)
    print('\nCity\n%s'%('='*10))
    c.execute('SELECT * FROM city')
    rows = c.fetchall()
    for row in rows:
        print(row)
    print('\nCost\n%s'%('='*10))
    c.execute('SELECT * FROM cost')
    rows = c.fetchall()
    for row in rows:
        print(row)
    print('\nLarge\n%s'%('='*10))
    c.execute('SELECT * FROM large')
    rows = c.fetchall()
    for row in rows:
        print(row)
    conn.close()
test_db()

