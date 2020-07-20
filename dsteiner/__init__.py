# cleaned version
from typing import *
import networkx as nx
import numpy as np
import functools


@functools.lru_cache()
def cost(g, terminal_nodes):
  e = g.number_of_edges()
  k = 0
  # found = terminal_nodes.intersection(set(g.nodes()))

  for n in terminal_nodes:
    if n in g.nodes():
      k += 1
  if k == 0:
    return np.inf
  return e / k


# def get_shortest_path_graph(g, source, target):
#   try:
#     path = nx.shortest_path(g, source=source, target=target)
#     return g.subgraph(path)
#   except nx.NetworkXNoPath:
#     return nx.DiGraph()


def has_path(g, n1, n2):
  if n1 in g and n2 in g[n1]:
    return True
  return False

@functools.lru_cache()
def _recursive_d_steiner(g: nx.DiGraph, k: int, r: Hashable, t: Set[Hashable], i=0):
  reachable_nodes = set(nx.bfs_tree(g, r).nodes())
  reachable_terminal_nodes = t.intersection(reachable_nodes)

  # initialize tree
  tree = nx.DiGraph()
  # tree.add_node(r)

  # terminate early if k terminals are not reachable
  if k > len(reachable_terminal_nodes):
    return tree

  while k > 0:
    # greedily find the best tree for the most terminal nodes possible

    # initialize a new tree
    t_best = nx.DiGraph()
    t_best.add_node(r)

    # for all reachable nodes
    t_best_cost = None
    for v in g.successors(r):
      if v == r:
        continue

      # recursively evaluate best steiner trees containing k' terminal nodes
      for _k in range(1, k+1):
        # propose a new tree as the union of path P(r,v) and T(k', v, t)
        _tree = _recursive_d_steiner(g, _k, v, t, i+1)
        _tree.add_edge(r, v)
        if t_best_cost is None:
          t_best = _tree
          t_best_cost = cost(t_best, t)
        else:
          # update the best tree
          _tree_cost = cost(_tree, t)
          if _tree_cost < t_best_cost:
            t_best = _tree
            t_best_cost = _tree_cost

    # union of tree and best_tree for k terminal nodes
    if t_best.number_of_nodes():
      tree = nx.compose(tree, t_best)
    elif not tree.number_of_nodes():
      tree = t_best

    # each loop should be guaranteed to find k terminal nodes
    n_term = len(t.intersection(set(t_best.nodes())))
    if n_term == 0:
      raise Exception("({}) Did not find {} terminal node(s). {}".format(i, k, t))

    # update terminal nodes
    k = k - len(t.intersection(set(t_best.nodes())))
    t = frozenset(t - set(t_best.nodes()))

  return tree


def directed_steiner_tree(g: nx.DiGraph, k: int, r: Hashable, t: Set[Hashable]):

  if isinstance(t, list):
    t = frozenset(t)
  elif isinstance(t, tuple):
    t = frozenset(t)
  elif isinstance(t, set):
    t = frozenset(t)

  return _recursive_d_steiner(g, k, r, t)