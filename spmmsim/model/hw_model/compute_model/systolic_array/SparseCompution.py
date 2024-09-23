from spmmsim.model.hw_model.compute_model.systolic_array.SystolicArray import SystolicArray
from spmmsim.model.hw_model.compute_model.systolic_array.utils.IndexBuffer import IndexBuffer
import numpy as np
import argparse
import os
import configparser as cp


parser = argparse.ArgumentParser()
parser.add_argument('-c', metavar='Config file', type=str,
                        default="./systolic_array.cfg",
                        help="Path to the config file")
args   = parser.parse_args()
    


class SparseCompution:
    # 对于密集计算buffer_col无意义
    def __init__(self, buffer_row_opt, buffer_col_opt, systolic_col_opt):


        config = args.c
        if not os.path.exists(config):
            print("ERROR: Config file not found") 
            print("Input file:" + config)
            print('Exiting')
            exit()
        else: 
            config_file = config

        config = cp.ConfigParser()
        config.read(config_file)

        section = 'systolic_array_presets'
        buffer_width    = int(config.get(section, 'buffer_width'))
        systolic_row    = int(config.get(section, 'systolic_row'))
        systolic_col    = int(config.get(section, 'systolic_col'))
        
        if buffer_row_opt == -1:
            self.buffer_row =  systolic_row
        else:
            self.buffer_row =  buffer_row_opt
        
        if buffer_col_opt == -1:
            self.buffer_col = buffer_width
        else:
            self.buffer_col = buffer_col_opt

        if systolic_col_opt == -1:
            self.systolic_col = systolic_col
        else:
            self.systolic_col = systolic_col_opt
            


        self.index_buffer   = IndexBuffer(row_num=self.buffer_row , col_num=self.buffer_col, systolic_col=self.systolic_col)
        self.systolic_array = SystolicArray(self.buffer_row, self.systolic_col) # 这里的compute是单纯的计算
        self.systolic_array.reset()
    
    def dense_compute(self, matrix_A, matrix_B):
        self.systolic_array.compute(matrix_A, matrix_B)

    def load_matrix(self,A,B):
        self.A = A
        self.B = B
        self.index_buffer.preload_sparse_matrix(A)
    # 带上稀疏的计算
    def sparse_compute(self, A, B, enable=False, mode=1):
        self.load_matrix(A,B)
        # 计算块的数量
        block_num = int(self.A.matrix.shape[0]/self.buffer_row)

        C = np.zeros((self.A.matrix.shape[0], self.B.shape[1]))
        for i in range(block_num):
            # 设计计算块的id(ptr)
            self.index_buffer.block_ptrs = i
            self.index_buffer.clear_buffer()

            read_finish = np.sum(self.index_buffer.row_end)
            compute_finish = np.sum(self.index_buffer.buffer_en)
            # 累加器堆
            temp_C = np.zeros((self.buffer_row, self.B.shape[1]))
            while read_finish != self.buffer_row or compute_finish != 0:
                
                self.index_buffer.load_index()
                index_matrix, index_B = self.index_buffer.launch_inst(mode)

                temp_A = np.zeros((self.buffer_row, self.systolic_col))
                # 加载A矩阵权重
                for j in range(self.buffer_row):
                    for k in range(self.systolic_col):
                        if index_matrix[j][k] == -1:
                            temp_A[j][k] = 0
                        else:
                            row_index = i*self.buffer_row + j
                            temp_A[j][k] = self.A.matrix[row_index][index_matrix[j][k]]
                            
                temp_B = self.B[index_B,:]

                temp_C_ = self.systolic_array.compute(temp_A, temp_B, enable)
                temp_C = temp_C + temp_C_
                
                read_finish = np.sum(self.index_buffer.row_end)
                compute_finish = np.sum(self.index_buffer.buffer_en)

            C[i*self.buffer_row:i*self.buffer_row+self.buffer_row,:] = temp_C
            self.index_buffer.clear_buffer()
        return C  



            

