from note import Note, write_solution
from optparse import OptionParser
from util import Constraint, Constraint3, Csp, Link, Variable
import copy
import logging
import midi
import random
import sys
import timeit

# ensure repeatability
random.seed(5)
NUM_BARS = 4
NOTE_RANGE = [45, 47, 48, 50, 52, 53, 55, 57, 59, 60, 62, 64, 65, 67, 69]

def main(options=None):
    num_bars = options.num_bars
    cantus_file = options.cantus_file
    solution_file = options.solution_file
    sa_file = options.sa_file

    test_dir = options.test_dir
    testing = options.testing
    dfs_csv = options.dfs_csv
    sa_csv = options.sa_csv

    song_list = ['mary', 'ariana', 'shootingstar']

    arc_consistency = options.arc_consistency
    extra_harmonic = options.extra_harmonic

    if options.preset_song in song_list:
        print 'options.preset_song is {}'.format(options.preset_song)
    elif options.preset_song != '':
    	print 'preset song not found, proceeding with default'

    csp = Csp()
    cp = [] # list of counterpoint variables
    cf = [] # list of __ variables
    binary = [] # list of Constraint objects

    if options.preset_song == song_list[0]:
    	note_list = [64, 62, 60, 62, 64, 64, 64, 62, 62, 62, 64, 67, 67, 64, 62, \
					60, 62, 64, 64, 64, 64, 62, 62, 64, 62, 60]
    	num_bars = len(note_list)
    elif options.preset_song == song_list[1]:
    	num_bars = 8
    	note_list = [69, 67, 66, 67, 66, 64, 66, 64]
    elif options.preset_song == song_list[2]:
    	num_bars = 10
    	note_list = [71, 71, 72, 67, 64, 71, 71, 72, 67, 64]
    elif testing:
        print('Generating a cantus firmus over ' + str(num_bars) + ' bars')
        note_list = []
        for i in range(num_bars):
            note_list.append(random.choice(NOTE_RANGE))
    else:
        note_list = [57,60,59,57] # default

    for i in range(num_bars):
        cp.append(Variable('cp' + str(i)))
        csp.addToVariables(cp[i])
        binary.append(Constraint())
        binary[i].setVariable(cp[i])

        cf.append(Variable('cf' + str(i)))
        csp.addToVariables(cf[i])

    for i in range(len(note_list)):
        note = Note(note_list[i])
        cf[i].addToDomain(note)

    print('Cantus firmus sequential note pitches: ')
    print(note_list)

    for i in range(num_bars):
        cp_note_list = range(30, 100)
        
        if i != (num_bars - 2):
            map(lambda x: cp[i].addToDomain(Note(x)), cp_note_list)
        else:
            cp_note_list = range(60, 70)
            map(lambda x: cp[i].addToDomain(Note(x)), cp_note_list)

    # binary constraints, p. 109 of Ovans
    for i in range(1, num_bars):
        L = Link()
        L.setNode(binary[i-1])
        L.setLabel(Note.melodic)
        cp[i].addToNeighbors(L)

        L = Link()
        L.setNode(binary[i])
        L.setLabel(Note.melodic)
        cp[i-1].addToNeighbors(L)

        """# extra constraint!!!!
        if extra_harmonic and i != num_bars - 1:
		    L = Link()
		    L.setNode(binary[i+1])
		    L.setLabel(Note.harmonic)
		    cp[i].addToNeighbors(L)"""

    L = Link()
    L.setNode(binary[0])
    L.setLabel(Note.perfectCfHarmonic)
    cf[0].addToNeighbors(L)

    # harmonic constraints for each cantus firmus note
    for i in range(1, num_bars-2):
        L = Link()
        L.setNode(binary[i])
        L.setLabel(Note.harmonic)
        cf[i].addToNeighbors(L)

    # perfect harmonic constraints in last two bars
    for i in range(num_bars-2, num_bars):
        L = Link()
        L.setNode(binary[i])
        L.setLabel(Note.perfectHarmonic)
        cf[i].addToNeighbors(L)

    test_csp = copy.deepcopy(csp)

    if arc_consistency:
        arc_start = timeit.default_timer()
        if csp.AC3():
            arc_stop = timeit.default_timer()
            print 'Made initial arcs consistent in {} seconds.'.format(arc_stop - arc_start)
            print 'Arc consistent - looking for a solution with DFS'

            sol_start = timeit.default_timer()
            csp.backtracking_search()
            sol_stop = timeit.default_timer()

            print('Trying simulated annealing...')
            sim_start = timeit.default_timer()
            test_csp.simAnnealing()
            sim_stop = timeit.default_timer()
            print 'Completed simulated annealing after {} seconds.'.format(sim_stop - sim_start)
            print 'Simulated annealing returns with cost {}, after {} iterations.'.format(test_csp.getCost(test_csp.vars), test_csp.iters)
        else:
            arc_stop = timeit.default_timer()
            print 'Failed to make initial arcs consistent after {} seconds.'.format(arc_stop - arc_start)
            print('Not consistent')
            return None
    else:
        sol_start = timeit.default_timer()
        csp.backtracking_search()
        sol_stop = timeit.default_timer()
        print('Attempt to find a DFS solution finished after {} seconds.'.format(sol_stop - sol_start))

        print('Trying simulated annealing...')
        sim_start = timeit.default_timer()
        test_csp.simAnnealing()
        sim_stop = timeit.default_timer()
        print 'Completed simulated annealing after {} seconds.'.format(sim_stop - sim_start)
        print 'Simulated annealing returns with cost {}, after {} iterations.'.format(test_csp.getCost(test_csp.vars), test_csp.iters)
        print('Looking for a solution with DFS')

    if csp.one_sol is not None:
        print('Found a solution with arc consistency! Expanded {} nodes with {} backtracks'.format(csp.getNodes(), csp.getBts()))

        # Log stats in csv file for testing
        if testing:
            dfs_trial_info = '{},{},{},{}\n'.format(num_bars, csp.getNodes(), csp.getBts(), sol_stop - sol_start)
            with open(dfs_csv, 'a+') as f:
                f.write(dfs_trial_info)
            f.closed
    else:
        print('No solution found')
        return None

    write_solution(csp.one_sol, num_bars=num_bars, solution_file=test_dir + '/' + solution_file)
    if test_csp.getCost(test_csp.vars) == 0:
        write_solution(test_csp.vars, num_bars=num_bars,solution_file=test_dir + '/' + sa_file)

        # Log stats in csv file for testing
        if testing:
            sim_trial_info = '{},{},{},{}\n'.format(num_bars, test_csp.getCost(test_csp.vars), test_csp.iters, sim_stop - sim_start)
            with open(sa_csv, 'a+') as f:
                f.write(sim_trial_info)
            f.closed
    else:
        print('Simulated annealing failed, not writing to output')
    if testing:
        return csp

