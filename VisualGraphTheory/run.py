'''
Requirements:
    Python: 3.6, 3.7, 3.8

Instructions:
    To begin the program call in cmd:
        python -m VisualGraphTheory
    
    Feel free to manipulate the algorithms
    used in the algorithm.py module.
    
Controls:
    General Controls:
        Scroll using the Middle Mouse Wheel to
        change modes. These modes include the
        following:
            1. (Wheel Section) Algorithms 
            2. (Wheel Section) Configuration
            3. (Green) Node Manipulation 
            4. (Blue) Diretional Edge Manipulation 
            5. (Red) Unidirectional Edge Manipulation 
        
        Click and hold the Middle Mouse Wheel
        to drag the screen around.
    
    1. Algorithms Controls:
        Is a wheel with 3 options:
            - (Option) DFS-IF (Depth First Search Island Finder)
            - (Option) BFS-PF (Breath First Search Path Finder)
            - (Option) Exit
        
        To select an option hold the Right
        Mouse Button and move in the direction
        of the desired option and let go.
        
        DFS-IF (Depth First Search Island Finder) Action:
            If chosen, then an animation using
            the nodes and edges created by the
            user will mirror the DFS algorithm.
            During the animation General controls
            will be disabled. Note will only run
            if all edges are of the same type.
        
        BFS-PF (Breath First Search Path Finder) Action:
            If chosen, then an animation using
            the nodes and edges created by the
            user will mirror the BFS algorithm.
            During the animation General controls
            will be disabled. Note will only run
            if all edges are of the same type.
        
        Exit:
            Is an option to not perform any of
            the above animations.
    
    2. Configuration Controls:
        Is a wheel with 4 sections/options:
            - (Setting) S-Node (Start Node)
            - (Setting) E-Node (End Node)
            - (Setting) dt (delta time)
            - (Option) Reset
        
        To manipulate a setting hold the Right
        Mouse and move in the direction of the
        desired option and use the Middle Mouse
        Button to Scroll and change values.
        
        To select an option hold the Right
        Mouse Button and move in the direction
        of the desired option and let go.
        
        S-Node (Start Node) Setting:
            Is used to identify which node
            will act as the starting node
            for each algorithm.
        
        E-Node (End Node) Setting:
            Is used to identify which node
            will act as the ending node for
            each algorithm, if applicable
            (i.e. BFS).
        
        dt (delta time) Setting:
            Is used to determine the step
            time of the animation. (i.e.
            how fast the animation moves)
        
        Reset Action:
            Resets all configurations and
            removes all nodes/edges.
    
    3. Node Manipulation Controls:
        Allows for the creation, manipulation
        and removal of nodes.
        
        To create a node click the Left
        Mouse Button.
        
        To move a node hold the Right
        Mouse Button.
        
        To delete a node double click
        the Right Mouse Button.
    
    4. Diretional Edge Manipulation Controls:
        Allows for the creation and
        removal of a directional edges.
        
        To create a directed edge, hold
        the Left Mouse Button on a node
        and release on another node.
        
        To remove a directed edge, double
        click a directed edge.
    
    5. Unidirectional Edge Manipulation Controls:
        Allows for the creation and
        removal of a unidirectional edges.
        
        To create a unidirected edge, hold
        the Left Mouse Button on a node
        and release on another node.
        
        To remove a unidirected edge, double
        click a directed edge.
'''

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

import time
import traceback
from threading import Thread, Event
from weakref import WeakValueDictionary as WVD, WeakSet

from .mouse import*
from .algorithms import DFS, BFS

from .Graphics.color3f import*
from .Graphics import Window, render, Mouse
from .Graphics.objects.object2d import Circle, TextCircle, Rectangle, Connection, Pointer, SectionedSphere, coord_to_theta, ClassifierSectionedSphere

