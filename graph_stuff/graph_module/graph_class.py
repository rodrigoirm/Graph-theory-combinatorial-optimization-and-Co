import numpy as np
from collections.abc import Hashable



class _BaseGraph[T: Hashable]:
    """
    Base class for directed and undirected graphs and multigraphs.

    Vertices are inferred from both the dictionary keys and their
    adjacency lists. Vertices appearing only in adjacency lists are
    automatically added to the graph.

    For directed graphs, each adjacency list specifies outgoing edges.
    For undirected graphs, reverse adjacency entries are automatically
    generated.

    Each occurrence of a neighbor in the input represents one edge.
    Every edge receives a unique integer identifier, allowing parallel
    edges to be distinguished.

    Self-loops are supported.

    Parameters
    ----------
    G : dict[T, list[T]]
        Dictionary representing the graph. Vertices may appear as
        dictionary keys, in adjacency lists, or both. Vertices that
        appear only in adjacency lists are automatically included.

        Isolated vertices must be explicitly declared as keys with
        empty adjacency lists.

    directed : bool, optional
        Whether the graph is directed. Defaults to False.

    Attributes
    ----------
    directed : bool
        Whether the graph is directed.

    vertices : tuple[T, ...]
        Vertices of the graph. Dictionary keys appear first, in
        insertion order, followed by newly discovered vertices
        in order of their first appearance in adjacency lists.

    encoded_vertices : dict[T, int]
        Mapping from vertices to consecutive integer labels,
        starting at zero.

    adj_list_rep : dict[T, list[T]]
        Internal adjacency-list representation of the graph.
        For undirected graphs, adjacency lists are symmetric.

    adj_edge_ids : dict[T, list[int]]
        Adjacency lists containing edge identifiers instead of
        neighboring vertices. In directed graphs, these identify
        outgoing edges; in undirected graphs, incident edges.

    edges : dict[int, tuple[T, T]]
        Mapping from unique edge identifiers to their endpoints.
        Accessing this property returns a copy of the registry.

    adj_matrix_rep : numpy.ndarray
        Adjacency matrix of the graph, with integer entries.
        Parallel edges are counted with multiplicity.
        Undirected self-loops contribute 2 to the diagonal.

    Notes
    -----
    The graph structure is assumed to remain fixed after initialization.
    Modifying adj_list_rep or adj_edge_ids directly may cause
    inconsistencies between the different representations.

    The class attribute allows_parallel_edges determines whether
    parallel edges are permitted. Its value is defined by subclasses.

    For an undirected multigraph, specifying both (u, v) and (v, u)
    in the input dictionary creates two distinct parallel edges.

    For directed graphs, vertices appearing only in adjacency lists
    have no outgoing edges unless explicitly specified otherwise.
    """

    allows_parallel_edges: bool = False

    def __init__(self, G: dict[T, list[T]], directed: bool = False) -> None:
        self.directed = directed

        # Infer vertices from dictionary keys and adjacency lists.
        vertices = list(G)
        seen_vertices = set(vertices)

        for u, neighbors in G.items():
            if not isinstance(neighbors, list):
                raise TypeError(f"Expected a list of neighbors for vertex {u!r}")

            for v in neighbors:
                if not isinstance(v, Hashable):
                    raise TypeError(f"Neighbor {v!r} is not hashable")

                if v not in seen_vertices:
                    seen_vertices.add(v)
                    vertices.append(v)

        self.vertices: tuple[T, ...] = tuple(vertices)

        self.encoded_vertices: dict[T, int] = {
            vertex: i for i, vertex in enumerate(self.vertices)
        }

        # Edge registry: edge_id -> (tail, head).
        # This terminology is also used for undirected graphs.
        self._edges: dict[int, tuple[T, T]] = {}

        # Representation of G using adjacency lists.
        self.adj_list_rep: dict[T, list[T]] = {
            vertex: [] for vertex in self.vertices
        }

        # Adjacency lists containing edge identifiers.
        self.adj_edge_ids: dict[T, list[int]] = {
            vertex: [] for vertex in self.vertices
        }

        # Store previously encountered edges for duplicate detection.
        seen_edges: set[tuple[T, T]] = set()

        for u, neighbors in G.items():
            for v in neighbors:

                # Canonical representation for duplicate detection.
                if directed or (
                    self.encoded_vertices[u] <= self.encoded_vertices[v]
                ):
                    edge = (u, v)
                else:
                    edge = (v, u)

                if not self.allows_parallel_edges and edge in seen_edges:
                    raise ValueError(f"Parallel edge detected: {edge!r}")

                seen_edges.add(edge)

                # Assign a unique identifier to the new edge.
                edge_id = len(self._edges)
                self._edges[edge_id] = (u, v)

                # Update adjacency-list representations.
                self.adj_list_rep[u].append(v)
                self.adj_edge_ids[u].append(edge_id)

                # Add reverse adjacency for undirected edges.
                if not directed and u != v:
                    self.adj_list_rep[v].append(u)
                    self.adj_edge_ids[v].append(edge_id)

    @property
    def edges(self) -> dict[int, tuple[T, T]]:
        """Return a copy of the edge registry."""
        return self._edges.copy()

    @property
    def adj_matrix_rep(self) -> np.ndarray:
        """
        Return the adjacency matrix of the graph.

        Parallel edges are counted with multiplicity.
        Undirected self-loops contribute 2 to the diagonal.

        Returns
        -------
        numpy.ndarray
            Square integer matrix whose rows and columns correspond
            to the vertices in self.vertices.
        """
        return self._adjacency_matrix()

    def _adjacency_matrix(self) -> np.ndarray:
        """Construct the adjacency matrix from the edge registry."""
        n_vert = len(self.vertices)
        adjacency_matrix = np.zeros((n_vert, n_vert), dtype=int)

        for u, v in self._edges.values():
            i = self.encoded_vertices[u]
            j = self.encoded_vertices[v]

            if self.directed:
                adjacency_matrix[i, j] += 1
            elif i == j:
                adjacency_matrix[i, i] += 2
            else:
                adjacency_matrix[i, j] += 1
                adjacency_matrix[j, i] += 1

        return adjacency_matrix


