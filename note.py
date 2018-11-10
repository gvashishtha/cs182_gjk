"""
note.py
Implements the Note class from Note.m in page 102 of Ovans and Cercone (1990)

"""

import midi

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

class Note(object):
    def __init__(self, pitch):
        self.pitch = pitch

    def getPitch(self):
        return self.pitch

    def harmonic(self, other):
        interval = abs(self.pitch - other.getPitch())
        return ((interval == MINOR3RD) or
                (interval == MAJOR3RD) or
                (interval == FIFTH) or
                (interval == MINOR6TH) or
                (interval == MAJOR6TH) or
                (interval == OCTAVE) or
                (interval == MINOR10TH) or
                (interval == MAJOR10TH) or
                (interval == TWELFTH))

    def perfectHarmonic(self, other):
        interval = abs(self.pitch - other.getPitch())
        return ((interval == UNISON) or
                (interval == FIFTH) or
                (interval == OCTAVE) or
                (interval == TWELFTH))

    # TODO: add the rest of the constraints


def compile_notes(notes_list):
    """
    Takes in a list of Note objects and returns a playable midi track

    example use of midi library defined here:
    https://github.com/vishnubob/python-midi

    Follow installation instructions from Github readme to use.
    """
    pattern = midi.Pattern()
    track = midi.Track()
    pattern.append(track)
    for note in notes_list:
        on = midi.NoteOnEvent(tick = 0, velocity=20, pitch = note.getPitch())
        track.append(on)
        off = midi.NoteOffEvent(tick = 100, pitch = note.getPitch())
        track.append(off)
    eot = midi.EndOfTrackEvent(tick=1)
    track.append(eot)
    midi.write_midifile("example.mid", pattern)

# TODO: create/import helper function to convert human-readable pitches to MIDI
G = [Note(43)]
A = [Note(45)]
B = [Note(47)]
compile_notes(G + A + B)
