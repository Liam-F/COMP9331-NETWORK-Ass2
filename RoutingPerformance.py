# COMP3331/9331 Computer Network and Applications
# Written by Stephen Wang and Zachary He for Assessment 2
# The topic of the assessment is about using 3 different router Algorithms to compute the shortest path in a topology network.

#!/usr/bin/python3

import re
import sys
import math
import queue
import time


# graph data structure
class Graph:
     # Class Constructor
     # self referes to the object being called on
     def __init__(self):
          # init dict for vertices
          self.vertList = {}
          # init new vert count
          self.numVertices = 0
          # add a vertex to the graph, updating count etc.
          # better to use the add edge method below
     def addVertex(self, name):
          # method called on graph, increments the vert count
          self.numVertices = self.numVertices+1
          newVertex = Vertex(name)
          self.vertList[name] = newVertex
          return newVertex
     # check a vertex and return its value etc.
     def getVertex(self, vertex):
          if vertex in self.vertList:
               return self.vertList[vertex]
          else:
               return None
     # __contains__ used for:  'for key in object:'
     def __contains__(self,vertex ):
          return vertex in self.vertList
     # add an edge, populate req. members of class
     def addEdge(self, v1, v2, edge):
          if v1 not in self.vertList:
               nv = self.addVertex(v1)
          if v2 not in self.vertList:
               nv = self.addVertex(v2)
          self.vertList[v1].addNeighbor(self.vertList[v2], edge)
          # return vert keys (ie, all the of the node names)
     def getVertices(self):
          return self.vertList.keys()
     # iterator for class
     def __iter__(self):
          return iter(self.vertList.values())
     def numVertices(self):
          return self.numVertices


# class for vertex/node information
class Vertex:
     # Class Constructor
     # initialise new vertex
     def __init__(self, name):
          self.id = name
          self.connectedTo = {}

     # add connected nodes
     def addNeighbor(self, neighbor, edge):
          self.connectedTo[neighbor] = edge
     # return the string (for printing)
     def __str__(self):
          return str(self.id)
     # return the keys from the connectedTo dict
     def checkConnAvailability(self, neighbor, startTime):
          if self.connectedTo[neighbor].checkConnection(startTime):
               return 1
          return 0
     # sets the connection end time of the edge for the new request
     def setUsedConnection(self, neighbor, endTime):
          self.connectedTo[neighbor].setConnection(endTime)
     # returns a list of connected routers
     def getConnections(self):
          return self.connectedTo.keys()
     # returns the id (name) of the router
     def getId(self):
          return self.id
     # returns the propagation delay of the link between the router and the suplied neighbour router
     def getDelay(self, neighbor):
          return self.connectedTo[neighbor].getDelay()
     # returns the capacity of the link between the router and the supplied neighbour router
     def getCapacityRatio(self, neighbor, startTime):
          return self.connectedTo[neighbor].getRatio(startTime)
     # returns the max capacity of the link between the router and the supplied neighbour router
     def getCapacity(self, neighbor):
          return self.connectedTo[neighbor].getCapacity()



#############################################################################################


# edge data structure
class Edge:
   
   # Class Constructor
   # delay = propegation delay for edge
   # capacity = number of connections allowed over connection
   # usedConn = number of connections curently in use in edge
   # conn = finishing times of the current connections
   def __init__(self, delay, capacity):
      self.delay = float(delay)
      self.capacity = int(capacity)
      self.usedConn = 0
      self.conn = []
   
   # returns delay of current edge
   def getDelay(self):
      return self.delay
   
   # populate the connections array if there is an available space
   # return 1 on success, 0 on failure condition
   def checkConnection(self, startTime):
      self.updateEdge(startTime)
      if self.usedConn < self.capacity:
         return 1
      return 0
   
   # sets a used connection and end time of the connection
   def setConnection(self, endTime):
      self.usedConn += 1
      self.conn.append(endTime)
   
   # updates the list of connections,
   # ie, remove if the connection has expired
   def updateEdge(self, time):
      for timeCursor in self.conn:
         if timeCursor <= time:
            #print "%f %f\n" % (timeCursor, time)
            self.conn.pop(self.conn.index(timeCursor))
            self.usedConn -= 1
      return
   
   # checks the active connecitons on the edge at time (start)
   def checkEdge(self, start):
      available = 0
      for timeCursor in self.conn:
         if timeCursor <= start:
            available += 1
      return float(self.usedConn-available)/self.capacity
   
   # returns the ratio of current connections and capcity of the edge at the given startTime
   def getRatio(self, startTime):
      ratio = self.checkEdge(startTime)
      return float(ratio)
   
   # returns the max connection capacity of the edge
   def getCapacity(self):
      return self.capacity





