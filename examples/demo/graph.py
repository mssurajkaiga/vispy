#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vispy: gallery 60

"""
Dynamic planar graph layout.
"""

import numpy as np
from vispy import gloo
from vispy import app
from vispy.gloo import set_viewport, set_state, clear
import markers

vs = """
attribute vec3 a_position;
attribute vec4 a_fg_color;
attribute vec4 a_bg_color;
attribute float a_size;
attribute float a_linewidth;

void main(){
    gl_Position = vec4(a_position, 1.);
}
"""

fs = """
void main(){
    gl_FragColor = vec4(0., 0., 0., 1.);
}
"""

n = 100
ne = 100
data = np.zeros(n, dtype=[('a_position', np.float32, 3),
                          ('a_fg_color', np.float32, 4),
                          ('a_bg_color', np.float32, 4),
                          ('a_size', np.float32, 1),
                          ('a_linewidth', np.float32, 1),
                          ])
edges = np.random.randint(size=(ne, 2), low=0, high=n).astype(np.uint32)
data['a_position'] = np.hstack((.25 * np.random.randn(n, 2), np.zeros((n, 1))))
data['a_fg_color'] = 0, 0, 0, 1
color = np.random.uniform(0.5, 1., (n, 3))
data['a_bg_color'] = np.hstack((color, np.ones((n, 1))))
data['a_size'] = np.random.randint(size=n, low=10, high=30)
data['a_linewidth'] = 2
u_antialias = 1


class Canvas(app.Canvas):

    def __init__(self, **kwargs):
        # Initialize the canvas for real
        app.Canvas.__init__(self, close_keys='escape', **kwargs)
        self.size = 512, 512
        self.position = 50, 50

        self.vbo = gloo.VertexBuffer(data)
        self.index = gloo.IndexBuffer(edges)
        self.view = np.eye(4, dtype=np.float32)
        self.model = np.eye(4, dtype=np.float32)
        self.projection = np.eye(4, dtype=np.float32)

        self.program = gloo.Program(markers.vert, markers.frag + markers.disc)
        self.program.bind(self.vbo)
        self.program['u_size'] = 1
        self.program['u_antialias'] = u_antialias
        self.program['u_model'] = self.model
        self.program['u_view'] = self.view
        self.program['u_projection'] = self.projection

        self.program_e = gloo.Program(vs, fs)
        self.program_e.bind(self.vbo)

        # self.timer = app.Timer(.01)
        # self.timer.connect(self.on_timer)
        # self.timer.start()

    def on_initialize(self, event):
        set_state(clear_color='white', depth_test=False, blend=True,
                  blend_func=('src_alpha', 'one_minus_src_alpha'))

    def on_key_press(self, event):
        if event.text == ' ':
            if self.timer.running:
                self.timer.stop()
            else:
                self.timer.start()

    def on_timer(self, event):
        self.update()

    def on_resize(self, event):
        width, height = event.size
        set_viewport(0, 0, width, height)

    def on_draw(self, event):
        clear(color=True, depth=True)
        self.program_e.draw('lines', self.index)
        self.program.draw('points')

if __name__ == '__main__':
    c = Canvas(title="Graph")
    c.show()
    app.run()
