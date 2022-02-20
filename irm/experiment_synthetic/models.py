# Copyright (c) Facebook, Inc. and its affiliates.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#

import numpy as np
import torch
import math
import csv

from sklearn.linear_model import LinearRegression
from itertools import chain, combinations
from scipy.stats import f as fdist
from scipy.stats import ttest_ind

import torch
from torch.autograd import grad

import scipy.optimize

import matplotlib
import matplotlib.pyplot as plt

from progress.bar import Bar

def pretty(vector):
    """used for printing"""
    vlist = vector.view(-1).tolist()
    return "[" + ", ".join("{:+.4f}".format(vi) for vi in vlist) + "]"


class InvariantRiskMinimization(object):
    """Object to perform IRM"""

    def __init__(self, environments, args):
        best_reg = 0
        best_err = 1e6

        #print(f"CUDA reserved memory (MB) before instantiation : {torch.cuda.memory_reserved() / 1024**2}")        
        #print(f"CUDA allocated memory (MB) before instantiation : {torch.cuda.memory_allocated() / 1024**2}")        
        try:
            self._uses_cuda = args["irm_cuda"]
            if args["verbose"]:
                if self._uses_cuda:
                    print("IRM using cuda")
                else:
                    print("IRM on the CPU")
            # if cuda is enabled pass data from all environments to cuda only once
            self.environments = [(x.data.to("cuda"), y.data.to("cuda")) for x, y in environments] if self._uses_cuda else environments
            #print(torch.cuda.memory_summary())

            x_val = self.environments[-1][0]
            y_val = self.environments[-1][1]

            # TODO : make this a param
            with open("irm_record.csv", "w", encoding="utf-8") as _irm_record:
                csv_writer = csv.writer(_irm_record, delimiter=",")
                header = "iteration, reg, error, penalty".split(", ")
                csv_writer.writerow(header)

                # Regularise using the last environment, train with all others
                regs_ls = [0, 1e-5, 1e-4, 1e-3, 1e-2, 1e-1]
                #_reg_bar = Bar("Regularizing", max=len(regs_ls))
                for reg in regs_ls:
                    self.train(self.environments[:-1], args, csv_writer=csv_writer, reg=reg)
                    err = (x_val @ self._raw_solution() - y_val).pow(2).mean().item()

                    if err < best_err:
                        best_err = err
                        best_reg = reg
                        best_phi = self.phi.clone()
                    #else:
                    #    del self.phi
                    #    torch.cuda.empty_cache()
                    #_reg_bar.next()
                    if args["verbose"]:
                        print(
                            " IRM (reg={:.6f}) has {:.3f} validation error.".format(reg, err)
                        )
                self.phi = best_phi
                #_reg_bar.finish()
        except Exception as e:
            raise e
        finally:
            del self.environments
            torch.cuda.empty_cache()
            #print(f"CUDA reserved memory (MB) after instantiation : {torch.cuda.memory_reserved() / 1024**2}")        
            #print(f"CUDA allocated memory (MB) after instantiation : {torch.cuda.memory_allocated() / 1024**2}\n\n")        

    def train(
        self,
        environments,
        args,
        csv_writer,
        reg=0,
    ):
        """train the IRM model across environments"""
        dim_x = environments[0][0].size(1)

        self.phi = torch.nn.Parameter(torch.eye(dim_x, dim_x), requires_grad=True)
        self.w = torch.ones(dim_x, 1)
        self.w.requires_grad = True
        if self._uses_cuda:
            self.phi = self.phi.data.to('cuda')
            self.w = self.w.to('cuda')

        opt = torch.optim.Adam([self.phi], lr=args["lr"])
        loss = torch.nn.MSELoss()

        for iteration in range(args["n_iterations"]):
            penalty = 0
            error = 0
            for x_e, y_e in environments:
                error_e = loss(x_e @ self.phi @ self.w, y_e)
                penalty += grad(error_e, self.w, create_graph=True)[0].pow(2).mean()
                error += error_e

            opt.zero_grad()
            (reg * error + (1 - reg) * penalty).backward()
            opt.step()

            if args["verbose"] and iteration % args["irm_epoch_size"] == 0:
                csv_writer.writerow([iteration, reg, error.item(), penalty.item()])
                #w_str = pretty(self.solution())
                #print(
                #    "{:05d} | {:.5f} | {:.5f} | {:.5f} | {}".format(
                #        iteration, reg, error, penalty, w_str
                #    )
                #)

    def solution(self):
        """Get the coefficients, always on cpu"""
        _coeffs = (self.phi @ self.w).view(-1, 1)
        return _coeffs.data.to('cpu') if self._uses_cuda else _coeffs

    def _raw_solution(self):
        """ Get the solution without any preprocessing """
        return (self.phi @ self.w).view(-1, 1)

