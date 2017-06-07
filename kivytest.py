from kivy.app import App
from kivy.lang import Builder
from kivy.uix.widget import Widget
from kivy.lang import Builder
from kivy.vector import Vector
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.recycleview import RecycleView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.behaviors import ButtonBehavior
from kivy.config import Config
from kivy.properties import ListProperty, StringProperty
from kivy.graphics import Color, Rectangle, Ellipse
from classes import *
from multiprocessing import Process
from functools import partial
from math import sin, cos, radians
from colorsys import hls_to_rgb
import yaml

Config.set('graphics', 'width', '400')
Config.set('graphics', 'height', '700')

from kivy.core.window import Window
Window.clearcolor = (1, 1, 1, 1)

RB = '''
<CButton>:
    text: 'bla'
    font_name: 'font/LibreBaskerville-Bold.ttf'
    font_size: self.height * 0.35
    color: 0,0,0,1
    canvas.before:
        Color:
            rgba: self.btn_color
        Ellipse:
            pos: self.pos
            size: self.size
        Color:
            rgba: 0,0,0,1
        Line:
            ellipse: self.pos[0], self.pos[1], self.size[0], self.size[1]
            width: self.height * 0.01
'''

Builder.load_string(RB)


class CButton(ButtonBehavior, Label):
    btn_color = ListProperty()
    def __init__(self,**kwargs):
        self.btn_color = kwargs['btn_color']
        super(CButton, self).__init__(**kwargs)
        self.text = kwargs['text']
    def collide_point(self, x, y):
        return Vector(x, y).distance(self.center) <= self.width / 2

class Welcome(Screen):
    pass

class Builtin(Screen):
    pass

class DrillScreen(Screen):
    answer = StringProperty('')
    def __init__(self, **kwargs):
        self.thedrill = drill(kwargs['options'])
        self.thedrill.bind(on_answer = self.printtest)
        self.worker = Process(target=self.thedrill.run)
        super(DrillScreen, self).__init__(**kwargs)
        self.answer = self.thedrill.answer
        for i in self.thedrill.opt.deg:
            x = 0.5 + 0.37 * cos(radians(90 - 30*i))
            y = 0.5 + 0.37 * sin(radians(90 - 30*i))
            c = list(hls_to_rgb(0.28 + (7.0 * i) / 12, 0.6, 1))
            c.append(1)

            b = CButton(
                    text = SYLL[i],
                    btn_color = c,
                    size_hint = [ 0.16, 0.16 ],
                    pos_hint = {'center_x':x,'center_y':y},
                    background_color = c)
            b.bind(on_release = self.printtest)
            self.ids.wheelbox.add_widget(b)

    def printtest(self,*args):
        self.answer = self.thedrill.answer
        print('This is printtest(): ', self.ids.answerlabel.text)

    def startdrill(self):
        if not self.worker.is_alive():
            self.worker.start()
        else:
            #self.worker.terminate() doesn't work here
            pass

    def stopdrill(self):
        self.worker.stop()

    def leave(self):
        self.worker.join()
        app = App.get_running_app()
        app.root.add_widget(drillscreen)
        app.root.current = 'builtin'




class BuiltinView(RecycleView):
    def __init__(self, **kwargs):
        super(BuiltinView, self).__init__(**kwargs)

        with open('builtin.yaml', 'r') as builtin:
            self.drills = yaml.load(builtin)

        self.data = [ {'text': self.drills[i]['name'],
            'on_release': self.startermaker(i)}
            for i in sorted(self.drills.keys()) ]
    
    def startermaker(self,num):
        def startdrill():
            drillscreen = DrillScreen(
                    name = 'drill',
                    options = drilloptions(self.drills[num]))

            app = App.get_running_app()
            app.root.add_widget(drillscreen)
            app.root.current = 'drill'

        return startdrill


class Manager(ScreenManager):
    pass

class TestingApp(App):
    #def build(self):
    #    return Manager()
    pass

TestingApp().run()
