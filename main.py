from util import Constraint, Constraint3, Csp, Link, Variable
from note import Note, write_solution
import copy
import random
import midi

# ensure repeatability
random.seed(5)
NUM_BARS = 4
NOTE_RANGE = [45, 47, 48, 50, 52, 53, 55, 57, 59, 60, 62, 64, 65, 67, 69]

def main(num_bars=NUM_BARS, cantus_file='cantus_firmus.mid',
            solution_file='solution.mid', sa_file='simulated_annealing.mid', test_dir='', testing=False):
    csp = Csp()
    cp = [] # list of counterpoint variables
    cf = [] # list of __ variables
    binary = [] # list of Constraint objects
    for i in range(num_bars):
        cp.append(Variable('cp' + str(i)))
        csp.addToVariables(cp[i])
        binary.append(Constraint())
        binary[i].setVariable(cp[i])

        cf.append(Variable('cf' + str(i)))
        csp.addToVariables(cf[i])

    if testing:
        print('Generating a cantus firmus over ' + str(num_bars) + ' bars')
        note_list = []
        for i in range(num_bars):
            note_list.append(random.choice(NOTE_RANGE))

    else:
        note_list = [57,60,59,57]

    for i in range(len(note_list)):
        note = Note(note_list[i])
        cf[i].addToDomain(note)

    print('Cantus firmus sequential note pitches: ')
    print(note_list)

    for i in range(num_bars):
        cp_note_list = [45, 47, 48, 50, 52, 53, 55, 57, 59, 60, 62, 64, 65, 67, 69]

        if i != (num_bars - 2):
            map(lambda x: cp[i].addToDomain(Note(x)), cp_note_list)
        else:
            cp_note_list = [56, 68]
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

    L = Link()
    L.setNode(binary[0])
    L.setLabel(Note.perfectCfHarmonic)
    cf[0].addToNeighbors(L)

    for i in range(1, num_bars-2):
        L = Link()
        L.setNode(binary[i])
        L.setLabel(Note.harmonic)
        cf[i].addToNeighbors(L)

    # no harmonic constraint 2nd to last bar
    L = Link()
    L.setNode(binary[num_bars - 1])
    L.setLabel(Note.perfectHarmonic)
    cf[num_bars-1].addToNeighbors(L)

    # the Ternary constraints ...
    # for i in range(0, num_bars - 2):
    #     ternary = Constraint3()
    #     ternary.setVariable(cp[i+1])
    #     ternary.setVariable2(cp[i+2])
    #     L = Link()
    #     L.setNode(ternary)
    #     L.setLabel(Note.skip)
    #     cp[i].addToNeighbors(L)
    #
    #     ternary = Constraint3()
    #     ternary.setVariable(cp[i])
    #     ternary.setVariable2(cp[i+2])
    #     L = Link()
    #     L.setNode(ternary)
    #     L.setLabel(Note.skipped)
    #     cp[i+1].addToNeighbors(L)
    #
    #     ternary = Constraint3()
    #     ternary.setVariable(cp[i])
    #     ternary.setVariable2(cp[i+1])
    #     L = Link()
    #     L.setNode(ternary)
    #     L.setLabel(Note.step)
    #     cp[i+2].addToNeighbors(L)

    if csp.AC3():
    #if csp.makeArcConsistent():
        print('Arc consistent - looking for a solution')
        csp.findASolution()
        print('Trying simulated annealing...')
        csp.simAnnealing()
        print 'Simulated annealing returns solution with cost {}, after {} iterations.'.format(csp.getCost(csp.vars), csp.iters)
    else:
        print('Not consistent')
        return None

    if csp.one_sol is not None:
        print('Found {} solutions with arc consistency! Expanded {} nodes with {} backtracks'.format(csp.getSol(), csp.getNodes(), csp.getBts()))
    else:
        print('No solution found')
        return None

    write_solution(csp.one_sol, num_bars=num_bars, solution_file=test_dir+solution_file)
    if csp.getCost(csp.vars) == 0:
        write_solution(csp.vars, num_bars=num_bars,solution_file=test_dir+sa_file)
    else:
        print('Simulated annealing failed, not writing to output')
    if testing:
        return csp

if __name__ == '__main__':
    main()
