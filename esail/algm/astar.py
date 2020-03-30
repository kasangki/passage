from __future__ import print_function
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from .mongo_database import MongoDatabase
import pandas as pd
import numpy as np

class AStarGraph(object):
    # Define a class board like grid with two barriers

    def __init__(self):

        self.barriers = []
        self.lat_start = 0
        self.lat_dest  = 0
        self.long_start = 0
        self.long_dest = 0

    def set_boundary(self,lat_start,lat_dest,long_start,long_dest):
        self.lat_start = lat_start
        self.lat_dest  = lat_dest
        self.long_start = long_start
        self.long_dest = long_dest

    def heuristic(self, start, goal):
        # Use Chebyshev distance heuristic if we can move one square either
        # adjacent or diagonal
        D = 1
        D2 = 1
        dx = abs(start[0] - goal[0])
        dy = abs(start[1] - goal[1])
        heu_value = round((D * (dx + dy) + (D2 - 2 * D) * min(dx, dy)),1)
        return heu_value



    def get_vertex_neighbours(self, pos):
        n = []
        # Moves allow link a chess king
        for dx, dy in [(0.1, 0), (-0.1, 0), (0, 0.1), (0, -0.1), (0.1, 0.1), (-0.1, 0.1), (0.1, -0.1), (-0.1, -0.1)]:
            x2 = round((pos[0] + dx),1)
            y2 = round((pos[1] + dy),1)
            if(self.lat_start > self.lat_dest) :
                if(self.long_start > self.long_dest) :
                    if x2 > self.lat_start or x2 < self.lat_dest or y2 > self.long_start  or y2 < self.long_dest:
                        continue
            if (self.lat_start > self.lat_dest):
                if (self.long_start < self.long_dest):
                    if x2 > self.lat_start or x2 < self.lat_dest or y2 < self.long_start or y2 > self.long_dest:
                        continue
            if (self.lat_start < self.lat_dest):
                if (self.long_start > self.long_dest):
                    if x2 < self.lat_start or x2 > self.lat_dest or y2 > self.long_start or y2 < self.long_dest:
                        continue
            if (self.lat_start < self.lat_dest):
                if (self.long_start < self.long_dest):
                    if x2 < self.lat_start or x2 > self.lat_dest or y2 < self.long_start or y2 > self.long_dest:
                        continue
            n.append((x2, y2))
        return n



    def move_cost(self, a, b):
        for barrier in self.barriers:
            #if b in barrier:
            if b in barrier:
                return 100  # Extremely high cost to enter barrier squares
        return 0.1  # Normal movement cost


    "장애물 세팅"
    def set_barriers(self,diff_depth):

        temp_barrier = []
        for depth in diff_depth:
            temp_barrier.append(depth)
        self.barriers.append(temp_barrier)

        # for depth in diff_depth:
        #     log.debug('L.marker([%s',str(depth[0]), ',%s',str(depth[1]), '],{icon: pointIcon}).addTo(map);')


    "장애물 추가 "
    def add_barriers(self, bar):

        isExist = bar in self.barriers[0]
        if isExist == False:
            self.barriers[0].append(bar)

        #print(self.barriers)



def AStarSearch(start, end, graph):
    G = {}  # Actual movement cost to each position from the start position(시작위치에서 현재위치까지 비용)
    F = {}  # Estimated movement cost of start to end going via this position(현재위치에서 도착위치까지 비용)

    # Initialize starting values
    G[start] = 0
    F[start] = round(graph.heuristic(start, end),1)



    closedVertices = set()
    openVertices = set([start])
    cameFrom = {}

    while len(openVertices) > 0:
        # Get the vertex in the open list with the lowest F score
        current = None
        currentFscore = None
        for pos in openVertices:
            if current is None or F[pos] < currentFscore:
                currentFscore = round(F[pos],1)
                current = pos

        # Check if we have reached the goal
        if current == end:
            # Retrace our route backward
            path = [current]
            while current in cameFrom:
                current = cameFrom[current]
                path.append(current)
            path.reverse()
            return path, F[end]  # Done!

        # Mark the current vertex as closed
        openVertices.remove(current)
        closedVertices.add(current)

        # Update scores for vertices near the current position
        for neighbour in graph.get_vertex_neighbours(current):
            if neighbour in closedVertices:
                continue  # We have already processed this node exhaustively
            candidateG = G[current] + graph.move_cost(current, neighbour)

            if neighbour not in openVertices:
                openVertices.add(neighbour)  # Discovered a new vertex(새로운길발견)
            elif candidateG >= G[neighbour]:
                continue  # This G score is worse than previously found

            # Adopt this G score
            cameFrom[neighbour] = current
            G[neighbour] = candidateG
            H = round(graph.heuristic(neighbour, end),1)
            F[neighbour] = round(G[neighbour] + H,1)
    print("G == >",G)
    print("F == >",F)
    raise RuntimeError("A* failed to find a solution")