def run(window):
    def draw():                                            # ondraw is called all the time
        glEnable(GL_DEPTH_TEST)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT) # clear the screen
        glLoadIdentity()                                   # reset position
        
        glViewport(0, 0, window.width, window.height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        
        glOrtho(window.x_offset, window.x_offset+window.width, window.y_offset, window.y_offset+window.height, 0.0, 1.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
        render(window)
        onAlways(window.Mouse)
        
        window.width, window.height = glutGet(GLUT_WINDOW_WIDTH), glutGet(GLUT_WINDOW_HEIGHT)
        
        glutSwapBuffers()                                  # important for double buffering
    
    glutInit()                                             # initialize glut
    glutInitDisplayMode(GLUT_RGBA)
    glutInitWindowSize(window.width, window.height)                      # set window size
    glutInitWindowPosition(0, 0)                           # set window position

    W = glutCreateWindow("Visual Graph Theory")                   # create window with title
    
    glutDisplayFunc(draw)                                  # set draw function callback
    glutIdleFunc(draw)                                     # draw all the time
    
    glutPassiveMotionFunc(window.PASSIVE_MOTION)
    glutMotionFunc(window.ACTIVE_MOTION)
    glutMouseFunc(window.CLICK)
    
    glutSetOption(GLUT_ACTION_ON_WINDOW_CLOSE, GLUT_ACTION_GLUTMAINLOOP_RETURNS)
    glutMainLoop()                                         # start everything

def visited(window, n, neighbors, visited, weighted):
    nodes = list(window.storage['Nodes'].values())
    
    node = nodes[n]
    current = TextCircle(node.r, node.x, node.y, edges=node.edges, text=node.text.text, scale=node.scale, theta=node.theta, color3f=Orange)
    window.storage['Anim_Objs'].add(current)
    
    if not visited[n]:
        #blink
        time.sleep(window.storage['Anim_Speed'])
        current.color3f = Yellow
        time.sleep(window.storage['Anim_Speed'])
        current.color3f = Orange
    
    time.sleep(window.storage['Anim_Speed'])
    
    for props in neighbors:
        if weighted:
            to, weight = props
        else:
            to = props
            weight = None
        
        node = nodes[to]
        
        neighbor = TextCircle(node.r, node.x, node.y, edges=node.edges, text=node.text.text, scale=node.scale, theta=node.theta, color3f=Orange)
        conn = Pointer(current, neighbor, 5, color3f=Orange)
        window.storage['Anim_Objs'].add(neighbor)
        window.storage['Anim_Objs'].add(conn)
        
        #blick if not visited
        time.sleep(window.storage['Anim_Speed'])
        neighbor.color3f = Yellow
        if visited[to]:
            time.sleep(window.storage['Anim_Speed'])
            neighbor.color3f = Orange
        
        time.sleep(window.storage['Anim_Speed'])
    
def animate(window, done):
    while not done.is_set():
        time.sleep(0.1)
        index = window.storage['Animation']
        
        if index is not None and index != 2:
            window.Mouse.ENABLED = False
            
            window.storage['Anim_Objs'] = WeakSet()
            
            Nodes = window.storage['Nodes']
            Edges = window.storage['Edges']
            
            og_node_color3f = []
            for node in Nodes.values():
                og_node_color3f.append(node.color3f)
                node.color3f = Blue
            
            of_edge_color3f = []
            for edge in Edges.values():
                of_edge_color3f.append(edge.color3f)
                edge.color3f = Blue
            
            if len(Nodes) > 0:
                nodes = list(Nodes.values())
                
                if index == 0:
                    print('Performing Depth First Search Island Finder')
                    try:
                        islands = DFS(window, Nodes, Edges, weighted=False, start=window.storage['Start_Node'], visited_fn=visited)
                    except:
                        islands = []
                        
                        print('='*80)
                        traceback.print_exc()
                        print('='*80)
                    
                    print('Islands:', islands)
                    
                    if len(islands) > 0:
                        colors = randColor(len(islands))
                        
                        for i in range(len(islands)):
                            for n in islands[i]:
                                color = colors[i]
                                node = nodes[n]
                                color_node = TextCircle(node.r, node.x, node.y, edges=node.edges, text=node.text.text, scale=node.scale, theta=node.theta, color3f=color)
                                
                                window.storage['Anim_Objs'].add(color_node)
                                time.sleep(window.storage['Anim_Speed'])
                elif index == 1:
                    print('Performing Breath First Search Path Finder')
                    try:
                        path = BFS(window, Nodes, Edges, weighted=False, start=window.storage['Start_Node'], end=window.storage['End_Node'], visited_fn=visited)
                    except:
                        path = []
                        
                        print('='*80)
                        traceback.print_exc()
                        print('='*80)
                    
                    print('Path:', path)
                    
                    color = randColor(1)[0]
                    if len(path) == 1:
                        node = nodes[path[0]]
                        color_node = TextCircle(node.r, node.x, node.y, edges=node.edges, text=node.text.text, scale=node.scale, theta=node.theta, color3f=color)
                        window.storage['Anim_Objs'].add(color_node)
                    else:
                        for i in range(len(path)-1):
                            node1 = nodes[path[i]]
                            node2 = nodes[path[i+1]]
                            
                            color_node1 = TextCircle(node1.r, node1.x, node1.y, edges=node1.edges, text=node1.text.text, scale=node1.scale, theta=node1.theta, color3f=color)
                            color_node2 = TextCircle(node2.r, node2.x, node2.y, edges=node2.edges, text=node2.text.text, scale=node2.scale, theta=node2.theta, color3f=color)
                            conn = Pointer(color_node1, color_node2, 5, color3f=color)
                            
                            window.storage['Anim_Objs'].add(color_node1)
                            window.storage['Anim_Objs'].add(color_node2)
                            window.storage['Anim_Objs'].add(conn)
                            time.sleep(window.storage['Anim_Speed'])
            
            time.sleep(2)
            
            [obj.DELETE() for obj in window.storage['Anim_Objs']]
            del window.storage['Anim_Objs']
            
            window.storage['Animation'] = None
            window.Mouse.ENABLED = True
            
            for n, node in enumerate(Nodes.values()):
                node.color3f = og_node_color3f[n]
                
            for n, edge in enumerate(Edges.values()):
                edge.color3f = of_edge_color3f[n]

def initialize():
    with Window(1024, 512) as window:
        window.storage['Nodes'] = WVD({})
        window.storage['Edges'] = WVD({})
        window.storage['Animation'] = None
        window.storage['Anim_Speed'] = 0.25
        window.storage['Start_Node'] = None
        window.storage['End_Node'] = None
        
        #Default Mouse (Node)
        window.Mouse.cursor = ClassifierSectionedSphere(10, 80, 10, 0, 0, sections=3, radial_vertices=5,
            text=['DFS-IF', 'BFS-PF', 'None'], sel_color3f=(0.5, 0.5, 0.5), color3f=(1, 1, 1), priority=1, hidden=False, locked=True)
        window.Mouse.onActive = DefaultOnActive
        window.Mouse.onPassive = DefaultOnPassive
        window.Mouse.onClick = DefaultOnClick
        
        ConfigMouse = Mouse(window, onActive=ConfigOnActive, onPassive=ConfigOnPassive, onClick=ConfigOnClick)
        ConfigMouse.cursor = ClassifierSectionedSphere(10, 120, 10, 0, 0, sections=4, radial_vertices=5,
            text=['S-Node: ', 'E-Node: ', 'dt: {}'.format(window.storage['Anim_Speed']), 'Reset'], sel_color3f=SummerSky, color3f=Silver, priority=1, hidden=True, locked=True)
        
        NodeMouse = Mouse(window, onActive=NodeOnActive, onPassive=NodeOnPassive, onClick=NodeOnClick)
        NodeMouse.cursor = Circle(5, 0, 0, edges=7, color3f=Green, priority=1, hidden=True, locked=True)
        
        PointMouse = Mouse(window, onActive=moveCursor, onPassive=moveCursor, onClick=PointerOnClick)
        PointMouse.cursor = Circle(5, 0, 0, edges=7, color3f=Blue, priority=1, hidden=True, locked=True)
        
        ConnMouse = Mouse(window, onActive=moveCursor, onPassive=moveCursor, onClick=ConnectionOnClick)
        ConnMouse.cursor = Circle(5, 0, 0, edges=7, color3f=Red, priority=1, hidden=True, locked=True)
        
        window.append_mouse(ConfigMouse)
        window.append_mouse(NodeMouse)
        window.append_mouse(PointMouse)
        window.append_mouse(ConnMouse)
        
        origin = Circle(10, 0, 0, edges=8, color3f=(1,1,1), locked=True, name='Origin')
        y_axis = Rectangle(4096, 4, 0, 0, color3f=(1,1,1), locked=True, name='y-axis')
        x_axis = Rectangle(4, 4096, 0, 0, color3f=(1,1,1), locked=True, name='x-axis')
        
        done = Event()
        Animation = Thread(target=animate, args=(window, done))
        Animation.start()
        
        run(window)
        
        done.set()
        Animation.join()




