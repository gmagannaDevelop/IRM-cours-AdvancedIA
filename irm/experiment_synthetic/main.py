# Copyright (c) Facebook, Inc. and its affiliates.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#

import sys
import torch
import numpy
import multiprocessing as mp

from .sem import ChainEquationModel
from .models import *


def errors(w, w_hat):
    """Compute errors"""
    w = w.view(-1)
    w_hat = w_hat.view(-1)

    i_causal = torch.where(w != 0)[0].view(-1)
    i_noncausal = torch.where(w == 0)[0].view(-1)

    if len(i_causal):
        error_causal = (w[i_causal] - w_hat[i_causal]).pow(2).mean()
        error_causal = error_causal.item()
    else:
        error_causal = 0

    if len(i_noncausal):
        error_noncausal = (w[i_noncausal] - w_hat[i_noncausal]).pow(2).mean()
        error_noncausal = error_noncausal.item()
    else:
        error_noncausal = 0

    return error_causal, error_noncausal


def run_experiment(args):
    """run the experiment"""
    if args["seed"] >= 0:
        torch.manual_seed(args["seed"])
        numpy.random.seed(args["seed"])
        torch.set_num_threads(args["n_threads"])

    if args["setup_sem"] == "chain":
        setup_str = "chain_ones={}_hidden={}_hetero={}_scramble={}".format(
            args["setup_ones"],
            args["setup_hidden"],
            args["setup_hetero"],
            args["setup_scramble"],
        )
    elif args["setup_sem"] == "icp":
        # WARNING : the setup_str is set but it has not been implemented
        setup_str = "sem_icp"
    else:
        raise NotImplementedError

    all_methods = {
        "ERM": EmpiricalRiskMinimizer,
        "ICP": InvariantCausalPrediction,
        "IRM": InvariantRiskMinimization,
    }

    if args["methods"] == "all":
        methods = all_methods
    else:
        methods = {m: all_methods[m] for m in args["methods"].split(",")}

    all_sems = []
    all_solutions = []
    all_environments = []

    for rep_i in range(args["n_reps"]):
        if args["setup_sem"] == "chain":
            sem = ChainEquationModel(
                args["dim"],
                ones=args["setup_ones"],
                hidden=args["setup_hidden"],
                scramble=args["setup_scramble"],
                hetero=args["setup_hetero"],
            )

            env_list = [float(e) for e in args["env_list"].split(",")]
            environments = [sem(args["n_samples"], e) for e in env_list]
        else:
            raise NotImplementedError

        all_sems.append(sem)
        all_environments.append(environments)

    for sem, environments in zip(all_sems, all_environments):
        sem_solution, sem_scramble = sem.solution()

        solutions = [
            "{} SEM {} {:.5f} {:.5f}".format(setup_str, pretty(sem_solution), 0, 0)
        ]

        for method_name, method_constructor in methods.items():
            # training occurs at instantiation time.
            method = method_constructor(environments, args)
            # the method (Optimisation technique) has been applied so the solution is available
            method_solution = sem_scramble @ method.solution()
            err_causal, err_noncausal = errors(sem_solution, method_solution)

            solutions.append(
                "{} {} {} {:.5f} {:.5f}".format(
                    setup_str,
                    method_name,
                    pretty(method_solution),
                    err_causal,
                    err_noncausal,
                )
            )

        all_solutions += solutions

    return all_solutions
