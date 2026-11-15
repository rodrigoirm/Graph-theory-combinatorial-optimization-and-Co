"""
Here I implement two algorithms related to connectivity of
graphs: one that finds all of a graph's connected components
and other that finds all of a digraph's strongly connected
components. I follow Korte and Vygen's combinatorial optimization
book (2ed).

Implemented algorithms:
- Graph scanning algorithm

To be implemented:
- Connected components algorithm
- Kosaraju's strongly connected components algorithm
"""

from graph_module.graph_class import Graph, MultiGraph
from collections.abc import Hashable
from collections import deque

def graph_scanning[T: Hashable](G: Graph[T] | MultiGraph[T], s: T):
    """
    Given a graph G and a starting vertex s, uses breadth-first 
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

    T: set[tuple[T,T]]
        A list of edges such that (R,T) is a tree or an
        arborescence rooted at s.

    """
    R, Q, T = {s}, deque([s]), set()
    while Q:
        v = Q.popleft()

        for edge_id, w in zip(G.adj_edge_ids[v], G.adj_list_rep[v]):
            if w not in R:
                R.add(w)
                Q.append(w)
                T.add((edge_id, v,w))

    return R, T


if __name__ == "__main__":

    g = {"A": ["B", "C","C"], "B": ["D", "E", "F"]}
    G = MultiGraph(g, directed=True)

    print(graph_scanning(G, "A"))