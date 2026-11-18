"""
Here I implement two algorithms related to connectivity of
graphs: one that finds all of a graph's connected components
and other that finds all of a digraph's strongly connected
components. I follow Korte and Vygen's combinatorial optimization
book (6ed).

Implemented algorithms:
- Connected components algorithm
- Kosaraju's algorithm
"""

from graph_module.graph_class import Graph, MultiGraph
from collections.abc import Hashable
from collections import deque

def BFS_graph_scanning[T: Hashable](G: Graph[T] | MultiGraph[T], s: T) -> tuple[set[T], set[tuple[T,T]]]:
    """
    Given a graph G and a starting vertex s, performs breadth-first 
    search to find a tree or an arborescence rooted at this vertex.
    
    Parameters
    ----------

    G: Graph[T] | MultiGraph[T] 
        An instance of Graph or MultiGraph.
    s: T
        A vertex from G.
    
    Returns
    -------

    R: set[T]
        A list containing all vertices reachable from s.

    tree_edges: set[tuple[T,T]]
        A list of edges such that (R,T) is a tree or an
        arborescence rooted at s.

    """
    R, Q, tree_edges = {s}, deque([s]), set()
    while Q:
        v = Q.popleft()

        for edge_id, w in zip(G.adj_edge_ids[v], G.adj_list_rep[v]):
            if w not in R:
                R.add(w)
                Q.append(w)
                tree_edges.add((edge_id, v,w))

    return R, tree_edges



def connected_components[T: Hashable](G: Graph[T] | MultiGraph[T]):
    """
    Computes the connected components of an undirected (multi)graph G.
    
    Each component is returned as a graph of the same class
    as G, containing all its vertices and edges, including
    self-loops and parallel edges.

    Parameters
    ----------

    G: Graph[T] | MultiGraph[T]
        An undirected graph or multigraph.

    Returns
    -------

    connected_components: List[Graph[T] | MultiGraph[T]]
        A list containing the connected components of G.
    """

    if G.directed:
        raise ValueError(f"G must be an undirected graph.")
    
    seen = set()
    components = []
    edges = G.edges

    for s in G.vertices:
        if s in seen:
            continue

        R = BFS_graph_scanning(G,s)[0]
        seen = seen.union(R)
        h = {v: [] for v in R}
        for v in R:
            for i in G.adj_edge_ids[v]:
                u, w = edges[i]
                if u == v:
                    h[v].append(w)

        H = type(G)(h, directed=False)
        components.append(H)

    return components



def _visit_1(G, v, R, N, psi):
    """
    Performs DFS to label the vertices belonging to an arborescence rooted at 
    a chosen starting vertex.
    """
    R.add(v)
    for w in G.adj_list_rep[v]:
        if w not in R:
            N = _visit_1(G, w, R, N, psi)

    N = N + 1
    psi[v] = N

    return N

def _visit_2(tail_vertices, v, R, K, comp):
    """Performs DFS to label vertices from the same connected component."""
    R.add(v)
    comp[v] = K
    for w in tail_vertices[v]:
        if w not in R:
            _visit_2(tail_vertices, w, R, K, comp)

    return comp

def kosarajus_algorithm[T: Hashable](G: Graph[T] | MultiGraph[T]) -> dict[T: int]:
    """
    Kosaraju's algorithm for computing the strongly connected components of a
    directed graph G.

    Parameters
    ----------

    G: Graph[T] | MultiGraph[T]
        A directed graph or multigraph.
    
    Returns
    -------
    comp: dict[T: int]
        A dictionary mapping each vertex to its strongly connected component.
    """
    if not G.directed:
        raise ValueError(f"G must be a directed graph.")
    
    #1st DFS
    R, N, psi = set(), 0, {}
    for v in G.vertices:
        if v not in R:
            N = _visit_1(G, v, R, N, psi)
    enumeration_inv = {label: u for u, label in psi.items()}
    
    adjacent_list_transpose = {v: [] for v in G.vertices}
    for u in G.vertices:
        for v in G.adj_list_rep[u]:
                adjacent_list_transpose[v].append(u)
    
    #2nd DFS
    M = len(G.vertices) 
    R, K, comp = set(), 0, {}
    for i in range(M, 0, -1):
        if enumeration_inv[i] not in R:
            K = K + 1
            comp = _visit_2(adjacent_list_transpose, enumeration_inv[i], R, K, comp)
            
    return comp

if __name__ == "__main__":

    #Application of connected components algorithm
    g1 = {"A": ["B", "C","C"], "B": ["D", "E", "F"], "G": ["H", "I"]}
    G1 = MultiGraph(g1, directed=False)

    for H in connected_components(G1):
        print(H.adj_list_rep)

    #Application of Kosaraju's algorithm
    g2 = {"A": ["G"], "B": ["A"], "C": ["D", "G"], "D": ["E"], "E": ["D"], "F": ["A", "E"], "G": ["B", "D", "E", "F"]}
    G2 = Graph(g2, directed=True)

    component_mapping = kosarajus_algorithm(G2)
    num_components = len({k for k in component_mapping.values()})

    print(f"The components of the given graph/multigraph are:")
    for i in range(1, num_components + 1):
        component = [vertex for vertex in component_mapping.keys() if component_mapping[vertex] == i]
        print(component)