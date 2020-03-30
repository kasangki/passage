
import psycopg2 as postgress
import pandas as pd



"""
 postgress 데이터베이스 클래스
 :param 
 :return: 
 """
class PostDatabase:
    def __init__(self):
        conn_string = "host='211.220.27.191' dbname ='ecbm' user='ecbm' password='ecbm1q2w3e4r!'"
        self.conn = postgress.connect(conn_string)
        self.cur = self.conn.cursor()



    """
     데이터베이스 연결
     :param 
     :return: 
     """
    def get_connection(self):
        conn_string = "host='211.220.27.191' dbname ='ecbm' user='ecbm' password='ecbm1q2w3e4r!'"
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