# circuit network
class Request:
   
     # class constructor
     # start = connection start time
     # nodeFrom = starting node in connection
     # nodeTo = destination node in connection
     # end = end time of the connection (start time + total duration of connection)
     # numPackets = number of packets sent over the duration of the connection
     def __init__(self, start, nodeFrom, nodeTo, duration, packetRate):
          self.start = float(start)
          self.nodeFrom = nodeFrom
          self.nodeTo = nodeTo
          self.end = float(float(start) + float(duration))
          self.numPackets = int(math.ceil((packetRate) * float(duration)))
   
     # returns start time of connection
     def getStart(self):
          return self.start

     # returns end time of connection
     def getEnd(self):
          return self.end

     # returns start node in connection
     def getNodeFrom(self):
          return self.nodeFrom

     # returns end node in connection
     def getNodeTo(self):
          return self.nodeTo

     # prints all Request class fields
     def printRequest(self):
          print (self.start)
          print (self.nodeFrom)
          print (self.nodeTo)
          print (self.end)
          print (self.numPackets)
     # returns total number of packets for the request
     def getNumPackets(self):
          return self.numPackets

#############################################################################################


# packet network
class PacketRequest(Request):
     # class constructor
     # Request fields
     # packets = array of all packet start and end times in the connection
     # secPerPacket = number of seconds between the transmission of each packet
     # currPacket = current number of packets that have been transmitted
     def __init__(self, start, nodeFrom, nodeTo, duration, packetRate):
          Request.__init__(self, start, nodeFrom, nodeTo, duration, packetRate)
          self.packets = []
          self.secPerPacket = 1/float(packetRate)
          self.currPacket = 0
          self.setPackets()
     # sets the packets array
     # each element of the array contains a tuple of start and end time for each packet required to be sent over the connection
     # start = start time of the connection + the total duration the previously sent packets
     # end time = start time of connection + total duration of the previously sent packets + the delay between sending each packet (secPerPacket)
     def setPackets(self):
          start = Request.getStart(self)
          end = start + self.secPerPacket
          while end < Request.getEnd(self):
               self.packets.append((start, end))
               start = end
               end = start + self.secPerPacket
          self.packets.append((start, Request.getEnd(self)))
          # returns the start time of the current packet
     def getPacketStart(self):
          if self.currPacket < Request.getNumPackets(self):
               return self.packets[self.currPacket][0]
          return
     # returns the end time of the current packet
     def getPacketEnd(self):
          if self.currPacket < Request.getNumPackets(self):
               self.currPacket += 1
               return self.packets[self.currPacket-1][1]
          return self.end
     # prints start and end times of the current packet
     def printPackets(self):
          while self.currPacket < Request.getNumPackets(self):
               print(self.getPacketStart())
               print(self.getPacketEnd())



################################################################################

# prints the final statistics for the network
def printResults ():
   
     print("total number of virtual circuit requests: %d\n" % (totalRequests))
     print("total number of packets: %d\n" % (totalPackets))
     print("number of successfully routed packets: %d\n" % (totalSuccessPackets))
     print("percentage of successfully routed packets: %.2f\n" % (float(totalSuccessPackets)/float(totalPackets)*100))
     print("number of blocked packets: %d\n" % (totalPackets - totalSuccessPackets))
     print("percentage of blocked packets: %.2f\n" % (float(totalPackets - (totalSuccessPackets))/float(totalPackets)*100))
     print("average number of hops per circuit: %.2f\n" % (float(totalHops)/float(totalSuccessCircuit)))
     print("average cumulative propagation delay per circuit: %.2f\n" % (float(totalDelay)/float(totalSuccessCircuit)))
     end_time = time.clock()
     duration_time = end_time-start_time
     print("running time is: %.2f\n" % float(duration_time))


