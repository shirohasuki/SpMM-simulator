import numpy as np
import matplotlib.pyplot as plt
from numpy.lib.stride_tricks import sliding_window_view
from scipy.sparse import coo_matrix
from format import SparseRepresentFormat

class SparseSkip:
    def __init__(self, sparse_matrix, skip_strategy):
        #
        # 输入稀疏矩阵
        # 输出skip后的toarray矩阵, 每个value修改输入矩阵中的绝对坐标
        #
        self.skip_func_map = {
            "col_dim": self.col_dim_skip(sparse_matrix), 
            "row_dim": self.row_dim_skip(sparse_matrix), 
            "two_dim": self.two_dim_skip(sparse_matrix), 
            "concat" : self.concat_skip(sparse_matrix), 
            "OoO"    : self.OoO_skip(sparse_matrix)
        } # map字典

        if skip_strategy not in self.skip_func_map:
            raise ValueError(f"Unknown strategy: {skip_strategy}")
        
        self.skip_func = self.skip_func_map[skip_strategy]
    
    def col_dim_skip(self, sparse_matrix):
        # 将稀疏矩阵转换为密集矩阵
        dense_matrix = sparse_matrix.toarray()
        dense_matrix = self.replace_value_to_idx(dense_matrix)
        # 去除全零列
        non_zero_cols = ~np.all(dense_matrix == 0, axis=0)  # 找到非全零的列
        col_skip_matrix = dense_matrix[:, non_zero_cols]  # 提取这些列
        
        return col_skip_matrix

    def row_dim_skip(self, sparse_matrix):
        # 将稀疏矩阵转换为密集矩阵
        dense_matrix = sparse_matrix.toarray()
        dense_matrix = self.replace_value_to_idx(dense_matrix)
        
        # 去除全零行
        non_zero_rows = ~np.all(dense_matrix == 0, axis=1)  # 找到非全零的行
        row_skip_matrix = dense_matrix[non_zero_rows, :]    # 提取这些行
        
        return row_skip_matrix
    
    def two_dim_skip(self, sparse_matrix):
        # 将稀疏矩阵转换为密集矩阵
        dense_matrix = sparse_matrix.toarray()
        dense_matrix = self.replace_value_to_idx(dense_matrix)
        
        # 去除全零行
        non_zero_rows = ~np.all(dense_matrix == 0, axis=1)  # 找到非全零的行
        dense_matrix = dense_matrix[non_zero_rows, :]        # 提取非全零行

        # 去除全零列
        non_zero_cols = ~np.all(dense_matrix == 0, axis=0)  # 找到非全零的列
        two_dim_skip_matrix = dense_matrix[:, non_zero_cols]  # 提取非全零列
        
        return two_dim_skip_matrix
    

    def concat_skip(self, sparse_matrix):
  
        return sparse_matrix
    

    def OoO_skip(self, sparse_matrix):
  
        return sparse_matrix
    

    # 将value换为(x,y)
    def replace_value_to_idx(self, dense_matrix):
        rows, cols = dense_matrix.nonzero()  
        idx_matrix = np.zeros(dense_matrix.shape, dtype=object)
        for r, c in zip(rows, cols):
            idx_matrix[r, c] = (r, c)
        return idx_matrix

    # # WS 得到 A 矩阵的访存
    # def sliding_window(self, gate_matrix_a, window_size=(16, 16)):
    #     # 获取矩阵的行列数
    #     # print(gate_matrix_a)
    #     rows, cols = gate_matrix_a.shape

    #     # 计算需要填充的行和列，使得矩阵维度可以被16x16整除
    #     row_padding = (window_size[0] - rows % window_size[0]) % window_size[0]
    #     col_padding = (window_size[1] - cols % window_size[1]) % window_size[1]

    #     # 使用np.pad填充矩阵，填充为-1, 得到可以整除的矩阵
    #     padded_matrix = np.pad(gate_matrix_a, 
    #                         ((0, row_padding), (0, col_padding)), 
    #                         mode='constant', constant_values=-1)

    #     tiled_matmul = sliding_window_view(padded_matrix, window_shape=window_size)
    #     return tiled_matmul
    
    # def aligned_access(self, tiled_matmul_a, gate_matrix_b):
    #     A_access_seq = []
    #     B_access_seq = []
    #     row_block_id = 0
    #     PE_id = 0
    #     for row_block in range(len(tiled_matmul_a)):
    #         row_block_id += 1
    #         for PE_block in range(len(tiled_matmul_a[row_block])):
    #             for PE in range(len(tiled_matmul_a[row_block][PE_block])):
    #                 tiled_A = tiled_matmul_a[row_block][PE_block][PE]
    #                 # 获取tiled_A每列的第一个非零元素
    #                 tiled_B = tiled_A[np.argmax(tiled_A != 0, axis=0), np.arange(tiled_A.shape[1])]
    #                 # 对于全零列，将其设为 0
    #                 tiled_B[np.all(tiled_A == 0, axis=0)] = 0
    #                 A_access_seq.append((row_block_id, PE_id, tiled_A))
    #                 B_access_seq.append((row_block_id, PE_id, tiled_B))
    #                 PE_id += 1
                             
    #     return A_access_seq, B_access_seq


        
    
if __name__ == '__main__':
    # sparse_matrix = np.array([[
    #     [1, 2, 3, 0, 1],  
    #     [0, 0, 2, 0, 1],         
    #     [0, 3, 9, 0, 0],     
    #     [1, 0, 5, 0, 1]         
    # ]])

    sparse_matrix = np.array([
        [5, 8, 10,  0, 16],
        [3, 10, 11, 0, 16],
        [0, 0, 0, 0, 0],
        [1, 10, 17, 0, 18],
        [7, 10, 15, 0, 19],
        [0, 0, 0, 0, 0],
    ]) 
    
    sparse_aligen = SparseSkip(coo_matrix(sparse_matrix), skip_strategy="col_dim").skip_func
    print(sparse_aligen)
    sparse_aligen = SparseSkip(coo_matrix(sparse_matrix), skip_strategy="row_dim").skip_func
    print(sparse_aligen)
    sparse_aligen = SparseSkip(coo_matrix(sparse_matrix), skip_strategy="two_dim").skip_func
    print(sparse_aligen)