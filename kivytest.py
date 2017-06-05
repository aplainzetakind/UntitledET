from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.recycleview import RecycleView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.config import Config
from classes import *
from multiprocessing import Process
import yaml
Config.set('graphics', 'width', '400')
Config.set('graphics', 'height', '700')

class Welcome(Screen):
    pass

class Builtin(Screen):
    pass

class DrillScreen(Screen):
    def __init__(self, **kwargs):
        super(DrillScreen, self).__init__(**kwargs)
        self.options = kwargs['options']
        self.desc = self.options.des
        self.thedrill = drill(self.options)
        desc = Label(
                text=self.options.des,
                size_hint_x=0.9,
                size_hint_y=1)
        button = Button(
                text = 'Start',
                size_hint=[0.4,0.1])
        button.bind(on_release=self.thedrill.run)
        self.add_widget(desc)
        self.add_widget(button)


class BuiltinView(RecycleView):
    def __init__(self, **kwargs):
        super(BuiltinView, self).__init__(**kwargs)
        with open('builtin.yaml', 'r') as builtin:
            self.drills = yaml.load(builtin)
        self.data = [ {'text': self.drills[i]['name'],
            'on_release': self.startermaker(i,self.drills[i])}
            for i in sorted(self.drills.keys()) ]
    
    def startermaker(self,num,options):
        def startdrill():
            options = drilloptions(self.drills[num])
            drillscreen = DrillScreen(name='drill', options=options)
            app = App.get_running_app()
            app.root.add_widget(drillscreen)
            app.root.current = 'drill'
            #drillscreen.thedrill.run()
        return startdrill


class Manager(ScreenManager):
    pass

class TestingApp(App):
    def build(self):
        return Manager()

TestingApp().run()