# passes the requests for the circuit network to the routing protocol
def getCircuitRequests (workLoadArray, protocol, newGraph):
   
     global totalSuccessPackets
     global totalSuccessCircuit
     global totalPackets
   
     for request in workLoadArray:
          totalPackets += request.getNumPackets()
          source = request.getNodeFrom()
          dest = request.getNodeTo()
          start = request.getStart()
          finish = request.getEnd()
          if (protocol == "SHP"): result = shortestHopPath(source, dest,start, finish, newGraph)
          if (protocol == "SDP"): result = shortestDelayPath(source, dest,start, finish, newGraph)
          if (protocol == "LLP"): result = leastLoadedPath(source, dest, start, finish, newGraph)
          totalSuccessPackets += (result * request.getNumPackets())
          totalSuccessCircuit += result


# passes the requests for the packet circuit to the routing protocol
def getPacketRequests (workLoadArray, protocol, newGraph):
   
     global totalSuccessPackets
     global totalSuccessCircuit
     global totalPackets
   
     for request in workLoadArray:
          finish = 0
          source = request.getNodeFrom()
          dest = request.getNodeTo()
          while finish != request.getEnd():
               start = request.getPacketStart()
               finish = request.getPacketEnd()
               if (protocol == "SHP"): result = shortestHopPath(source, dest,start, finish, newGraph)
               if (protocol == "SDP"): result = shortestDelayPath(source, dest,start, finish, newGraph)
               if (protocol == "LLP"): result = leastLoadedPath(source, dest, start, finish, newGraph)
               totalPackets += 1
               totalSuccessPackets += result
               totalSuccessCircuit += result


# determines if the path selected by the routing algorithm is available
# returns 1 if available, 0 if unavailable
def checkResources(nodeList, start, end):
     available = 0
     i=1
     while i<len(nodeList):
          if nodeList[i-1].checkConnAvailability(nodeList[i], start):
               available += 1
          i += 1
     if available == len(nodeList)-1:
          i=1
          while i<len(nodeList):
               nodeList[i-1].setUsedConnection(nodeList[i], end)
               i += 1
          return 1
     else:
          return 0

# algorithm for the shortest hop path protocol
def shortestHopPath(source, target, startTime, endTime, newGraph):
     global totalHops
     global totalDelay
     global totalRequests
     totalRequests += 1
     distance = {}
   #distance[source] = 0
     previous = {}
     vertList = {}
   
     printList = []
   
     delay = 0
   
   
     for vertex in newGraph:
          if (vertex != source):
               distance[vertex] = 9999999999
               previous[vertex] = "undefined"
          vertList[vertex] = distance[vertex]
     currentNode = newGraph.getVertex(source)
     targetNode = newGraph.getVertex(target)
   
     distance[currentNode] = 0
   
     while(currentNode != targetNode):
          del vertList[currentNode]
          connectionList = currentNode.getConnections()

          for vertex in connectionList:
               altRoute = distance[currentNode] + 1
         
               if (altRoute < distance[vertex]):
                    distance[vertex] = altRoute
                    previous[vertex] = currentNode
                    vertList[vertex] = distance[vertex]
          currentNode = sorted(vertList, key=vertList.get)[0]

     tempNode = targetNode
     sumDistance = 0
     found = 0
     printList.append(targetNode)
   
     while (previous[tempNode] != "undefined"):
          printList.append(previous[tempNode])
          delay += int(tempNode.getDelay(previous[tempNode]))
          sumDistance += 1
          tempNode = previous[tempNode]
   
     if checkResources(printList,startTime, endTime):
          totalHops += sumDistance
          totalDelay += delay
          return 1
     else:
          return 0


def shortestDelayPath(source, target, startTime, endTime, newGraph):
     global totalHops
     global totalDelay
     global totalRequests
     totalRequests += 1
     distance = {}
     distance[source] = 0
     previous = {}
     vertList = {}
     printList = []
     delay = 0
   
     for vertex in newGraph:
          if (vertex != source):
               distance[vertex] = 9999999999
               previous[vertex] = "undefined"
          vertList[vertex] = distance[vertex]
     currentNode = newGraph.getVertex(source)
     targetNode = newGraph.getVertex(target)
   
     distance[currentNode] = 0

     while(currentNode != targetNode):
          del vertList[currentNode]
          connectionList = currentNode.getConnections()
          for vertex in connectionList:
               altRoute = distance[currentNode] + int(currentNode.getDelay(vertex))
         
               if (altRoute < distance[vertex]):
                    distance[vertex] = altRoute
                    previous[vertex] = currentNode
                    vertList[vertex] = distance[vertex]
          currentNode = sorted(vertList, key=vertList.get)[0]
   
     tempNode = targetNode
     sumDistance = 0
     printList.append(targetNode)

     while (previous[tempNode] != "undefined"):
          printList.append(previous[tempNode])
          delay += int(tempNode.getDelay(previous[tempNode]))
          sumDistance += 1
          tempNode = previous[tempNode]
     if checkResources(printList, startTime, endTime):
          totalHops += sumDistance
          totalDelay += delay
          return 1
     else:
          return 0


