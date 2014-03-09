# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from __future__ import division

from .. import gloo
from ..util import event


"""
API Issues to work out:

  * Need Visual.bounds() as described here:
    https://github.com/vispy/vispy/issues/141
    
  * Design of VisualComponent still needs a bit more direction..
    will see where to take it with more examples.

"""



# Commonly-used GL option groups.
GLOptions = {
    'opaque': {
        'GL_DEPTH_TEST': True,
        'GL_BLEND': False,
        #'GL_ALPHA_TEST': False,
        'GL_CULL_FACE': False,
    },
    'translucent': {
        'GL_DEPTH_TEST': True,
        'GL_BLEND': True,
        #'GL_ALPHA_TEST': False,
        'GL_CULL_FACE': False,
        'glBlendFunc': ('GL_SRC_ALPHA', 'GL_ONE_MINUS_SRC_ALPHA'),
    },
    'additive': {
        'GL_DEPTH_TEST': False,
        'GL_BLEND': True,
        #'GL_ALPHA_TEST': False,
        'GL_CULL_FACE': False,
        'glBlendFunc': ('GL_SRC_ALPHA', 'GL_ONE'),
    },
}    


class Visual(object):
    """ 
    Abstract class representing a drawable object. Visuals implement the 
    following interfaces:
    
        * paint() calls all of the GL commands necessary to paint the visual.
        * bounds() describes the bounding rectangle of the visual.
        * gl_options() is used to configure the OpenGL state immediately
          before the visual is painted.
          
    
    Events:
    
    update : Event
        Emitted when the visual has changed and needs to be repainted.
    bounds_change : Event
        Emitted when the bounding rectangle of the visual has changed.
    """
    def __init__(self):
        
        # Dict of {'GL_FLAG': bool} and {'glFunctionName': (args)} 
        # specifications. By default, these are enabled whenever the Visual 
        # if painted. This provides a simple way for the user to customize the
        # appearance of the Visual. Example:
        # 
        #     { 'GL_BLEND': True,
        #       'glBlendFunc': ('GL_SRC_ALPHA', 'GL_ONE') }
        # 
        self._gl_options = {}
        
        self.events = event.EmitterGroup(source=self,
                                         update=event.Event,
                                         bounds_change=event.Event)
    
    def paint(self):
        """
        Paint this visual now.
        
        The default implementation configures GL flags according to the contents
        of self._gl_options            
        
        """
        for name, val in self._gl_options.items():
            if isinstance(val, bool):
                flag = getattr(gloo.gl, name)
                if val:
                    gloo.gl.glEnable(flag)
                else:
                    gloo.gl.glDisable(flag)
            else:
                args = []
                for arg in val:
                    if isinstance(arg, str):
                        arg = getattr(gloo.gl, arg)
                    args.append(arg)
                func = getattr(gloo.gl, name)
                func(*args)

    def set_gl_options(self, default=None, **opts):
        """
        Set all GL options for this Visual. 
        Keyword arguments must be one of two formats:
        
        * GL_FLAG=bool
        * glFunctionName=(args)
        
        These options are invoked every time the Visual is drawn.
        Optionally, *default* gives the name of a pre-set collection of options
        from the GLOptions global.
        """
        if default is not None:
            opts = GLOptions[default]
        self._gl_options = opts
        
    def update_gl_options(self, default=None, **opts):
        """
        Update GL options rather than replacing all. See set_gl_options().
        
        Optionally, *default* gives the name of a pre-set collection of options
        from the GLOptions global.
        """
        if default is not None:
            opts = GLOptions[default]
        self._gl_options.update(opts)
        
    def gl_options(self):
        """
        Return a dict describing the GL options in use for this Visual. 
        See set_gl_options().
        """
        return self._gl_options.copy()


class VisualComponent(object):
    """
    Base for classes that encapsulate some modular component of a Visual.
    
    These define Functions for extending the shader code as well as an 
    activate() method that inserts these Functions into a program.
    
    VisualComponents may be considered friends of the Visual they are attached
    to; often they will need to access internal data structures of the Visual
    to make decisions about constructing shader components.
    """
    def __init__(self, visual=None):
        self._visual = None
        if visual is not None:
            self._attach(visual)
        
    @property
    def visual(self):
        """The Visual that this component is attached to."""
        return self._visual

    def _attach(self, visual):
        """Attach this component to a Visual. This should be called by the 
        Visual itself.
        """
        self._visual = visual

    def _detach(self):
        """Detach this component from its Visual.
        """
        self._visual = None
        
    def update(self):
        """
        Called by the Visual immediately before drawing; this method should be
        overridden to handle any changes to the visual that have teken place.
        """
        raise NotImplementedError
