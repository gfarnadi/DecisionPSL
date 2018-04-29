#!/usr/bin/env python
# coding: utf-8

import tempfile, subprocess, os, sys
from collections import namedtuple

BddNode = namedtuple('BDDNode', ['id', 'varid', 'hi', 'lo'])
Variable = namedtuple('Variable', ['id', 'pweight', 'nweight', 'is_decision'])
BDD = namedtuple('BDD', ['bdd_nodes', 'bdd_vars', 'roots', 'max_vars'])

def read_bdd(filename):
    with open(filename) as f:
        nn, nv = map(int, f.readline().strip().split())
        bdd_vars = [Variable(i, 1.0, 1.0, False) for i in range(nv)]
        roots = set(map(int, f.readline().strip().split()))
        bdd_nodes = [None] * nn
        for i in range(nn):
            varid, lo, hi = map(int, f.readline().strip().split())
            bdd_nodes[i] = BddNode(i, varid, hi, lo)

        weights = list(map(float, f.readline().strip().split()))
        for i in range(nv):
            bdd_vars[i] = bdd_vars[i]._replace(pweight=weights[2*i],
                                               nweight=weights[2*i + 1])

        max_vars = set(map(int, f.readline().strip().split()))
        for v in max_vars:
            bdd_vars[v] = bdd_vars[v]._replace(is_decision=True)

    return BDD(bdd_nodes, bdd_vars, roots, max_vars)


def create_dot(bdd):
    dot_str = 'digraph G {\n\tntrue [shape=box,label="1"];\n\tnfalse [shape=box,label="0"];\n'
    for node in bdd.bdd_nodes:
        description = 'label="v%d (%d)"'%(node.varid, node.id)
        if bdd.bdd_vars[node.varid].is_decision:
            description += ',shape=diamond'
        dot_str += '\tn%d [%s];\n'%(node.id, description)

    for node in bdd.bdd_nodes:
        for ctype in ('hi', 'lo'):
            child = getattr(node, ctype)
            if child == -2:
                target = 'ntrue'
            elif child == -1:
                target = 'nfalse'
            else:
                target = 'n%d'%child
            properties = []
            bvar = bdd.bdd_vars[node.varid]
            if not bvar.is_decision:
                if ctype == 'lo':
                    w = bvar.nweight
                else:
                    w = bvar.pweight
                properties.append('label="%.2f"'%w)
            if ctype == 'lo':
                properties.append('style=dashed')
            properties = ','.join(properties)
            if properties:
                properties = '[%s]'%properties
            dot_str += '\tn%d -> %s%s;\n'%(node.id, target, properties)
    dot_str += '}\n'
    return dot_str


def draw_bdd(bdd, pdfname):
    dot_str = create_dot(bdd)
    _, dotfile = tempfile.mkstemp()
    with open(dotfile, 'w') as f:
        print(dot_str, file=f)
    subprocess.run(['dot', '-Tpdf', dotfile, '-o', pdfname])
    os.remove(dotfile)


if __name__  == '__main__':
    if len(sys.argv) != 3:
        print('usage: %s BDD_FILE PDF_FILE'%sys.argv[0])
        exit(1)

    bdd = read_bdd(sys.argv[1])
    draw_bdd(bdd, sys.argv[2])

