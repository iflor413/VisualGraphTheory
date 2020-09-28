import math
from weakref import WeakValueDictionary as WVD

from .Graphics.color3f import*
from .Graphics.objects import get_global_objects, get_names
from .Graphics.objects.object2d import Circle, TextCircle, Rectangle, Connection, Pointer, SectionedSphere, coord_to_theta, ClassifierSectionedSphere

def detect_object(self): #self is a Mouse object
    locked_objs = []
    unlocked_objs = []
    for obj in get_global_objects().values():
        if obj.detected:
            props = (obj.Name, (obj.x, obj.y), (self.x, self.y))
            if obj.locked:
                locked_objs.append(props)
            else:
                unlocked_objs.append(props)
    return unlocked_objs, locked_objs

def onAlways(self): #self is a Mouse object
    #print(glReadPixels(self.x, self.y, 1, 1, GL_RGBA, GL_FLOAT))
    
    for n, node in enumerate(self.window.storage['Nodes'].values()):
        node.text.text = str(n)
    
    if self.MMB.down: #offset screen
        x_offset, y_offset = self.x_click-self.x_local, self.y_click-self.y_local
        
        if x_offset < -self.window.height*2-1:
            x_offset = -self.window.height*2-1
        elif x_offset > 0:
            x_offset = 0
        
        if y_offset < -self.window.height:
            y_offset = -self.window.height
        elif y_offset > 0:
            y_offset = 0
        
        self.window.x_offset, self.window.y_offset = x_offset, y_offset

def moveCursor(self):
    self.cursor.x = self.x
    self.cursor.y = self.y

def changeMouse(self):
    #switch mouse
    if self.LMB.up and self.RMB.up and self.MMB.up and (self.ScrlUp.roll or self.ScrlUp.rolling or self.ScrlDown.roll or self.ScrlDown.rolling) and self.state == 1:
        mice = self.window.Mice
        m = (mice.index(self)+1)%len(mice) if self.ScrlUp.is_current else mice.index(self)-1
        
        if self.cursor is not None:
            self.cursor.hidden = True
        
        if mice[m].cursor is not None:
            mice[m].cursor.hidden = False
        
        self.window.set_mouse(m)
        [moveCursor(mouse) for mouse in self.window.Mice]

#########DefaultMouse#########

def DefaultOnActive(self):
    if self.RMB.down:
        if self.window.selected is None:
            self.window.selected = Circle(10, self.RMB.x, self.RMB.y, color3f=self.cursor.color3f).Name
        
        origin = get_global_objects()[self.window.selected]
        mag = ((self.x-origin.x)**2+(self.y-origin.y)**2)**0.5
        if mag < 1e-5:
            mag = 1
        _dir = ((self.x-origin.x)/mag, (self.y-origin.y)/mag)
        if mag > self.cursor.inner_r:
            self.cursor.x = origin.x+_dir[0]*self.cursor.inner_r
            self.cursor.y = origin.y+_dir[1]*self.cursor.inner_r
        
        theta = coord_to_theta(self.x-self.RMB.x, self.y-self.RMB.y)
        for i in range(self.cursor.sections):
            min_theta = 2*math.pi*(i)/self.cursor.sections
            max_theta = 2*math.pi*(i+1)/self.cursor.sections
            
            if theta > min_theta and theta < max_theta:
                self.cursor.sel_index = (i-1)%self.cursor.sections
                break

def DefaultOnPassive(self):
    moveCursor(self)

def DefaultOnClick(self):
    if not self.RMB.down:
        moveCursor(self)
    changeMouse(self)
    
    window = self.window
    
    if self.RMB.up and self.window.selected is not None:
        get_global_objects()[self.window.selected].DELETE()
        index = self.cursor.sel_index
        window.storage['Animation'] = index
        
        self.window.selected = None
        self.cursor.sel_index = None

#########DefaultMouse#########

#########ConfigMouse#########

