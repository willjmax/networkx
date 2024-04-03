"""Basic algorithms for breadth-first searching the nodes of a graph."""
from collections import deque

import networkx as nx

__all__ = [
    "bfs_edges",
    "bfs_tree",
    "bfs_predecessors",
    "bfs_successors",
    "descendants_at_distance",
    "bfs_layers",
    "bfs_labeled_edges",
    "generic_bfs_edges",
    "lexicographic_bfs"
]


@nx._dispatchable
def generic_bfs_edges(G, source, neighbors=None, depth_limit=None, sort_neighbors=None):
    """Iterate over edges in a breadth-first search.

    The breadth-first search begins at `source` and enqueues the
    neighbors of newly visited nodes specified by the `neighbors`
    function.

    Parameters
    ----------
    G : NetworkX graph

    source : node
        Starting node for the breadth-first search; this function
        iterates over only those edges in the component reachable from
        this node.

    neighbors : function
        A function that takes a newly visited node of the graph as input
        and returns an *iterator* (not just a list) of nodes that are
        neighbors of that node with custom ordering. If not specified, this is
        just the ``G.neighbors`` method, but in general it can be any function
        that returns an iterator over some or all of the neighbors of a
        given node, in any order.

    depth_limit : int, optional(default=len(G))
        Specify the maximum search depth.

    sort_neighbors : Callable (default=None)

        .. deprecated:: 3.2

           The sort_neighbors parameter is deprecated and will be removed in
           version 3.4. A custom (e.g. sorted) ordering of neighbors can be
           specified with the `neighbors` parameter.

        A function that takes an iterator over nodes as the input, and
        returns an iterable of the same nodes with a custom ordering.
        For example, `sorted` will sort the nodes in increasing order.

    Yields
    ------
    edge
        Edges in the breadth-first search starting from `source`.

    Examples
    --------
    >>> G = nx.path_graph(7)
    >>> list(nx.generic_bfs_edges(G, source=0))
    [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6)]
    >>> list(nx.generic_bfs_edges(G, source=2))
    [(2, 1), (2, 3), (1, 0), (3, 4), (4, 5), (5, 6)]
    >>> list(nx.generic_bfs_edges(G, source=2, depth_limit=2))
    [(2, 1), (2, 3), (1, 0), (3, 4)]

    The `neighbors` param can be used to specify the visitation order of each
    node's neighbors generically. In the following example, we modify the default
    neighbor to return *odd* nodes first:

    >>> def odd_first(n):
    ...     return sorted(G.neighbors(n), key=lambda x: x % 2, reverse=True)

    >>> G = nx.star_graph(5)
    >>> list(nx.generic_bfs_edges(G, source=0))  # Default neighbor ordering
    [(0, 1), (0, 2), (0, 3), (0, 4), (0, 5)]
    >>> list(nx.generic_bfs_edges(G, source=0, neighbors=odd_first))
    [(0, 1), (0, 3), (0, 5), (0, 2), (0, 4)]

    Notes
    -----
    This implementation is from `PADS`_, which was in the public domain
    when it was first accessed in July, 2004.  The modifications
    to allow depth limits are based on the Wikipedia article
    "`Depth-limited-search`_".

    .. _PADS: http://www.ics.uci.edu/~eppstein/PADS/BFS.py
    .. _Depth-limited-search: https://en.wikipedia.org/wiki/Depth-limited_search
    """
    if neighbors is None:
        neighbors = G.neighbors
    if sort_neighbors is not None:
        import warnings

        warnings.warn(
            (
                "The sort_neighbors parameter is deprecated and will be removed\n"
                "in NetworkX 3.4, use the neighbors parameter instead."
            ),
            DeprecationWarning,
            stacklevel=2,
        )
        _neighbors = neighbors
        neighbors = lambda node: iter(sort_neighbors(_neighbors(node)))
    if depth_limit is None:
        depth_limit = len(G)

    seen = {source}
    n = len(G)
    depth = 0
    next_parents_children = [(source, neighbors(source))]
    while next_parents_children and depth < depth_limit:
        this_parents_children = next_parents_children
        next_parents_children = []
        for parent, children in this_parents_children:
            for child in children:
                if child not in seen:
                    seen.add(child)
                    next_parents_children.append((child, neighbors(child)))
                    yield parent, child
            if len(seen) == n:
                return
        depth += 1


