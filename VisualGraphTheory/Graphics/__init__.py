from collections import deque as _deque
from itertools import islice as _islice
import time

_windows = {}
_current_window = None

def get_current_window():
    return _current_window

from . import color3f
from . import objects
from .objects import ObjectCollection, render, GLObject


def Islice(iterable, start, stop, step):
    return _islice( iterable,
                    start if start is None else start%len(iterable),
                    stop if stop is None else stop%len(iterable),
                    step)

class Deque(_deque):
    def __getitem__(self, index):
        return  (list(Islice(self, index.start, index.stop, index.step))
                if isinstance(index, slice) else
                super(Deque, self).__getitem__(index))

class MouseEvent():
    @property
    def history(self): return self._history
    @property
    def count(self):
        return len(self._history)
    
    @property
    def time(self): return self.get_property(-1, 0)
    @property
    def x(self): return self.get_property(-1, 1)
    @property
    def y(self): return self.get_property(-1, 2)
    @property
    def x_local(self): return self.get_property(-1, 3)
    @property
    def y_local(self): return self.get_property(-1, 4)
    @property
    def button(self): return self.get_property(-1, 5)
    @property
    def state(self): return self.get_property(-1, 6)
    
    @property
    def is_current(self):
        return self._Mouse.button == self._button 
    
    def __init__(self, mouse, button, max_history=32):
        assert isinstance(mouse, Mouse)
        self._Mouse = mouse
        self._button = button
        
        self._history = Deque([(time.time(), 0, 0, 0, 0, button, 1)], max_history) #append((time.time(), x, y, x_local, y_local, button, state))
    
    def get_property(self, index, prop):
        return None if self.count == 0 else self._history[index][prop]
    
    def update(self):
        if self.is_current:
            self._history.append((time.time(),)+self._Mouse.get_state_properties())

class MouseButton(MouseEvent):
    @property
    def down(self):
        return (self.state == 0)
    @property
    def up(self):
        return (self.state == 1)
    @property
    def click(self):
        return (self.is_current and
                self.count >= 2 and
                self.get_property(-2, 6) == 0 and
                self.get_property(-1, 6) == 1)
    @property
    def double_click(self):
        return (self.is_current and
                self.count >= 4 and
                self.get_property(-4, 6) == 0 and
                self.get_property(-3, 6) == 1 and
                self.get_property(-2, 6) == 0 and
                self.get_property(-1, 6) == 1 and
                self.time - self.get_property(-4, 0) < 0.35)

class MouseWheel(MouseEvent):
    @property
    def rolling(self):
        return (self.is_current and
                self.count >= 3 and
                self.time - self.get_property(-3, 0) < 0.2)
    @property
    def roll(self):
        return (self.is_current and
                self.count >= 3 and
                self.get_property(-3, 6) == 1 and
                self.get_property(-2, 6) == 0 and
                self.get_property(-1, 6) == 1 and
                self.time - self.get_property(-3, 0) > 0.2)

