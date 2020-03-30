import sys
sys.path.append('./')

from .mongo_database import MongoDatabase
from .dijkstra import Dijkstra
from .astar import AStarSearch,AStarGraph
import pandas as pd
import numpy as np
from . import util

def main(passage_id):

    if(passage_id == 1):
        "울산 ==>  광양 항로"
        csv_name = 'esail/algm/data/KRUSN_KRKAN.csv'   # 울산 ==> 광양
        start_port = "KRUSN"    # 울산
        dest_port = "KRKAN"     # 광양
        start_point = (35.38, 129.42)
        dest_point  = (34.75, 127.83)
        wave_info_csv = 'esail/algm/data/wave_info_KRUSN_KRKAN.csv'     # 파고정보
        lat_start = 34.3
        lat_dest = 35.6
        long_start = 127.5
        long_dest = 129.5

        #lat_values = np.arange(lat_start, lat_dest, interval)  # 실험영역( A Star 적용시에 필요) 위도
        #long_values = np.arange(long_start, long_dest, interval)  # 실험영역( A Star 적용시에 필요) 경도
    else :

        "광양 ==>  싱가폴 항로"
        csv_name = 'esail/algm/data/KRKAN_SGSIN.csv'  # 광양 ==> 싱가폴
        start_port = "KRKAN"  # 광양
        dest_port = "SGSIN"  # 싱가폴
        start_point = (34.7472222, 127.8325)
        dest_point  = (1.2311111, 103.8961111)
        wave_info_csv = 'esail/algm/data/wave_info_KRUSN_KRKAN.csv'     # 파고정보
        lat_start = 1
        lat_dest = 35
        long_start = 103
        long_dest = 128
        # lat_values = np.arange(lat_start, lat_dest, interval)  # 실험영역( A Star 적용시에 필요) 위도
        # long_values = np.arange(long_start, long_dest, interval)  # 실험영역( A Star 적용시에 필요) 경도

    interval = 0.1
    depth = -20


    mongo_db = MongoDatabase()  # 몽고디비 생성

    dijk = Dijkstra()  # 다익스트라 알고리즘 생성
    dijk.astar_graph.set_boundary(lat_start, lat_dest, long_start, long_dest);

    "============================================================================"
    "장애물 저장(수심)"
    "============================================================================"
    "수심 20미터 이하 조회"
    #mongo_db_depth_info_df = mongo_db.get_depth_path(lat_start,lat_dest,long_start,long_dest,depth,'$lte')
    "격자점 - 수심20미터 이하 ===> 장애물"
    #diff_depth = mongo_db.get_depth_barriers(lat_values,long_values,mongo_db_depth_info_df)
    "====================================================================================="


    "수심 20미터 이상 조회 장애물"

    mongo_db_depth_info_df = mongo_db.get_depth_path(lat_start, lat_dest, long_start, long_dest, depth, '$gte')
    depth_set = mongo_db.change_depth_to_list(mongo_db_depth_info_df)
    print("장애물 ====>",depth_set)
    for passage_plan in depth_set:
        print('L.marker([', passage_plan[0], ',', passage_plan[1], '],{icon: pointIcon}).addTo(map);')

    dijk.astar_graph.set_barriers(depth_set)




    "============================================================================"
    "항로별 노드저장"
    "============================================================================"
    passage_plan_dict  = dijk.create_passage_plan(start_port,dest_port,csv_name)
    print("사전 ========= > ",passage_plan_dict)



    "============================================================================"
    "선분의 교점을 구해서 그래프에 추가"
    "============================================================================"
    dijk.add_cross_point_to_graph(start_port,dest_port,csv_name)


    "============================================================================"
    "모든 노드들을 표시하기 위한 좌표정보"
    "============================================================================"
    for passage_plan in dijk.graph.nodes:
        print('L.marker([', passage_plan[0], ',', passage_plan[1], '],{icon: red_pointIcon}).addTo(map);')


    "============================================================================"
    "등록된 모든 노드들의 최단경로"
    "============================================================================"
    route_set = dijk.shortest_path(start_point, dest_point)

    for route in route_set:
        dijk.log.debug('최단거리 ==================>  %s ', route)


    "============================================================================"
    "최단거리 좌표(지도표시용)"
    "============================================================================"
    dijk.log.debug('============================최단거리 좌표(지도표시용)============================== ')
    for route in route_set :
        print('[',route[0],',',route[1],'],')



    "============================================================================"
    "Dijkstra 알고리즘으로 적용 후 총거리와 시간 구하기"
    "============================================================================"
    i = 0
    total_dist = 0
    total_time = 0
    while i < len(route_set) - 1:
        start = route_set[i]
        dest = route_set[i + 1]
        dist = util.calc_distance(start, dest)
        "안전속도 일단 16으로 고정"
        time = dist / 16
        total_dist = total_dist + dist
        print("좌표 ==> ", (start, dest), " 거리 == >", dist, "시간 = ", time)
        total_time = total_time + time
        i = i + 1
    print("DIJKSTRA 알고리즘 총거리 == ", total_dist)
    print("DIJKSTRA 알고리즘 총시간 == ", total_time)


    "============================================================================"
    "파고 높이 장애물 구하기                                                             "
    "============================================================================"
    wave_info_df = pd.read_csv(wave_info_csv)
    wave_barriers = dijk.get_wave_height(route_set,wave_info_df)



    "============================================================================"
    " 파고높이를 장애물로 추가                                                       "
    "============================================================================"
    i = 0
    while i < len(wave_info_df):
        lat = wave_info_df.iloc[i, 5]  # 위도
        long = wave_info_df.iloc[i, 6]  # 경도
        bar = (lat, long)
        dijk.astar_graph.add_barriers(bar)
        i = i + 1

    print("장애물 정보       ================================================>",dijk.astar_graph.barriers)
    #print("장애물 정보 =========> ",graph.barriers)
    #print("장애물 정보 =========> ", len(graph.barriers))
    for passage_plan in dijk.astar_graph.barriers[0]:
         print('L.marker([', passage_plan[0], ',', passage_plan[1], '],{icon: pointIcon}).addTo(map);')

    "============================================================================"
    " AStar 알고리즘으로 경로 찾기                                           "
    "============================================================================"
    i = 0
    astar_path_list = []
    while i < len(wave_barriers) :
        idx = wave_barriers[i]
        start_point = route_set[idx-1]
        dest_point = route_set[idx]
        start,dest = util.get_rounding(start_point,dest_point)
        result, cost = AStarSearch(start, dest, dijk.astar_graph)
        astar_path_list.append(result)
        # print("AStar 신규경로  == > ",result)
        # route_set.insert(idx + i,result)

        i = i + 1


    print("AStar 경로 ",astar_path_list)
    print("최종경로 === > ",route_set)

    "============================================================================"
    " 경로중에 장애물에 걸린 경로는 삭제                                           "
    "============================================================================"
    i = 0
    while i < len(wave_barriers):
        idx = wave_barriers[len(wave_barriers) - i - 1]
        del route_set[idx]
        i = i + 1

    "============================================================================"
    " 기존 다익스트라 경로중에서 AStar경로 삽입                                          "
    "============================================================================"
    i = 0
    while i < len(wave_barriers) :
        idx = wave_barriers[i]
        route_set.insert(idx,astar_path_list[i])
        i = i + 1



    " AStar로 최단거리 찾는부분"
    # start,dest =  util.get_rounding((34.5708333, 128.6463889),(34.4741667, 128.0738889))
    #
    # graph = AStarGraph()
    # result, cost = AStarSearch(start, dest, graph)



    # for route in result:
    #     dijk.log.debug('AStar 최단거리 ==================>  %s ', route)

        #print('[', route[0], ',', route[1], '],')


    "장애물 삭제"
    #route_set.remove((34.5211111, 128.4472222))

    "AStar 알고리즘으로 구한 최단경로 추가"
    #route_set.insert(5,result)



    "dijkstra와 AStar 조합 결과"
    final_route = []

    final_route = []
    for route in route_set:
        if (len(route) > 2):
            for rt in route:
                # dijk.log.debug('AStar 최단거리 ==================>  %s' , rt)
                print('[', rt[0], ',', rt[1], '],')
                final_route.append(rt)
        else:
            # dijk.log.debug('최종 최단거리 ==================>  %s', route)
            print('[', route[0], ',', route[1], '],')
            final_route.append(route)


    print("최종 = ",final_route)
    final_route_text = []
    final_route_marker = []
    for passage_plan in final_route:
        print('L.marker([', passage_plan[0], ',', passage_plan[1], '],{icon: red_pointIcon}).addTo(map);')
        marker_str = 'L.marker([' + str(passage_plan[0])+ ','+ str(passage_plan[1])+ '],{icon: red_pointIcon}).addTo(map);'
        route_str = '['+ str(passage_plan[0])+ ','+ str(passage_plan[1])+ ']'
        final_route_text.append(route_str)
        final_route_marker.append(marker_str)


    "dijkstra와 AStar 조합 결과(경과시간)"
    i = 0
    total_dist = 0
    total_time = 0
    while i < len(final_route) - 1:
        start = final_route[i]
        dest = final_route[i + 1]
        dist = util.calc_distance(start,dest)
        "안전속도 일단 16으로 고정"
        time = dist/16
        total_dist = total_dist + dist
        print("좌표 ==> ", (start, dest)," 거리 == >",dist,"시간 = ",time)
        total_time = total_time + time
        i = i + 1
    print("총거리 == ",total_dist)
    print("총시간 == ",total_time)


    return final_route_text,final_route_marker,passage_plan_dict



    #
    # "20미터 이하 수심정보(운행가능한 수심)"
    # mongo_db_depth_info_df = mongo_db.depth_info
    #
    # print(mongo_db_depth_info_df)
    # "범위내 0.01 단위로 격자화"
    # depth_info_df = pd.DataFrame(depth_info)






    # i = 0
    # while i < len(depth_info_df) :
    #     lat = depth_info_df.iloc[i,0]
    #     long = depth_info_df.iloc[i,1]
    #     depth = depth_info_df.iloc[i,2]
    #     j = 0
    #     while j < len(mongo_db_depth_info_df) :
    #         m_lat = mongo_db_depth_info_df.iloc[j, 0]
    #         m_long = mongo_db_depth_info_df.iloc[j, 1]
    #         m_depth = mongo_db_depth_info_df.iloc[j, 2]
    #         #print(mongo_db_depth_info_df.iloc[j])
    #         if(lat == m_lat and long == m_long and depth == m_depth):
    #             #print(mongo_db_depth_info_df.iloc[j])
    #             break
    #         j += 1
    #     i += 1