@nx._dispatchable
def bfs_edges(G, source, reverse=False, depth_limit=None, sort_neighbors=None):
    """Iterate over edges in a breadth-first-search starting at source.

    Parameters
    ----------
    G : NetworkX graph

    source : node
       Specify starting node for breadth-first search; this function
       iterates over only those edges in the component reachable from
       this node.

    reverse : bool, optional
       If True traverse a directed graph in the reverse direction

    depth_limit : int, optional(default=len(G))
        Specify the maximum search depth

    sort_neighbors : function (default=None)
        A function that takes an iterator over nodes as the input, and
        returns an iterable of the same nodes with a custom ordering.
        For example, `sorted` will sort the nodes in increasing order.

    Yields
    ------
    edge: 2-tuple of nodes
       Yields edges resulting from the breadth-first search.

    Examples
    --------
    To get the edges in a breadth-first search::

        >>> G = nx.path_graph(3)
        >>> list(nx.bfs_edges(G, 0))
        [(0, 1), (1, 2)]
        >>> list(nx.bfs_edges(G, source=0, depth_limit=1))
        [(0, 1)]

    To get the nodes in a breadth-first search order::

        >>> G = nx.path_graph(3)
        >>> root = 2
        >>> edges = nx.bfs_edges(G, root)
        >>> nodes = [root] + [v for u, v in edges]
        >>> nodes
        [2, 1, 0]

    Notes
    -----
    The naming of this function is very similar to
    :func:`~networkx.algorithms.traversal.edgebfs.edge_bfs`. The difference
    is that ``edge_bfs`` yields edges even if they extend back to an already
    explored node while this generator yields the edges of the tree that results
    from a breadth-first-search (BFS) so no edges are reported if they extend
    to already explored nodes. That means ``edge_bfs`` reports all edges while
    ``bfs_edges`` only reports those traversed by a node-based BFS. Yet another
    description is that ``bfs_edges`` reports the edges traversed during BFS
    while ``edge_bfs`` reports all edges in the order they are explored.

    Based on the breadth-first search implementation in PADS [1]_
    by D. Eppstein, July 2004; with modifications to allow depth limits
    as described in [2]_.

    References
    ----------
    .. [1] http://www.ics.uci.edu/~eppstein/PADS/BFS.py.
    .. [2] https://en.wikipedia.org/wiki/Depth-limited_search

    See Also
    --------
    bfs_tree
    :func:`~networkx.algorithms.traversal.depth_first_search.dfs_edges`
    :func:`~networkx.algorithms.traversal.edgebfs.edge_bfs`

    """
    if reverse and G.is_directed():
        successors = G.predecessors
    else:
        successors = G.neighbors

    if sort_neighbors is not None:
        yield from generic_bfs_edges(
            G, source, lambda node: iter(sort_neighbors(successors(node))), depth_limit
        )
    else:
        yield from generic_bfs_edges(G, source, successors, depth_limit)


@nx._dispatchable(returns_graph=True)
def bfs_tree(G, source, reverse=False, depth_limit=None, sort_neighbors=None):
    """Returns an oriented tree constructed from of a breadth-first-search
    starting at source.

    Parameters
    ----------
    G : NetworkX graph

    source : node
       Specify starting node for breadth-first search

    reverse : bool, optional
       If True traverse a directed graph in the reverse direction

    depth_limit : int, optional(default=len(G))
        Specify the maximum search depth

    sort_neighbors : function (default=None)
        A function that takes an iterator over nodes as the input, and
        returns an iterable of the same nodes with a custom ordering.
        For example, `sorted` will sort the nodes in increasing order.

    Returns
    -------
    T: NetworkX DiGraph
       An oriented tree

    Examples
    --------
    >>> G = nx.path_graph(3)
    >>> list(nx.bfs_tree(G, 1).edges())
    [(1, 0), (1, 2)]
    >>> H = nx.Graph()
    >>> nx.add_path(H, [0, 1, 2, 3, 4, 5, 6])
    >>> nx.add_path(H, [2, 7, 8, 9, 10])
    >>> sorted(list(nx.bfs_tree(H, source=3, depth_limit=3).edges()))
    [(1, 0), (2, 1), (2, 7), (3, 2), (3, 4), (4, 5), (5, 6), (7, 8)]


    Notes
    -----
    Based on http://www.ics.uci.edu/~eppstein/PADS/BFS.py
    by D. Eppstein, July 2004. The modifications
    to allow depth limits based on the Wikipedia article
    "`Depth-limited-search`_".

    .. _Depth-limited-search: https://en.wikipedia.org/wiki/Depth-limited_search

    See Also
    --------
    dfs_tree
    bfs_edges
    edge_bfs
    """
    T = nx.DiGraph()
    T.add_node(source)
    edges_gen = bfs_edges(
        G,
        source,
        reverse=reverse,
        depth_limit=depth_limit,
        sort_neighbors=sort_neighbors,
    )
    T.add_edges_from(edges_gen)
    return T


