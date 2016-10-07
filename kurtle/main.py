# -*- coding: utf-8 -*-
# Kurtle
# Version: 0.1.0
# Copyright (C) 2016, KeyWeeUsr(Peter Badida) <keyweeusr@gmail.com>
# License: MIT, More info in LICENSE.txt

# [examples]
# star: 5x(line, right, 144, 150)
# circle: 72x(line, right, 5, 20)
# pointy circle: 80x{4x(line, right, 45, 50);(line, left, 145, 50)}
# four random circles:
#    1x{clear};
#    78x{(line, right, 60, 50);(line, left, 145, 50)};
#    74x{4x(line, right, 45, 50);(line, left, 145, 50)};
#    72x{9x(line, right, 45, 50);4x(line, left, 145, 150)};
#    6x{4x(line, right, 45, 50);(line, left, 145, 50)};
#    60x{10x(line, right, 45, 50);7x(line, left, 145, 50)};

from kivy.config import Config
Config.set('graphics', 'window_state', 'maximized')

from kivy.app import App
from kivy.utils import rgba
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.boxlayout import BoxLayout
from kivy.logger import Logger, LoggerHistory
from kivy.properties import ListProperty, NumericProperty, BooleanProperty
from kivy.graphics import Color, Point, Line, PushMatrix, PopMatrix, Rotate

import re
from random import randint
from os import linesep as sep
from functools import partial
from os.path import join, abspath, dirname
from math import sin, cos, radians, degrees


