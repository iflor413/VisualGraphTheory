This is a 2D graphical program that uses pyOpenGL to
animate a steps-by-step process of basic Graph Theory
algorithms. This include a Depth First Search and a
Breath First Search algorithm that runs through a 
user created graph to identify isolated nodes or
find a path between two points.

### Requirements:
**Python:** 3.6, 3.7, 3.8  
**Library(s):** pyopengl

### Instructions:
**To begin the program call in cmd:**  
```
python -m VisualGraphTheory
```

or

**In a python IDE:**
```
>>> from VisualGraphTheory import initialize
>>> initialize()
```
    
# Controls:
## General Controls:
Scroll using the Middle Mouse Wheel to
change modes. These modes include the
following:  
1. (Wheel Section) **Algorithms**  
2. (Wheel Section) **Configuration**  
3. (Green) **Node Manipulation** 
4. (Blue) **Diretional Edge Manipulation**  
5. (Red) **Unidirectional Edge Manipulation**  
        
Click and hold the Middle Mouse Wheel
to drag the screen around.
    
### 1. Algorithms Controls: 
Is a wheel with 3 options:  
- (Option) **DFS-IF (Depth First Search Island Finder)**  
- (Option) **BFS-PF (Breath First Search Path Finder)**  
- (Option) **Exit**  
        
To select an option hold the Right
Mouse Button and move in the direction
of the desired option and let go.  
        
**DFS-IF (Depth First Search Island Finder) Action:**  
If chosen, then an animation using
the nodes and edges created by the
user will mirror the DFS algorithm.
During the animation General controls
will be disabled. Note will only run
if all edges are of the same type.  
        
**BFS-PF (Breath First Search Path Finder) Action:**  
If chosen, then an animation using
the nodes and edges created by the
user will mirror the BFS algorithm.
During the animation General controls
will be disabled. Note will only run
if all edges are of the same type.  
        
**Exit:**  
Is an option to not perform any of
the above animations.  
    
### 2. Configuration Controls:
Is a wheel with 4 sections/options:  
- (Setting) **S-Node (Start Node)**  
- (Setting) **E-Node (End Node)**  
- (Setting) **dt (delta time)**  
- (Option) **Reset**  
        
To manipulate a setting hold the Right
Mouse and move in the direction of the
desired option and use the Middle Mouse
Button to Scroll and change values.
To select an option hold the Right
Mouse Button and move in the direction
of the desired option and let go.  
        
**S-Node (Start Node) Setting:**  
Is used to identify which node
will act as the starting node
for each algorithm.  
        
**E-Node (End Node) Setting:**  
Is used to identify which node
will act as the ending node for
each algorithm, if applicable
(i.e. BFS).  

**dt (delta time) Setting:**  
Is used to determine the step
time of the animation. (i.e.
how fast the animation moves)  
        
**Reset Action:**  
Resets all configurations and
removes all nodes/edges.  
    
### 3. Node Manipulation Controls:
Allows for the creation, manipulation
and removal of nodes.
To create a node click the Left
Mouse Button.
To move a node hold the Right
Mouse Button.
To delete a node double click
the Right Mouse Button.  
    
### 4. Directional Edge Manipulation Controls:
Allows for the creation and
removal of a directional edges.
To create a directed edge, hold
the Left Mouse Button on a node
and release on another node.
To remove a directed edge, double
click a directed edge.  
    
### 5. Unidirectional Edge Manipulation Controls:
Allows for the creation and
removal of a unidirectional edges.
To create a unidirected edge, hold
the Left Mouse Button on a node
and release on another node.
To remove a unidirected edge, double
click a directed edge.  

