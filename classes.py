from notefunctions import *
from mingus.core import progressions, keys
from mingus.containers import Track, Note
from mingus.midi import fluidsynth
from kivy.event import EventDispatcher
from time import sleep

SYLL = ['do', 'di', 're', 'me', 'mi', 'fa', 'fi', 'so', 'le', 'la', 'te', 'ti']
SF2 = 'sf/piano.sf2'


class drilloptions:
    '''Holds all the drill options read from the yaml file.'''
    def __init__(self, drills=None):
        self.nam = drills['name']
        self.des = drills['desc']
        self.dir = drills['direction']
        self.mod = drills['modes']
        self.ton = drills['tonic']
        self.deg = drills['degrees']
        self.ran = drills['range']
        self.con = drills['context']
        self.har = drills['harmony']
        self.len = drills['length']
        self.bpm = drills['bpm']
        self.dur = drills['duration']
        self.sou = drills['sound']

class drill(EventDispatcher):
    '''The drill class. Takes a number of parameters and repeatedly
    instantiates Exercise() randomly within those parameters and plays it'''
    def __init__(self, opt):
        self.halted = False
        #self.register_event_type('on_answer')
        self.ex = None
        self.opt = opt
        self.answer = ''

    #def on_answer(self,*args):
    #    pass

    def run(self,a):
        '''Starts the drill loop to produce Exercise() instances.'''
        self.halted = False
        try:
            #We should not just assume alsa.
            fluidsynth.init(SF2, 'alsa')
        except:
            print("Could not initiate Fluidsynth. Aborting.")
            sys.exit(1)
        #These instructions shouldn't be in every drill by default. Perhaps add
        #an instruction field to the yaml file.
        #print('''\n\tINSTRUCTIONS
#You will hear a sequence of chords, then a single tone. Respond with the
#movable do solfege syllable corresponding to the tone. After a brief response
#window, the correct syllable will be displayed.\n\nDo not attempt to refer to familiar melodies in your head, or intellectualize in any way. Blindly guess if you have no idea, and keep listening.  Gradually, you will "just know".\nHave fun.\n''')
        #raw_input('Press ENTER to continue...\n')

        while not self.halted:
            key = pickkey(self.opt.ton, self.opt.mod)
            cadence = pickcadence(self.opt.con)
            prompt = promptmaker(self.opt.har, self.opt.len, self.opt.deg,
                    self.opt.ran, self.opt.ton) 
            
            self.ex = Exercise(self.opt.dir, cadence, key, prompt)
            self.ex.play(self.opt.bpm)
           
            sleep(90 / self.opt.bpm)

            self.answer = '\n'.join(
                    [ ','.join(i) for i in self.ex.answer() ] )

            a.value = self.answer
            #self.dispatch('on_answer', self.answer)

            sleep(2)

            a.value, self.answer = '', ''
            #self.dispatch('on_answer', self.answer)


            

    def halt(self):
        '''Halts the drill and goes back to the previous screen.'''
        #this is intended to be called by a button press event. Such a button
        #press shouldn't have to wait for the current audio to finish, so this
        #should also call something like self.ex.stop(), which doesn't exist
        #yet
        self.halted = True
        self.ex.stop()
        
class Exercise:
    '''a class describing musically the exercise'''
    def __init__(self,direction,context,key,prompt):
        self.direction = direction
        self.context = Context(context)
        self.prompt = prompt
        self.key = key
        self.track = Track()
        self.response = None

    def Track(self):
        '''puts together the context and the prompt with appropriate rests and
        forms a mingus track object'''
        q_track = Track()
        chords = self.context.Instantiate(self.key)
        
        for chord in chords:
            q_track.add_notes(chord,4)

        if self.direction:
            q_track.add_notes(None,4)
        else:
            q_track.add_notes(None,2)

        for note in self.prompt:
            q_track.add_notes(note,4)

        if not self.direction:
            q_track.add_notes(None,2)
        else:
            q_track.add_notes(None,4)

        self.track = q_track

        return q_track

    def play(self,bpm=60):
        '''Plays exercise through fluidsynth'''
        self.Track()
        fluidsynth.play_Track(self.track,1,bpm)

    def stop(self):
        fluidsynth.stop_everything()

    def answer(self):
        '''Returns the correct answer to the question as a list, empty if the
        question is a reproduction exercise.'''
        if self.direction:
            global SYLL
            tonic = Note()
            tonic.set_note(keys.get_notes(self.key)[0])
            diff = [ [ int(i) - int(tonic) for i in j ] for j in self.prompt ]
            return [ [ SYLL[i % 12] for i in j ] for j in diff ]

    def result(self):
        "reports the results to the stats db"
        pass

class Context:
    '''This probably doesn't deserve to be a class, it's only used as a
    function, taking a chord progression in roman numeral notation and
    returning an actual voicing. However, if there's a possibility of having
    contexts other than generated chord sequences in the future, keeping things
    modular might be convenient.'''
    def __init__(self,elements=[]):
        self.elements = elements

    def Length(self):
        "Returns the number of objects in the context."
        return len(self.elements)

    def Instantiate(self,key):
        "Takes key as an input and instantiates the context to that key"
        chords = progressions.to_chords(self.elements,key)
        return voiceLead(chords)

