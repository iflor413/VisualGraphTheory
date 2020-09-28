from OpenGL.GL import *
from OpenGL.GLUT import *

import ctypes
import numpy as np
import math
from collections import deque

from .. import get_current_window
from . import GLObject, get_global_objects

golden = 1.6180339887

def inside_tiangle(verts, x, y):
    assert len(verts) == 3, 'Verticies must be composed of 3 2D-points.'
    
    def same_side(lp, p3):
        (x1, y1), (x2, y2) = lp
        x3, y3 = p3
        
        m = ((y2-y1 >= 0)*2-1)*10e10 if x2-x1 == 0 else (y2-y1)/(x2-x1)
        b = y1-m*x1
        
        return (y >= m*x+b) == (y3 >= m*x3+b)
    return (same_side((verts[0], verts[1]), verts[2]) and
            same_side((verts[1], verts[2]), verts[0]) and
            same_side((verts[2], verts[0]), verts[1]))

def inside(verts, x, y):
    for i in range(len(verts)-2):
        if inside_tiangle((verts[0], verts[i+1], verts[0] if i == len(verts)-2 else verts[i+2]), x, y):
            return True
    return False

def coord_to_theta(x, y):
    if x > 0 and y >= 0:
        theta = math.atan(y/x)
    elif x == 0 and y > 0:
        theta = math.pi/2
    elif x < 0 and y >= 0:
        theta = math.pi-math.atan(abs(y/x))
    elif x < 0 and y < 0:
        theta = math.pi+math.atan(abs(y/x))
    elif x == 0 and y < 0:
        theta = math.pi*3/2
    elif x > 0 and y < 0:
        theta = 2*math.pi-math.atan(abs(y/x))
    else: #if x == 0 and y == 0:
        theta = math.pi/2
    
    return theta

class GLText(GLObject):
    @property
    def text(self):
        return self._text
    
    @text.setter
    def text(self, value):
        self._text = value if value is None else str(value)
    
    def __init__(self, x, y, font=GLUT_BITMAP_HELVETICA_12, text=None, color3f=(0.0, 0.0, 0.0), name='Text', **kwargs):
        super(GLText, self).__init__(locked=True, name=name, **kwargs)
        
        self.x = x
        self.y = y
        
        self.font = font
        self._text = text
        
        self.color3f = color3f
    
    def render(self, window):
        if self.hidden or self._DELETED or self._text is None:
            return
        
        glColor3f(*self.color3f)
        glWindowPos2f(self.x-window.x_offset, self.y-window.y_offset)
        
        for ch in self._text:
            glutBitmapCharacter(self.font, ctypes.c_int(ord(ch)))

class GLObject2D(GLObject):
    def __init__(self, x, y, scale=1, theta=0, color3f=(1.0, 0.0, 3.0), name='2DObject', **kwargs):
        super(GLObject2D, self).__init__(name=name, **kwargs)
        
        self.x = x
        self.y = y
        
        self.scale = scale
        self.theta = theta
        
        self.color3f = color3f
        
    def transform_matrix(self, local_matrix):
        theta = self.theta/180*math.pi
        rot_matrix = np.array([[np.cos(self.theta), np.sin(self.theta)], [-np.sin(self.theta), np.cos(self.theta)]])
        
        return np.array([self.x, self.y])+self.scale*np.matmul(local_matrix, rot_matrix)
    
    def center(self, *objs):
        self.x, self.y = np.mean([[obj.x, obj.y] for obj in objs], axis=0)
    
    def is_inside(self, x, y):
        a = inside(self.transform_matrix(self.local_matrix()), x, y)
        return a
    
    def lookat(self, obj):
        self.theta = coord_to_theta(obj.x-self.x, obj.y-self.y)
    
    def local_matrix(self):
        raise NotImplementedError('Cannot call local_matrix() as a GLObject2D.')
    
    def render(self, window):
        if self.hidden or self._DELETED:
            return
        
        global_matrix = self.transform_matrix(self.local_matrix()) #transform matrix
        
        if window is not None and not self.hidden:
            self.detected = inside(global_matrix, window.Mouse.x, window.Mouse.y)
        
        glColor3f(*self.color3f)
        glBegin(GL_TRIANGLE_FAN)
        [glVertex2f(*coord) for coord in global_matrix] #draw verts
        glEnd()

class IsoTriangle(GLObject2D):
    def __init__(self, h, b, *args, name='IsoTriangle', **kwargs):
        super(IsoTriangle, self).__init__(name=name, *args, **kwargs)
        
        self.h = h
        self.b = b
    
    def local_matrix(self):
        return np.array([[-self.b/2, -self.h/2], [0, self.h/2], [self.b/2, -self.h/2]]) #establish shape

