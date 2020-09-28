import copy

_render = None
_names = None
_global_objects = None

_not_implemented_message = 'You must define an ObjectCollection to create and access objects/functionality.'

def get_names():
    if _names is None:
        raise NotImplementedError(_not_implemented_message)
    return copy.copy(_names)

def get_global_objects():
    if _global_objects is None:
        raise NotImplementedError(_not_implemented_message)
    return copy.copy(_global_objects)

def render(window):
    if _render is None:
        raise NotImplementedError(_not_implemented_message)
    _render(window)

class ObjectCollection():
    @property
    def global_objects(self):
        return self._global_objects
    
    @property
    def names(self):
        return self._Names
    
    def __init__(self):
        self._Names = {}
        self._global_objects = {}
    
    def switch(self):
        global _render, _names, _global_objects
        _render = self._render
        _names = self.names
        _global_objects = self.global_objects

    def _render(self, window):
        trash = [obj.Name for obj in self._global_objects.values() if hasattr(obj, 'DELETE') and obj.DELETED]
        for obj in trash:
            del self._global_objects[obj]
        
        objs = list(self._global_objects.values())
        priority = {}
        for obj in objs:
            if hasattr(obj, 'render') and hasattr(obj, 'priority'):
                if not obj.priority in priority:
                    priority.update({obj.priority: []})
                
                priority[obj.priority].append(obj)
        
        order = list(priority.keys())
        order.sort()
        
        [obj.render(window) for p in order for obj in priority[p]]

class GLObject():
    '''
        Note there should only be one reference
        of this instance when an object is created.
    '''
    @property
    def ID(self):
        return self._ID
    
    @property
    def Name(self):
        return self._Name
    @Name.setter
    def Name(self, new_name):
        assert isinstance(new_name, str) and not '.' in new_name, _not_implemented_message
        
        if self._Name is not None:
            if self._Name in _global_objects:
                del _global_objects[self._Name] #remove self from dict with old name
            
            #decrease current name count by 1
            name = self._Name.split('.')[0]
            if name in _names and _names[name] < 0:
                del _names[name]
        else:
            name = new_name
        
        #increase/create count of new name by 1
        if new_name in _names:
            _names.update({new_name: _names[new_name]+1})
            new_name = '%s.%i' % (name, _names[new_name])
        else:
            _names.update({new_name: 0})
        
        _global_objects.update({new_name: self}) #insert self in dict with new name
        
        self._Name = new_name
    
    @property
    def DELETED(self):
        return self._DELETED
    
    @property
    def priority(self):
        return self._priority
    
    @priority.setter
    def priority(self, value):
        assert isinstance(value, int)
        self._priority = value
    
    def __init__(self, priority=0, hidden=False, locked=False, name='Object'):
        assert _global_objects is not None, 'Must create an environment to define GLObjects.'
        
        self._Name = None
        self.Name = name
        
        self._ID = id(self)
        self._priority = priority
        self.locked = locked
        self.hidden = hidden
        self.detected = False
        self._DELETED = False
    
    def DELETE(self):
        self._DELETED = True


