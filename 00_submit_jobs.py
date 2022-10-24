import os

TRANSFORMATIONS = ['no_trans', 'stan', 'norm']
SAMPLING = ['lhs', 'sobol']
BUDGET_FACTOR = [50, 100, 250, 500]

path = './templates/job_template.cmd'
out_path = './jobs/'

if not os.path.exists(out_path):
  os.makedirs(out_path)

def _create_job_files():
    with open(path, 'r') as input_:
        exp_file = str(input_.read())
        for trans in TRANSFORMATIONS:
            for sample in SAMPLING:
                for factor in BUDGET_FACTOR:
                    suffix = f'{trans}_{sample}_{factor}'
                    output = exp_file.replace('PLACEHOLDER_JOB_NAME', 'rpr_' + suffix)\
                                        .replace('PLACEHOLDER_ARGS', f'{trans} {sample} {factor}')
                    with open(os.path.join(out_path,suffix + '.cmd'), 'w') as out:
                        out.write(output)

def _submit_jobs():
    for trans in TRANSFORMATIONS:
        for sample in SAMPLING:
            for factor in BUDGET_FACTOR:
                suffix = f'{trans}_{sample}_{factor}'
                f_name = suffix + '.cmd'
                print(os.system('sbatch ' + os.path.join(out_path, f_name)))

if __name__ == '__main__':
    _create_job_files()
    _submit_jobs()
    