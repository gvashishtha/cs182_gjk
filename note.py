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
        return ((interval == MINOR3RD) or
                (interval == MAJOR3RD) or
                (interval == FIFTH) or
                (interval == MINOR6TH) or
                (interval == MAJOR6TH) or
                (interval == OCTAVE) or
                (interval == MINOR10TH) or
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
    @staticmethod
    def noThree(self, other, other2):
        self.checks += 1
        return (self.pitch != other.getPitch() or self.pitch != other2.getPitch())

    @staticmethod
    def skip(self, other, other2):
        self.checks += 1
        interval = abs(self.pitch-other.getPitch())
        if interval >= MINOR3RD:
            return ((abs(other.getPitch()-other2.getPitch()) <= MAJOR2ND) and self.noThree(self,other, other2))
        else:
            return self.noThree(self,other, other2)

    @staticmethod
    def skipped(self, other, other2):
        self.checks += 1
        interval = abs(self.pitch -other.getPitch())
        if interval >= MINOR3RD:
            return ((abs(self.pitch-other2.getPitch()) <= MAJOR2ND) and self.noThree(self, other, other2))
        else:
            return self.noThree(self, other, other2)

    @staticmethod
    def step(self, other, other2):
        self.checks += 1
        interval = abs(self.pitch - other2.getPitch())

        if interval <= MAJOR2ND:
            return self.noThree(self, other, other2)
        else:
            return ((abs(other.getPitch()-other2.getPitch()) < MINOR3RD) and self.noThree(self, other, other2))

    @staticmethod
    def perfect(self, x1, x2):
        interval = abs(x1-x2)

        return (interval == UNISON) or interval == FIFTH or interval == OCTAVE or INTERVAL == TWELFTH

    @staticmethod
    def noParallel(self, x2, x3, x4):
        self.checks += 2
        if (x2.getPitch()==x4.getPitch()): # no motion
            return True

        if ((abs(x4.getPitch()-x3.getPitch())==OCTAVE) and \
            ((abs(x4.getPitch() - x2.getPitch()) > MAJOR2ND) or\
             (abs(self.pitch - x3.getPitch()) > MAJOR2ND))):
             return False

        if (self.perfect(x4.getPitch(), x3.getPitch())):
            return ((float(self.pitch - x3.getPitch())/float(x2.getPitch()-x4.getPitch())) <= 0.0)
        else:
            return True

    @staticmethod
    def noPerfect(self, x2, x3, x4):
        self.checks += 2
        if (self.pitch == x2.getPitch()):
            return True

        if (abs(x4.getPitch()-self.pitch) == OCTAVE) and ((abs(x4.getPitch() - x3.getPitch()) > MAJOR2ND) or (abs(self.pitch - x2.getPitch()) > MAJOR2ND)):
             return False

        if (perfect(x4.getPitch(), self.pitch)):
            return (float(x4.getPitch()-x3.getPitch())/float(self.pitch-x2.getPitch())<= 0.0)
        else:
            return True

    def getChecks(self):
        return self.checks


    # TODO: add the rest of the constraints
