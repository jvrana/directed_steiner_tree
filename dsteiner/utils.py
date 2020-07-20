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