#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys, time
from dtproblog_program_generator import run_dtproblog

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('usage: %s NUM_NODES OUTFILE'%sys.argv[0])
        exit(1)
    
    num_nodes = int(sys.argv[1])
    start = time.time()    
    decisions, score,  _ = run_dtproblog(num_nodes)
    runtime = time.time() - start
    
    outfile = sys.argv[2]
    with open(outfile, 'w') as f:
        print(score, file=f)
        print(decisions, file=f)
        print(runtime, file=f)
   