class Body(BoxLayout):
    plane_size = ListProperty([10000, 10000])
    old_point = ListProperty([5000, 5000])
    new_point = ListProperty([5000, 5000])
    old_angle = NumericProperty(0)
    default_x = default_y = 4992
    head = BooleanProperty(True)
    instructions = []
    history = []

    def __init__(self, **kwargs):
        super(Body, self).__init__(**kwargs)
        self.app = App.get_running_app()
        turtle = partial(Image, size_hint=[None, None], size=[16, 16],
                         pos=[self.default_x, self.default_y],
                         source=self.app.icon)
        self.turtle = turtle

    def help(self):
        help_str = (
            'Import a file with instructions:\n'
            '    import "path"\n\n'
            'Export instructions to a file:\n'
            '    export "path"\n\n'
            'Draw an instruction:\n'
            '    (type, direction, angle, length, color)\n\n'
            'Draw multiple times:\n'
            '    10x(type, direction, angle, length, color)\n\n'
        )
        con = Label(text=help_str)
        pop = Popup(title='Help', content=con, size_hint=[0.5, 0.5],
                    pos_hint={'center': 0.5})
        pop.open()

    def rotate_turtle(self, angle):
        '''nyi'''
        return
        angle = degrees(angle)
        turtle = self.ids.plane.children[0].children[0]
        with turtle.canvas.before:
            PushMatrix()
            Rotate(angle=angle,
                   axis=(0, 0, 1),
                   origin=turtle.center)
        with turtle.canvas:
            PopMatrix()

    def move_turtle(self, point):
        turtle = self.ids.plane.children[0].children[0]
        turtle.pos = [point[0] - turtle.size[0] / 2.0,
                      point[1] - turtle.size[1] / 2.0]

    def clear(self):
        self.old_point = [5000, 5000]
        self.new_point = [5000, 5000]
        self.old_angle = 0
        self.head = True
        plane = self.ids.plane
        plane.children[0].canvas.before.clear()
        plane.children[0].clear_widgets()
        plane.add_widget(self.turtle())

    def instr_export(self, path):
        if '/' in path:
            path = path.split('/')
        elif '\\' in path:
            path = path.split('\\')
        with open(path, 'w') as f:
            f.write('\n'.join(self.history))

    def instr_import(self, path):
        if '/' in path:
            path = path.split('/')
        elif '\\' in path:
            path = path.split('\\')
        with open(path) as f:
            lines = f.readlines()
        for line in lines:
            self.crun(line.strip(sep))

    def crun(self, command):
        times = 1

        # multiple multiplied sequences
        if '};' in command:
            self.command = command.split('};')
            for com in self.command:
                self.crun(com + '}')
            return

        # multiply sequences
        if '{' in command:
            where = command.find('{')
            times = int(command[:where - 1])
            command = command[where + 1:-1]
            for i in range(times):
                self.crun(command)
            return

        # parse sequence
        if ';' in command:
            self.command = command.split(';')
            for com in self.command:
                self.crun(com)
            return

        if 'import' in command:
            self.instr_import(command[8:-1])
            return
        elif 'export' in command:
            self.instr_export(command[8:-1])
            return

        # multiply command
        if 'x' in command:
            where = command.find('x')
            times = int(command[:where])
            command = command[where + 1:]

        if 'clear' in command:
            self.clear()

        match = re.findall(r'\((.*?)\)', command)
        if match:
            match = [m.strip() for m in match[0].split(',')]
            match = [m.replace("'", '') for m in match]
            for i in range(times):
                self.instructions.append(match)
        for instr in self.instructions:
            self.run(*instr)
        self.instructions = []

    def run(self, dtype=None, dir=None,
            angle=None, length=None, color=None):
        _angle = angle
        if ':' in ''.join([dtype, dir, angle]):
            Logger.info('Kurtle: No necessary parameters for Body.run')
            return

        try:
            angle = radians(float(angle)) if angle else self.old_angle
            length = float(length)
        except ValueError:
            Logger.exception('Kurtle: Invalid `angle` or `length` values')

        if color and color != 'random':
            try:
                rgba(color)
            except ValueError:
                Logger.exception('Kurtle: Invalid `color` value')
        elif color == 'random':
            r = randint
            color = '#' + '{}{}{}'.format(r(0, 255), r(0, 255), r(0, 255))
        else:
            color = '#FF0000'

        if dir == 'forward':
            angle = self.old_angle
            if self.head:
                x = self.old_point[0] + length * sin(angle)
                y = self.old_point[1] + length * cos(angle)
            else:
                x = self.old_point[0] - length * sin(angle)
                y = self.old_point[1] - length * cos(angle)
        elif dir == 'back':
            self.rotate_turtle(180)
            angle = self.old_angle
            if self.head:
                x = self.old_point[0] - length * sin(angle)
                y = self.old_point[1] - length * cos(angle)
            else:
                x = self.old_point[0] + length * sin(angle)
                y = self.old_point[1] + length * cos(angle)
            self.head = not self.head
        elif dir == 'left':
            self.rotate_turtle(angle)
            angle = self.old_angle - angle
            if self.head:
                x = self.old_point[0] + length * sin(angle)
                y = self.old_point[1] + length * cos(angle)
            else:
                x = self.old_point[0] - length * sin(angle)
                y = self.old_point[1] - length * cos(angle)
        elif dir == 'right':
            self.rotate_turtle(-angle)
            angle = self.old_angle + angle
            if self.head:
                x = self.old_point[0] + length * sin(angle)
                y = self.old_point[1] + length * cos(angle)
            else:
                x = self.old_point[0] - length * sin(angle)
                y = self.old_point[1] - length * cos(angle)

        self.new_point = [x, y]
        self.move_turtle(self.new_point)
        if dtype == 'point':
            drawcls = Point
        elif dtype == 'line':
            drawcls = Line
        else:
            return

        points = self.old_point + self.new_point
        self.old_point = self.new_point
        self.old_angle = angle
        with self.ids.plane.children[0].canvas.before:
            Color(rgba=rgba(color))
            drawcls(points=points)
        self.history.append(
            '({}, {}, {}, {}, {})'.format(dtype, dir, _angle, length, color)
        )


class Kurtle(App):
    path = abspath(dirname(__file__))
    icon = join(path, 'data', 'icon.png')

    def build(self):
        return Body()

if __name__ == '__main__':
    Kurtle().run()
