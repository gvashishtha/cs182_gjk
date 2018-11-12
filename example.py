import midi
from note import Note

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
        on = midi.NoteOnEvent(tick=0, velocity=70, pitch=note.getPitch())
        track.append(on)
        off = midi.NoteOffEvent(tick=100, pitch=note.getPitch())
        track.append(off)
    eot = midi.EndOfTrackEvent(tick=1)
    track.append(eot)
    midi.write_midifile("example.mid", pattern)

note_list = [midi.G_3, midi.A_3, midi.B_3]
note_list = map(lambda x: Note(x), note_list)
print(note_list)
compile_notes(note_list)
