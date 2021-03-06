"""
note.py
Implements the Note class from Note.m in page 102 of Ovans and Cercone (1990)

"""
import midi
import random

UNISON = 0
MINOR2ND = 1
MAJOR2ND = 2
MINOR3RD = 3
MAJOR3RD = 4
FOURTH = 5
TRITONE = 6
FIFTH = 7
MINOR6TH = 8
MAJOR6TH = 9
OCTAVE = 12
MINOR10TH = 15
MAJOR10TH = 16
TWELFTH = 19

# ensure repeatability
random.seed(5)

def write_solution(one_sol, num_bars, solution_file, cp_chord=False, cf_chord=True, random_length=True):
    cp_pitches = []
    cf_pitches = []

    one_sol[1].domain[0].getPitch()
    for i in range(len(one_sol)):
        if i%2 == 0: # Note is from counterpoint
            base = one_sol[i].domain[0].getPitch()
            if cp_chord:
                cp_pitches.append([base, base+4, base+7])
            else:
                cp_pitches.append([one_sol[i].domain[0].getPitch() + OCTAVE*2])
        else: # Note is from the cantus firmus
            base = one_sol[i].domain[0].getPitch()
            if cf_chord:
                if i == num_bars*2 - 3:
                    cf_pitches.append([base, base-4, base-7, base-12])
                else:
                    cf_pitches.append([base, base-3, base-7, base-12])
            else:
                cf_pitches.append([base])
    # Helper function to add a note to a track
    def append_note(track, pitch, velocity=70):
        on = midi.NoteOnEvent(tick=0, velocity=velocity, pitch=pitch)
        track.append(on)
        off = midi.NoteOffEvent(tick=180, pitch=pitch)
        track.append(off)

    # Initialize MIDI variables
    pattern = midi.Pattern()
    track_cf = midi.Track()
    track_cp = midi.Track()
    pattern.append(track_cf)
    pattern.append(track_cp)

    notelengths = [60, 120, 180, 240]

    # Add all cantus firmus and counterpoint pitches to the track
    for i in range(num_bars):
        if random_length:
            length = random.choice(notelengths)
        else:
            length = 180
        for pitch in cf_pitches[i]:
            # Keep notes in the same chord at the same point
            on = midi.NoteOnEvent(tick=0, velocity=60, pitch=pitch)
            track_cf.append(on)
        off = midi.NoteOffEvent(tick=length, pitch=cf_pitches[i][0])
        track_cf.append(off)
        for pitch in cf_pitches[i][1:]:
            off = midi.NoteOffEvent(tick=0, pitch=pitch)
            track_cf.append(off)
        for pitch in cp_pitches[i]:
            on = midi.NoteOnEvent(tick=0, velocity=60, pitch=pitch)
            track_cp.append(on)
        off = midi.NoteOffEvent(tick=length, pitch = cp_pitches[i][0])
        track_cp.append(off)
        for pitch in cp_pitches[i][1:]:
            off = midi.NoteOffEvent(tick=0, pitch=pitch)
            track_cp.append(off)
        #cp_pitch = cp_pitches[i]
        #append_note(track_cp, cp_pitch, 60)
    eot = midi.EndOfTrackEvent(tick=1)
    track_cp.append(eot)
    track_cf.append(eot)

    midi.write_midifile(solution_file, pattern)

    #print('\nCantus firmus midi: ' + cantus_file)
    print('Solution midi: ' + solution_file)

class Note(object):
    def __init__(self, pitch):
        self.pitch = pitch
        self.checks = 0

    def __repr__(self):
        return ('<Note pitch: {}>'.format(self.pitch))

    def getPitch(self):
        return self.pitch

    @staticmethod
    def harmonic(self, other):
        self.checks += 1
        interval = abs(self.pitch - other.getPitch())
        #print ('interval between {} and {} is {}'.format(self, other, interval))
        return ((interval == MAJOR3RD) or
                (interval == FIFTH) or
                (interval == MAJOR6TH) or
                (interval == OCTAVE) or
                (interval == MAJOR10TH) or
                (interval == TWELFTH))

    @staticmethod
    def perfectHarmonic(self, other):
        self.checks += 1
        interval = abs(self.pitch - other.getPitch())
        return ((interval == UNISON) or
                (interval == FIFTH) or
                (interval == OCTAVE) or
                (interval == TWELFTH))

    @staticmethod
    def perfectCfHarmonic(self, other):
        self.checks += 1
        interval = abs(self.pitch -other.getPitch())
        if self.pitch > other.getPitch():
            return ((interval == UNISON) or (interval == OCTAVE))
        else:
            return ((interval == UNISON) or
                (interval == FIFTH) or
                (interval == OCTAVE) or
                (interval == TWELFTH))

    @staticmethod
    def melodic(self, other):
        self.checks += 1
        interval = abs(self.pitch - other.getPitch())
        return ((interval <= MINOR6TH) and interval != TRITONE)

    def getChecks(self):
        return self.checks


    # TODO: add the rest of the constraints