class Graph[T: Hashable](_BaseGraph[T]):
    """
    Represent a directed or undirected graph without parallel edges.

    Self-loops are permitted. Each edge is assigned a unique integer
    identifier.

    Parameters
    ----------
    G : dict[T, list[T]]
        Dictionary representing the graph.

    directed : bool, optional
        Whether the graph is directed. Defaults to False.

    Examples
    --------
    Undirected graph:

    >>> G1 = {"A": ["B", "D"], "B": ["C"], "C": ["D"], "D": []}
    >>> graph1 = Graph(G1, directed=False)
    >>> graph1.adj_matrix_rep
    array([[0, 1, 0, 1],
           [1, 0, 1, 0],
           [0, 1, 0, 1],
           [1, 0, 1, 0]])

    Directed graph:

    >>> G2 = {"A": ["B", "D"], "B": ["C"], "C": ["D"], "D": []}
    >>> graph2 = Graph(G2, directed=True)
    >>> graph2.adj_matrix_rep
    array([[0, 1, 0, 1],
           [0, 0, 1, 0],
           [0, 0, 0, 1],
           [0, 0, 0, 0]])
    """

    allows_parallel_edges = False


class MultiGraph[T: Hashable](_BaseGraph[T]):
    """
    Represent a directed or undirected multigraph.

    Parallel edges and self-loops are permitted. Every edge receives
    a unique integer identifier, even when multiple edges share
    the same endpoints.

    Parameters
    ----------
    G : dict[T, list[T]]
        Dictionary representing the multigraph.

    directed : bool, optional
        Whether the multigraph is directed. Defaults to False.

    Examples
    --------
    Undirected multigraph:

    >>> G3 = {
    ...     "A": ["B", "D", "E"],
    ...     "B": ["C", "D"],
    ...     "C": ["E"],
    ...     "D": ["A", "C"],
    ...     "E": [],
    ...     "F": []
    ... }
    >>> graph3 = MultiGraph(G3, directed=False)
    >>> graph3.adj_matrix_rep
    array([[0, 1, 0, 2, 1, 0],
           [1, 0, 1, 1, 0, 0],
           [0, 1, 0, 1, 1, 0],
           [2, 1, 1, 0, 0, 0],
           [1, 0, 1, 0, 0, 0],
           [0, 0, 0, 0, 0, 0]])

    >>> graph3.edges[1]
    ('A', 'D')
    >>> graph3.edges[6]
    ('D', 'A')

    Directed multigraph:

    >>> G4 = {"A": ["B", "B"], "B": ["A"], "C": ["A", "C"]}
    >>> graph4 = MultiGraph(G4, directed=True)
    >>> graph4.adj_matrix_rep
    array([[0, 2, 0],
           [1, 0, 0],
           [1, 0, 1]])

    >>> graph4.edges[0]
    ('A', 'B')
    >>> graph4.edges[1]
    ('A', 'B')
    """

    allows_parallel_edges = True