def ConfigOnActive(self):
    if self.RMB.down:
        if self.window.selected is None:
            self.window.selected = Circle(10, self.RMB.x, self.RMB.y, color3f=self.cursor.color3f).Name
        
        origin = get_global_objects()[self.window.selected]
        mag = ((self.x-origin.x)**2+(self.y-origin.y)**2)**0.5
        _dir = ((self.x-origin.x)/mag, (self.y-origin.y)/mag)
        if mag > self.cursor.inner_r:
            self.cursor.x = origin.x+_dir[0]*self.cursor.inner_r
            self.cursor.y = origin.y+_dir[1]*self.cursor.inner_r
        
        theta = coord_to_theta(self.x-self.RMB.x, self.y-self.RMB.y)
        for i in range(self.cursor.sections):
            min_theta = 2*math.pi*(i)/self.cursor.sections
            max_theta = 2*math.pi*(i+1)/self.cursor.sections
            
            if theta > min_theta and theta < max_theta:
                self.cursor.sel_index = (i-1)%self.cursor.sections
                break

def ConfigOnPassive(self):
    moveCursor(self)

def ConfigOnClick(self):
    if not self.RMB.down:
        moveCursor(self)
    
    changeMouse(self)
    
    window = self.window
    
    if self.RMB.up and self.cursor.sel_index == 3: #reset
        [node.DELETE() for node in window.storage['Nodes'].values()]
        [edge.DELETE() for edge in window.storage['Edges'].values()]
        
        window.storage['Nodes'] = WVD({})
        window.storage['Edges'] = WVD({})
        
        window.storage['Animation'] = None
        window.storage['Anim_Speed'] = 0.25
        window.storage['Start_Node'] = None
        window.storage['End_Node'] = None
        
        if window.storage['Start_Node'] is None:
            self.cursor.text[0] = '{}: '.format(self.cursor.text[0].split(': ')[0])
        else:
            self.cursor.text[0] = '{}: {}'.format(self.cursor.text[0].split(': ')[0], window.storage['Start_Node'])
        
        if window.storage['End_Node'] is None:
            self.cursor.text[1] = '{}: '.format(self.cursor.text[1].split(': ')[0])
        else:
            self.cursor.text[1] = '{}: {}'.format(self.cursor.text[1].split(': ')[0], window.storage['End_Node'])
        
        self.cursor.text[2] = '{}: {}'.format(self.cursor.text[2].split(': ')[0], window.storage['Anim_Speed'])
    
    nodes = len(window.storage['Nodes'])
    start_node = window.storage['Start_Node']
    end_node = window.storage['End_Node']
    
    if start_node is not None and start_node >= nodes:
        window.storage['Start_Node'] = nodes-1
    elif start_node is not None and nodes == 0:
        start_node = None
    
    if end_node is not None and end_node >= nodes:
        window.storage['End_Node'] = nodes-1
    elif end_node is not None and nodes == 0:
        end_node = None
    
    if (self.ScrlUp.roll or self.ScrlUp.rolling or self.ScrlDown.roll or self.ScrlDown.rolling) and self.window.selected is not None:
        index = self.cursor.sel_index
        
        _dir = -1 if self.ScrlDown.rolling or self.ScrlDown.roll else 1
        
        new_value = None
        if index == 0: #start index
            if start_node is None:
                start_node = 0
            if nodes == 0:
                new_value = None
            else:
                new_value = (start_node+1)%nodes if self.ScrlUp.is_current else start_node-1 #TODO not indexing all nodes
                if new_value < 0:
                    new_value = nodes - abs(new_value)%nodes
            window.storage['Start_Node'] = new_value
        elif index == 1: #end index
            if end_node is None:
                end_node = 0
            if nodes == 0:
                new_value = None
            else:
                new_value = (end_node+1)%nodes if self.ScrlUp.is_current else end_node-1 #TODO not indexing all nodes
                if new_value < 0:
                    new_value = nodes - abs(new_value)%nodes
            window.storage['End_Node'] = new_value
        elif index == 2: #spd
            new_value = window.storage['Anim_Speed']+0.05*_dir
            new_value*=100
            new_value = math.floor(new_value)
            new_value/=100
            
            if new_value <= 0:
                new_value = 0.05
            if new_value > 1:
                new_value = 1
            
            window.storage['Anim_Speed'] = new_value
        
        if index != 3:
            if not new_value is None:
                self.cursor.text[index] = '{}: {}'.format(self.cursor.text[index].split(': ')[0], str(new_value))
            else:
                self.cursor.text[index] = '{}: '.format(self.cursor.text[index].split(': ')[0])
    
    if self.RMB.up and self.window.selected is not None:
        get_global_objects()[self.window.selected].DELETE()
        
        self.window.selected = None
        self.cursor.sel_index = None