@nx._dispatchable
def bfs_predecessors(G, source, depth_limit=None, sort_neighbors=None):
    """Returns an iterator of predecessors in breadth-first-search from source.

    Parameters
    ----------
    G : NetworkX graph

    source : node
       Specify starting node for breadth-first search

    depth_limit : int, optional(default=len(G))
        Specify the maximum search depth

    sort_neighbors : function (default=None)
        A function that takes an iterator over nodes as the input, and
        returns an iterable of the same nodes with a custom ordering.
        For example, `sorted` will sort the nodes in increasing order.

    Returns
    -------
    pred: iterator
        (node, predecessor) iterator where `predecessor` is the predecessor of
        `node` in a breadth first search starting from `source`.

    Examples
    --------
    >>> G = nx.path_graph(3)
    >>> dict(nx.bfs_predecessors(G, 0))
    {1: 0, 2: 1}
    >>> H = nx.Graph()
    >>> H.add_edges_from([(0, 1), (0, 2), (1, 3), (1, 4), (2, 5), (2, 6)])
    >>> dict(nx.bfs_predecessors(H, 0))
    {1: 0, 2: 0, 3: 1, 4: 1, 5: 2, 6: 2}
    >>> M = nx.Graph()
    >>> nx.add_path(M, [0, 1, 2, 3, 4, 5, 6])
    >>> nx.add_path(M, [2, 7, 8, 9, 10])
    >>> sorted(nx.bfs_predecessors(M, source=1, depth_limit=3))
    [(0, 1), (2, 1), (3, 2), (4, 3), (7, 2), (8, 7)]
    >>> N = nx.DiGraph()
    >>> nx.add_path(N, [0, 1, 2, 3, 4, 7])
    >>> nx.add_path(N, [3, 5, 6, 7])
    >>> sorted(nx.bfs_predecessors(N, source=2))
    [(3, 2), (4, 3), (5, 3), (6, 5), (7, 4)]

    Notes
    -----
    Based on http://www.ics.uci.edu/~eppstein/PADS/BFS.py
    by D. Eppstein, July 2004. The modifications
    to allow depth limits based on the Wikipedia article
    "`Depth-limited-search`_".

    .. _Depth-limited-search: https://en.wikipedia.org/wiki/Depth-limited_search

    See Also
    --------
    bfs_tree
    bfs_edges
    edge_bfs
    """
    for s, t in bfs_edges(
        G, source, depth_limit=depth_limit, sort_neighbors=sort_neighbors
    ):
        yield (t, s)


@nx._dispatchable
def bfs_successors(G, source, depth_limit=None, sort_neighbors=None):
    """Returns an iterator of successors in breadth-first-search from source.

    Parameters
    ----------
    G : NetworkX graph

    source : node
       Specify starting node for breadth-first search

    depth_limit : int, optional(default=len(G))
        Specify the maximum search depth

    sort_neighbors : function (default=None)
        A function that takes an iterator over nodes as the input, and
        returns an iterable of the same nodes with a custom ordering.
        For example, `sorted` will sort the nodes in increasing order.

    Returns
    -------
    succ: iterator
       (node, successors) iterator where `successors` is the non-empty list of
       successors of `node` in a breadth first search from `source`.
       To appear in the iterator, `node` must have successors.

    Examples
    --------
    >>> G = nx.path_graph(3)
    >>> dict(nx.bfs_successors(G, 0))
    {0: [1], 1: [2]}
    >>> H = nx.Graph()
    >>> H.add_edges_from([(0, 1), (0, 2), (1, 3), (1, 4), (2, 5), (2, 6)])
    >>> dict(nx.bfs_successors(H, 0))
    {0: [1, 2], 1: [3, 4], 2: [5, 6]}
    >>> G = nx.Graph()
    >>> nx.add_path(G, [0, 1, 2, 3, 4, 5, 6])
    >>> nx.add_path(G, [2, 7, 8, 9, 10])
    >>> dict(nx.bfs_successors(G, source=1, depth_limit=3))
    {1: [0, 2], 2: [3, 7], 3: [4], 7: [8]}
    >>> G = nx.DiGraph()
    >>> nx.add_path(G, [0, 1, 2, 3, 4, 5])
    >>> dict(nx.bfs_successors(G, source=3))
    {3: [4], 4: [5]}

    Notes
    -----
    Based on http://www.ics.uci.edu/~eppstein/PADS/BFS.py
    by D. Eppstein, July 2004.The modifications
    to allow depth limits based on the Wikipedia article
    "`Depth-limited-search`_".

    .. _Depth-limited-search: https://en.wikipedia.org/wiki/Depth-limited_search

    See Also
    --------
    bfs_tree
    bfs_edges
    edge_bfs
    """
    parent = source
    children = []
    for p, c in bfs_edges(
        G, source, depth_limit=depth_limit, sort_neighbors=sort_neighbors
    ):
        if p == parent:
            children.append(c)
            continue
        yield (parent, children)
        children = [c]
        parent = p
    yield (parent, children)


