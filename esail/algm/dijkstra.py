import sys
sys.path.append('./')

from .graph import Graph, Remove_Graph
from .astar import AStarGraph
from .post_database import PostDatabase

import numpy as np
import pandas as pd
import logging
from logging.handlers import TimedRotatingFileHandler
import sys
from . import util
#import util

"""
 다익스트라알고리즘 클래스
 :return: 
 """
#BARRIERS_DISTANCE = 0.000000001
#BARRIERS_DISTANCE = 0.0056   # 임의로 주석처리
BARRIERS_DISTANCE = 0.000000001    #

class Dijkstra :
    def __init__(self):

       # self.log = logging.getLogger()
       # self.set_logger()
       self.graph = Graph()
       self.astar_graph = AStarGraph()

       self.db    = PostDatabase()



       # 장애물 추가
      #self.astar_graph.barriers.append(self.mongo_db.get_depth_barriers())

    def set_mongo_db(self,mongo_db):
        self.mongo_db = mongo_db



    # def set_logger(self):
    #     formatter = logging.Formatter("[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s")
    #
    #     std_handler = logging.StreamHandler(sys.stdout)
    #     std_handler.setFormatter(formatter)
    #     self.log.addHandler(std_handler)
    #
    #     file_handler = TimedRotatingFileHandler('esail/algm/logs/node-graph-service.log', when='midnight', interval=1,
    #                                             encoding='utf8')
    #
    #     file_handler.setFormatter(formatter)
    #     self.log.addHandler(file_handler)
    #
    #     self.log.setLevel(logging.DEBUG)



    """
     다익스트라알고리즘
     :param initial_node(시작지점)
     :return: 
     """
    def dijkstra(self, initial_node):
        visited = {initial_node: 0}
        current_node = initial_node
        path = {}

        nodes = set(self.graph.nodes)
        while nodes:
            min_node = None
            for node in nodes:
                if node in visited:
                    if min_node is None:
                        min_node = node
                    elif visited[node] < visited[min_node]:
                        min_node = node

            if min_node is None:
                break

            nodes.remove(min_node)
            cur_wt = visited[min_node]

            for edge in self.graph.edges[min_node]:
                wt = cur_wt + self.graph.distances[(min_node, edge)]
                if edge not in visited or wt < visited[edge]:
                    visited[edge] = wt
                    path[edge] = min_node

        return visited, path



    """
     가장 최단거리 역순으로 구함
     :param initial_node(시작지점), goal_node(목표지점)
     :return: 최단거리 경로 좌표
     """
    def shortest_path(self, initial_node, goal_node):

        distances, paths = self.dijkstra(initial_node)
        # print("거리 ==== >",distances)
        # print("경로 ====>",paths)
        route = [goal_node]
        while goal_node != initial_node:
            try:
                route.append(paths[goal_node])
                goal_node = paths[goal_node]
            except KeyError:
                return None
        route.reverse()
        return route


    """
    항로번호별 그래프에 거리 저장
    :param voyage_no_df(항로번호별 데이터프레임)
    :return: Graph
    """
    def add_passage_distance(self,voyage_no_df) :
        #print(voyage_no_df)
        # for voyage_no in voyage_no_df:
        i = 0
        while i < len(voyage_no_df):
            if (i == 0):  # 첫번쨰 행은 노드에만 삽입(거리가 0 이기 때문)
                lat = voyage_no_df.iloc[i, 5]          # 위도
                long = voyage_no_df.iloc[i, 6]        # 경도
                self.graph.add_node((lat, long))
            else:  # 두번째 행부터 거리저장
                lat = voyage_no_df.iloc[i - 1, 5]      # 이전행 위도
                long = voyage_no_df.iloc[i - 1, 6]    # 이전행 경도

                next_lat = voyage_no_df.iloc[i, 5]      # 위도
                next_long = voyage_no_df.iloc[i, 6]    # 경도
                #distance = voyage_no_df.iloc[i, 12]     # 거리

                self.graph.add_node((next_lat, next_long))

                """장애물과 만나면 그래프 연결 삭제
                """
                distance_barriers = self.get_barriers_distance((lat,long), (next_lat,next_long))
                if(distance_barriers <= BARRIERS_DISTANCE) :
                    #print("================================ 장애물 발견 ================================",(lat,long), (next_lat,next_long),distance_barriers)
                    """AStar 알고리즘으로 경로추가"""
                    pass
                   # graph = AStarGraph()
                    #result = AStarSearch((lat, long), (next_long, next_lat), graph)
                    #self.graph.add_edge((lat, long), (next_lat, next_long), 100000)
                else :
                    distance = round(util.calc_distance((lat, long), (next_lat, next_long)), 7)
                    if (distance != 0.0):
                        self.graph.add_edge((lat, long), (next_lat, next_long), distance)
                # is_barriers = False
                # for barrier in self.astar_graph.barriers:
                #     for bar in barrier:
                #         if(is_barriers) :
                #             continue
                #         distance_barriers = util.dist_point_to_line(bar,(lat,long), (next_lat,next_long))
                #         if (distance_barriers < 0.5):
                #             self.graph.add_edge((lat, long), (next_lat, next_long), 100000)
                #             print("장애물간 거리 ===== >",(lat, long), (next_lat, next_long),distance_barriers)
                #             is_barriers = True
                #         else :
                #             distance = round(util.calc_distance((lat, long), (next_lat, next_long)),7)
                #             if(distance != 0.0):
                #                 self.graph.add_edge((lat, long), (next_lat, next_long), distance)

            i += 1

        return self.graph

    """
       항로번호별 그래프에 거리 저장
       :param voyage_no_df(항로번호별 데이터프레임)
       :return: Graph
       """

    def add_passage_distance_old(self, voyage_no_df):
        print("항로 == ", voyage_no_df)
        # for voyage_no in voyage_no_df:
        i = 0
        while i < len(voyage_no_df):
            if (i == 0):  # 첫번쨰 행은 노드에만 삽입(거리가 0 이기 때문)
                lat = voyage_no_df.iloc[i, 8]  # 위도
                long = voyage_no_df.iloc[i, 9]  # 경도
                self.graph.add_node((lat, long))
            else:  # 두번째 행부터 거리저장
                lat = voyage_no_df.iloc[i - 1, 8]  # 이전행 위도
                long = voyage_no_df.iloc[i - 1, 9]  # 이전행 경도

                next_lat = voyage_no_df.iloc[i, 8]  # 위도
                next_long = voyage_no_df.iloc[i, 9]  # 경도
                # distance = voyage_no_df.iloc[i, 12]     # 거리

                self.graph.add_node((next_lat, next_long))

                """장애물과 만나면 그래프 연결 삭제
                """
                distance_barriers = self.get_barriers_distance((lat, long), (next_lat, next_long))
                if (distance_barriers <= BARRIERS_DISTANCE):
                    # print("================================ 장애물 발견 ================================",(lat,long), (next_lat,next_long),distance_barriers)
                    """AStar 알고리즘으로 경로추가"""
                    pass
                # graph = AStarGraph()
                # result = AStarSearch((lat, long), (next_long, next_lat), graph)
                # self.graph.add_edge((lat, long), (next_lat, next_long), 100000)
                else:
                    distance = round(util.calc_distance((lat, long), (next_lat, next_long)), 7)
                    if (distance != 0.0):
                        self.graph.add_edge((lat, long), (next_lat, next_long), distance)
                # is_barriers = False
                # for barrier in self.astar_graph.barriers:
                #     for bar in barrier:
                #         if(is_barriers) :
                #             continue
                #         distance_barriers = util.dist_point_to_line(bar,(lat,long), (next_lat,next_long))
                #         if (distance_barriers < 0.5):
                #             self.graph.add_edge((lat, long), (next_lat, next_long), 100000)
                #             print("장애물간 거리 ===== >",(lat, long), (next_lat, next_long),distance_barriers)
                #             is_barriers = True
                #         else :
                #             distance = round(util.calc_distance((lat, long), (next_lat, next_long)),7)
                #             if(distance != 0.0):
                #                 self.graph.add_edge((lat, long), (next_lat, next_long), distance)

            i += 1

        return self.graph




    "노드삽입"
    def add_distance_nodes(self,p1,p2,p3,p4,point):

        self.graph.add_node(point)


        distance_barriers = self.get_barriers_distance(point, p1)
        if (distance_barriers <= BARRIERS_DISTANCE):
            pass
            """AStar 알고리즘으로 경로추가"""
            # graph = AStarGraph()
            # result = AStarSearch((lat, long), (next_long, next_lat), graph)
            # self.graph.add_edge((lat, long), (next_lat, next_long), 100000)

        else:
            distance = round(util.calc_distance(point, p1), 7)
            if (distance != 0.0):
                self.graph.add_edge(point, p1, distance)


        distance_barriers = self.get_barriers_distance(point, p2)
        if (distance_barriers <= BARRIERS_DISTANCE):
            pass
            """AStar 알고리즘으로 경로추가"""
            # graph = AStarGraph()
            # result = AStarSearch((lat, long), (next_long, next_lat), graph)
            # self.graph.add_edge((lat, long), (next_lat, next_long), 100000)

        else:
            distance = round(util.calc_distance(point, p2), 7)
            if (distance != 0.0):
                self.graph.add_edge(point, p2, distance)




        distance_barriers = self.get_barriers_distance(point, p3)
        if (distance_barriers <= BARRIERS_DISTANCE):
            pass
            """AStar 알고리즘으로 경로추가"""
            # graph = AStarGraph()
            # result = AStarSearch((lat, long), (next_long, next_lat), graph)
            # self.graph.add_edge((lat, long), (next_lat, next_long), 100000)

        else:
            distance = round(util.calc_distance(point, p3), 7)
            if (distance != 0.0):
                self.graph.add_edge(point, p3, distance)



        distance_barriers = self.get_barriers_distance(point, p4)
        if (distance_barriers <= BARRIERS_DISTANCE):
            pass
            """AStar 알고리즘으로 경로추가"""
            # graph = AStarGraph()
            # result = AStarSearch((lat, long), (next_long, next_lat), graph)
            # self.graph.add_edge((lat, long), (next_lat, next_long), 100000)

        else:
            distance = round(util.calc_distance(point, p4), 7)
            if (distance != 0.0):
                self.graph.add_edge(point, p4, distance)

        # distance = util.calc_distance(point, p1)
        # self.graph.add_edge(point, p1, distance)
        #
        # distance = util.calc_distance(point, p2)
        # self.graph.add_edge(point, p2, distance)
        #
        # distance = util.calc_distance(point, p3)
        # self.graph.add_edge(point, p3, distance)
        #
        # distance = util.calc_distance(point, p4)
        # self.graph.add_edge(point, p4, distance)



    "노드에 교점추가"
    def add_cross_point(self,voyage_no_start_df, voyage_no_dest_df):
        i = 0
        while i < len(voyage_no_start_df) - 1:
            start_lat1 = voyage_no_start_df.iloc[i, 5]  # 위도
            start_long1 = voyage_no_start_df.iloc[i, 6]  # 경도
            start_lat2 = voyage_no_start_df.iloc[i + 1, 5]  # 위도
            start_long2 = voyage_no_start_df.iloc[i + 1, 6]  # 경도
            p1 = (start_lat1, start_long1)
            p2 = (start_lat2, start_long2)
            # self.graph.add_node(start)
            j = 0
            while j < len(voyage_no_dest_df) - 1:
                dest_lat1 = voyage_no_dest_df.iloc[j, 5]  # 위도
                dest_long1 = voyage_no_dest_df.iloc[j, 6]  # 경도
                dest_lat2 = voyage_no_dest_df.iloc[j + 1, 5]  # 위도
                dest_long2 = voyage_no_dest_df.iloc[j + 1, 6]  # 경도

                p3 = (dest_lat1, dest_long1)
                p4 = (dest_lat2, dest_long2)

                point = util.get_cross_point(p1, p2, p3, p4)
                if point != None:
                    "선분간의 교점을 구한 후 꼭지점간 거리계산후 그래프에 추가"
                    self.add_distance_nodes(p1, p2, p3, p4, point)
                    #print("교점=========> ", point)
                # self.graph.add_node(dest)
                # self.graph.add_edge(start, dest, distance)
                j += 1
            i += 1


    "passage plan 대하여 시작좌표부터 종료좌표까지 그래프에 노드를 추가하고 거리를 저장한다. " \
    "입력 param :  항로데이터 데이터프레임"
    def make_start_to_end_graph(self,voyage_df):
        i = 0
        while i < len(voyage_df) - 1:
            start_lat = voyage_df.iloc[i, 5].astype('float')  # 위도
            start_long = voyage_df.iloc[i, 6].astype('float')  # 경도
            start = (start_lat, start_long)
            self.graph.add_node(start)

            dest_lat = voyage_df.iloc[i + 1, 5].astype('float')  # 위도
            dest_long = voyage_df.iloc[i + 1, 6].astype('float')  # 경도
            dest = (dest_lat, dest_long)

            distance = util.calc_distance(start, dest)
            self.graph.add_node(dest)
            self.graph.add_edge(start, dest, distance)
            i += 1


    """
       선분의 교점을 그래프에 추가한다.
       :입력 param 출발항구, 목적지항구
        출발항구 목적지항구의 passage plan을 불러와서 해당되는 항로중 교점들간의 거리와 노드를 
        그래프에 추가한다. 
       :return:
       """
    def add_cross_point_to_graph(self,passage_plan_df,voyage_info_seq_df,search_count):

        # passage_plan_df = self.db.get_passage_plan_list(start_port_code, dest_port_code)
        # voyage_info_seq_df = passage_plan_df['voyage_info_seq'].drop_duplicates()  # 항차번호
        #
        # passage_plan_df.set_index('voyage_info_seq', inplace=True)  # 항차번호로 index 세팅
        #
        # passage_plan_df['latitude'] = passage_plan_df['latitude'].astype('float')  # 형변환
        # passage_plan_df['longitude'] = passage_plan_df['longitude'].astype('float')  # 형변환


        #voyage_df = self.db.get_voyage_no(start_port, dest_port)  # 항로번호 조회
        #passage_plan_df = pd.read_csv(csv_name)
        #passage_plan_df = passage_plan_df.loc[passage_plan_df['type'] == 'RWP']  # RWP만 조회
        #voyage_df = passage_plan_df['voyage_no'].drop_duplicates()  # 항차수번호 KRUSN_KRKAN.csv 파일 항차수 컬럼 추가

        #voyage_no_arr = np.array(voyage_df.iloc[:, 0:1])

        voyage_no_arr = np.array(voyage_info_seq_df)
        print("항로갯수 ===>",len(voyage_no_arr))

        #passage_plan_df = pd.read_csv('KRUSN_KRKAN.csv', index_col='voyage_no')

        #passage_plan_df.set_index('voyage_no', inplace=True)


        i = 0
        #while i < len(voyage_no_arr) :
        while(i < search_count):
             voyage_no_start = voyage_no_arr[i]
             # if (str(type(passage_plan_df)) == "<class 'pandas.core.series.Series'>"):
             #     continue

             voyage_no_start_df = round(passage_plan_df.loc[voyage_no_start],7)
             print(voyage_no_start,'     ', str(i+1))
             "항로생성"
             #self.make_start_to_end_graph(voyage_no_start_df)
             j = i + 1
             #while j < len(voyage_no_arr) :
             while j < search_count :
                 #voyage_no_dest = voyage_no_arr[j][0]
                 voyage_no_dest = voyage_no_arr[j]
                 "거리계산할 항로좌표를 가져온다"
                 # if (str(type(passage_plan_df)) == "<class 'pandas.core.series.Series'>"):

                 #     continue
                 #print(passage_plan_df)
                 #print(passage_plan_df.loc[voyage_no_dest])
                 voyage_no_dest_df = round(passage_plan_df.loc[voyage_no_dest],7)
                 #voyage_no_dest_df = self.db.get_passage_plan(voyage_no_dest, start_port, dest_port)
                 #print(voyage_no_dest_df)
                 #voyage_no_dest_df = pd.read_csv('esail_01.csv')

                 "voyage_no_start와 voyage_no_dest간 거리계산후에 저장"
                 #self.make_start_to_end_graph(voyage_no_start_df,voyage_no_dest_df)
                 #self.make_start_to_end_graph(voyage_no_dest_df)
                 "직선의 방정식 교점 구한후 그래프에 추가"

                 self.add_cross_point(voyage_no_start_df, voyage_no_dest_df)

                 j += 1
             i = i + 1

    """
          선분의 교점을 그래프에 추가한다.
          :입력 param 출발항구, 목적지항구
           출발항구 목적지항구의 passage plan을 불러와서 해당되는 항로중 교점들간의 거리와 노드를 
           그래프에 추가한다. 
          :return:
          """

    def add_cross_point_to_graph_old(self, start_port, dest_port, csv_name):
        voyage_df = self.db.get_voyage_no(start_port, dest_port)  # 항로번호 조회
        # voyage_df = pd.read_csv('esail_no.csv')
        passage_plan_df = pd.read_csv(csv_name)
        # passage_plan_df = pd.read_csv('KRKAN_SGSIN.csv')
        passage_plan_df = passage_plan_df.loc[passage_plan_df['type'] == 'RWP']  # RWP만 조회
        voyage_df = passage_plan_df['voyage_no'].drop_duplicates()  # 항차수번호 KRUSN_KRKAN.csv 파일 항차수 컬럼 추가

        # voyage_no_arr = np.array(voyage_df.iloc[:, 0:1])
        voyage_no_arr = np.array(voyage_df)
        # passage_plan_df = pd.read_csv('KRUSN_KRKAN.csv', index_col='voyage_no')

        passage_plan_df['latitude'] = passage_plan_df['latitude'].astype('float')  # 형변환
        passage_plan_df['longitude'] = passage_plan_df['longitude'].astype('float')  # 형변환
        passage_plan_df.set_index('voyage_no', inplace=True)

        i = 0
        while i < len(voyage_no_arr):
            # voyage_no_start = voyage_no_arr[i][0]
            voyage_no_start = voyage_no_arr[i]
            # voyage_no_start_df = self.db.get_passage_plan(voyage_no_start, start_port, dest_port)
            voyage_no_start_df = round(passage_plan_df.loc[voyage_no_start], 7)
            "항로생성"
            # self.make_start_to_end_graph(voyage_no_start_df)
            j = i + 1
            while j < len(voyage_no_arr):
                # voyage_no_dest = voyage_no_arr[j][0]
                voyage_no_dest = voyage_no_arr[j]
                "거리계산할 항로좌표를 가져온다"
                voyage_no_dest_df = round(passage_plan_df.loc[voyage_no_dest], 7)
                # voyage_no_dest_df = self.db.get_passage_plan(voyage_no_dest, start_port, dest_port)
                # print(voyage_no_dest_df)
                # voyage_no_dest_df = pd.read_csv('esail_01.csv')

                "voyage_no_start와 voyage_no_dest간 거리계산후에 저장"
                # self.make_start_to_end_graph(voyage_no_start_df,voyage_no_dest_df)
                # self.make_start_to_end_graph(voyage_no_dest_df)
                "직선의 방정식 교점 구한후 그래프에 추가"
                self.add_cross_point(voyage_no_start_df, voyage_no_dest_df)

                j += 1
            i = i + 1

    """
       항로별 노드와 거리를 그래프에 저장.
       :return:
       """
    def create_passage_plan(self,passage_plan_df,voyage_info_seq_df,search_count):
        
        passage_plan_dict = {}
        passage_plan_dict_distance = {}

        color_list = util.get_sorted_color_names()
        print("색상갯수 ============ >", len(color_list))
        print("조회갯수 ============ >", search_count)
        i = 0
        count = 0 # 갯수 조절하기 위해
        for voyage_info_seq in np.array(voyage_info_seq_df):
            if(count >= search_count) :
                break
            #voyage_no_df = round(passage_plan_df.loc[voyage],7)
            voyage_info_df = passage_plan_df.loc[voyage_info_seq]
            if (str(type(voyage_info_df)) == "<class 'pandas.core.series.Series'>"):
                continue
            #print(voyage_info_df)
            print(voyage_info_df)
            #voyage_no_df = round(passage_plan_df.loc[passage_plan_df['voyage_seq'] == voyage], 7)
            "해당항로번호에 대하여 노드정보와 노드간의 거리를 DB에서 가져옴"
            #voyage_no_df = self.db.get_passage_plan(voyage_no, start_port, dest_port)
            #print(np.array(voyage_no_df.iloc[:,9:11]))
            #self.log.debug('지도표시용 항로번호[%s]  갯수 [%s]', voyage, len(voyage_no_df))
            passage_plan_unit = []
            passage_plan_unit_distance = []
            for passage_plan in np.array(voyage_info_df.loc[:,'latitude':'voyage_no']) :
                if passage_plan[1] <= 0 :
                    passage_plan[1] = passage_plan[1] + 360
                #print('[',passage_plan[0],',',passage_plan[1],'],')
                passage_plan_str = '[' + str(passage_plan[0]) + ',' + str(passage_plan[1]) + ']'
                voyage_no = passage_plan[2]
                passage_plan_tu = (passage_plan[0],passage_plan[1])
                passage_plan_unit_distance.append(passage_plan_tu)
                passage_plan_unit.append(passage_plan_str)
            if(i > len(color_list)-1) :
                passage_plan_dict[str(voyage_info_seq) + ' ' + color_list[len(color_list)-1]] = passage_plan_unit  # 지도칼라에 넣기 위해 voyage_no에서 voyage_info_seq 변경
            else :
                passage_plan_dict[str(voyage_info_seq)+' '+color_list[i]] = passage_plan_unit  # 지도칼라에 넣기 위해 voyage_no에서 voyage_info_seq 변경
            #passage_plan_dict_distance[str(voyage_info_seq) + ' ' + color_list[i]] = passage_plan_unit_distance  # 지도칼라에 넣기 위해 voyage_no에서 voyage_info_seq 변경
            #passage_plan_dict[str(voyage_info_seq)] = passage_plan_unit  # 지도칼라에 넣기 위해 voyage_no에서 voyage_info_seq 변경
            passage_plan_dict_distance[str(voyage_info_seq)+'_'+voyage_no] = passage_plan_unit_distance  # 항차번호(항차)

            i = i + 1
            "항로번호별로 노드간 거리 저장"
            self.add_passage_distance(voyage_info_df)
            count = count + 1
        #voyage_lit = voyage_df.values.tolist()
        #print("passage_plan_dict_distance ==== >",passage_plan_dict_distance)
        return passage_plan_dict,passage_plan_dict_distance # 화면에 표시해주기 위해



    """
           항로별 노드와 거리를 그래프에 저장.
           :return:
           """

    def create_passage_plan_old(self, start_port_code, dest_port_code, csv_name):

        passage_plan_df = self.db.get_passage_plan_list(start_port_code, dest_port_code)
        voyage_df = passage_plan_df['voyage_info_seq'].drop_duplicates()  # 항차번호

        # passage_plan_df = pd.read_csv(csv_name)
        # passage_plan_df = passage_plan_df.loc[passage_plan_df['type'] == 'RWP']    # RWP만 조회

        passage_plan_df['latitude'] = passage_plan_df['latitude'].astype('float')  # 형변환
        passage_plan_df['longitude'] = passage_plan_df['longitude'].astype('float')  # 형변환

        # voyage_df = passage_plan_df['voyage_seq'].drop_duplicates()  # 항차수번호 KRUSN_KRKAN.csv 파일 항차수 컬럼 추가
        voyage_df = passage_plan_df['voyage_no'].drop_duplicates()  # 항차수번호 Kcsv 파일 항차RUSN_KRKAN.수 컬럼 추가
        passage_plan_df.set_index('voyage_no', inplace=True)
        passage_plan_dict = {}
        passage_plan_dict_distance = {}

        color_list = util.get_colors()
        i = 0
        for voyage in np.array(voyage_df):
            # voyage_no = voyage[0]
            voyage_no_df = round(passage_plan_df.loc[voyage], 7)
            # voyage_no_df = round(passage_plan_df.loc[passage_plan_df['voyage_seq'] == voyage], 7)
            "해당항로번호에 대하여 노드정보와 노드간의 거리를 DB에서 가져옴"
            # voyage_no_df = self.db.get_passage_plan(voyage_no, start_port, dest_port)
            # print(np.array(voyage_no_df.iloc[:,9:11]))
            # self.log.debug('지도표시용 항로번호[%s]  갯수 [%s]', voyage, len(voyage_no_df))
            passage_plan_unit = []
            passage_plan_unit_distance = []
            for passage_plan in np.array(voyage_no_df.loc[:, 'latitude':'longitude']):
                if passage_plan[1] <= 0:
                    passage_plan[1] = passage_plan[1] + 360
                # print('[',passage_plan[0],',',passage_plan[1],'],')
                passage_plan_str = '[' + str(passage_plan[0]) + ',' + str(passage_plan[1]) + ']'
                passage_plan_tu = (passage_plan[0], passage_plan[1])
                passage_plan_unit_distance.append(passage_plan_tu)
                passage_plan_unit.append(passage_plan_str)

            passage_plan_dict[voyage + ' ' + color_list[i]] = passage_plan_unit  # 지도칼라에 넣기 위해
            passage_plan_dict_distance[voyage + ' ' + color_list[i]] = passage_plan_unit_distance  # 지도칼라에 넣기 위해

            i = i + 1
            "항로번호별로 노드간 거리 저장"
            self.add_passage_distance(voyage_no_df)

        # voyage_lit = voyage_df.values.tolist()
        return passage_plan_dict, passage_plan_dict_distance  # 화면에 표시해주기 위해
        # voyage_no_df = db.get_passage_plan('0046W')

        # self.log.debug('최단거리 ======>  %s ' ,self.graph.distances)

        # for passage_plan in np.array(passage_plan_df.iloc[:,9:11]) :
        #     if passage_plan[1] <= 0 :
        #         passage_plan[1] = passage_plan[1] + 360
        #     print('[',passage_plan[0],',',passage_plan[1],'],')
        #     #print('L.marker([', passage_plan[0], ',', passage_plan[1], ']).addTo(map);')

        # route_set = shortest_path(gg, (35.53, 129.3933333), (34.8911111, 127.6561111))
        # dist = dijk.calc_distance((35.5269444, 129.3938889), (35.4761111, 129.4058333))
        # print("거리 = ",dist)
        # route_set = dijk.shortest_path((35.53, 129.3933333), (34.8911111, 127.6561111))
        # for route in route_set:
        #     print(route)

    """
           항로별 노드와 거리를 그래프에 저장.
           :return:
           """



    """
           항로별 노드와 거리를 그래프에 저장.
           :return:
           """
    def create_passage_plan_KRKAN(self, start_port, dest_port):
        voyage_df = self.db.get_voyage_no(start_port, dest_port)  # 항로번호 조회

        # passage_plan_df = pd.read_csv('KRUSN_KRKAN.csv', index_col='voyage_no') # 울산-광양
        passage_plan_df = pd.read_csv('path_usa.csv', index_col='voyage_no')

        passage_plan_df = passage_plan_df.loc[passage_plan_df['type'] == 'RWP']  # RWP만 조회

        passage_plan_df['latitude'] = passage_plan_df['latitude'].astype('float')  # 형변환
        passage_plan_df['longitude'] = passage_plan_df['longitude'].astype('float') # 형변환

        voyage_df = passage_plan_df['voyage_seq'].drop_duplicates()  # 항차수번호 KRUSN_KRKAN.csv 파일 항차수 컬럼 추가

        for voyage in np.array(voyage_df.iloc[:, 0:1]):
            voyage_no = voyage[0]
            voyage_no_df = round(passage_plan_df.loc[voyage_no], 7)
            #print(voyage_no_df)
            "해당항로번호에 대하여 노드정보와 노드간의 거리를 DB에서 가져옴"
            # voyage_no_df = self.db.get_passage_plan(voyage_no, start_port, dest_port)
            # print(np.array(voyage_no_df.iloc[:,9:11]))
            #self.log.debug('지도표시용 항로번호[%s]  갯수 [%s]', voyage_no, len(voyage_no_df))
            for passage_plan in np.array(voyage_no_df.loc[:, 'latitude':'longitude']):
                if passage_plan[1] <= 0:
                    passage_plan[1] = passage_plan[1] + 360
                print('[', passage_plan[0], ',', passage_plan[1], '],')

            "항로번호별로 노드간 거리 저장"
            self.add_passage_distance(voyage_no_df)

        return passage_plan_df  # 화면에 표시해주기 위해
        # voyage_no_df = db.get_passage_plan('0046W')

        # self.log.debug('최단거리 ======>  %s ' ,self.graph.distances)

        # for passage_plan in np.array(passage_plan_df.iloc[:,9:11]) :
        #     if passage_plan[1] <= 0 :
        #         passage_plan[1] = passage_plan[1] + 360
        #     print('[',passage_plan[0],',',passage_plan[1],'],')
        #     #print('L.marker([', passage_plan[0], ',', passage_plan[1], ']).addTo(map);')

        # route_set = shortest_path(gg, (35.53, 129.3933333), (34.8911111, 127.6561111))
        # dist = dijk.calc_distance((35.5269444, 129.3938889), (35.4761111, 129.4058333))
        # print("거리 = ",dist)
        # route_set = dijk.shortest_path((35.53, 129.3933333), (34.8911111, 127.6561111))
        # for route in route_set:
        #     print(route)

    "연결된 노드사이에 장애물이 있는지 체크하고 노드간의 선분과 장애물 상이의 거리를 구해서 기준값 이하면 통과하지 못하는" \
    "경로로 인식해서 경로대상에서 삭제 " \
    "입력 param :  항로데이터 데이터프레임"
    def remove_barriers_path(self,barriers):
        #print("장벽들 =====================>>>>",barriers)
        remove_graph = Remove_Graph()
        for dis in self.graph.distances:
            for barrier in barriers:
                for bar in barrier:
                    distance = util.dist_point_to_line(bar,dis[0],dis[1])
                    #print("직선사이 거리 ===== >",bar,dis[0],dis[1],distance)
                    if(distance < 1):
                        remove_graph.add_node(dis[0])
                        remove_graph.add_node(dis[1])
                        remove_graph.add_edge(dis[0], dis[1], distance)



        # print("삭제될 노드들 =============> ", remove_graph.distances)
        # print("삭제될 노드들 =============> ", remove_graph.edges)
        # print("삭제될 노드들 =============> ", remove_graph.nodes)
        #remove_graph.nodes.remove((4,7))
        # for rmd in remove_graph.distances:
        #    del (self.graph.distances[rmd])
        # for rmd in remove_graph.edges:
        #    del (self.graph.edges[rmd])

        # for rmd in remove_graph.nodes:
        #    self.graph.nodes.remove(rmd)


        # print("삭제될 거리 =============> ", remove_graph.distances)
        # print("삭제될 엣지 =============> ", remove_graph.edges)
        # print("삭제될 노드 =============> ", remove_graph.nodes)
        #
        # print(" 거리 =============> ", self.graph.distances)
        # print(" 엣지 =============> ", self.graph.edges)
        # print(" 노드 =============> ", self.graph.nodes)


    def get_barriers_distance(self,start,dest):
        distance = 0
        distance_list = []

        for barrier in self.astar_graph.barriers:
            for bar in barrier:
                distance = util.dist_point_to_line(bar, start,dest)
                #print("직선사이 거리 ===== >", bar, start,dest, distance)
                distance_list.append(distance)
                if(distance <= BARRIERS_DISTANCE) :
                    #print("장애물 ===================> ",start,dest,distance,bar)
                    return distance
        min_distance = min(distance_list)
        #print("장애물 ===================> min ", start, dest, min_distance)
        return min_distance



    def get_wave_distance(self,start,dest,wave_info_df):
        distance = 0
        distance_list = []
        i = 0
        bar = None
        while i < len(wave_info_df):
            lat = wave_info_df.iloc[i, 5]  # 위도
            long = wave_info_df.iloc[i, 6]  # 경도
            #bar = (start_lat1,start_long1)
            bar = (lat, long)
            distance = util.dist_point_to_line(bar, start,dest)
            #print("장애물사이 거리 ===== >", bar, start,dest, distance)
            distance_list.append(distance)
            if(distance <= BARRIERS_DISTANCE) :
                return distance,bar
            i = i + 1
        min_distance = min(distance_list)
        return min_distance,bar


    def get_wave_height(self,route_set,wave_info_df):

        i = 0
        wave_barriers = []
        total_dist = 0
        total_time = 0
        while i < len(route_set) - 1 :
            start = route_set[i]
            dest  = route_set[i+1]

            dist = util.calc_distance(start, dest)
            "안전속도 일단 16으로 고정"
            time = dist / 16
            total_dist = total_dist + dist
            print("좌표 ==> ", (start, dest), " 거리 == >", dist, "시간(분) = ", time*60)
            total_time = total_time + time
            print("시간토탈(분) = ", total_time * 60)


            min_distance ,bar = self.get_wave_distance(start,dest,wave_info_df)
            #print("장매물 사이의 거리 === >  ",start,dest,bar,min_distance)
            "경로중에 장애물이 있으면 start, dest 저장"
            #node = set()
            if (min_distance <= BARRIERS_DISTANCE and (total_time*60 <= 480 and total_time*60 >=400)):
                #node.add(start)
                #node.add(dest)
                wave_barriers.append(i)
            i = i + 1
        #print("제거되어야 할 노드 ===>",wave_barriers)
        return wave_barriers
            # start_lat1 = route_set.iloc[i, 4]  # 위도
            # start_long1 = route_set.iloc[i, 5]  # 경도
            # start_lat2 = route_set.iloc[i + 1, 4]  # 위도
            # start_long2 = route_set.iloc[i + 1, 5]  # 경도
            # p1 = (start_lat1, start_long1)
            # p2 = (start_lat2, start_long2)
