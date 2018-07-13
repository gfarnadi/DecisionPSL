#!/usr/bin/env python
# coding: utf-8

import os
import sys
sys.path.append(os.environ["PROBLOG_HOME"])
import problog
from problog.tasks.dtproblog import dtproblog
from problog.program import PrologString
from problog.tasks import sample
import time


def save_file(path, content):
    try:
        os.remove(path)
    except OSError:
        pass
    with open(path, 'a') as out:
        out.write(content+'\n')


def run_dtproblog(node_size, model_path, output_file):
    text = ''
    model_text = get_program(model_path, node_size)
    print(model_text)
    program = PrologString(model_text)
    current_milli_time = lambda: int(round(time.time() * 1000))
    decisions, score, statistics = dtproblog(program)
    after_milli_time = lambda: int(round(time.time() * 1000))
    processing_time = after_milli_time - current_milli_time
    text+="++++++++ Program for node size = "+ str(node_size)+"++++++++"+'\n'
    text+= '+ statistics: '+str(statistics)+'\n'
    text+= '+ score: '+str(score)+'\n'
    text+= '+ processing time: '+str(processing_time)+'\n'
    print("++++++++ Program for node size = "+ str(node_size)+"++++++++")
    for name, value in decisions.items():
        print ('%s: %s' % (name, value))
        text+= str(name)+'\t'+str(value)+'\n'
    save_file(output_file, text)    


def get_program(model_path, node_size):
    file_path = model_path+'dtproblog_model-'+str(node_size)+'.txt'
    model_text = ''
    with open(file_path, 'r') as myfile:
        model_text = myfile.read()
    return model_text


if __name__  == '__main__':
    if len(sys.argv) < 2:
        print('usage: %s NUM_NODES'%sys.argv[0])
        exit(1)
        
    model_path = '../sample_graphs2/'
    node_size = int(sys.argv[1])
    output_file = model_path+'output/dtproblog_model-'+str(node_size)+'.txt'
    run_dtproblog(node_size, model_path+'model/', output_file)