@nx._dispatchable
def bfs_layers(G, sources):
    """Returns an iterator of all the layers in breadth-first search traversal.

    Parameters
    ----------
    G : NetworkX graph
        A graph over which to find the layers using breadth-first search.

    sources : node in `G` or list of nodes in `G`
        Specify starting nodes for single source or multiple sources breadth-first search

    Yields
    ------
    layer: list of nodes
        Yields list of nodes at the same distance from sources

    Examples
    --------
    >>> G = nx.path_graph(5)
    >>> dict(enumerate(nx.bfs_layers(G, [0, 4])))
    {0: [0, 4], 1: [1, 3], 2: [2]}
    >>> H = nx.Graph()
    >>> H.add_edges_from([(0, 1), (0, 2), (1, 3), (1, 4), (2, 5), (2, 6)])
    >>> dict(enumerate(nx.bfs_layers(H, [1])))
    {0: [1], 1: [0, 3, 4], 2: [2], 3: [5, 6]}
    >>> dict(enumerate(nx.bfs_layers(H, [1, 6])))
    {0: [1, 6], 1: [0, 3, 4, 2], 2: [5]}
    """
    if sources in G:
        sources = [sources]

    current_layer = list(sources)
    visited = set(sources)

    for source in current_layer:
        if source not in G:
            raise nx.NetworkXError(f"The node {source} is not in the graph.")

    # this is basically BFS, except that the current layer only stores the nodes at
    # same distance from sources at each iteration
    while current_layer:
        yield current_layer
        next_layer = []
        for node in current_layer:
            for child in G[node]:
                if child not in visited:
                    visited.add(child)
                    next_layer.append(child)
        current_layer = next_layer


REVERSE_EDGE = "reverse"
TREE_EDGE = "tree"
FORWARD_EDGE = "forward"
LEVEL_EDGE = "level"


@nx._dispatchable
def bfs_labeled_edges(G, sources):
    """Iterate over edges in a breadth-first search (BFS) labeled by type.

    We generate triple of the form (*u*, *v*, *d*), where (*u*, *v*) is the
    edge being explored in the breadth-first search and *d* is one of the
    strings 'tree', 'forward', 'level', or 'reverse'.  A 'tree' edge is one in
    which *v* is first discovered and placed into the layer below *u*.  A
    'forward' edge is one in which *u* is on the layer above *v* and *v* has
    already been discovered.  A 'level' edge is one in which both *u* and *v*
    occur on the same layer.  A 'reverse' edge is one in which *u* is on a layer
    below *v*.

    We emit each edge exactly once.  In an undirected graph, 'reverse' edges do
    not occur, because each is discovered either as a 'tree' or 'forward' edge.

    Parameters
    ----------
    G : NetworkX graph
        A graph over which to find the layers using breadth-first search.

    sources : node in `G` or list of nodes in `G`
        Starting nodes for single source or multiple sources breadth-first search

    Yields
    ------
    edges: generator
       A generator of triples (*u*, *v*, *d*) where (*u*, *v*) is the edge being
       explored and *d* is described above.

    Examples
    --------
    >>> G = nx.cycle_graph(4, create_using=nx.DiGraph)
    >>> list(nx.bfs_labeled_edges(G, 0))
    [(0, 1, 'tree'), (1, 2, 'tree'), (2, 3, 'tree'), (3, 0, 'reverse')]
    >>> G = nx.complete_graph(3)
    >>> list(nx.bfs_labeled_edges(G, 0))
    [(0, 1, 'tree'), (0, 2, 'tree'), (1, 2, 'level')]
    >>> list(nx.bfs_labeled_edges(G, [0, 1]))
    [(0, 1, 'level'), (0, 2, 'tree'), (1, 2, 'forward')]
    """
    if sources in G:
        sources = [sources]

    neighbors = G._adj
    directed = G.is_directed()
    visited = set()
    visit = visited.discard if directed else visited.add
    # We use visited in a negative sense, so the visited set stays empty for the
    # directed case and level edges are reported on their first occurrence in
    # the undirected case.  Note our use of visited.discard -- this is built-in
    # thus somewhat faster than a python-defined def nop(x): pass
    depth = {s: 0 for s in sources}
    queue = deque(depth.items())
    push = queue.append
    pop = queue.popleft
    while queue:
        u, du = pop()
        for v in neighbors[u]:
            if v not in depth:
                depth[v] = dv = du + 1
                push((v, dv))
                yield u, v, TREE_EDGE
            else:
                dv = depth[v]
                if du == dv:
                    if v not in visited:
                        yield u, v, LEVEL_EDGE
                elif du < dv:
                    yield u, v, FORWARD_EDGE
                elif directed:
                    yield u, v, REVERSE_EDGE
        visit(u)


