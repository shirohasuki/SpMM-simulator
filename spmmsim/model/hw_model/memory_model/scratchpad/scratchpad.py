class Scratchpad:
    def __init__(self,bank_num,bank_row,dim,data_size):
        self.bank_num = bank_num
        self.bank_row =bank_row 
        self.dim=dim
        self.data_size = data_size
        self.backing_mem = None
        
    def read(self,addr):
        req_num = int(self.dim*(self.data_size/8)/self.backing_mem.line_size)#需要去读的cacheline的数目
        data_num = int(self.backing_mem.line_size/self.backing_mem.data_size)

        rdata = [0 for _ in range(req_num*(data_num))]
        for i in range(req_num):
            data = self.backing_mem.read_line(addr)
            for j  in range(data_num):
                rdata[j+i*data_num] = data[j]
        return rdata

    def write(self,addr,data):
        req_num = int(self.dim*(self.data_size/8)/self.backing_mem.line_size)#需要去写的cacheline的数目
        data_num = int(self.backing_mem.line_size/self.backing_mem.data_size)

        wdata = [[0 for _ in range(data_num)] for _ in range(req_num)]


        for i in range(req_num):
            for j  in range(data_num):
                wdata[i][j] = data[j+i*data_num]
        for i in range(req_num):
            self.backing_mem.write_line(wdata[i],addr)