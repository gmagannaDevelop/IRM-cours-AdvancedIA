import pandas as pd
from pathlib import Path as path
path(".").resolve().name
path(".").resolve()
list(path(".").resolve().glob("irm_training"))
list(path(".").resolve().glob("irm_training*"))
import plotnine as p
for rep, file in enumerate()
for rep, file in enumerate(path(".").resolve().glob("irm_training*")):
    print(f"{i} : {file}")
for rep, file in enumerate(path(".").resolve().glob("irm_training*")):
    print(f"{rep} : {file}")
dfs = []
for rep, file in enumerate(path(".").resolve().glob("irm_training*")):
    _x = pd.read_csv(file)
    dfs.append(_x)
_x
ls
dfs
dfs = []
for rep, file in enumerate(path(".").resolve().glob("irm_training*")):
    _x = pd.read_csv(file)
    _x.loc[:, "Repetition"] = rep
    dfs.append(_x)
dfs
pd.concat(dfs, axis='rows')
pd.concat(dfs, axis='rows', ignore_index=T)
pd.concat(dfs, axis='rows', ignore_index=True)
pd.concat(dfs, axis='rows', ignore_index=False)
pd.concat(dfs, axis="rows", ignore_index=True)
pd.concat(dfs, axis="rows", ignore_index=True).index.is_unique
pd.concat(dfs, axis="rows", ignore_index=False).index.is_unique
x = pd.concat(dfs, axis="rows", ignore_index=True)
x
p.ggplot(x, p.aes(x="iteration", y="error")) + p.geom_point(aes(colour="Repetition"))
p.ggplot(x, p.aes(x="iteration", y="error")) + p.geom_point(p.aes(colour="Repetition"))
y = x.copy()
y.Repetition.astype("o")
y.Repetition.astype("str")
y.loc[:, "Repetition"] = y.Repetition.astype("str")
y
y.dtypes
x.dtypes
p.ggplot(y, p.aes(x="iteration", y="error")) + p.geom_point(
    p.aes(colour="Repetition"), alpha=0.4
)
p.ggplot(y, p.aes(x="iteration", y="error")) + p.geom_line(
    p.aes(colour="Repetition"), alpha=0.4
)
help(p.geom_line)
p.ggplot(y, p.aes(x="iteration", y="error")) + p.geom_path(
    p.aes(colour="Repetition"), alpha=0.4
)
dfs
dfs[1]
y.loc[:, "reg"] = y.reg.astype("str")
!ls
!pwd
!cd ../4/
%cd ../4/
%ls
!head irm_results_2022-02-21_17\:22\:24.csv
dfs[1]
test - dfs[1].copy(deep=True)
test =  dfs[1].copy(deep=True)
test
test.append([1, 2, 3, 4, 5])
pd.concat(test, [1, 2, 3, 4, 5], axis="rows")
pd.concat([test, [1, 2, 3, 4, 5]], axis="rows")
pd.row
pd.loc[1, :]
test.loc[1, :]
test.loc[1, :].copy()
test.loc[1, :].copy(deep=True)
test.loc[1, :].copy(deep=True) is test.loc[1, :].copy(deep=True)
test.loc[1, :].copy(deep=True) is test.loc[1, :]
test.loc[1, :].copy(deep=False) is test.loc[1, :]
test.loc[1, :].copy(deep=False)[1] is test.loc[1, :][1]
test.loc[1, :].copy(deep=True)[1] is test.loc[1, :][1]
test.loc[1, :].copy(deep=True)[1]
test.loc[1, :].copy(deep=True)
wo = test.loc[1, :].copy(deep=True)
wp
wo
wo.sum()
wo.mean()
%history -f explor.py
