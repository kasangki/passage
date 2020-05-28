import os

os.environ["CUDA_VISIBLE_DEVICES"]="0"

import sys
sys.path.append('./')
from .post_database import PostDatabase
from .mongo_database import MongoDatabase
from .dijkstra import Dijkstra
from .astar import AStarSearch,AStarGraph
import pandas as pd
import numpy as np
#import util
from . import util



def makePassagePlanAll():
    post_db = PostDatabase()
    start_port_codes = post_db.get_start_port_code()
    start_port_codes_list = start_port_codes['PORT_CODE'].tolist()
    i = 0
    post_db.get_connection()
    while i < len(start_port_codes_list) :
        post_db = PostDatabase()
        start_port_code = start_port_codes_list[i]
        dest_port_codes = post_db.get_dest_port_code(start_port_code=start_port_code)
        dest_port_codes_list = dest_port_codes['PORT_CODE'].tolist()
        j = 0
        while j < len(dest_port_codes_list) :
            post_db = PostDatabase()
            dest_port_code = dest_port_codes_list[j]
            main(start_port_code,dest_port_code)
            j = j + 1
            post_db.close_connection()
        i = i + 1
        post_db.close_connection()
    post_db.close_connection()



def main(start_port_code,dest_port_code):

    # TB_PORT_CODE 테이블 저장 시작
    post_db = PostDatabase()

    port_code_df = post_db.get_start_dest_port(start_port_code,dest_port_code)
    if(len(port_code_df) == 0) :
        return None
    post_db.save_port_code(port_code_df)
    # TB_PORT_CODE 테이블 저장 끝

    start_latitude = port_code_df.loc[0, 'latitude']
    start_longitude = port_code_df.loc[0, 'longitude']
    dest_latitude = port_code_df.loc[len(port_code_df) - 1, 'latitude']
    dest_longitude = port_code_df.loc[len(port_code_df) - 1, 'longitude']
    start_port_name = port_code_df.loc[0, 'start_port_name']
    dest_port_name = port_code_df.loc[0, 'dest_port_name']
    start_portUnLoCode = port_code_df.loc[0, 'start_portUnLoCode']
    dest_portUnLoCode = port_code_df.loc[0, 'dest_portUnLoCode']
    start_point = (start_latitude,start_longitude)
    dest_point = (dest_latitude,dest_longitude)

    # 작업영역 경계지정
    lat_start = 34.3
    lat_dest = 35.6
    long_start = 127.5
    long_dest = 129.5
    ################


    wave_info_csv = 'esail/algm/data/wave_info_KRUSN_KRKAN.csv'  #
    #wave_info_csv = 'data/wave_info_KRUSN_KRKAN.csv'  #
    # 파고정보
    interval = 0.1
    depth = -20

    #
    #
    #
    #
    # if(passage_id < 50):
    #     "울산 ==>  광양 항로"
    #
    #     csv_name = 'esail/algm/data/KRUSN_KRKAN_'+str(passage_id)+'.csv'   # 울산 ==> 광양
    #
    #     start_port_code = "KRUSN"    # 울산
    #     dest_port_code = "KRKAN"     # 광양
    #     #start_point = (35.38, 129.42)
    #     #dest_point  = (34.75, 127.83)
    #     wave_info_csv = 'esail/algm/data/wave_info_KRUSN_KRKAN.csv'     # 파고정보
    #     lat_start = 34.3
    #     lat_dest = 35.6
    #     long_start = 127.5
    #     long_dest = 129.5
    #
    #     #lat_values = np.arange(lat_start, lat_dest, interval)  # 실험영역( A Star 적용시에 필요) 위도
    #     #long_values = np.arange(long_start, long_dest, interval)  # 실험영역( A Star 적용시에 필요) 경도
    # else :
    #
    #     "광양 ==>  싱가폴 항로"
    #     csv_name = 'esail/algm/data/KRKAN_SGSIN.csv'  # 광양 ==> 싱가폴
    #     start_port_code = "KRKAN"  # 광양
    #     dest_port_code = "SGSIN"  # 싱가폴
    #     #start_point = (34.7472222, 127.8325)
    #     #dest_point  = (1.2311111, 103.8961111)
    #     wave_info_csv = 'esail/algm/data/wave_info_KRUSN_KRKAN.csv'     # 파고정보
    #     lat_start = 1
    #     lat_dest = 35
    #     long_start = 103
    #     long_dest = 128
    #     # lat_values = np.arange(lat_start, lat_dest, interval)  # 실험영역( A Star 적용시에 필요) 위도
    #     # long_values = np.arange(long_start, long_dest, interval)  # 실험영역( A Star 적용시에 필요) 경도




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
    #print("장애물 ====>",depth_set)
    # for passage_plan in depth_set:
    #     print('L.marker([', passage_plan[0], ',', passage_plan[1], '],{icon: pointIcon,title:','테스트','}).addTo(map);')

    dijk.astar_graph.set_barriers(depth_set)




    "============================================================================"
    "항로정보 조회"
    "============================================================================"
    passage_plan_df = dijk.db.get_passage_plan_list_max(start_port_code, dest_port_code)

    if(len(passage_plan_df) < 2) : # 조회해서 1건 이하면 리턴
        return None
    voyage_info_seq_df = passage_plan_df['voyage_info_seq'].drop_duplicates()  # 항차번호

    voyage_info_seq_temp_df = voyage_info_seq_df.copy()

    passage_plan_df.set_index('voyage_info_seq', inplace=True)  # 항차번호로 index 세팅

    passage_plan_df['latitude'] = passage_plan_df['latitude'].astype('float')  # 형변환
    passage_plan_df['longitude'] = passage_plan_df['longitude'].astype('float')  # 형변환

    for voyage_info_seq in np.array(voyage_info_seq_temp_df):

        voyage_info_df = passage_plan_df.loc[voyage_info_seq]
        if(str(type(voyage_info_df)) == "<class 'pandas.core.series.Series'>") :
            continue
        voyage_info_df.iloc[0, 5] = start_latitude
        voyage_info_df.iloc[0, 6] = start_longitude
        voyage_info_df.iloc[-1, 5] = dest_latitude
        voyage_info_df.iloc[-1, 6] = dest_longitude



    # search_count = 20 # 프로그램 속도 감안해서 갯수 지정
    # if(len(voyage_info_seq_df) < search_count) :
    #     search_count = len(voyage_info_seq_df)

    search_count = len(voyage_info_seq_df)
    print("항로조회갯수===",search_count)
    print(passage_plan_df)

    "============================================================================"
    "항로별 노드저장"
    "============================================================================"
    passage_plan_dict ,passage_plan_dict_distance  = dijk.create_passage_plan(passage_plan_df,voyage_info_seq_df,search_count)
    #print("항로 그래프 == ,",dijk.graph.nodes)

    passage_plan_dict_distance = util.make_passage_plan_distance(passage_plan_dict_distance)


    "============================================================================"
    "선분의 교점을 구해서 그래프에 추가"
    "============================================================================"
    dijk.add_cross_point_to_graph(passage_plan_df,voyage_info_seq_df,search_count)


    "============================================================================"
    "모든 노드들을 표시하기 위한 좌표정보"
    "============================================================================"
    # for passage_plan in dijk.graph.nodes:
    #     print('L.marker([', passage_plan[0], ',', passage_plan[1], '],{icon: red_pointIcon}).addTo(map);')


    "============================================================================"
    "등록된 모든 노드들의 최단경로"
    "============================================================================"
    print("start_point = ",start_point,"start_point = ",dest_point)
    route_set = dijk.shortest_path(start_point, dest_point)

    #print(route_set)




    "============================================================================"
    "Dijkstra 알고리즘으로 적용 후 총거리와 시간 구하기"
    "============================================================================"
    i = 0
    total_dist = 0
    total_time = 0
    #print("경로집합 ===> ",route_set)
    if(route_set == None):
        return None
    while i < len(route_set) - 1:
        start = route_set[i]
        dest = route_set[i + 1]
        dist = util.calc_distance(start, dest)
        "안전속도 일단 16으로 고정"
        time = dist / 16
        total_dist = total_dist + dist
        #print("좌표 ==> ", (start, dest), " 거리 == >", dist, "시간 = ", time)
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

    #print("장애물 정보       ================================================>",dijk.astar_graph.barriers)
    #print("장애물 정보 =========> ",graph.barriers)
    #print("장애물 정보 =========> ", len(graph.barriers))
    # for passage_plan in dijk.astar_graph.barriers[0]:
    #      print('L.marker([', passage_plan[0], ',', passage_plan[1], '],{icon: pointIcon}).addTo(map);')

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


    #print("AStar 경로 ",astar_path_list)
    #print("최종경로 === > ",route_set)

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
    #print("경로집합 === >",route_set)
    for route in route_set:
        if (len(route) > 2):
            for rt in route:
                # dijk.log.debug('AStar 최단거리 ==================>  %s' , rt)
                print('[', rt[0], ',', rt[1], '],')
                final_route.append(rt)
        else:
            # dijk.log.debug('최종 최단거리 ==================>  %s', route)
            #print('[', route[0], ',', route[1], '],')
            final_route.append(route)


    select_result = post_db.is_passage_plan(start_portUnLoCode,dest_portUnLoCode)

    if len(select_result) > 0:
        post_db.delete_passage_plan(start_portUnLoCode,dest_portUnLoCode)
        post_db.save_final_route(start_portUnLoCode,dest_portUnLoCode,route_set)
    else:
        post_db.save_final_route(start_portUnLoCode,dest_portUnLoCode,route_set)



    #print("최종 = ",final_route)
    final_route_text = []
    final_route_marker = []
    for passage_plan in final_route:

        longitude_temp = passage_plan[1]  # 경도가 마이너스를 360도 더해서 처리
        if longitude_temp <= 0:
            longitude_temp = longitude_temp + 360

        temp_coord = '['+str(passage_plan[0])+ ','+ str(longitude_temp)+']'
        marker_str = 'L.marker([' + str(passage_plan[0])+ ','+ str(longitude_temp)+ '],{icon: red_pointIcon,title:"'+temp_coord+'"}).bindPopup("'+temp_coord+'").addTo(map).openPopup();'
        route_str = '['+ str(passage_plan[0])+ ','+ str(longitude_temp)+ ']'
        final_route_text.append(route_str)
        final_route_marker.append(marker_str)

    #print(final_route_marker)
    final_route_distance = util.make_route_distance(final_route)


    barriers_list = []
    for barrier in dijk.astar_graph.barriers[0]:
        barrier_str = '['+ str(barrier[0])+ ','+ str(barrier[1])+ ']'
        barriers_list.append(barrier_str)



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
        #print("좌표 ==> ", (start, dest)," 거리 == >",dist,"시간 = ",time)
        total_time = total_time + time
        i = i + 1
    #print("총거리 == ",total_dist)
    #print("총시간 == ",total_time)
    print("출발항구명 ==>",start_port_name)
    print("목적항구명 ==>",dest_port_name)
    title = start_port_name + '->' + dest_port_name
    context = {'passages': final_route,
     'markers': final_route_marker,
     'passage_plan_dict': passage_plan_dict,
     'title': title,
     'barriers_list': barriers_list,
     'final_route_distance': final_route_distance,
     'passage_plan_dict_distance': passage_plan_dict_distance
     }
    #return final_route_text,final_route_marker,passage_plan_dict,barriers_list,final_route_distance,passage_plan_dict_distance,title
    return context



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


#makePassagePlanAll()
#main('KRUSN','KRKAN')
#main('KRMAS','KRMOK')