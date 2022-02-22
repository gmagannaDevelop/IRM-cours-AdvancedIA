# Copyright (c) Facebook, Inc. and its affiliates.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#

import datetime as dt

import torch
import numpy
import pandas as pd

from tqdm import tqdm

from .sem import ChainEquationModel
from .models import *

_SETUP_STR_SEPARATOR = "|"


def vector_to_dict(vector):
    """Format a vector as dictionary
    containing a list of values"""


def errors(w, w_hat):
    """Compute errors
    return causal and non-causal"""
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
    # Set up the random number generator and threads
    if args["seed"] >= 0:
        torch.manual_seed(args["seed"])
        numpy.random.seed(args["seed"])
        torch.set_num_threads(args["n_threads"])

    # Create a setup string (TODO: modify this)
    if args["setup_sem"] == "chain":
        _setup_ls = ["chain_ones={}", "hidden={}", "hetero={}", "scramble={}"]
        setup_str = _SETUP_STR_SEPARATOR.join(_setup_ls).format(
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

    for rep_i in tqdm(range(args["n_reps"])):
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

    # TODO : save parameter estimations
    # For an explanation of the names given to columns, see the article
    # section 5.1 Synthetic Data
    results_df = pd.DataFrame(
        columns=[
            *"Coefficients,GraphObservation,Dispersion,Scramble,Method,ErrCausal,ErrNonCausal".split(
                ","
            ),
            *[f"X{ii+1}" for ii in range(args["dim"])],
        ],
        index=list(range(len(all_sems) * len(methods) + len(all_sems))),
    )
    i = 0

    try:
        for sem, environments in tqdm(
            zip(all_sems, all_environments),
            desc="Repetitions",
            unit="environment",
        ):
            sem_solution, sem_scramble = sem.solution()
            # Save the solution before saving the methods
            results_df.loc[i, :] = (
                *map(
                    lambda x: x.split("=", maxsplit=1)[-1],
                    setup_str.split(_SETUP_STR_SEPARATOR),
                ),
                "SEM",
                0.0,
                0.0,
                *sem_solution.view(-1).tolist(),
            )
            i += 1
            for method_name, method_constructor in tqdm(
                methods.items(), desc="Methods Loop", unit="method"
            ):
                # training occurs at instantiation time.
                method = method_constructor(environments, args)
                # the method (Optimisation technique) has been applied so the solution is available
                solution = method.solution()
                method_solution = sem_scramble @ solution
                if args["irm_cuda"] and method_name == "IRM":
                    del method
                    torch.cuda.empty_cache()
                err_causal, err_noncausal = errors(sem_solution, method_solution)

                # TODO : save parameter estimations
                results_df.loc[i, :] = (
                    *map(
                        lambda x: x.split("=", maxsplit=1)[-1],
                        setup_str.split(_SETUP_STR_SEPARATOR),
                    ),
                    method_name,
                    err_causal,
                    err_noncausal,
                    *method_solution.view(-1).tolist(),
                )
                i += 1

    except Exception as _e:
        raise _e
    finally:
        _results_dest = f"irm_results_{str(dt.datetime.now()).split('.', maxsplit=1)[0].replace(' ', '_')}.csv"
        results_df.to_csv(_results_dest, index=False)

    return results_df


def format_results_df(results_df):
    """Give the proper formatting to the contents of results_df
    !!!!!!!!!WARNING : the formatting happens in_place !!!!!!!"""
    results_df.loc[:, "Coefficients"] = results_df.Coefficients.replace(
        {0: "Random", 1: "Ones"}  # See sem.py for details
    )
    results_df.loc[:, "GraphObservation"] = results_df.GraphObservation.replace(
        {0: "F", 1: "P"}  # Full, Partial
    )
    results_df.loc[:, "Dispersion"] = results_df.Dispersion.replace(
        {0: "O", 1: "E"}  # hOmoscedastic, # hEteroscedastic
    )
    results_df.loc[:, "Scramble"] = results_df.Scramble.replace(
        {0: "U", 1: "S"}  # Unscrambled, Scrambled
    )
    results_df.loc[:, "Acronym"] = (
        results_df.GraphObservation + results_df.Dispersion + results_df.Scramble
    )

    return results_df
