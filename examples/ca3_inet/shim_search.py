import ray
import pandas
import json
import os
import numpy
from ray import tune
from ray import air
from ray.air import session
from ray.tune.search import create_searcher, ConcurrencyLimiter, SEARCH_ALG_IMPORT
from pubtk.runtk.dispatchers import SFS_Dispatcher, UNIXINET_Dispatcher
from pubtk.runtk.submits import Submit, ZSHSubmitSOCK
import time

ALGORITHM = "optuna"
ALGO = ALGORITHM
absolute_path = os.path.abspath("../ray_ses")

CONCURRENCY = 1

NTRIALS = 250

SAVESTR = "{}{}.csv".format(ALGO, NTRIALS)

if ALGO not in SEARCH_ALG_IMPORT.keys():
    print("script requires an algorithm from the following options: ")
    print(SEARCH_ALG_IMPORT.keys())
    raise KeyError

searcher = create_searcher(ALGO)

cwd = os.getcwd()

template = """\
#!/bin/bash
#$ -N job{label}
#$ -pe smp 5
#$ -l h_vmem=32G
#$ -o {cwd}/{label}.run
cd {cwd}
source ~/.bashrc
export OUTFILE="{label}.out"
export SGLFILE="{label}.sgl"
{env}
time mpiexec -np $NSLOTS -hosts $(hostname) nrniv -python -mpi init.py
"""

tune_range = tune.quniform(
    1e-6,
    100000e-6,
    1e-6,
)

params = [
    'PYR->BC_AMPA' , 'PYR->OLM_AMPA', 'PYR->PYR_AMPA',
    'BC->BC_GABA'  , 'BC->PYR_GABA' , 'OLM->PYR_GABA',
    'PYR->BC_NMDA' , 'PYR->OLM_NMDA', 'PYR->PYR_NMDA',
]

param_space = {"netParams.connParams.{}.weight".format(k) : tune_range for k in params}

TARGET = pandas.Series(
    {'PYR': 3.33875,
     'BC' : 19.725,
     'OLM': 3.47,}
)

def local_run(config):
    #this below substitutes submit
    sockname = "/tmp/mysocket.s"
    run =  ZSHSubmitSOCK(script_template=template, sockname=sockname)
    #dispatcher = SFS_Dispatcher(cwd = cwd, env = {}, submit = sge)
    dispatcher = UNIXINET_Dispatcher(project_path = cwd, env={}, submit=run, socket_type = 'UNIX')
    dispatcher.run()
    data = dispatcher.get_run()
    while not data:
        data = dispatcher.get_run()
        time.sleep(5)
    dispatcher.clean(args='rswo')
    data = pandas.read_json(data, typ='series', dtype=float)
    loss = numpy.square( TARGET - data[ ['PYR', 'BC', 'OLM'] ] ).mean()
    conf_report = data[ params ].to_dict()
    report = {'loss': loss, 'PYR': data['PYR'], 'BC': data['BC'], 'OLM': data['OLM']}
    report.update(conf_report)
    session.report(report)

ray.init(
    runtime_env={"working_dir": ".", # needed for import statements
                 "excludes": ["*.csv", "*.out", "*.run",
                              "*.sh", "*.sgl",
                              ]}
)

algo = ConcurrencyLimiter(searcher=searcher, max_concurrent=CONCURRENCY, batch=True)

print("====={} search=====")
print(param_space)

tuner = tune.Tuner(
    local_run, #objective (on machine) sge_objective (on submit)
    tune_config=tune.TuneConfig(
        search_alg=algo,
        metric="loss",
        mode="min",
        num_samples=NTRIALS,
    ),
    run_config=air.RunConfig(
        local_dir=absolute_path,
        name=ALGORITHM,
    ),
    param_space=param_space,
)

results = tuner.fit()

resultsdf = results.get_dataframe()

resultsdf.to_csv(SAVESTR)
