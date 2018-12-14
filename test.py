from main import main as generate_music
from optparse import Values
import os
import timeit


# Number of bars to test
bars_range = [4, 8, 12, 24]
# Number of trials for each bar number
num_trials = 4
# Directory to write midi test files
test_dir = 'tests/'

if not os.path.exists(test_dir):
    os.makedirs(test_dir)

# Insert column headers for dfs trials info
with open('dfs_trial_info.csv', 'w+') as f:
    f.write('bars,nodes expanded,backtracks,runtime\n')
f.closed

# Insert column headers for simulated annealing trials info
with open('simulated_annealing_trial_info.csv', 'w+') as f:
    f.write('bars,cost,iterations,runtime\n')
f.closed

def file_name_generator(type, num_bars, trial_num):
    return type + str(num_bars) + '_bars_trial_' + str(trial_num) + '.mid'

# Generate composition with specified parameters. Returns runtime in seconds
def test_generation(num_bars, cantus_file, solution_file, sa_file, test_dir):
    options = Values()
    options.preset_song = ''
    options.num_bars = num_bars
    options.cantus_file = cantus_file
    options.solution_file = solution_file
    options.sa_file = sa_file
    options.test_dir = test_dir
    options.testing = True
    options.arc_consistency = True

    start = timeit.default_timer()
    returned_csp = generate_music(options=options)
    if returned_csp is not None:
        assert(returned_csp.getCost(returned_csp.one_sol)==0)
    stop = timeit.default_timer()
    return stop - start

print('Bars range:' + str(bars_range))
print(str(num_trials) + ' trials')
print('Midi location: ' + test_dir)

for num_bars in bars_range:
  print('\n##### Generating ' + str(num_bars) + ' bar compositions #####')
  for i in range(num_trials):
    print('TRIAL ' + str(i) + ':')
    cantus_file = 'cantus_firmus_{}_bars_trial_{}.mid'.format(num_bars, i)
    solution_file = 'solution_{}_bars_trial_{}.mid'.format(num_bars, i)
    sa_file = 'simulated_annealing_{}_bars_trial_{}.mid'.format(num_bars, i)
    runtime = test_generation(num_bars, cantus_file, solution_file, sa_file, test_dir)
    print('\nCompleted in ' + str(runtime) + ' seconds\n')
