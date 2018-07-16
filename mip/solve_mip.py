# coding: utf-8

from gurobipy import Model, GRB, quicksum

class mip_model(object):
    def __init__(self, samples, delta=1.0):
        self.n_nodes = samples.n_nodes
        self.n_samples = samples.n_samples
        self.delta = delta

        self.B = samples.B
        self.T = samples.T
        self.F = samples.F

        self.model = Model('DPSL')
        self.create_model()

    def create_model(self):
        self.U = self.model.addVars(self.n_nodes,
                                    self.n_samples,
                               name='U', lb=0, ub=1,
                               vtype=GRB.CONTINUOUS)
        self.M = self.model.addVars(self.n_nodes,
                               name='M', lb=0, ub=1,
                               vtype=GRB.CONTINUOUS)

        self.y = self.model.addVars(self.n_nodes,
                                    self.n_samples,
                               name='y', lb=0, ub=1,
                               vtype=GRB.CONTINUOUS)

        self.z = self.model.addVars(self.n_nodes,
                                    self.n_nodes,
                                    self.n_samples,
                               name='z', lb=0, ub=1,
                               vtype=GRB.CONTINUOUS)


        self.model.addConstrs((self.y[i, n] >= -1 + self.M[i]
                                          + self.B[i, n]
                                          - self.U[i, n])
                              for i in range(self.n_nodes)
                              for n in range(self.n_samples))

        self.model.addConstrs((self.z[i, j, n] >= -2 + self.T[i, j, n]
                                             + self.F[i, j, n]
                                             + self.U[j, n]
                                             - self.U[i, n])
                              for i in range(self.n_nodes)
                              for j in range(self.n_nodes)
                              for n in range(self.n_samples)
                              if i != j)

        cost_expr = (2 * quicksum(self.M) -
                    (5 / self.n_samples) * quicksum(self.U))
        dist_expr = (quicksum(self.y) + quicksum(self.z) +
                    quicksum(self.U))

        self.model.setObjective(cost_expr + self.delta * dist_expr,
                                GRB.MINIMIZE)
    def solve(self):
        self.model.optimize()
        for i in range(self.n_nodes):
            print(self.M[i].x)




