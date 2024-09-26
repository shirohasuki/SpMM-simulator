import numpy as np
import matplotlib.pyplot as plt
from numpy.lib.stride_tricks import sliding_window_view
from scipy.sparse import coo_matrix
from format import SparseRepresentFormat

class SparseSkip:
    def __init__(self, ):
        self.matrix_row = 0
        self.matrix_col = 0
        self.sparse_strategy = ["col_dim", "row_dim", "two_dim", "insert", "OoO"]
	
    # def col_dim_skip(self, sparse_matrix):
    #     # 将稀疏矩阵转换为密集矩阵
    #     dense_matrix = sparse_matrix.toarray()

    #     # 去除全零列
    #     non_zero_cols = ~np.all(dense_matrix == 0, axis=0)  # 找到非全零的列
    #     col_skip_matrix = dense_matrix[:, non_zero_cols]    # 提取这些列
        
    #     return col_skip_matrix
    
    def col_dim_skip(self, sparse_matrix):
        # 将稀疏矩阵转换为密集矩阵
        dense_matrix = sparse_matrix.toarray()

        rows, cols = sparse_matrix.nonzero()  
        new_dense_matrix = np.zeros(dense_matrix.shape, dtype=object)
        # 将value换为(x,y)
        for r, c in zip(rows, cols):
            new_dense_matrix[r, c] = (r, c)

        # 去除全零列
        non_zero_cols = ~np.all(new_dense_matrix == 0, axis=0)  # 找到非全零的列
        col_skip_matrix = new_dense_matrix[:, non_zero_cols]  # 提取这些列
        
        # print(col_skip_matrix)
        return col_skip_matrix

    
    def row_dim_skip(self, sparse_matrix):
        # 将稀疏矩阵转换为密集矩阵
        dense_matrix = sparse_matrix.toarray()

        # 去除全零行
        non_zero_rows = ~np.all(dense_matrix == 0, axis=1)  # 找到非全零的行
        row_skip_matrix = dense_matrix[non_zero_rows, :]    # 提取这些行
        
        return row_skip_matrix
    
    def two_dim_skip(self, sparse_matrix):
        # 将稀疏矩阵转换为密集矩阵
        dense_matrix = sparse_matrix.toarray()

        # 去除全零行
        non_zero_rows = ~np.all(dense_matrix == 0, axis=1)  # 找到非全零的行
        dense_matrix = dense_matrix[non_zero_rows, :]        # 提取非全零行

        # 去除全零列
        non_zero_cols = ~np.all(dense_matrix == 0, axis=0)  # 找到非全零的列
        two_dim_skip_matrix = dense_matrix[:, non_zero_cols]  # 提取非全零列
        
        return two_dim_skip_matrix
    


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
    
    sparse_aligen = SparseSkip().col_dim_skip(coo_matrix(sparse_matrix))
    print(sparse_aligen)
    sparse_aligen = SparseSkip().row_dim_skip(coo_matrix(sparse_matrix))
    print(sparse_aligen)
    sparse_aligen = SparseSkip().two_dim_skip(coo_matrix(sparse_matrix))
    print(sparse_aligen)