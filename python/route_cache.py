from collections import defaultdict

class RouteCache:
  def __init__(self, myID):
    self.__edge_list = defaultdict(set)
    self.__me = myID

  def offer_route(self, route):
    #attach the route information into the cache
    for i in range(len(route)-1):
      self.add_link(route[i], route[i+1])
    
  def add_link(self, fromID, toID):
    #adds a single link the cache
    self.__edge_list[fromID].add(toID)
    self.__edge_list[toID].add(fromID)

  def remove_link(self, fromID, toID):
    #removes a given link from the cache
    self.__edge_list[fromID].discard(toID)
    self.__edge_list[toID].discard(fromID)
    
  def get_shortest_path(self, toID):
    #perform a simple bfs to find the SSSP
    q = []
    q.append([self.__me])
    visited = set()
    visited.add(self.__me)
    while q:
      path = q.pop(0)
      curr = path[-1]
      if curr == toID:
        return path
      for child in self.__edge_list[curr]:
        if not (child in visited):
          p = list(path)
          p.append(child)
          q.append(p)
          visited.add(child)
    return None
      
      
    
    
if __name__ == '__main__':
  print("Just some testing, don't mind me...")
  rc = RouteCache(5)
  rc.offer_route([1,2,3,5,7,11])
  rc.offer_route([11,5,4,8,9])
  print("{}".format(rc.get_shortest_path(11)))
  rc.remove_link(5, 11)
  print("{}".format(rc.get_shortest_path(11)))
  print("{}".format(rc.get_shortest_path(9)))
  print("{}".format(rc.get_shortest_path(12)))