class Rectangle(GLObject2D):
    def __init__(self, h, w, *args, name='Rectangle', **kwargs):
        super(Rectangle, self).__init__(name=name, *args, **kwargs)
        
        self.h = h
        self.w = w
    
    def local_matrix(self):
        return np.array([[-self.w/2, -self.h/2], [self.w/2, -self.h/2], [self.w/2, self.h/2], [-self.w/2, self.h/2]]) #establish shape

class Circle(GLObject2D):
    def __init__(self, r, *args, edges=16, name='Circle', **kwargs):
        assert edges >= 3
        
        super(Circle, self).__init__(name=name, *args, **kwargs)
        
        self.r = r
        self.edges = edges
    
    def local_matrix(self):
        theta = np.arange(self.edges+1)*2*math.pi/self.edges
        return np.concatenate(([[0, 0]], self.r*np.stack((np.cos(theta), np.sin(theta)), axis=-1)))

class TextCircle(Circle):
    @property
    def text(self):
        return self._text
    
    def __init__(self, *args, font=GLUT_BITMAP_HELVETICA_12, text=None, text_color3f=(1.0, 0.0, 3.0), name='TextCircle', **kwargs):
        super(TextCircle, self).__init__(name=name, *args, **kwargs)
        
        self._text = GLText(0, 0, font=font, text=text, color3f=text_color3f, hidden=True)

    def render(self, window):
        super(TextCircle, self).render(window)
        
        self._text.hidden = self.hidden
        text = self._text.text
        if text is not None:
            self._text.x = self.x-12*len(text)/4
            self._text.y = self.y-12*len(text)/4
        
        self._text.render(window)

    def DELETE(self):
        self._text.DELETE()
        super(TextCircle, self).DELETE()

class SectionedSphere(GLObject2D):
    def __init__(self, inner_r, outer_r, separation, *args, sections=4, radial_vertices=4, name='SectionedSphere', **kwargs):
        assert sections >= 2
        super(SectionedSphere, self).__init__(name=name, *args, **kwargs)
        
        self.inner_r = inner_r
        self.outer_r = outer_r
        self.separation = separation
        self.sections = sections
        self.radial_vertices = radial_vertices
        
    def local_matrix(self):
        def coords(x, y):
            sectional_theta = 2*math.pi/self.sections
            is_outer = np.where(x<self.radial_vertices, 0, 1)
            
            r = np.where(is_outer, self.outer_r, self.inner_r)
            theta = sectional_theta*np.where(is_outer, self.radial_vertices*2-1-x, x)/(self.radial_vertices-1)
            
            return r*np.where(y%2==0, np.cos(theta), np.sin(theta))+self.separation/2
        
        return np.fromfunction(coords, (self.radial_vertices*2, 2))
    
    def render(self, window):
        if self.hidden or self._DELETED:
            return
        
        og_theta = self.theta
        
        detected = False
        for i in range(self.sections):
            self.theta = self.theta + 2*math.pi/self.sections
            global_matrix = self.transform_matrix(self.local_matrix()) #transform matrix
            
            if window is not None and not detected and not self.hidden:
                detected = inside(global_matrix, window.Mouse.x, window.Mouse.y)
            
            glColor3f(*self.color3f)
            glBegin(GL_TRIANGLE_FAN)
            [glVertex2f(*coord) for coord in global_matrix] #draw verts
            glEnd()
        
        self.detected = detected
        self.theta = og_theta

