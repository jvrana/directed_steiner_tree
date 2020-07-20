"""dsteiner/__init__.py"""


from typing import *
import networkx as nx
import numpy as np
import functools


def longest_shortest_path(g, src: List[Hashable], dest: List[Hashable]):
  nodelist = list(g.nodes())
  if src not in nodelist:
    return np.inf
  else:
    src_index = nodelist.index(src)
  dest_indices = []
  for _dest in dest:
    if _dest not in nodelist:
      pass
    else:
      dest_indices.append(nodelist.index(_dest))
  if not dest_indices:
    return np.inf

  w = nx.floyd_warshall_numpy(g, nodelist=nodelist)
  return w[src_index, dest_indices].max()




@functools.lru_cache()
def cost(g, r, terminal_nodes):
  found = terminal_nodes.intersection(set(g.nodes()))
  if len(found) == 0:
    return np.inf
  return g.number_of_edges() / len(found)

@functools.lru_cache()
def path_cost(g, root, terminal_nodes):
  """Alternative cost function that accounts for the 'longest shortest-path'"""
  found = terminal_nodes.intersection(set(g.nodes()))
  if len(found) == 0:
    return np.inf

  x = longest_shortest_path(g, root, terminal_nodes)
  return (x + g.number_of_edges()) / len(found)


# cost = path_cost

# TODO: implement edge weighted
# TODO: implement generic pairs
# TODO: implement 'longest shortest path'
@functools.lru_cache()
def _recursive_d_steiner(g: nx.DiGraph, k: int, r: Hashable, t: Set[Hashable], i=0):
  reachable_nodes = set(nx.bfs_tree(g, r).nodes())
  reachable_terminal_nodes = t.intersection(reachable_nodes)

  # initialize tree
  tree = nx.DiGraph()

  # TODO: do we need to add the root node??
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
          t_best_cost = cost(t_best, r, t)
        else:
          # update the best tree
          _tree_cost = cost(_tree, r, t)
          if _tree_cost < t_best_cost:
            t_best = _tree
            t_best_cost = _tree_cost

    # union of tree and best_tree for k terminal nodes
    if t_best.number_of_nodes():
      tree = nx.compose(tree, t_best)
    elif not tree.number_of_nodes():
      tree = t_best

    # each loop should be guaranteed to find k terminal nodes
    t_best_nodes = set(t_best.nodes())
    n_term = len(t.intersection(t_best_nodes))
    if n_term == 0:
      raise Exception("({}) Did not find {} terminal node(s). {}".format(i, k, t))

    # update terminal nodes
    k = k - n_term
    t = frozenset(t - t_best_nodes)

  return tree


def directed_steiner_tree(g: nx.DiGraph, k: int, r: Hashable, t: Set[Hashable]):
  """
  Approximate the optimal steiner tree rooted at 'r' to set of 'k' terminal nodes
  't'.

  :param g: directed networkx graph
  :param k: number of terminal nodes to find a steiner tree for
  :param r: root node
  :param t: set of terminal nodes
  :return: approximate steiner tree
  """

  if isinstance(t, list):
    t = frozenset(t)
  elif isinstance(t, tuple):
    t = frozenset(t)
  elif isinstance(t, set):
    t = frozenset(t)

  return _recursive_d_steiner(g, k, r, t)