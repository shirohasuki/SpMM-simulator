import numpy as np
from SparseMatirx import SparseMatrix

class IndexBuffer:
    def __init__(self,row_num,col_num,systolic_col):
        self.row_num = row_num
        self.col_num = col_num
        self.systolic_col = systolic_col

        self.buffer = np.zeros((row_num,col_num))
        self.buffer_flag = np.zeros((row_num,col_num)) #记录数据是否有效，1有效，0无效或已经送出
        self.row_ptrs = np.zeros(row_num) # 记录每一行加载到第几个数了
        self.block_ptrs = 0 #记录运算到哪一块了
        self.row_finish = np.zeros(row_num) #记录每一行是否已经算完

    def preload_sparse_matrix(self,matrix):
        self.matrix = matrix

    def load_index(self):
        for i in range(self.row_num):
            row_index = i + self.block_ptrs*self.row_num
            length = self.matrix.indptr[row_index+1] - self.matrix.indptr[row_index]
            for j in range(self.col_num):
                if(self.row_ptrs[i] == length):
                    self.row_finish[i] = 1
                    break
                if not self.buffer_flag[i][j]:
                    index = int(self.matrix.indptr[row_index] + self.row_ptrs[i])
                    self.buffer[i][j] = self.matrix.indices[index]
                    self.buffer_flag[i][j] = 1
                    self.row_ptrs[i] = self.row_ptrs[i] + 1


    def clear_buffer(self):
        self.buffer = np.zeros((self.row_num,self.col_num))
        self.buffer_flag = np.zeros((self.row_num,self.col_num)) #记录数据是否有效，1有效，0无效或已经送出
        self.row_ptrs = np.zeros(self.row_num) # 记录每一行加载到第几个数了
        self.row_finish = np.zeros(self.row_num)

    def launch_inst(self,mode=1):
        index_matrix = np.full((self.row_num, self.systolic_col), -1)

        col_to_value = {}
        value_to_col = {}

        n,m = self.buffer.shape
        if mode == 0:
            for i in range(n):
                for j in range(m):
                    if self.buffer_flag[i][j]:
                        value = int(self.buffer[i][j])

                        if value in value_to_col:
                            col_idx = value_to_col[value]
                            index_matrix[i][col_idx] = value
                            self.buffer_flag[i][j] = 0
                        else:
                            for col in range(self.systolic_col):
                                if col not in col_to_value:
                                    col_to_value[col] = value
                                    value_to_col[value] = col
                                    index_matrix[i][col] = value
                                    self.buffer_flag[i][j] = 0
                                    break
                                elif col_to_value[col] == value:
                                    index_matrix[i][col] = value
                                    self.buffer_flag[i][j] = 0
                                    break
        else:
            for j in range(m):
                for i in range(n):
                    if self.buffer_flag[i][j]:
                        value = int(self.buffer[i][j])

                        if value in value_to_col:
                            col_idx = value_to_col[value]
                            index_matrix[i][col_idx] = value
                            self.buffer_flag[i][j] = 0
                        else:
                            for col in range(self.systolic_col):
                                if col not in col_to_value:
                                    col_to_value[col] = value
                                    value_to_col[value] = col
                                    index_matrix[i][col] = value
                                    self.buffer_flag[i][j] = 0
                                    break
                                elif col_to_value[col] == value:
                                    index_matrix[i][col] = value
                                    self.buffer_flag[i][j] = 0
                                    break
        # print(col_to_value)
        # print(index_matrix)
        index_B = np.zeros(self.systolic_col,dtype=int)
        for key,value in col_to_value.items():
            index_B[key] = value

        return index_matrix,index_B


    