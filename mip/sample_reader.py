
# coding: utf-8

import os, sys, pickle
import numpy as np
sys.path.append(os.environ["PROBLOG_HOME"])
from collections import namedtuple

sample_type = namedtuple('sample', ['n_nodes','n_samples', 'B', 'T', 'F'])
def read_samples(filename):
    with open(filename, 'rb') as f:
        samples = pickle.load(f)

    buy_marketing_samples = {}
    buy_trust_samples = {}
    trust_samples = {}
    for k, v in samples.items():
        s = k.signature
        if s == 'buy_from_marketing/1':
            n = k.args[0].value
            buy_marketing_samples[n] = v
        elif s == 'buy_from_trust/2':
            n1 = k.args[0].value
            n2 = k.args[1].value
            buy_trust_samples[(n1, n2)] = v
        elif s == 'trusts/2':
            n1 = k.args[0].value
            n2 = k.args[1].value
            trust_samples[(n1, n2)] = v
        else:
            print('unknown predicate')
            exit(1)

    n_nodes = len(buy_marketing_samples.keys())
    n_samples = len(trust_samples[list(trust_samples.keys())[0]])
    B = np.zeros((n_nodes, n_samples))
    for i in range(n_nodes):
        for n in range(n_samples):
            if buy_marketing_samples[i][n]:
                B[i, n] = 1

    T = np.zeros((n_nodes, n_nodes, n_samples))
    F = np.zeros((n_nodes, n_nodes, n_samples))
    for i in range(n_nodes):
        for j in range(n_nodes):
            if j == i: continue
            if trust_samples[(i, j)][n]:
                T[i, j, n] = 1
            if buy_trust_samples[(i, j)][n]:
                F[i, j, n] = 1

    s = sample_type(n_nodes, n_samples, B, T, F)
    return s