#########ConfigMouse#########

#########NodeMouse#########

def NodeOnActive(self):
    moveCursor(self)
    
    if self.RMB.down and self.window.selected is not None:
        obj_name, (x_obj, y_obj), (x, y) = self.window.selected
        obj = get_global_objects()[obj_name]
        obj.x = x_obj+self.x-x
        obj.y = y_obj+self.y-y

def NodeOnPassive(self):
    moveCursor(self)

def NodeOnClick(self):
    moveCursor(self)
    changeMouse(self)
    unlocked, _ = detect_object(self)
    obj = None if len(unlocked) == 0 else unlocked[-1]
    
    if self.LMB.click and obj is None:
        node = TextCircle(15, self.x, self.y, edges=8, color3f=(1.0, 0.0, 3.0) if self.cursor is None else self.cursor.color3f)
        self.window.storage['Nodes'].update({node.Name: node})
    
    if self.RMB.down and self.window.selected is None and obj is not None: #select object
        self.window.selected = obj
    
    if self.RMB.up:
        self.window.selected = None

    if self.RMB.double_click and obj is not None:
        get_global_objects()[obj[0]].DELETE()
        
        if self.window.selected is not None:
            self.window.selected = None

#########NodeMouse#########

#########Pointer/ConnectionMouse#########

def edge(_type):
    def OnClick(self):
        '''
            add:
                RMB deletes
                Scroll adds weight
        '''
        moveCursor(self)
        changeMouse(self)
        unlocked, locked = detect_object(self)
        obj = None if len(unlocked) == 0 else unlocked[-1]
        locked_obj = None if len(locked) == 0 else locked[-1]
        
        if self.LMB.down and obj is not None and self.window.selected is None:
            obj1 = get_global_objects()[obj[0]]
            edge = _type(obj1, self, 5, color3f=(1.0, 0.0, 3.0) if self.cursor is None else self.cursor.color3f)
            self.window.selected = edge.Name
            self.window.storage['Edges'].update({edge.Name: edge})
        
        if self.LMB.up and self.window.selected is not None:
            conn = get_global_objects()[self.window.selected]
            
            if obj is None or (obj is not None and conn.obj1.Name is obj[0]):
                conn.DELETE()
            else:
                conn.obj2 = get_global_objects()[obj[0]]
            
            self.window.selected = None
        
        if self.LMB.down and self.window.selected is not None and (self.ScrlUp.roll or self.ScrlUp.rolling or self.ScrlDown.roll or self.ScrlDown.rolling and locked_obj is not None):
            obj = get_global_objects()[self.window.selected]
            if isinstance(obj, _type):
                if obj.weight is None:
                    obj.weight = 0
                else:
                    obj.weight += -1 if self.ScrlDown.rolling or self.ScrlDown.roll and locked_obj is not None else 1
        
        if self.RMB.double_click and locked_obj is not None:
            obj = get_global_objects()[locked_obj[0]]
            if isinstance(obj, _type):
                obj.DELETE()
                
                if self.window.selected is not None:
                    self.window.selected = None
    return OnClick

PointerOnClick = edge(Pointer)
ConnectionOnClick = edge(Connection)

#########Pointer/ConnectionMouse#########

