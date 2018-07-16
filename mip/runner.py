#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from sample_reader import read_samples
from solve_mip import mip_model

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('usage: %s SAMPLE_FILE'%sys.argv[0])
        exit(1)

    samples = read_samples(sys.argv[1])
    m  = mip_model(samples, delta=1.0)
    m.solve()
