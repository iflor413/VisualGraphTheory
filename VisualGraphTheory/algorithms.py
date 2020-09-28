from .Graphics.objects.object2d import Connection, Pointer

from collections import deque

def create_bin_adj_list(Nodes, Edges, weighted=False):
    '''
        Binary Adj. List Format: 
            Weighted:
                [(From, To, Weight),
                 ...,
                 (From, None, None)]
            
            Unweighted:
                [(From, To),
                 ...,
                 (From, None)]
            
            Any pairs with a None 'To', are not
            connected.
            
        Time Complexity:
            O(E+V)
            
            , where E is the # of Edges,
            and V is the number of vertecies
        
        'From' and 'To' are Nodes represented 
        by their index, respectively to the
        Nodes.values()
        
        return list size len(Nodes)
    '''
    
    nodes = list(Nodes.values())
    
    indecies = set()
    
    _type = None
    adj_list = []
    for edge in Edges.values():
        if _type is None:
            _type = edge.__class__
        
        if not isinstance(edge, _type):
            raise Exception("All edges must be of the same class/type.")
        
        index1, index2 = nodes.index(edge.obj1), nodes.index(edge.obj2)
        indecies.add(index1)
        
        adj_list.append((index1, index2)+(((0,) if edge.weight is None else (edge.weight,)) if weighted else ()))
        
        if _type is Connection:
            adj_list.append((index2, index1)+(((0,) if edge.weight is None else (edge.weight,)) if weighted else ()))
    
    [adj_list.append((n, None)+((None,) if weighted else ())) for n in range(len(nodes)) if not n in indecies]
    print('Binary Adj. List:', adj_list)
    return adj_list

def create_adj_dict(Nodes, Edges, weighted=False):
    '''
        Adj. List Format:
            Weighted:   {From: [(To, Weight), ...],
                         ...,
                         From: []}
                         
            Unweighted: {From: [To, ...],
                         ...,
                         From: []}
        
            Any pairs with a [] Value,
            are not connected.
            
        Time Complexity:
            O(2*(E+V))
            
            , where E is the # of Edges,
            and V is the number of
            vertecies.
        
        return dict size len(Nodes)
    '''
    
    bin_adj_list = create_bin_adj_list(Nodes, Edges, weighted=weighted)
    weighted = len(bin_adj_list[0]) == 3
    
    adj_dict = {}
    for pair in bin_adj_list:
        from_, to, weight = pair+(() if weighted else (None,))
        
        if not from_ in adj_dict:
            adj_dict.update({from_: []})
        
        if to is not None:
            if weighted:
                adj_dict[from_].append((to, weight))
            else:
                adj_dict[from_].append(to)
    print('Adj. dictionary:', adj_dict)
    return adj_dict

def DFS(window, Nodes, Edges, weighted=False, start=None, visited_fn=None): #Depth First Search Island Finder
    assert start is None or (isinstance(start, int) and start >= 0 and start < len(Nodes)), "Starting index must be None or in range: [0, '%i']." % len(Nodes)-1
    adj_dict = create_adj_dict(Nodes, Edges, weighted=weighted)
    
    nodes = len(adj_dict)
    visited = [False for _ in range(nodes)]
    
    islands = []
    
    def dfs(n=0):
        if visited[n]:
            return
        visited[n] = True
        islands[-1] += (n,)
        
        if visited_fn is not None:
            visited_fn(window, n, adj_dict[n], visited, weighted)
        
        [dfs(n=node[0] if weighted else node) for node in adj_dict[n]]
    
    if not start is None:
        islands.append(())
        dfs(n=start)
    
    for n in range(nodes):
        if not visited[n]:
            islands.append(())
            dfs(n=n)

    return islands

def BFS(window, Nodes, Edges, weighted=False, start=None, end=None, visited_fn=None): #Breath First Search Path Finder
    assert start is None or (isinstance(start, int) and start >= 0 and start < len(Nodes)), "Starting index must be None or in range: [0, '%i']." % len(Nodes)-1
    adj_dict = create_adj_dict(Nodes, Edges, weighted=weighted)
    
    nodes = len(adj_dict)
    queue = deque()
    visited = [False for _ in range(nodes)]
    s = 0 if start is None else start
    
    queue.append(s)
    visited[s] = True
    
    prev = [None for _ in range(nodes)]
    while not len(queue) == 0:
        node = queue.pop()
        conns = adj_dict[node]
        
        if visited_fn is not None and node == s:
            visited_fn(window, node, adj_dict[node], visited, weighted)
        
        for props in conns:
            if weighted:
                n, weight = props
            else:
                n = props
                weight = None
            
            if not visited[n]:
                queue.append(n)
                visited[n] = True
                prev[n] = node
                
                if visited_fn is not None:
                    visited_fn(window, n, adj_dict[n], visited, weighted)
    
    if end is None:
        return []
    
    path = [end]
    while path[-1] != s and path[-1] is not None:
        path.append(prev[path[-1]])
    path.reverse()
    
    return path if path[0] == s else []


