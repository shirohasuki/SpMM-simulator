class DRAM:
    def __init__(self,data_num):
        self.data_num = data_num
        # print(f"Dram data num{data_num}")
        self.data = [0 for _ in range(self.data_num)]
    def read_line(self,addr):
        return self.data
    def write_line(self,addr,data):
        None
    def read(self,addr):
        return 0