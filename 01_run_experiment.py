import cocoex
import itertools
import numpy as np
import os
import pandas as pd
import pflacco.classical_ela_features as pf
import random
import sys

from config import REPETITIONS
from multiprocessing import Pool
from pflacco.sampling import create_initial_sample

ROOT = '/scratch/tmp/r_prag01/ela_norm'
#ROOT = './'

def run_experiment(experiment):
    results = []

    # Initialize BBOB Suite
    suite = cocoex.Suite("bbob", f"instances:{experiment[2]}", f"function_indices:{experiment[0]} dimensions:{experiment[1]}")

    for problem in suite:
        # Get meta information about the opt problem
        fid = problem.id_function
        iid = problem.id_instance
        dim = problem.dimension
        
        for rep in range(REPETITIONS):
            # Set seeds, this ensures, that at least for every (fid,dim,iid) the seeds are different over all x repetitions
            np.random.seed(int(fid) * int(iid) * int(dim) *(rep + 1))
            random.seed(int(fid) * int(iid) * int(dim) * (rep + 1))
            
            X = create_initial_sample(dim, sample_coefficient = experiment[5], sample_type = experiment[4], lower_bound = -5, upper_bound = 5)
            y = X.apply(lambda x: problem(x), axis = 1)

            if experiment[3] == 'stan':
                y = (y - y.mean())/y.std()
            elif experiment[3] == 'norm':
                y = (y - y.min())/(y.max() - y.min())

            ela_distr = pf.calculate_ela_distribution(X, y)
            ela_meta = pf.calculate_ela_meta(X, y)
            ic = pf.calculate_information_content(X, y)
            nbc = pf.calculate_nbc(X, y)
            disp = pf.calculate_dispersion(X, y)
            pca = pf.calculate_pca(X, y)

            # Add results to python list 'results' as Python dict
            data = {
                'fid': fid,
                'dim': dim,
                'iid': iid,
                'rep': rep,
                'mode': experiment[3],
                'sampling': experiment[4],
                'budget_factor': experiment[5],
                **ela_distr,
                **ela_meta,
                **ic,
                **nbc,
                **disp,
                **pca
            }
            results.append(data)

    # Convert list of python dicts to pandas dataframe and store as CSV to disk
    df = pd.DataFrame(results)
   
    return df


# Function wrapper needed for multiprocessing
if __name__ ==  '__main__':
    if len(sys.argv) == 4:

        mode = str(sys.argv[1])
        sampling = str(sys.argv[2])
        factor = int(sys.argv[3])
        fids = range(1, 25)
        dims = [2, 3, 5, 10]
        iids = range(1, 6)

        cart_prod = itertools.product(*[fids, dims, iids])
        cart_prod = [x + (mode, sampling, factor,) for x in cart_prod]

        # Debug code:
        for experiment in cart_prod:
            run_experiment(experiment)
        
        with Pool(32) as p:
            results = p.map(run_experiment, cart_prod)

        # Calculate ERT for each problem x config
        data = pd.concat(results).reset_index(drop = True)

        os.makedirs(os.path.join(ROOT, 'data'), exist_ok = True)
        data.to_csv(os.path.join(ROOT, 'data', f'00_ela_features_{mode}_{sampling}_{factor}D.csv'), index = False)
        
    else:
        raise SyntaxError("Insufficient number of arguments passed")
