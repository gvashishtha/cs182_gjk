from util import Constraint, Constraint3, Csp, Link, Variable
from note import Note
import midi

NUM_BARS = 4

def main():
    csp = Csp()
    cp = [] # list of counterpoint variables
    cf = [] # list of __ variables
    binary = [] # list of binary constraints
    for i in range(NUM_BARS):
        cp.append(Variable('cp' + str(i)))
        csp.addToVariables(cp[i])
        binary.append(Constraint())
        binary[i].setVariable(cp[i])

        cf.append(Variable('cf' + str(i)))
        csp.addToVariables(cf[i])

    # the cantus firmus
    note_list = [57, 60, 59, 57]

    #mary had a little lamb
    #note_list = [midi.E_2, midi.D_2, midi.C_2, midi.D_2, midi.E_2, midi.E_2, midi.E_2]

    for i in range(len(note_list)):
        note = Note(note_list[i])
        cf[i].addToDomain(note)

    for i in range(NUM_BARS):
        note_list = [45, 47, 48, 50, 52, 53, 55, 57, 59, 60, 62, 64, 65, 67, 69]

        # included major 3rd, minor 3rd, and fifth for all notes in Mary
        # https://en.wikipedia.org/wiki/Harmony#Intervals
        #note_list = [midi.Gs_2, midi.G_2, midi.B_2, midi.Fs_2, midi.F_2, midi.A_2, midi.E_2, midi.Fs_2, midi.G_2]
        #note_list = [45, 47, 60]
        if i != (NUM_BARS - 2):
            map(lambda x: cp[i].addToDomain(Note(x)), note_list)
        else:
            note_list = [56, 68]
            map(lambda x: cp[i].addToDomain(Note(x)), note_list)

    #print(csp.vars)



    # binary constraints, p. 109 of Ovans
    for i in range(1, NUM_BARS):
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

    for i in range(1, NUM_BARS-2):
        L = Link()
        L.setNode(binary[i-1])
        L.setLabel(Note.harmonic)
        #L.setLabel(lambda x, y: L.node.var.harmonic(y))
        cf[i].addToNeighbors(L)

    # no harmonic constraint 2nd to last bar
    L = Link()
    L.setNode(binary[NUM_BARS - 1])
    L.setLabel(Note.perfectHarmonic)
    #L.setLabel(lambda x: L.node.var.harmonic)
    cf[NUM_BARS-1].addToNeighbors(L)

    # the Ternary constraints ...
    for i in range(0,0): #, NUM_BARS - 2):
        ternary = Constraint3()
        ternary.setVariable(cp[i+1])
        ternary.setVariable2(cp[i+2])
        L = Link()
        L.setNode(ternary)
        L.setLabel(Note.skip)
        #L.setLabel(lambda x,y,z: Note.skip(x,y,z) and Note.step(x,y,z))
        cp[i].addToNeighbors(L)

        ternary = Constraint3()
        ternary.setVariable(cp[i])
        ternary.setVariable2(cp[i+2])
        L = Link()
        L.setNode(ternary)
        L.setLabel(Note.skipped)
        #L.setLabel(lambda x,y,z: Note.skipped(x,y,z) and Note.step(x,y,z))
        cp[i+1].addToNeighbors(L)

        ternary = Constraint3()
        ternary.setVariable(cp[i])
        ternary.setVariable2(cp[i+1])
        L = Link()
        L.setNode(ternary)
        L.setLabel(Note.step)
        #L.setLabel(lambda x,y,z: Note.step(x,y,z) and Note.skip(x,y,z))
        cp[i+2].addToNeighbors(L)

    if csp.makeArcConsistent():
        print('Consistent - looking for a solution')
        csp.findASolution()
    else:
        print('Not consistent')
        return

    print('Found {} solutions!'.format(csp.sol))

    def append_note(track, pitch):
        on = midi.NoteOnEvent(tick=0, velocity=70, pitch=pitch)
        track.append(on)
        off = midi.NoteOffEvent(tick=100, pitch=pitch)
        track.append(off)

    pattern = midi.Pattern()
    track_cf = midi.Track()
    track_cp = midi.Track()
    pattern.append(track_cf)
    pattern.append(track_cp)
    for i in range(NUM_BARS):
        cp_pitch = cp[i].domain[0].getPitch()
        cf_pitch = cf[i].domain[0].getPitch()
        append_note(track_cf, cf_pitch)
        append_note(track_cp, cp_pitch)
    eot = midi.EndOfTrackEvent(tick=1)
    track_cp.append(eot)
    track_cf.append(eot)
    midi.write_midifile("solution.mid", pattern)

    # for note in cp:
    #     print(note)


if __name__ == '__main__':
    main()
