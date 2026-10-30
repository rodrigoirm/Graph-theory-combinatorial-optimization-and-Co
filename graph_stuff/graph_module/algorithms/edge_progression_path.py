"""
Simple algorithm I came up in my proof that every edge progression 
between two vertices implies in the existence of a path between 
these same vertices.

If you just want to create a path from an edge progression,
without working with an underlying graph, use the following function.

construct_path_from_ep()

Input: a sequence of edges.

Output: returns a path from the first to the last element of a
        sequence of edges.

        ATTENTION: this function does not check whether the sequence
                   is actually an edge progression. 

If you are explicitly working with a graph G and wish
to construct a path in it from an edge progression, use
the following function.

edge_progression_path():

Input: a graph or a multigraph and a sequence of edges.

Output: if the sequence is an edge progression, returns a path from 
        the first to the last element of thiss sequence.


"""

from graph_module.graph_class import Graph, MultiGraph
from collections.abc import Hashable

def _last_occurrence_and_slice[T: Hashable](L: list[T], target: T):
    """
    Finds the last occurrence of a given target in
    a list and removes all preceding entries plus
    the target itself.

    Parameters
    ----------
    L: list[T]
        A list with entries of a given type T.

    target: T
        An entry from the list.

    Returns
    -------
    tuple[int, list[T]]
        How many elements where removed (including target), 
        and the sliced list.
    """
    rev_L = list(reversed(L))
    n = len(L)
    i = rev_L.index(target)
    return n - i, L[n-i:]



def construct_path_from_ep[T: Hashable](edge_seq: list[tuple[int, T, T]]) -> tuple[list[T], list[tuple[int, T, T]]]:
    """
    Construct a path from an edge progression.

    Parameters
    ----------
    edge_seq : list[tuple[int, T, T]]
        Edge progression represented by triples (edge_id, u, v).
        Consecutive edges must have matching endpoints.

    Returns
    -------
    tuple[list[T], list[tuple[int, T, T]]]
        The vertices and edges of the resulting path.
    """

    vert_seq = [edge_seq[0][1]] + [v for _, _, v in edge_seq]

    v_current = vert_seq[0]
    target = vert_seq[-1]

    leftover_vertices = vert_seq
    path_vertices = [v_current]
    path_edges = []
    r = 0
    while v_current != target:
        s, leftover_vertices = _last_occurrence_and_slice(leftover_vertices, v_current)
        r += s
        v_current = leftover_vertices[0]
        path_vertices.append(v_current)
        path_edges.append(edge_seq[r - 1])

    return path_vertices, path_edges



def _validate_edge_prog[T: Hashable](G: Graph[T] | MultiGraph[T], edge_seq: list[tuple[int, T, T]]):
    """
    Parameters
    ----------
    G: Graph[T] | MultiGraph[T]
        An instance of the Graph or MultiGraph class.
    
    edge_seq: list[tuple[int, T, T]]
        A list representing a sequence of edges.

    Raises
    ------
    ValueError
        If the edge progression is empty, contains invalid edge
        identifiers, or violates the required incidence conditions.
    """
    if not edge_seq:
        raise ValueError("The edge progression cannot be empty.")

    edges = G.edges
    for (edge_id, u, v) in edge_seq:
        endpoints = edges.get(edge_id)
        if G.directed:
            valid = ((u,v) == endpoints)
        else:
            valid = ((u,v) == endpoints) or ((v,u) == endpoints)

        if not valid:
            raise ValueError(f"Edge {edge_id} does not connect vertices {u} and {v}.")

    for (_, _, v), (_, w, _) in zip(edge_seq, edge_seq[1:]):
        if v != w:
            raise ValueError("Invalid edge progression.")


def edge_progression_path[T: Hashable](G: Graph[T] | MultiGraph[T], edge_prog: list[tuple[int, T, T]]):
    """
    Computes a path that connects the endpoints of
       an edge progression in a graph or multi-graph.
    
    Parameters
    ----------
    G: Graph[T] | MultiGraph[T]
        A graph or a multi-graph.
    
    edge_prog: list[tuple[int, T, T]]
        An edge progression in G.
    
    Returns
    -------
    tuple[list[T], list[tuple[int, T, T]]]
        The vertices and edges of the resulting path.
    """
    _validate_edge_prog(G, edge_prog)

    return construct_path_from_ep(edge_prog)

           
if __name__ == "__main__":

    G1 = {"A": ["A","B","D"], "B": ["C"], "C": ["D"], "D": []}
    G2 = {"A": ["B","D","E"], "B": ["C","D"], "C": ["E","F"], "D": ["A","C"], "E": [], "F": []}
    G3 = {"A": ["B", "B"], "B": ["A"], "C": ["A", "C"]}


    g1 = Graph(G1,directed=False)
    g2 = MultiGraph(G2,directed=True)
    g3 = MultiGraph(G3,directed=False)

    edge_prog1 = [(2, "A", "D"), (4, "D", "C"), (3, "C", "B"), (1, "B", "A"), (0, "A", "A"), (2, "A", "D")]
    edge_prog2 = [(1, "A", "D"), (7, "D", "A"), (1, "A", "D"), (8, "D", "C"), (6, "C", "F")]
    edge_prog3 = [(0, "A", "B"), (2, "B", "A"), (1, "A", "B"), (0, "B", "A"), (3, "A", "C"), (4, "C", "C")]

    test_cases = {"G1": ["Undirected graph", g1, edge_prog1], 
                  "G2": ["Directed multigraph", g2, edge_prog2], 
                  "G3": ["Undirected multigraph", g3, edge_prog3]}

    for name, (graph_type, graph, edge_prog) in test_cases.items():
        path_vertices, path_edges = edge_progression_path(graph, edge_prog)

        print(f"Graph: {name} ({graph_type})")
        print(f" - Edges:\n     {graph.edges}")
        print(f" - Edge progression:\n     {edge_prog}")
        print(f" - Path's vertices:\n     {path_vertices}")
        print(f" - Path's edges:\n     {path_edges} \n")