@nx._dispatchable
def descendants_at_distance(G, source, distance):
    """Returns all nodes at a fixed `distance` from `source` in `G`.

    Parameters
    ----------
    G : NetworkX graph
        A graph
    source : node in `G`
    distance : the distance of the wanted nodes from `source`

    Returns
    -------
    set()
        The descendants of `source` in `G` at the given `distance` from `source`

    Examples
    --------
    >>> G = nx.path_graph(5)
    >>> nx.descendants_at_distance(G, 2, 2)
    {0, 4}
    >>> H = nx.DiGraph()
    >>> H.add_edges_from([(0, 1), (0, 2), (1, 3), (1, 4), (2, 5), (2, 6)])
    >>> nx.descendants_at_distance(H, 0, 2)
    {3, 4, 5, 6}
    >>> nx.descendants_at_distance(H, 5, 0)
    {5}
    >>> nx.descendants_at_distance(H, 5, 1)
    set()
    """
    if source not in G:
        raise nx.NetworkXError(f"The node {source} is not in the graph.")

    bfs_generator = nx.bfs_layers(G, source)
    for i, layer in enumerate(bfs_generator):
        if i == distance:
            return set(layer)
    return set()


def lexicographic_bfs(G, minus=False, initial_order=None):
    """Returns a lexicographic breadth-first ordering.

    Parameters
    ----------
    G : NetworkX graph
        Undirected graph

    minus : boolean
        If minus=True the LexBFS- algorithm will be performed. LexBFS is
        essentially just LexBFS on the complement graph. See [2] for a
        reference.

    inital_order : List of vertices
        A subset of vertices. The ordering defines the priority
        used to break ties within hte LexBFS algorithm.
    
    Returns
    -------
    order : Dictionary
        A lexicographic ordering of the vertices of G in the form 
        {vertex : int}

    Notes
    -----
    This implementation uses partition refinement and is
    based off the pseudo code given in
    https://en.wikipedia.org/wiki/Lexicographic_breadth-first_search

    References
    ----------
    [1] Algorithmic Aspects of Vertex Elimination on Graphs
        Donald J. Rose, R. Endre Tarjan, and George S. Lueker
        https://doi.org/10.1137/0205021

    [2] A Simple Linear Time LexBFS Cograph Recognition Algorithm
        Anna Bretscher, Derek Corneil, Michel Habib & Christophe Paul 
        https://doi.org/10.1007/978-3-540-39890-5_11
    """
    if len(G.nodes) == 0:
        return {}

    if initial_order is None:
        initial_order = []

    # set direction that new sets are inserted
    if minus:
        d1 = "prev"
        d2 = "next"
    else:
        d1 = "next"
        d2 = "prev"

    vertices = set(G.nodes)
    n = len(G.nodes)
    lookup = {}

    # initialize ordered set
    if initial_order:
        head = {"next": None, "prev": None, "vertex": initial_order[0]}
        tail = head
        lookup[initial_order[0]] = head
        vertices.remove(initial_order[0])

        for v in initial_order[1:]:
            new_vertex = {"next": None, "prev": tail, "vertex": v}
            tail["next"] = new_vertex
            tail = new_vertex
            lookup[v] = new_vertex
            vertices.remove(v)
    else:
        v = vertices.pop()
        head = {"next": None, "prev": None, "vertex": v}
        tail = head
        lookup[v] = head

    # handle unordered vertices
    for v in vertices:
        new_vertex = {"next": None, "prev": tail, "vertex": v}
        tail["next"] = new_vertex
        tail = new_vertex
        lookup[v] = new_vertex

    # order neighborhoods based on initial_order
    neighborhoods, edge_lookup = _sort_adjacency_lists(G, initial_order)

    first_set = {
        "next": None,
        "prev": None,
        "set_head": head,
        "set_tail": tail,
        "lookup": lookup,
        "last_processed": 0,
    }
    get_set = {v: first_set for v in G.nodes}
    order = {}
    i = 1

    while first_set:
        v = first_set["set_head"]["vertex"]
        first_set["set_head"] = first_set["set_head"]["next"]

        if first_set["set_head"]:
            first_set["set_head"]["prev"] = None

        first_set["lookup"].pop(v)

        if not first_set["set_head"]:
            if first_set["next"]:
                first_set["next"]["prev"] = None

            first_set = first_set["next"]

        get_set[v] = None
        neighbor = neighborhoods[v]["head"]

        while neighbor is not None:
            u = neighbor["vertex"]
            S = get_set[u]

            if S is None:
                neighbor = neighbor["next"]
                continue

            # add u to T
            # By default, d1='next' and d2='prev'
            # In minus mode, d1='prev' and d2='next'
            if S["last_processed"] < i:
                head = {"next": None, "prev": None, "vertex": u}
                tail = head
                T = {
                    d1: S,
                    d2: S[d2],
                    "set_head": head,
                    "set_tail": tail,
                    "lookup": {},
                    "last_processed": 0,
                }

                if S[d2]:
                    S[d2][d1] = T
                S[d2] = T
                S[d2]["lookup"][u] = head
                S["last_processed"] = i

                # By default a set may be placed in front of the first set
                # This does not happen in minus mode
                if S is first_set and not minus:
                    first_set = T
            else:
                new_vertex = {"next": None, "prev": S[d2]["set_tail"], "vertex": u}
                S[d2]["set_tail"]["next"] = new_vertex
                S[d2]["set_tail"] = new_vertex
                S[d2]["lookup"][u] = new_vertex

            get_set[u] = S[d2]

            # remove u from S
            old_vertex = S["lookup"][u]
            S["lookup"].pop(u)
            if old_vertex is S["set_head"]:
                S["set_head"] = old_vertex["next"]
            else:
                old_vertex["prev"]["next"] = old_vertex["next"]

            if old_vertex is S["set_tail"]:
                S["set_tail"] = old_vertex["prev"]
            else:
                old_vertex["next"]["prev"] = old_vertex["prev"]

            if S["set_head"] is None:
                if S["prev"]:
                    S["prev"]["next"] = S["next"]
                if S["next"]:
                    S["next"]["prev"] = S["prev"]
                if S is first_set:
                    first_set = S["next"]
                del S

            neighbor = neighbor["next"]

        i = i + 1
        yield v

    #return order


def _sort_adjacency_lists(G, order):
    vertices = set(G.nodes)
    heads = {
        v: {
            "next": None,
            "prev": None,
            "vertex": None,
        }
        for v in G.nodes
    }
    tails = {v: heads[v] for v in G.nodes}
    lookup = {}

    # handle ordered vertices
    for v in order:
        _append_to_adjacency_list(G, v, heads, tails, lookup)
        vertices.remove(v)

    # handle unordered vertices
    for v in vertices:
        _append_to_adjacency_list(G, v, heads, tails, lookup)

    adj_lists = {v: {"head": heads[v], "tail": tails[v]} for v in G.nodes}

    return adj_lists, lookup


def _append_to_adjacency_list(G, v, heads, tails, lookup):
    for e in G.edges(v):
        u = e[1]
        if heads[u]["vertex"] is None:
            heads[u]["vertex"] = v
        else:
            new_vertex = {"next": None, "prev": tails[u], "vertex": v}
            tails[u]["next"] = new_vertex
            tails[u] = new_vertex
            lookup[(u, v)] = new_vertex