class ClassifierSectionedSphere(SectionedSphere):
    @property
    def text(self):
        return self._text
    
    @text.setter
    def text(self, new_text):
        if not isinstance(new_text, (list, tuple)):
            new_text = [new_text]
        assert isinstance(new_text, (list, tuple)) and len(new_text) <= self.sections
        
        self._text = new_text
    
    @property
    def sel_index(self):
        return self._sel_index
    
    @sel_index.setter
    def sel_index(self, value):
        assert value is None or (isinstance(value, int) and value < self.sections)
        self._sel_index = value
    
    def __init__(self, *args, text=[], sel_index=None, text_color3f=(0.0, 0.0, 0.0), sel_color3f=(0.5, 0.0, 2.5), name='ClassifierSectionedSphere', **kwargs):
        super(ClassifierSectionedSphere, self).__init__(name=name, *args, **kwargs)
        
        self._text = []
        self.text = text
        self._text_objects = deque([])
        self.text_color3f = text_color3f
        
        self._sel_index = sel_index
        self.sel_color3f = sel_color3f

    def render(self, window):
        for tb in self._text_objects:
            tb.hidden = self.hidden
        
        if self.hidden or self._DELETED:
            return
        
        num_objs = len(self._text_objects)
        num_text = len(self.text)
        
        if num_objs > self.sections: #delete extra
            for _ in range(num_objs-self.sections):
                obj = self._text_objects.pop()
                obj.DELETE()
         
        if num_objs < num_text: #add  GLText objs
            for i in range(num_text-num_objs):
                self._text_objects.append(GLText(0, 0, font=GLUT_BITMAP_HELVETICA_12, text=self._text[num_objs+i], color3f=self.text_color3f, hidden=True))
        
        og_theta = self.theta
        
        detected = False
        for i in range(self.sections):
            self.theta = self.theta + 2*math.pi/self.sections
            global_matrix = self.transform_matrix(self.local_matrix()) #transform matrix
            
            if window is not None and not detected and not self.hidden:
                detected = inside(global_matrix, window.Mouse.x, window.Mouse.y)
            
            glColor3f(*(self.sel_color3f if i == self._sel_index else self.color3f))
            glBegin(GL_TRIANGLE_FAN)
            [glVertex2f(*coord) for coord in global_matrix] #draw verts
            glEnd()
            
            if i < len(self._text_objects):
                text = self._text_objects[i]
                text.text = self._text[i]
                text.x, text.y = np.mean(global_matrix, axis=0)
                text.x-=10*len(text.text)/4
                text.color3f = self.text_color3f
                
                text.render(window)
        
        self.detected = detected
        self.theta = og_theta

    def DELETE(self):
        [obj.DELETE() for obj in self._text_objects]
        super(ClassifierSectionedSphere, self).DELETE()

class Connection(Rectangle):
    @property
    def obj1(self):
        try:
            return get_global_objects()[self._obj1]
        except:
            return None
    
    @obj1.setter
    def obj1(self, obj):
        self._obj1 = obj if isinstance(obj, str) else obj.Name
    
    @property
    def obj2(self):
        try:
            return get_global_objects()[self._obj2]
        except:
            return None
    
    @obj2.setter
    def obj2(self, obj):
        self._obj2 = obj if isinstance(obj, str) else obj.Name
    
    @property
    def text(self):
        return self._text
    
    def __init__(self, obj1, obj2, h, color3f=(1.0, 0.0, 3.0), hidden=False, name='Connection'):
        self._obj1 = None
        self._obj2 = None
        
        self.obj1 = obj1
        self.obj2 = obj2
        
        self.weight = None
        
        super(Connection, self).__init__(h, 0, 0, 0, theta=0, color3f=color3f, priority=-1, hidden=hidden, locked=True, name=name)
        
        self._text = GLText(self.x, self.y, text=self.weight, color3f=(1, 1, 1))
        
    def render(self, window):
        if self.obj1 is None or self.obj2 is None:
            self.DELETE()
            return
        
        self.x = (self.obj1.x+self.obj2.x)/2
        self.y = (self.obj1.y+self.obj2.y)/2
        
        self.lookat(self.obj2)
        self.w = ((self.obj1.x-self.obj2.x)**2+(self.obj1.y-self.obj2.y)**2)**0.5
        
        super(Connection, self).render(window)
        
        if self.weight is not None:
            self._text.text = str(self.weight)
        
        self._text.x = self.x
        self._text.y = self.y
        self._text.render(window)

    def DELETE(self):
        self._text.DELETE()
        super(Connection, self).DELETE()

class Pointer(Connection):
    def __init__(self, *args, name='Pointer', **kwargs):
        super(Pointer, self).__init__(name=name, *args, **kwargs)
        self._tip = IsoTriangle(self.h*3*golden, self.h*3*golden, self.x, self.y, color3f=self.color3f, priority=-1, hidden=self.hidden, locked=True)
    
    def render(self, window):
        super(Pointer, self).render(window)
        if self.obj2 is None:
            return
        
        x_dir = self.obj2.x-self.x
        y_dir = self.obj2.y-self.y
        
        self._tip.color3f = self.color3f
        self._tip.x = self.x+x_dir*0.5
        self._tip.y = self.y+y_dir*0.5
        self._tip.h = self.h*3*golden
        self._tip.b = self.h*3*golden
        
        self._tip.theta = self.theta-math.pi/2
        
        self._tip.render(window)

    def DELETE(self):
        self._tip.DELETE()
        super(Pointer, self).DELETE()