def display_barriers_scatter(plt,barries):
    for barrier in barries:
        plt.scatter([v[0] for v in barrier], [v[1] for v in barrier], s=1,color='red')


def display_barriers_line(plt,barries):
    for barrier in barries:
        plt.plot([v[0] for v in barrier], [v[1] for v in barrier], color='black')

def display_barriers_rect(plt,barries):
    c = plt.Circle((4, 4), 0.5, fc='w', ec='b')
    a = plt.axes(xlim=(-1, 12), ylim=(-1, 12))
    i = 0
    print(barries)

    for barrier in barries:
        #plt.plot([v[0] for v in barrier], [v[1] for v in barrier], color='black')
        print("장애물 ===================>",barrier)
        #rect = patches.Rectangle((barrier[0], barrier[1]), 1, 1, linewidth=1, edgecolor='r', facecolor='none')
        for bar in barrier :
            rect = patches.Rectangle((bar[0] - 0.5, bar[1] - 0.5), 1, 1, linewidth=1, edgecolor='r', facecolor='none')
            a.add_patch(rect)

def display_barriers_circle(plt,barries):
    #c = plt.Circle((4, 4), 0.5, fc='w', ec='b')
    a = plt.axes(xlim=(100, 130), ylim=(0, 35))
    i = 0
    print(barries)

    for barrier in barries:
        #plt.plot([v[0] for v in barrier], [v[1] for v in barrier], color='black')
        print("장애물 ===================>",barrier)
        #rect = patches.Rectangle((barrier[0], barrier[1]), 1, 1, linewidth=1, edgecolor='r', facecolor='none')
        for bar in barrier :
            #rect = patches.Rectangle((bar[0] - 0.5, bar[1] - 0.5), 1, 1, linewidth=1, edgecolor='r', facecolor='none')
            #rect = patches.Rectangle((bar[0] - 0.5, bar[1] - 0.5), 1, 1, linewidth=1, edgecolor='r', facecolor='none')
            circle = plt.Circle((bar[0], bar[1]), 0.5, fc='w', ec='b')
            a.add_patch(circle)

def exec():


    start_point = (34.7, 127.8)
    dest_point = (1.2, 103.9)
    lat_start = 1
    lat_dest = 35
    long_start = 103
    long_dest = 128
    interval = 0.1
    depth = -20
    lat_values = np.arange(lat_start, lat_dest, interval)  # 실험영역( A Star 적용시에 필요) 위도
    long_values = np.arange(long_start, long_dest, interval)  # 실험영역( A Star 적용시에 필요) 경도
    mongo_db = MongoDatabase()

    #diff_depth = mongo_db.get_depth_barriers()
    mongo_db_depth_info_df = mongo_db.get_depth_path(lat_start, lat_dest, long_start, long_dest, depth, '$gte')
    #depth_set = mongo_db.change_depth_to_list(mongo_db_depth_info_df)
    graph = AStarGraph()

    depth_info_df = pd.read_csv('depth/depth.csv')
    print(depth_info_df)
    i = 0
    depth_list = []
    while i < len(depth_info_df):
        lat = depth_info_df.iloc[i, 2]  # 위도
        long = depth_info_df.iloc[i, 1]  # 경도
        bar = (lat, long)
        depth_list.append(bar)
        i = i + 1


    print("장애물 == >",depth_list)


    graph.set_barriers(depth_list)

    wave_info_df = pd.read_csv('wave_info_KRUSN_KRKAN.csv')
    # print(wave_info_df)
    # i = 0
    # while i < len(wave_info_df):
    #     lat = wave_info_df.iloc[i, 5]  # 위도
    #     long = wave_info_df.iloc[i, 6]  # 경도
    #     bar = (lat, long)
    #     graph.add_barriers(bar)
    #     i = i + 1
    # print(graph.barriers)
    #result, cost = AStarSearch((129.42, 35.38), (127.83, 34.75), graph)
    result, cost = AStarSearch(start_point, dest_point, graph)
    for route in result:
        print('[', route[0], ',', route[1], '],')

    display_barriers_circle(plt, graph.barriers)
    display_barriers_scatter(plt, graph.barriers)

    print("route", result)
    print("cost", cost)

    plt.plot([v[1] for v in result], [v[0] for v in result])

    # for barrier in graph.barriers:
    #     plt.plot([v[0] for v in barrier], [v[1] for v in barrier])
    plt.xlim(100, 130)
    plt.ylim(0, 40)
    plt.show()


if __name__ == "__main__":
    exec()





