import numpy as np
# from spmmsim.model.hw_model.compute_model.systolic_array.utils.SparseMatirx import SparseMatrix

class IndexBuffer:
    def __init__(self,row_num,col_num,systolic_col):
        self.row_num = row_num
        self.col_num = col_num
        self.systolic_col = systolic_col

        self.buffer = np.zeros((row_num, col_num))
        self.buffer_en = np.zeros((row_num, col_num)) # 脉动阵列大小的mask. 记录数据是否有效, 1有效, 0无效或已经送出
        self.row_ptrs = np.zeros(row_num) # 记录每一行加载到第几个数了
        self.block_ptrs = 0 # 记录运算到哪一块了
        self.row_end = np.zeros(row_num) #记录每一行是否已经算完

    def preload_sparse_matrix(self, matrix):
        self.matrix = matrix

    # 从CSR的稀疏矩阵中加载索引和值到缓冲区
    # def load_index(self):
    #     # 遍历row_num x col_num的buffer
    #     for i in range(self.row_num):
    #         row_index = i + self.block_ptrs*self.row_num # 总CSR的nnz里第几行
    #         length = self.matrix.indptr[row_index+1] - self.matrix.indptr[row_index] # 这一行多少数
    #         for j in range(self.col_num):
    #             if (self.row_ptrs[i] == length): # 这一行扫完了
    #                 self.row_end[i] = 1
    #                 break
    #             if not self.buffer_en[i][j]:
    #                 index = int(self.matrix.indptr[row_index] + self.row_ptrs[i]) # 总CSR的nnz里第几个)(第row_index行的row_ptrs列)
    #                 self.buffer_en[i][j] = 1 # 使能置为1
    #                 self.buffer[i][j] = self.matrix.indices[index] # 总CSR的nnz里第几个数的值
    #                 self.row_ptrs[i] = self.row_ptrs[i] + 1 # 这行的列指针接着往前走一步
    
    def load_index(self):
        # 遍历row_num x col_num的buffer
        for i in range(self.row_num):
            row_index = i + self.block_ptrs * self.row_num  # 总CSR的nnz里第几行
            length = self.matrix.indptr[row_index+1] - self.matrix.indptr[row_index]  # 这一行多少数

            # 打印当前行所用到的 indptr 和对应的 indices 范围
            # print(f"Processing row_index: {row_index}")
            # print(f"indptr[{row_index}] = {self.matrix.indptr[row_index]}, indptr[{row_index+1}] = {self.matrix.indptr[row_index+1]}")
            # print(f"indices used in this row: {self.matrix.indices[self.matrix.indptr[row_index]:self.matrix.indptr[row_index+1]]}")

            for j in range(self.col_num):
                if self.row_ptrs[i] == length:  # 这一行扫完了
                    self.row_end[i] = 1
                    break
                if not self.buffer_en[i][j]:
                    index = int(self.matrix.indptr[row_index] + self.row_ptrs[i])  # 总CSR的nnz里第几个)(第row_index行的row_ptrs列

                    # 打印正在加载的值
                    # print(f"Loading indices[{index}] for buffer[{i}][{j}]")
                    # print(f"indices[{index}] value: {self.matrix.indices[index]}")

                    self.buffer_en[i][j] = 1  # 使能置为1
                    self.buffer[i][j] = self.matrix.indices[index]  # 总CSR的nnz里第几个数的值
                    self.row_ptrs[i] = self.row_ptrs[i] + 1  # 这行的列指针接着往前走一步

        # 在函数结束后，打印出最终处理过的 indptr 和 indices 的整体情况
        # print("Final state of indptr used:")
        # print(self.matrix.indptr[:self.row_num + 1 + self.block_ptrs * self.row_num])
        
        # print("Final state of indices used:")
        # for i in range(self.row_num):
        #     row_index = i + self.block_ptrs * self.row_num
        #     print(f"indices for row {row_index}: {self.matrix.indices[self.matrix.indptr[row_index]:self.matrix.indptr[row_index+1]]}")



    def clear_buffer(self):
        self.buffer = np.zeros((self.row_num, self.col_num))
        self.buffer_en = np.zeros((self.row_num, self.col_num)) # 记录数据是否有效，1有效，0无效或已经送出
        self.row_ptrs = np.zeros(self.row_num) # 记录每一行加载到第几个数了
        self.row_end = np.zeros(self.row_num)

    def launch_inst(self, mode=1):
        index_matrix = np.full((self.row_num, self.systolic_col), -1)

        col_to_value = {}
        value_to_col = {}

        n, m = self.buffer.shape
        if mode == 0: # 行优先
            for i in range(n):
                for j in range(m):
                    if self.buffer_en[i][j]:
                        value = int(self.buffer[i][j])

                        if value in value_to_col:
                            col_idx = value_to_col[value]
                            index_matrix[i][col_idx] = value
                            self.buffer_en[i][j] = 0
                        else:
                            for col in range(self.systolic_col):
                                if col not in col_to_value:
                                    col_to_value[col] = value
                                    value_to_col[value] = col
                                    index_matrix[i][col] = value
                                    self.buffer_en[i][j] = 0
                                    break
                                elif col_to_value[col] == value:
                                    index_matrix[i][col] = value
                                    self.buffer_en[i][j] = 0
                                    break
        else: # 列优先
            for j in range(m):
                for i in range(n):
                    if self.buffer_en[i][j]:
                        value = int(self.buffer[i][j])

                        if value in value_to_col:
                            col_idx = value_to_col[value]
                            index_matrix[i][col_idx] = value
                            self.buffer_en[i][j] = 0
                        else:
                            for col in range(self.systolic_col):
                                if col not in col_to_value:
                                    col_to_value[col] = value
                                    value_to_col[value] = col
                                    index_matrix[i][col] = value
                                    self.buffer_en[i][j] = 0
                                    break
                                elif col_to_value[col] == value:
                                    index_matrix[i][col] = value
                                    self.buffer_en[i][j] = 0
                                    break
        # print(col_to_value)
        # print(index_matrix)
        index_B = np.zeros(self.systolic_col,dtype=int)
        for key,value in col_to_value.items():
            index_B[key] = value

        return index_matrix, index_B


    