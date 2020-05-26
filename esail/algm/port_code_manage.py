from .post_database import PostDatabase

class Port_code_manage :
    def __init__(self):
       self.db    = PostDatabase()


    def get_start_port_code(self):
        start_port_code_df = self.db.get_start_port_code()
        start_port_dict = {}
        i = 0
        while i < len(start_port_code_df) :
            port_code = start_port_code_df.iloc[i,0]
            port_name = start_port_code_df.iloc[i,1]
            start_port_dict[port_code] = port_name
            i = i+1
        return start_port_dict


    def get_dest_port_code(self,start_code):
        dest_port_code_df = self.db.get_dest_port_code(start_code)
        dest_port_dict = {}
        i = 0
        while i < len(dest_port_code_df) :
            port_code = dest_port_code_df.iloc[i,0]
            port_name = dest_port_code_df.iloc[i,1]
            dest_port_dict[port_code] = port_name
            i = i+1
        return dest_port_dict