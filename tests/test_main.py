import networkx as nx
from itertools import combinations
from dsteiner import directed_steiner_tree
import pytest
import numpy as np


def set_graph(list_of_sets, g=None):
  if g is None:
    g = nx.DiGraph()
  new_nodes = set()
  for s1 in list_of_sets:
    if len(s1) == 0:
      continue
    s1 = frozenset(s1)
    g.add_node(s1)
    for s2 in combinations(s1, r=len(s1)-1):
      s2 = frozenset(s2)
      g.add_edge(s2, s1, weight=10)
      new_nodes.add(s2)
  if new_nodes:
    set_graph(new_nodes, g=g)
  return g


@pytest.mark.parametrize('i', [0, 1, 2])
def test_basic(i):
    S = list([set([1, 2, 3]), set([2, 3, 4]), set([4, 5, ]), set([9])])
    g = set_graph(S)
    sol = directed_steiner_tree(g, len(S) - i, frozenset(), [frozenset(_s) for _s in S])
    print(nx.info(sol))


def test_medium():
  S = list([set([1, 2, 3]), set([2, 3, 4, 5, 6, 7, 8]), set([4, 5, ]), set([9])])

  g = set_graph(S)
  print(nx.info(g))
  sol = directed_steiner_tree(g, len(S), frozenset(), [frozenset(_s) for _s in S])

  print(nx.info(sol))


def test_large():
  S = set()

  for _ in range(20):
    size = np.random.randint(2, 6)
    s = set(np.random.randint(0, 20, size=size))
    S.add(frozenset(s))

  g = set_graph(S)

  print(nx.info(g))

  sol = directed_steiner_tree(g, len(S), frozenset(), S)
  print(nx.info(sol))