def leastLoadedPath(source, target, startTime, endTime, newGraph):
     global totalHops
     global totalDelay
     global totalRequests
     totalRequests += 1
     distance = {}
     previous = {}
     vertList = {}

     printList = []

     delay = 0

     for vertex in newGraph:
          if (vertex != source):
               distance[vertex] = 9999999999
               previous[vertex] = "undefined"
          vertList[vertex] = distance[vertex]
     # vertlist is now a "priorityqueue"
     currentNode = newGraph.getVertex(source)
     targetNode = newGraph.getVertex(target)

     distance[currentNode] = 0
   
     while(currentNode != targetNode):
          del vertList[currentNode]
          connectionList = currentNode.getConnections()
          for vertex in connectionList:
               altRoute = float(currentNode.getCapacityRatio(vertex, startTime))

               if altRoute < distance[currentNode]:
                    altRoute = distance[currentNode]

               if (altRoute < distance[vertex]):
                    distance[vertex] = altRoute
                    previous[vertex] = currentNode
                    vertList[vertex] = distance[vertex]
      
          currentNode = sorted(vertList, key=vertList.get)[0]
     tempNode = targetNode
     sumDistance = 0

     printList.append(targetNode)

     while (previous[tempNode] != "undefined"):
          printList.append(previous[tempNode])
          delay += int(tempNode.getDelay(previous[tempNode]))
          sumDistance += 1
          tempNode = previous[tempNode]
     if checkResources(printList, startTime, endTime):
          totalHops += sumDistance
          totalDelay += delay
          return 1
     else:
          return 0


######################        main      function       ######################

def main():
     #Create a Graph
     newGraph = Graph()

     ####    initialize the arguments

     Network_Scheme = sys.argv[1]    # input "CIRCUIT" or "PACKET"
     Routing_Scheme = sys.argv[2]    # input "SHP", "SDP", "LLP"
     Topology_File = sys.argv[3]     # Topology_file
     Workload_File = sys.argv[4]     # Workload_file
     Packet_rate = int(sys.argv[5])  # input a positive integer to show the number of packets per second



     # graph topology file decomposite
     topologyFile = [line.rstrip() for line in open(Topology_File)]

     # network workload file decomposite
     workloadFile = [line.rstrip() for line in open(Workload_File)]

     # make a list of connections
     for line in topologyFile:
          connection = line.split(" ")
          node1 = connection.pop(0)
          node2 = connection.pop(0)
          edge = Edge(connection.pop(0), connection.pop(0))
          # add double directed edge to make graph undirected
          newGraph.addEdge(node1, node2, edge)
          newGraph.addEdge(node2, node1, edge)

     # Request objects array
     workLoadArray = []

     for line in workloadFile:
          request = line.split(" ")
          if len(request) < 4:
               break
          if (Network_Scheme == "PACKET"):
               # constructs a new packet request
               currRequest = PacketRequest(request.pop(0), request.pop(0), request.pop(0), request.pop(0), Packet_rate)
          else:
               # constructs a new circuit request
               currRequest = Request(request.pop(0), request.pop(0), request.pop(0), request.pop(0), Packet_rate)

          workLoadArray.append(currRequest)

          
     if Network_Scheme == "PACKET":
          getPacketRequests(workLoadArray, Routing_Scheme, newGraph)
     else:
          getCircuitRequests(workLoadArray, Routing_Scheme, newGraph)

     printResults()




global totalPackets
global totalRequests
global totalHops
global totalDelay
global totalSuccessPackets
global totalSuccessCircuit

totalRequests = 0
totalPackets = 0
totalHops = 0
totalDelay = 0
totalSuccessPackets = 0
totalSuccessCircuit = 0


if __name__ == "__main__":
    start_time = time.clock() 
    main()