class Mouse(GLObject):
    '''
        *button:    Int.    Button
                    0       Left Mouse Button
                    1       Middle Mouse Button
                    2       Right Mouse Button
                    3       Up Scroll
                    4       Down Scroll
                    
        *state:     0 - Enter
                    1 - Exit
    '''
    
    @property
    def window(self): return self._window
    
    @property
    def cursor(self): return self._cursor
    @cursor.setter
    def cursor(self, new_cursor):
        self._cursor = new_cursor
    
    @property
    def ENABLED(self):
        return self._ENABLED
    @ENABLED.setter
    def ENABLED(self, value):
        assert isinstance(value, bool)
        
        if self._cursor is not None:
            self._cursor.hidden = not value
        self._ENABLED = value
    
    @property
    def LMB(self): return self._LMB
    @property
    def LRMB(self): return self._RMB
    @property
    def MMB(self): return self._MMB
    @property
    def RMB(self): return self._RMB
    @property
    def ScrlUp(self): return self._ScrlUp
    @property
    def ScrlDown(self): return self._ScrlDown
    
    def __init__(self, window, cursor=None, onActive=None, onPassive=None, onClick=None, name='Mouse'):
        super(Mouse, self).__init__(locked=True, name=name)
        self._window = window
        
        self._cursor = cursor
        self._ENABLED = True
        
        self.onActive = onActive
        self.onPassive = onPassive
        self.onClick = onClick
        
        self.x, self.y = 0, 0
        self.x_local, self.y_local = 0, 0
        self.x_motion, self.y_motion = 0, 0
        self.x_passive, self.y_passive = 0, 0
        self.x_click, self.y_click = 0, 0
        
        self.button, self.state = None, None
        
        self._LMB = MouseButton(self, 0)
        self._MMB = MouseButton(self, 1)
        self._RMB = MouseButton(self, 2)
        self._ScrlUp = MouseWheel(self, 3)
        self._ScrlDown = MouseWheel(self, 4)
    
    def _update(self):
        self._LMB.update()
        self._MMB.update()
        self._RMB.update()
        self._ScrlUp.update()
        self._ScrlDown.update()
    
    def coords(self):
        return self.x, self.y
    
    def get_state_properties(self):
        return (self.x, self.y, self.x_local, self.y_local, self.button, self.state)
    
    def get_properties(self):
        return (self.x, self.y, self.x_local, self.y_local,
                self.x_motion, self.y_motion, self.x_passive,
                self.y_passive, self.button, self.state,
                self.x_click, self.y_click)
    
    def set_properties(self, x, y, x_local, y_local,
                            x_motion, y_motion, x_passive,
                            y_passive, button, state,
                            x_click, y_click):
        self.x, self.y = x, y
        self.x_local, self.y_local = x_local, y_local
        self.x_motion, self.y_motion = x_motion, y_motion
        self.x_passive, self.y_passive = x_passive, y_passive
        self.button, self.state = button, state
        self.x_click, self.y_click = x_click, y_click
    
    def _onActive(self):
        if self.onActive is not None:
            self.onActive(self)

    def _onPassive(self):
        if self.onPassive is not None:
            self.onPassive(self)
    
    def _onClick(self):
        if self.onClick is not None:
            self.onClick(self)
    
    #########Actions#########
    
    def ACTIVE_MOTION(self, mx, my):
        if self._ENABLED:
            self.x_local, self.y_local = mx, self._window.height-my
            self.x, self.y = self.x_local+self.window.x_offset, self.y_local+self.window.y_offset
            self.x_motion, self.y_motion = self.coords()
            
            self._onActive()
    
    def PASSIVE_MOTION(self, mx, my):
        if self._ENABLED:
            self.x_local, self.y_local = mx, self._window.height-my
            self.x, self.y = self.x_local+self.window.x_offset, self.y_local+self.window.y_offset
            self.x_passive, self.y_passive = self.coords()
            
            self._onPassive()
    
    def CLICK(self, button, state, mx, my):
        if self._ENABLED:
            self.x_local, self.y_local = mx, self._window.height-my
            self.x, self.y = self.x_local+self.window.x_offset, self.y_local+self.window.y_offset
            self.button, self.state, self.x_click, self.y_click = button, state, self.x, self.y
            
            self._update()
            self._onClick()

class Window():
    @property
    def window_num(self):
        return self._window_num
    
    @property
    def collection(self):
        return self._collection
    
    @property
    def Mouse(self):
        return self._Mouse
    
    @property
    def Mice(self):
        return self._Mice
    
    def __init__(self, width, height):
        self._window_num = 0 if len(_windows) == 0 else list(_windows.keys())[-1]+1
        self._collection = ObjectCollection()
        
        if _current_window is None:
            self.switch()
        
        self.x_offset = 0
        self.y_offset = 0
        self.width = width
        self.height = height
        
        self._Mouse = Mouse(self)
        self._Mice = [self._Mouse]
        self.selected = None
        
        self.storage = {} #recommend on using weakref dictionaries to refer to GLObjects when categorizing
        
        self._prev_window = None
        
    def __del__(self):
        _windows[self._window_num]
        
        if self is _current_window:
            _current_window = None
    
    def set_mouse(self, m):
        assert isinstance(m, int)
        
        self._Mice[m].set_properties(*self._Mouse.get_properties()) #inherit properties
        self._Mouse = self._Mice[m]
        
    def append_mouse(self, mouse):
        assert isinstance(mouse, Mouse)
        self._Mice.append(mouse)
    
    def del_mouse(self, m):
        assert isinstance(m, int) and self._Mice[m] is not self._Mouse
        del self._Mice[m]
    
    def switch(self):
        _current_window = self
        self._collection.switch()
    
    def __enter__(self):
        if _current_window is not self:
            self._prev_window = _current_window
            self.switch()
        return self
    
    def __exit__(self, *args):
        try:
            self._prev_window.switch()
        except:
            pass
    
    def PASSIVE_MOTION(self, *args):
        self._Mouse.PASSIVE_MOTION(*args)
    
    def ACTIVE_MOTION(self, *args):
        self._Mouse.ACTIVE_MOTION(*args)
    
    def CLICK(self, *args):
        self._Mouse.CLICK(*args)


