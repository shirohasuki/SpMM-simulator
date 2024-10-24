import os
import math
from .utils.lru import LRU
from .cache.cache import L1Cache, L2Cache
from .dram.dram import DRAM 
from .scratchpad.scratchpad import Scratchpad 



    

##################################
class MemSim:
    def __init__(self):
        # self.way = 2
        # self.line_size  = 16 #byte
        # self.total_size = 8 #Kb     
        # self.addr_size = 32 #bit
        self.hit_latency = 1

        # self.l1cache   = L1Cache()
        # self.l2cache   = L2Cache()
    def set_params(self,bank_num,bank_row,dim,data_size,
                   l1_way,l1_total_size, l1_line_size,l1_replacement,l1_addr_size,l1_data_size,
                   l2_way,l2_total_size, l2_line_size,l2_replacement,l2_data_size):
        assert l1_line_size%2==0,"Cacheline size is unalign!"
        assert l1_total_size%2==0,"Cacheline size is unalign!"
        assert (l1_data_size>>3)<=l1_line_size, "Data size is too big,it must less than 64bits"
        assert l1_replacement=="PLRU"

##################init####################
        self.dram = DRAM(int(l1_line_size/(l1_data_size/8)))
        self.scratchpad = Scratchpad(bank_num,bank_row,dim,data_size)
        self.l2cache=L2Cache(l2_way,l2_total_size, l2_line_size,l2_replacement,l1_addr_size,l2_data_size,True)
        self.l1cache=L1Cache(l1_way,l1_total_size, l1_line_size,l1_replacement,l1_addr_size,l1_data_size,False)
        
        self.l2cache.backing_mem = self.dram 
        self.l1cache.backing_mem = self.l2cache    
        self.scratchpad.backing_mem = self.l2cache  
        # self.l1_way         = l1_way #way=0-> 全相连 way=-1 直接相连 way>1 组相联 
        # self.l1_line_size   = l1_line_size #byte
        # self.l1_total_size  = l1_total_size #Kb
        # self.l1_addr_size   = l1_addr_size
        # self.l1_data_size   = l1_data_size#bit
        
        # if(l1_way<1):
        #     self.l1_index_num   = int(l1_total_size*1024/l1_line_size)
        # else:
        #     self.l1_index_num   = int(l1_total_size*1024/l1_way/l1_line_size)

        # self.l1_index_bit   = int(math.log2(self.l1_index_num)) 
        # self.l1_tag_bit     = int(self.l1_addr_size-math.log2(self.l1_line_size)-self.l1_index_bit) 
        # self.l1_offset_bit  = l1_addr_size-self.l1_index_bit-self.l1_tag_bit


    def cache_read(self, addr):
        data = self.l1cache.read(addr)
        return  data
    def cache_write(self, addr, data):
        self.l1cache.write(addr,data)

    def spm_read(self,addr):
        # data = self.l1cache.read(addr)
        # return  data
        return self.scratchpad.read(addr)
    def spm_write(self,addr,data):
        # self.l1cache.write(addr,data)
        self.scratchpad.write(addr,data)

    def print_info(self):
        l1_miss,l1_hit=self.l1cache.print_info()
        l2_miss,l2_hit=self.l2cache.print_info()
        l1_miss_rate = l1_miss/(l1_miss+l1_hit+1)
        l2_miss_rate = l2_miss/(l2_hit+l2_miss+1)
        total_miss_rate = l1_miss_rate*l2_miss_rate    
        print(f'L1Cache hit {l1_hit}  miss {l1_miss} miss rate {l1_miss_rate}')
        print(f'L2Cache hit {l2_hit}  miss {l2_miss} miss rate {l2_miss_rate}')
        print(f'Total miss rate {total_miss_rate}')
    # def cache_write(self,addr,size,data):


    #     tag     = addr>>(self.offset_bit+self.index_bit)
    #     index   = (addr>>self.offset_bit)&((1<<(self.index_bit))-1)
    #     temp = int ((addr&((1<<(self.offset_bit))-1)))
    #     data_region = int(temp/(self.data_size/8))
    #     # assert addr
    #     self.l1cache.write(tag,index,0,data,data_region)
    #     # if not hit:
    #     #     data = self.dram.write(addr,0)
    #     # return  data