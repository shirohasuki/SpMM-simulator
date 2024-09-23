from spmmsim.model.hw_model.compute_model.systolic_array.SystolicArray import SystolicArray
from spmmsim.model.hw_model.compute_model.systolic_array.utils.IndexBuffer import IndexBuffer
import numpy as np

class SparseCompution:
    # 对于密集计算buffer_col无意义，随便填就行
    def __init__(self, buffer_row, buffer_col, systolic_col):
        self.buffer_row = buffer_row
        self.buffer_col = buffer_col
        self.systolic_col = systolic_col

        self.index_buffer   = IndexBuffer(row_num=buffer_row,col_num=buffer_col,systolic_col=systolic_col)
        self.systolic_array = SystolicArray(buffer_row, systolic_col) # 这里的compute是单纯的计算
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
        block_num = int(self.A.matrix.shape[0]/self.buffer_row)

        C = np.zeros((self.A.matrix.shape[0],self.B.shape[1]))
        for i in range(block_num):
            self.index_buffer.block_ptrs = i
            self.index_buffer.clear_buffer()
            read_finish = np.sum(self.index_buffer.row_finish)
            compute_finish = np.sum(self.index_buffer.buffer_flag)
            temp_C = np.zeros((self.buffer_row,self.B.shape[1]))
            while read_finish != self.buffer_row or compute_finish != 0:
                self.index_buffer.load_index()
                index_matrix,index_B = self.index_buffer.launch_inst(mode)

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
                
                read_finish = np.sum(self.index_buffer.row_finish)
                compute_finish = np.sum(self.index_buffer.buffer_flag)

            C[i*self.buffer_row:i*self.buffer_row+self.buffer_row,:] = temp_C
            self.index_buffer.clear_buffer()
        return C  



            