class InvariantCausalPrediction(object):
    """Direct ICP"""

    def __init__(self, environments, args):
        self.coefficients = None
        self.alpha = args["alpha"]

        x_all = []
        y_all = []
        e_all = []

        for e, (x, y) in enumerate(environments):
            x_all.append(x.numpy())
            y_all.append(y.numpy())
            e_all.append(np.full(x.shape[0], e))

        x_all = np.vstack(x_all)
        y_all = np.vstack(y_all)
        e_all = np.hstack(e_all)

        dim = x_all.shape[1]

        accepted_subsets = []
        for subset in self.powerset(range(dim)):
            if len(subset) == 0:
                continue

            x_s = x_all[:, subset]
            reg = LinearRegression(fit_intercept=False).fit(x_s, y_all)

            p_values = []
            for e in range(len(environments)):
                e_in = np.where(e_all == e)[0]
                e_out = np.where(e_all != e)[0]

                res_in = (y_all[e_in] - reg.predict(x_s[e_in, :])).ravel()
                res_out = (y_all[e_out] - reg.predict(x_s[e_out, :])).ravel()

                p_values.append(self.mean_var_test(res_in, res_out))

            # TODO: Jonas uses "min(p_values) * len(environments) - 1"
            p_value = min(p_values) * len(environments)

            if p_value > self.alpha:
                accepted_subsets.append(set(subset))
                if args["verbose"]:
                    print("Accepted subset:", subset)

        if len(accepted_subsets):
            accepted_features = list(set.intersection(*accepted_subsets))
            if args["verbose"]:
                print("Intersection:", accepted_features)
            self.coefficients = np.zeros(dim)

            if len(accepted_features):
                x_s = x_all[:, list(accepted_features)]
                reg = LinearRegression(fit_intercept=False).fit(x_s, y_all)
                self.coefficients[list(accepted_features)] = reg.coef_

            self.coefficients = torch.Tensor(self.coefficients)
        else:
            self.coefficients = torch.zeros(dim)

    def mean_var_test(self, x, y):
        """mean-variance test"""
        pvalue_mean = ttest_ind(x, y, equal_var=False).pvalue
        pvalue_var1 = 1 - fdist.cdf(
            np.var(x, ddof=1) / np.var(y, ddof=1), x.shape[0] - 1, y.shape[0] - 1
        )

        pvalue_var2 = 2 * min(pvalue_var1, 1 - pvalue_var1)

        return 2 * min(pvalue_mean, pvalue_var2)

    def powerset(self, s):
        """Yield from a powerset"""
        return chain.from_iterable(combinations(s, r) for r in range(len(s) + 1))

    def solution(self):
        """Return the estimated coeficients"""
        return self.coefficients.view(-1, 1)


class EmpiricalRiskMinimizer(object):
    """Plain ERM, fitting a data pooling together
    all environments."""

    def __init__(self, environments, args):
        x_all = torch.cat([x for (x, y) in environments]).numpy()
        y_all = torch.cat([y for (x, y) in environments]).numpy()

        w = LinearRegression(fit_intercept=False).fit(x_all, y_all).coef_
        self.w = torch.Tensor(w).view(-1, 1)

    def solution(self):
        """Get the coeficients"""
        return self.w
