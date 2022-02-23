import pandas as pd
import matplotlib.pyplot as plt
x = pd.read_csv("irm_results_2022-02-21_01:55:52.csv")
x = pd.read_csv("irm_results_2022-02-21_01:17:12.csv")
x
from irm.experiment_synthetic.main import format_results_df
format_results_df(x)
x
x.groupby(["Method"])
x.groupby("Method")
x.groupby("Method").ErrorCausal.mean()
x.groupby("Method")['ErrorCausal'].mean()
x.groupby("Method")['ErrCausal'].mean()
x.groupby("Method")["ErrCausal"].std()
x
y = x.copy()
y.loc[15:, :]
y.loc[15:, :].groupby("Method").ErrCausal.mean()
from irm.experiment_synthetic import sem
sem
sem.ChainEquationModel()
sem.ChainEquationModel(10)
sem = sem.ChainEquationModel(10)
sem
sem?
sem(1000, .3)
x, y = sem(1000, .3)
x
x.shape
* "Coefficients,GraphObservation,Dispersion,Scramble,Method,ErrCausal,ErrNonCausal".split(
    ","
)
[
    1,
    *"Coefficients,GraphObservation,Dispersion,Scramble,Method,ErrCausal,ErrNonCausal".split(
        ","
    ),
]
[
    *"Coefficients,GraphObservation,Dispersion,Scramble,Method,ErrCausal,ErrNonCausal".split(
        ","
    ),
    2,
]
%history -f explor1.py
