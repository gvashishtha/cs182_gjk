from main import main as generate_music
from optparse import Values
import os
import timeit

# Number of bars to test
bars_range = [4, 8, 12, 24, 48]
# Number of trials for each bar number
num_trials = 20

# Initialize test output csv files for dfs and sa with headers
def create_csvs(dfs_csv, sa_csv):
    # Insert column headers for dfs trials info
    with open(dfs_csv, 'w+') as f:
        f.write('bars,nodes expanded,backtracks,runtime\n')
    f.closed

    # Insert column headers for simulated annealing trials info
    with open(sa_csv, 'w+') as f:
        f.write('bars,cost,iterations,runtime\n')
    f.closed

def file_name_generator(type, num_bars, trial_num):
    return type + str(num_bars) + '_bars_trial_' + str(trial_num) + '.mid'

# Generate composition with specified parameters. Returns runtime in seconds
def test_generation(num_bars, cantus_file, solution_file, sa_file, dfs_csv,
                        sa_csv, arc_consistency, extra_harmonic, test_dir):
    options = Values()
    options.testing = True
    options.test_dir = test_dir

    options.preset_song = ''
    options.num_bars = num_bars

    options.cantus_file = cantus_file
    options.solution_file = solution_file
    options.sa_file = sa_file

    options.dfs_csv = dfs_csv
    options.sa_csv = sa_csv

    options.arc_consistency = arc_consistency
    options.extra_harmonic = extra_harmonic

    start = timeit.default_timer()
    returned_csp = generate_music(options=options)
    if returned_csp is not None:
        assert(returned_csp.getCost(returned_csp.one_sol)==0)
    stop = timeit.default_timer()
    return stop - start


print('Bars range:' + str(bars_range))
print(str(num_trials) + ' trials')

extra_harmonic_options = [False, True]
arc_consistency_options = [False, True]

for eh_option in extra_harmonic_options:
    eh_flag = 'with_eh' if eh_option else 'without_eh'
    for ac_option in arc_consistency_options:
        ac_flag = 'with_ac' if ac_option else 'without_ac'

        test_dir = 'tests_{}_{}'.format(eh_flag, ac_flag)
        print('Midi location: ' + test_dir)
        if not os.path.exists(test_dir):
            os.makedirs(test_dir)

        dfs_csv = 'dfs_trial_info_{}_{}.csv'.format(eh_flag, ac_flag)
        sa_csv = 'sa_trial_info_{}_{}.csv'.format(eh_flag, ac_flag)

        create_csvs(dfs_csv, sa_csv)

        print('##### Testing {} extra harmonic constraint and {} arc consistency #####\n'.format(eh_flag.split('_')[0], ac_flag.split('_')[0]))
        for num_bars in bars_range:
            print('\n##### Generating ' + str(num_bars) + ' bar compositions #####')
            for i in range(num_trials):
                print('TRIAL ' + str(i) + ':')
                cantus_file = 'cantus_firmus_{}_bars_trial_{}.mid'.format(num_bars, i)
                solution_file = 'solution_{}_bars_trial_{}.mid'.format(num_bars, i)
                sa_file = 'simulated_annealing_{}_bars_trial_{}.mid'.format(num_bars, i)
                runtime = test_generation(num_bars, cantus_file, solution_file,
                    sa_file, dfs_csv, sa_csv, ac_option, eh_option, test_dir)
                print('\nCompleted in ' + str(runtime) + ' seconds\n')
