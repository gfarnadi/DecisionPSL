
# coding: utf-8

# In[5]:

import sys
sys.path.append("../problogBitBucket")
import problog


# In[6]:

from problog.tasks.dtproblog import dtproblog
from problog.program import PrologString
from problog.tasks import sample


# In[ ]:

def make_sample():
    


# In[ ]:

def sample_model(model_text):
    model = PrologString(model_text)
    result = sample.sample(model, n=10, format='dict')
    for i in result:
        print(i)
        
sample_model(model_3) 

