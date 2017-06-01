from mingus.core import notes
from mingus.containers import Note
from math import ceil
from random import choice, sample
from decimal import Decimal

CADENCES = [
        ['I', 'IV', 'V', 'I'],
        ['I', 'IV', 'Vdom7', 'I'],
        ['I', 'V', 'I'],
        ['ii7', 'Vdom7', 'I']
        ]

#These describe the register within which the chord progressions will be
#voiced.
BASSREG = ['G-1', 'B-2']
UPPERREG = ['C-3', 'F-4']

def promptmaker(harmony, length, degrees, register, tonic):
    '''Creates a *length* long list of NoteContainer()'s from from scale
    degrees defined by *register* and *key*, each with *harmony*-note
    polyphony.'''
    #This if block is anticipating a future extension of *harmony* to allow
    #descriptive string values such as "diatonic second inversion triads",
    #which would be handled in the else block.
    if isinstance(harmony, int):
        shift = notes.note_to_int(tonic)
        pattern = [ sample(degrees, harmony) for i in range(length) ]
        pattern = [ [ Note(i + shift) for i in p ] for p in pattern ]
        prompt = notePlacer(pattern, register)
    
        return prompt
    
    else:
        return None

def voiceLead(unledChords):
    '''Takes a chord sequence as a list of NoteContainer()'s and tries to voice
    it with better-than-terrible voice-leading'''
    global BASSREG, UPPERREG
    #We call list(list) to avoid editing the input argument in place.
    chords = list(unledChords)
    
    #The following loops are messy, at least some of them could be iterated
    #over members of the list instead of running indices over range(len(())
    #constructions.

    #First make sure everything is in four parts:
    for i in range(len(chords)): 
        chords[i] = fourPart(chords[i])
    
    #Copy the base notes of each chord into a new double list:
    ledChords = [ [ noteFitter(chords[i][0],BASSREG) ] for i in range(len(chords)) ]

    #Remove the already copied bass notes from the original:
    for chord in chords:
        chord.pop(0)

    #Fit the notes of the first chord into the desired range:
    for i in range(len(chords[0])):
        chords[0][i] = noteFitter(chords[0][i],UPPERREG)
        ledChords[0].append(chords[0][i])

    '''For each remaining chord in the original list, compare with the previous
    chord for common tones, keep them the same'''
    #iterate from the second chord to the end
    for k in range(1,len(chords)):
        #these two iterate over all note pairs between the k-th chord and the
        #(k-1)-th
        for i in range(len(chords[k-1])):
            for j in range(len(chords[k])):
                a = Note(chords[k-1][i])
                b = Note(chords[k][j])
                #check if the notes are the same, ingoring octaves
                if (a.name == b.name):
                    #if they are, make sure the second one is in exactly the
                    #same octave
                    chords[k][j] = chords[k-1][i]
        #Fit all the chords to the required register. The already handled notes
        #can't break, because they are already in the correct range by
        #induction.
        for i in range(len(chords[k])):
            chords[k][i] = noteFitter(chords[k][i],UPPERREG)
            ledChords[k].append(chords[k][i])

    chords = ledChords
    return chords

def noteFitter(note, register):
    '''Takes a note, and if it lies outside a specified register, displaces it
    a number of octaves so it falls inside the register.'''
    n = Note(note)
    low = Note(register[0])
    high = Note(register[1])
    while n < low:
        n.octave_up()
    while n > high:
        n.octave_down()
    return n

def notePlacer(notecnt, register):
    '''Takes a note, and randomly chooses an octave displacement that fall in
    the given register. This is different from noteFitter, the latter displaces
    notes just enough, so for instance a note could never end up in the middle
    octave of a three octave range'''
    #This is intended to operate on prompts, which are lists of lists.

    #We convert each note to the numerical representation.
    a, b = [ Decimal(int(Note(note))) for note in register ]
    numbers = [ [ int(i) for i in note ] for note in notecnt ]
    #We collapse all the numbers to an ordinary list so we can pick the
    #greatest and smallest numbers easily.
    flat = [ int(i) for num in numbers for i in num ]
    flat.sort()
    
    m, n = Decimal(flat[0]), Decimal(flat[-1])
    interval = range(int(ceil((a-m)/12)), int(ceil((b-n)/12)))
    k = choice(interval)
    
    placed = [ [ Note(int(i) + 12 * k) for i in num ] for num in numbers ] 

    return placed
    
def fourPart(chord):
    '''Takes a chord, and if it has three parts, doubles the bass an octave
    above'''
    fpchord = list(chord)
    a = len(fpchord)
    if a < 3 or a > 4:
        print('''Something's wrong. fourPart() was handed a list of unexpected
                length''')
        exit()
    elif a == 3:
        n = Note(fpchord[0])
        n.octave_up()
        fpchord.append(n)
    return fpchord

def noteify(chords):
    '''Mingus has two different representations of notes. One is only a pitch
    class, like  'C', the other, Note() is octave specific, like 'C-4'. This
    converts the former to the latter so we have control over octave
    displacements.'''
    cds = [ [ Note(chords[i][j]) for j in range(len(chords[i])) ] for i in
            range(len(chords)) ]
    return cds

def pickkey(tonic, mode):
    '''Combines the tonic and the mode into a key'''
    both = [tonic,tonic.lower()]
    some = [ both[i] for i in mode ]   

    return choice(some)

def pickcadence(progs):
    '''Picks a cadence at random from a pool of available options.'''
    pool = [ CADENCES[i] for i in progs ]
    context = choice(pool)
    return context
