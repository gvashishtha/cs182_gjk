"""
note.py
Implements the Note class from Note.m in page 102 of Ovans and Cercone (1990)

"""

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

    def __repr__(self):
        return ('<Note pitch: {}>'.format(self.pitch))

    def getPitch(self):
        return self.pitch

    @staticmethod
    def harmonic(self, other):
        interval = abs(self.pitch - other.getPitch())
        print ('interval between {} and {} is {}'.format(self, other, interval))
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
