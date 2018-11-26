from main import main as generate_music
import timeit


# Number of bars to test
bars_range = [4, 8, 12, 24]
# Number of trials for each bar number
num_trials = 4
# Directory to write midi test files
test_dir = 'tests/'

# Generate composition with specified parameters. Returns runtime in seconds
def test_generation(num_bars, cantus_file, solution_file):
  start = timeit.default_timer()
  generate_music(num_bars=num_bars, cantus_file=cantus_file, solution_file=solution_file)
  stop = timeit.default_timer()
  return stop - start

print('Bars range:' + str(bars_range))
print(str(num_trials) + ' trials')
print('Midi location: ' + test_dir)

for num_bars in bars_range:
  print('\n##### Generating ' + str(num_bars) + ' bar compositions #####')
  for i in range(num_trials):
    print('TRIAL ' + str(i) + ':')
    cantus_file = 'cantus_firmus_' + str(num_bars) + '_bars_trial_' + str(i) + '.mid'
    solution_file = 'solution_' + str(num_bars) + '_bars_trial_' + str(i) + '.mid'
    runtime = test_generation(num_bars, test_dir + cantus_file, test_dir + solution_file) 
    print('\nCompleted in ' + str(runtime) + ' seconds\n')
