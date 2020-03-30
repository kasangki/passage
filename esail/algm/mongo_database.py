import pandas as pd
from urllib.parse import quote_plus
from pymongo import MongoClient
import argparse
import numpy as np

class MongoDatabase :
    def __init__(self):
        # conn_string = "host='211.220.27.191' dbname ='ecbm' user='ecbm' password='ecbm1q2w3e4r!'"
        # self.conn = postgress.connect(conn_string)
        # self.cur = self.conn.cursor()
        args = self.set_args_parser()
        # uri = "mongodb://%s:%s@%s/%s" % (quote_plus(args.user), quote_plus(args.password), args.db_host, args.db_name)
        uri = "mongodb://%s:%s@%s/%s" % (args['user'], args['password'], args['db_host'], args['db_name'])
        self.mongo_client = MongoClient(uri, replicaset=args['replica_set'])

    def set_args_parser(self):
        """
        command line parameter 를 파싱한다.
        :return:
        """
        args_dict = {
            'user': 'esailing',
            'password': 'toogram1!',
            #'db_host': '211.220.27.191:27017,211.220.27.191:27018,211.220.27.191:27019',
            'db_host': '211.220.27.191:27017,211.220.27.191:27018,211.220.27.191:27019',
            'db_name': 'esailing',
            'replica_set': 'das'
        }

        # parser = argparse.ArgumentParser()
        # parser.add_argument("", "--user", default='esailing')
        # parser.add_argument("", "--password", default='toogram1!')
        # parser.add_argument("", "--db_host", default='211.220.27.191:27017,211.220.27.191:27018,211.220.27.191:27019')
        # parser.add_argument("", "--db_name", default='esailing')
        # parser.add_argument("", "--replica_set", default='das')

        # return parser.parse_args()
        return args_dict

    def get_surface_pressure(self):
        collection_gfs_data = self.mongo_client.esailing.gfs_data

        valid_nodes = collection_gfs_data.find({'$and': [{'lat': {'$gte': 1}}, {'lat': {'$lte': 35}},
                                                           {'long': {'$gte': 103}}, {'long': {'$lte': 128}},
                                                           {'dateTime':'20190308000000'}
                                                           ]})

        df = pd.DataFrame(list(valid_nodes))
        return df


    "파고 구하기"
    def get_wave_height(self):

        collection_wave_data = self.mongo_client.esailing.windwave_data
        print(collection_wave_data)
        # valid_nodes = collection_wave_data.find({'$and': [{'lat': {'$gte': 34.3}}, {'lat': {'$lte': 35.6}},
        #                                                    {'long': {'$gte': 127.5}}, {'long': {'$lte': 129.5}},
        #                                                    {'dateTimeUTCK' : {'$gte' :'20200210210000'}}
        #                                                    ]})
        valid_nodes = collection_wave_data.find({}).limit(10)
        df = pd.DataFrame(list(valid_nodes))

        return df

    "수심 데이터프레임을 리스트로 변환"
    def change_depth_to_list(self,mongo_db_depth_info_df):
        depth_set = []
        i = 0
        while i < len(mongo_db_depth_info_df):
            depth_set.append((mongo_db_depth_info_df.iloc[i, 0], mongo_db_depth_info_df.iloc[i, 1]))
            i += 1
        return depth_set

    "깊이 정보"
    def get_depth_path(self,lat_start,lat_dest,long_start,long_dest,depth,tag):

        collection_depth_data = self.mongo_client.esailing.depth_data

        valid_nodes = collection_depth_data.find({'$and': [{'lat': {'$gte': lat_start}}, {'lat': {'$lte': lat_dest}},
                                                           {'long': {'$gte': long_start}}, {'long': {'$lte': long_dest}},
                                                           {'depth': {tag: depth}}]},
                                                 {'lat': 1, 'long': 1, 'depth': 1, '_id': 0})

        df = round(pd.DataFrame(list(valid_nodes)),1)

        return df

    "수심정보"
    def get_depth_barriers(self,lat_values,long_values,mongo_db_depth_info_df):
        i = 0
        total_set = []
        while i < len(lat_values):
            j = 0
            while j < len(long_values):
                total_set.append((np.round(lat_values[i],1),np.round(long_values[j],1)))
                j += 1
            i += 1

        "20미터 이하 수심정보(운행가능한 수심)"
        depth_set = []
        i = 0
        while i < len(mongo_db_depth_info_df):
            depth_set.append((mongo_db_depth_info_df.iloc[i,0],mongo_db_depth_info_df.iloc[i,1]))
            i += 1

        diff_depth = list(set(total_set).difference(set(depth_set)))

        print("전체격자모양 ======>", len(total_set))
        print("수심20미터 이하 크기 ======>", len(mongo_db_depth_info_df))
        print("장애물 사이즈 ==> ", len(diff_depth))

        return diff_depth





# lat_values = np.arange(1, 35, 0.1)      # 실험영역( A Star 적용시에 필요) 위도
# long_values = np.arange(103, 128, 0.1)   # 실험영역( A Star 적용시에 필요) 경도
# #lat_values = np.arange(34.3, 35.6, 0.1)      # 실험영역( A Star 적용시에 필요) 위도
# #long_values = np.arange(127.5, 129.5, 0.1)   # 실험영역( A Star 적용시에 필요) 경도
# mongo_db = MongoDatabase()


# 장애물 조회
# wave_height = mongo_db.get_wave_height()
# wave_height.to_csv(path_or_buf='wave_info_KRUSN_KRKAN.csv', encoding='utf-8-sig')

# sur_df = mongo_db.get_surface_pressure()
# print(sur_df['lat'],sur_df['long'])
#

# # 장애물 조회
# diff_depth = mongo_db.get_depth_barriers()
# for depth in diff_depth:
#     print(depth)


