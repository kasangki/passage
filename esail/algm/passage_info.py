class Passage_Info :

    def __init__(self,start_port,dest_port):
        self.start_port = start_port
        self.dest_port = dest_port


    def set_csv_name(self,csv_name):
        self.csv_name = csv_name



    def set_wave_info_csv_name(self,wave_info_csv_name):
        self.wave_info_csv_name = wave_info_csv_name


    def set_boundary(self, lat_start, lat_dest, long_start, long_dest):
        self.lat_start = lat_start
        self.lat_dest = lat_dest
        self.long_start = long_start
        self.long_dest = long_dest


    def set_interval(self,interval):
        self.interval = interval


    def set_depth(self,depth):
        self.depth = depth


    def set_start_point(self,start_point):
        self.start_point = start_point


    def set_dest_point(self, dest_point):
        self.dest_point = dest_point