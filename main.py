from util import Constraint, Constraint3, Csp, Link, Variable
from note import Note
import random
import midi

# ensure repeatability
random.seed(5)
NUM_BARS = 12
NOTE_RANGE = [45, 47, 48, 50, 52, 53, 55, 57, 59, 60, 62, 64, 65, 67, 69]

def main(num_bars=NUM_BARS, cantus_file='cantus_firmus.mid',
            solution_file='solution.mid', testing=True):
    csp = Csp()
    cp = [] # list of counterpoint variables
    cf = [] # list of __ variables
    binary = [] # list of binary constraints
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
            note_list.append(random.sample(NOTE_RANGE, 1)[0])
    else:
        note_list = [57,60,59,57]

    for i in range(len(note_list)):
        note = Note(note_list[i])
        cf[i].addToDomain(note)

    print('Cantus firmus sequential note pitches: ')
    print(note_list)

    for i in range(num_bars):
        note_list = [45, 47, 48, 50, 52, 53, 55, 57, 59, 60, 62, 64, 65, 67, 69]

        if i != (num_bars - 2):
            map(lambda x: cp[i].addToDomain(Note(x)), note_list)
        else:
            note_list = [56, 68]
            map(lambda x: cp[i].addToDomain(Note(x)), note_list)

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
    for i in range(0, num_bars - 2):
        ternary = Constraint3()
        ternary.setVariable(cp[i+1])
        ternary.setVariable2(cp[i+2])
        L = Link()
        L.setNode(ternary)
        L.setLabel(Note.skip)
        cp[i].addToNeighbors(L)

        ternary = Constraint3()
        ternary.setVariable(cp[i])
        ternary.setVariable2(cp[i+2])
        L = Link()
        L.setNode(ternary)
        L.setLabel(Note.skipped)
        cp[i+1].addToNeighbors(L)

        ternary = Constraint3()
        ternary.setVariable(cp[i])
        ternary.setVariable2(cp[i+1])
        L = Link()
        L.setNode(ternary)
        L.setLabel(Note.step)
        cp[i+2].addToNeighbors(L)

    if csp.makeArcConsistent():
        print('Arc consistent - looking for a solution')
        csp.findASolution()
    else:
        print('Not consistent')
        return

    print('Found {} solutions! Expanded {} nodes with {} backtracks'.format(csp.getSol(), csp.getNodes(), csp.getBts()))

    cp_pitches = []
    cf_pitches = []
    for i in range(len(csp.one_sol)):
        if i%2 == 0:
            cp_pitches.append(csp.one_sol[i].domain[0].getPitch())
        else:
            base = csp.one_sol[i].domain[0].getPitch()
            cf_pitches.append([base, base + 4, base + 7])


    def append_note(track, pitch, velocity=70):
        on = midi.NoteOnEvent(tick=0, velocity=velocity, pitch=pitch)
        track.append(on)
        off = midi.NoteOffEvent(tick=180, pitch=pitch)
        track.append(off)

    cantus_pattern = midi.Pattern()
    cantus_track = midi.Track()
    cantus_pattern.append(cantus_track)
    for i in range(num_bars):
        cantus_pitch = cf_pitches[i][0]
        append_note(cantus_track, cantus_pitch)

    pattern = midi.Pattern()
    pattern.make_ticks_abs()
    track_cf = midi.Track()
    track_cp = midi.Track()
    pattern.append(track_cf)
    pattern.append(track_cp)
    for i in range(num_bars):
        for pitch in cf_pitches[i]:
            on = midi.NoteOnEvent(tick=0, velocity=60, pitch=pitch)
            track_cf.append(on)
        for pitch in cf_pitches[i]:
            off = midi.NoteOffEvent(tick=60, pitch=pitch)
            track_cf.append(off)
        cp_pitch = cp_pitches[i]
        append_note(track_cp, cp_pitch, 60)
    eot = midi.EndOfTrackEvent(tick=1)
    track_cp.append(eot)
    track_cf.append(eot)

    cantus_track.append(eot)
    #midi.write_midifile(cantus_file, cantus_pattern)
    midi.write_midifile(solution_file, pattern)

    #print('\nCantus firmus midi: ' + cantus_file)
    print('Solution midi: ' + solution_file)

if __name__ == '__main__':
    main()