def configure_logging(loglevel):
    numeric_level = getattr(logging, loglevel.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: %s' % loglevel)

    root_logger = logging.getLogger('')
    strm_out = logging.StreamHandler(sys.__stdout__)
    strm_out.setFormatter(logging.Formatter('%(message)s'))
    root_logger.setLevel(numeric_level)
    root_logger.addHandler(strm_out)

def read_options(args):
    usage_msg = "Usage:  %prog [options]"
    parser = OptionParser(usage=usage_msg)

    def usage(msg):
        print "Error: %s\n" % msg
        parser.print_help()
        sys.exit()

    parser.add_option("--loglevel",
                      dest="loglevel", default="info",
                      help="Set the logging level: 'debug' or 'info'")

    parser.add_option("--num_bars",
                      dest="num_bars", default=4, type="int",
                      help="How long is the song?")

    parser.add_option("--cantus_file",
                      dest="cantus_file", default='cantus_firmus.mid', type="string",
                      help="Cantus Firmus Filename")

    parser.add_option("--solution_file",
                      dest="solution_file", default='solution.mid', type="string",
                      help="Solution filename")

    parser.add_option("--sa_file",
                      dest="sa_file", default='simulated_annealing.mid', type="string",
                      help="Simulated annealing filename")

    parser.add_option("--dfs_csv",
                      dest="dfs_csv", default='dfs_trial_info.csv', type="string",
                      help="CSV file output for DFS testing stats")

    parser.add_option("--sa_csv",
                      dest="sa_csv", default='simulated_annealing_trial_info.csv', type="string",
                      help="CSV file output for simulated annealing testing stats")

    parser.add_option("--test_dir",
                      dest="test_dir", default='.', type="string",
                      help="Test directory")

    parser.add_option("--preset_song",
                      dest="preset_song", default='', type="string",
                      help="Set the preset song")

    parser.add_option("--nac3",
                      action="store_false", dest="arc_consistency", default=True)

    parser.add_option("--neh",
                      action="store_false", dest="extra_harmonic", default=True)

    parser.add_option("-t",
                      action="store_true", dest="testing", default=True)

    parser.add_option("-n",
                      action="store_false", dest="testing")

    (options, args) = parser.parse_args()
    configure_logging(options.loglevel)

    return main(options=options)


if __name__ == "__main__":
    read_options(sys.argv)
