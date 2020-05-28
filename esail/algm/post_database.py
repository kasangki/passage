
import psycopg2 as postgress
import pandas as pd
import time
from datetime import datetime


"""
 postgress 데이터베이스 클래스
 :param 
 :return: 
 """
class PostDatabase:
    def __init__(self):
        conn_string = "host='211.51.150.221' dbname ='ecbm' user='ecbm' password='ecbm1q2w3e4r!'"
        self.conn = postgress.connect(conn_string)
        self.cur = self.conn.cursor()

    def close_connection(self):
        self.conn.close()

    """
     데이터베이스 연결
     :param 
     :return: 
     """
    def get_connection(self):
        conn_string = "host='211.51.150.221' dbname ='ecbm' user='ecbm' password='ecbm1q2w3e4r!'"
        conn = postgress.connect(conn_string)
        return conn


    """
     항로번호 조회
     :param start_port : 출발항구
     :param dest_port : 도착항구
     :return: 
     """
    def get_voyage_no(self,start_port,dest_port):
        sql = "SELECT DISTINCT(voyage_no) " \
              "FROM passage_plan " \
              "WHERE start_port = '"+start_port+"' " \
              "AND dest_port = '"+dest_port+"'" \
              "AND voyage_no != '0048E' " \
              "AND voyage_no != '0037W' " \
              #"AND voyage_no != '0045E' " \
              #"AND voyage_no != 'V0036' "\
              #"AND voyage_no != '0026E' " \

        self.cur.execute(sql)
        result = self.cur.fetchall()
        return pd.DataFrame(result)



    """
     항로별 항로번호 조회
     :param voyage_no : 항로번호 
     :param start_port : 출발항구
     :param dest_port : 도착항구
     :return: 
     """
    def get_passage_plan(self,voyage_no,start_port,dest_port):

        sql = "SELECT * FROM passage_plan " \
              "WHERE  voyage_no = '"+voyage_no+"' " \
              "AND start_port = '"+start_port+"' " \
              "AND dest_port = '"+dest_port+"' "
        self.cur.execute(sql)
        result = self.cur.fetchall()
        return pd.DataFrame(result)


    """
     출발항구조회
     :return: 출발항구
     """
    def get_start_port_code(self):

        sql = """
              SELECT DISTINCT("start_portUnLoCode")
              , start_port 
              FROM voyage_info                
              WHERE start_port != ''
              AND START_port >= 'A'
              --AND START_PORT < 'B'
              AND deleted_yn = 'N'
              ORDER BY start_port """
        self.cur.execute(sql)
        result = self.cur.fetchall()
        return pd.DataFrame(result,columns=['PORT_CODE','PORT_NAME'])

    """
     목적지항구조회
     :return: 출발항구
     """
    def get_dest_port_code(self,start_port_code):

        sql =  """
                SELECT DISTINCT("dest_portUnLoCode")
                , dest_port 
                FROM voyage_info 
                WHERE "start_portUnLoCode" = %s
                  AND start_port != %s
                  AND dest_port != %s
                  AND deleted_yn = 'N'
               --   AND dest_port >= 'PAPC'
                  ORDER BY dest_port
               """
        self.cur.execute(sql,(start_port_code,'',''))
        result = self.cur.fetchall()
        return pd.DataFrame(result,columns=['PORT_CODE','PORT_NAME'])



    def get_start_dest_port(self, start_port_code, dest_port_code):


        sql = """
               SELECT aa.voyage_info_seq
                      , aa.seq
                        , aa.latitude
                        , aa.longitude 
                        , bb.start_port
                        , bb.dest_port
                        , bb."start_portUnLoCode"
                        , bb."dest_portUnLoCode"
                FROM voyage_passage_plan aa, voyage_info bb
                WHERE voyage_info_seq = (SELECT  MIN(b.voyage_info_seq)
                FROM voyage_info a, voyage_passage_plan b
                WHERE a.seq = b.voyage_info_seq
                AND a."start_portUnLoCode" = %s
                AND a."dest_portUnLoCode" = %s
                AND b.type = 'RWP'
                AND a.deleted_yn = 'N'
                ) 
                AND TYPE='RWP'
                AND bb.deleted_yn = 'N'
                AND aa.voyage_info_seq = bb.seq
              """



        self.cur.execute(sql,(start_port_code, dest_port_code))
        result = self.cur.fetchall()
        return pd.DataFrame(result, columns=['voyage_info_seq', 'seq','latitude','longitude','start_port_name','dest_port_name','start_portUnLoCode','dest_portUnLoCode'])


    # TB_PORT_CODE 테이블 저장 #
    def save_port_code(self,port_code_df):
        start_latitude = port_code_df.loc[0, 'latitude']
        start_longitude = port_code_df.loc[0, 'longitude']
        dest_latitude = port_code_df.loc[len(port_code_df) - 1, 'latitude']
        dest_longitude = port_code_df.loc[len(port_code_df) - 1, 'longitude']
        start_port_name = port_code_df.loc[0, 'start_port_name']
        dest_port_name = port_code_df.loc[0, 'dest_port_name']
        start_portUnLoCode = port_code_df.loc[0, 'start_portUnLoCode']
        dest_portUnLoCode = port_code_df.loc[0, 'dest_portUnLoCode']


        ts = time.time()

        timestamp = datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        upsert_query = """
                            WITH to_be_upserted (start_portunlocode
                                                , dest_portunlocode
                                                , start_port_name
                                                , dest_port_name
                                                , start_latitude
                                                , start_longitude
                                                , dest_latitude
                                                , dest_longitude
                                                , update_dt
                                                , create_dt
                                                ) 

                            AS (VALUES(
                                  %s::VARCHAR
                                , %s::VARCHAR
                                , %s
                                , %s
                                , %s
                                , %s
                                , %s
                                , %s
                                , %s::TIMESTAMP
                                , %s::TIMESTAMP
                                ) ),

                            updated AS (UPDATE tb_port_code SET 
                                          start_portunlocode = to_be_upserted.start_portunlocode
                                        , dest_portunlocode = to_be_upserted.dest_portunlocode
                                        , start_port_name = to_be_upserted.start_port_name
                                        , dest_port_name = to_be_upserted.dest_port_name
                                        , start_latitude = to_be_upserted.start_latitude
                                        , start_longitude = to_be_upserted.start_longitude
                                        , dest_latitude = to_be_upserted.dest_latitude
                                        , dest_longitude = to_be_upserted.dest_longitude
                                        
                                        , update_dt = to_be_upserted.update_dt
                                        , create_dt = to_be_upserted.create_dt

                            FROM to_be_upserted 
                            WHERE tb_port_code.start_portunlocode = to_be_upserted.start_portunlocode 
                            AND tb_port_code.dest_portunlocode = to_be_upserted.dest_portunlocode
                            RETURNING tb_port_code.start_portunlocode, tb_port_code.dest_portunlocode)

                            INSERT INTO tb_port_code (start_portunlocode, dest_portunlocode, 
                            start_port_name, dest_port_name, start_latitude, start_longitude, 
                            dest_latitude, dest_longitude, create_dt)

                            SELECT start_portunlocode
                                 , dest_portunlocode
                                 , start_port_name
                                 , dest_port_name
                                 , start_latitude
                                 , start_longitude
                                 , dest_latitude
                                 , dest_longitude
                                 , create_dt FROM to_be_upserted
                                 WHERE (start_portunlocode, dest_portunlocode)
                                 NOT IN (SELECT start_portunlocode, 
                                 dest_portunlocode FROM tb_port_code)
                            ;
                            """

        self.cur.execute(upsert_query,
                         (start_portUnLoCode, dest_portUnLoCode, start_port_name, dest_port_name,
         start_latitude, start_longitude, dest_latitude, dest_longitude, timestamp, timestamp))

        self.conn.commit()






    def get_passage_plan_list(self,start_portUnLoCode, dest_portUnLoCode):
        sql = """
                       SELECT  b.voyage_info_seq
                              , b.seq
                              , a."start_portUnLoCode"
                              , a."dest_portUnLoCode"
                              , a.start_port
                              , a.dest_port
                              , b.latitude
                              , b.longitude
                              , a.voyage_no
                              , b."type"
                        FROM voyage_info a, voyage_passage_plan b
                        WHERE a.seq = b.voyage_info_seq
                        AND a."start_portUnLoCode" = %s
                        AND a."dest_portUnLoCode" = %s
                        AND b."type" = 'RWP'
                        AND a.deleted_yn = 'N'
                        ORDER BY b.voyage_info_seq, b.seq
                       """
        self.cur.execute(sql,(start_portUnLoCode,dest_portUnLoCode))
        result = self.cur.fetchall()

        return pd.DataFrame(result , columns=['voyage_info_seq', 'seq','start_portUnLoCode'
                                              ,'dest_portUnLoCode','start_port_name'
                                              ,'dest_port_name','latitude','longitude','voyage_no','type'])

    def get_passage_plan_list_max(self,start_portUnLoCode, dest_portUnLoCode):
        sql = """
                   SELECT  
                         D.voyage_info_seq
                       , F.seq
                       , E."start_portUnLoCode"
                       , E."dest_portUnLoCode"
                       , E.start_port
                       , E.dest_port
                       , F.latitude
                       , F.longitude
                       , D.voyage_no
                       , F."type"

                 FROM (
                         SELECT voyage_no  
                             ,  COUNT(voyage_no)    AS voyage_no_count
                             , MAX(voyage_info_seq)  AS voyage_info_seq
                         FROM 
                            (SELECT  B.voyage_info_seq
                                   , B.seq
                                   , A.voyage_no
                               FROM voyage_info a, voyage_passage_plan b
                               WHERE A.seq = B.voyage_info_seq
                                 AND A."start_portUnLoCode" =  %s
                                 AND A."dest_portUnLoCode" =  %s
                                 AND B."type" = 'RWP'
                                 AND a.deleted_yn = 'N'
                                 ORDER BY B.voyage_info_seq, B.seq 
                             ) C
                           GROUP BY voyage_no,voyage_info_seq
                       ) D ,voyage_info E, voyage_passage_plan F
                          WHERE D.voyage_no = E.voyage_no
                            AND D.voyage_info_seq = F.voyage_info_seq
                            AND E.seq = F.voyage_info_seq
                            AND E."start_portUnLoCode" =  %s
                            AND E."dest_portUnLoCode" =  %s
                            AND E.deleted_yn = 'N'
                            AND F."type" = 'RWP'   
                            AND D.voyage_no_count >= 2
                            ORDER BY voyage_info_seq     ,seq
                 """

        self.cur.execute(sql, (start_portUnLoCode, dest_portUnLoCode,start_portUnLoCode, dest_portUnLoCode))
        result = self.cur.fetchall()

        return pd.DataFrame(result, columns=['voyage_info_seq', 'seq', 'start_portUnLoCode'
            , 'dest_portUnLoCode', 'start_port_name'
            , 'dest_port_name', 'latitude', 'longitude', 'voyage_no','type'])



    def is_passage_plan(self,start_portUnLoCode,dest_portUnLoCode):
        sql = """
              SELECT * from tb_passage_plan 
                    WHERE start_portunlocode = %s
                    AND dest_portunlocode = %s
               """
        self.cur.execute(sql, (start_portUnLoCode, dest_portUnLoCode))
        result = self.cur.fetchall()
        return result

    def delete_passage_plan(self,start_portUnLoCode,dest_portUnLoCode):
        sql = """
                 DELETE from tb_passage_plan 
                 
                 WHERE start_portunlocode = %s
                 AND dest_portunlocode = %s
              """
        self.cur.execute(sql, (start_portUnLoCode, dest_portUnLoCode))
        self.conn.commit()

    def save_passage_plan(self, start_portunlocode, dest_portunlocode, passage_seq, latitude, longitude):
        ts = time.time()
        timestamp = datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

        insert_query = """
        INSERT INTO tb_passage_plan
        (start_portunlocode, dest_portunlocode, passage_seq, latitude, longitude, create_dt)
        VALUES
        (%s,%s,%s::INTEGER,%s,%s,%s::TIMESTAMP)
        """

        self.cur.execute(insert_query,
                         (start_portunlocode, dest_portunlocode, passage_seq,
                          latitude, longitude, timestamp))

        self.conn.commit()



    def save_final_route(self,start_portUnLoCode, dest_portUnLoCode, route_set):
        passage_seq = 1
        for route in route_set:
            latitude = float(route[0])
            longitude = float(route[1])
            self.save_passage_plan(start_portUnLoCode, dest_portUnLoCode, passage_seq, latitude, longitude)
            passage_seq = passage_seq + 1


