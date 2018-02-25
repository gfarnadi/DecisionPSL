
# coding: utf-8

# In[1]:

import sqlite3,os,random
conn = sqlite3.connect('viral_marketing.db')
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
        node = 'u'+str(i)
        text_nodes+=node+'\n'
        sensivity = random.choice('01')
        text_sensitive+=node+'\t'+sensivity+'\n'
    save_file('./user.txt',text_nodes)
    save_file('./sensitive.txt',text_sensitive)
    for i in range(edge_size):
        source = random.randint(0,node_size-1)
        target = random.randint(0,node_size-1)
        edge = 'u'+str(source)+'\t'+'u'+str(target)
        trial = 0
        while (target == source or edge in edges) and (trial<node_size-1):
            target = random.randint(0,node_size-1)
            edge = 'u'+str(source)+'\t'+'u'+str(target)
            trial+=1
        if (trial<node_size-1):
            edges.append(edge)
            text_edges+=edge+'\n'
    save_file('./trusts.txt',text_edges)
    
make_synthetic_network(node_size = 5, edge_size = 8)


# In[4]:

def create_db():
    query = 'DROP TABLE IF EXISTS trusts'
    c.execute(query)
    query = 'DROP TABLE IF EXISTS user'
    c.execute(query)
    query = 'DROP TABLE IF EXISTS cost'
    c.execute(query)
    query = 'DROP TABLE IF EXISTS reward'
    c.execute(query)
    query = 'DROP TABLE IF EXISTS sensitive'
    c.execute(query)
    conn.commit()
    query = ''' CREATE TABLE IF NOT EXISTS trusts
            (person1 string, person2 string, truth real)'''
    c.execute(query)
    query = ''' CREATE TABLE IF NOT EXISTS user
            (person string, truth real)'''
    c.execute(query)
    query = ''' CREATE TABLE IF NOT EXISTS cost
            (person string, truth real)'''
    c.execute(query)
    query = ''' CREATE TABLE IF NOT EXISTS reward
            (person string, truth real)'''
    c.execute(query)
    query = ''' CREATE TABLE IF NOT EXISTS sensitive
            (person string, truth real)'''
    c.execute(query)
    network_data = []
    with open('./trusts.txt') as f:
        for line in f:
            line = line.strip()
            if not line: continue
            line = line.split('\t')
            network_data.append(tuple(line))
    c.executemany('INSERT INTO trusts VALUES (?, ?, 1.0)', network_data)
    user_data = []
    sensitive_data = []
    with open('./user.txt') as f:
        for line in f:
            line = line.strip()
            if not line: continue
            line = line.split('\t')
            user_data.append(tuple(line))
    with open('./sensitive.txt') as f:
        for line in f:
            line = line.strip()
            if not line: continue
            line = line.split('\t')
            sensitive_data.append(tuple(line))
    c.executemany('INSERT INTO user VALUES (?, 1.0)', user_data)
    c.executemany('INSERT INTO cost VALUES (?, 1.0)', user_data)
    c.executemany('INSERT INTO reward VALUES (?, 1.0)', user_data)
    c.executemany('INSERT INTO sensitive VALUES (?, ?)', sensitive_data)
    conn.commit()
    
create_db()


# In[5]:

def test_db():
    print('\nTrusts\n%s'%('='*10))
    c.execute('SELECT * FROM trusts')
    rows = c.fetchall()
    for row in rows:
        print(row)
    print('\nUser\n%s'%('='*10))
    c.execute('SELECT * FROM user')
    rows = c.fetchall()
    for row in rows:
        print(row)
    print('\nCost\n%s'%('='*10))
    c.execute('SELECT * FROM cost')
    rows = c.fetchall()
    for row in rows:
        print(row)
    print('\nReward\n%s'%('='*10))
    c.execute('SELECT * FROM reward')
    rows = c.fetchall()
    for row in rows:
        print(row)
    print('\nSensitive\n%s'%('='*10))
    c.execute('SELECT * FROM sensitive')
    rows = c.fetchall()
    for row in rows:
        print(row)
    conn.close()
test_db()


# In[ ]:




# In[ ]:



