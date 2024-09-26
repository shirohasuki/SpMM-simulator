from format import SparseRepresentFormat
from sparse_align import SparseAlign
from sparse_addr_convert import SparseAddrConvert
from sparse_skip import SparseSkip
from numpy.lib.stride_tricks import sliding_window_view


from utils.sparse_matrix import SparseMatrix

import numpy as np


class SparseTile: 
    # 原则，软件上永远密集矩阵操作，直到输出
    def __init__(self, ):
        self.a = 0
    
    def sliding_window(self, matrix, window_size=(16, 16)):
        # 获取矩阵的行列数
        # print(gate_matrix_a)
        rows, cols = matrix.shape

        # 计算需要填充的行和列，使得矩阵维度可以被16x16整除
        row_padding = (window_size[0] - rows % window_size[0]) % window_size[0]
        col_padding = (window_size[1] - cols % window_size[1]) % window_size[1]

        # 使用np.pad填充矩阵，填充为-1, 得到可以整除的矩阵
        padded_matrix = np.pad(matrix, 
                            ((0, row_padding), (0, col_padding)), 
                            mode='constant', constant_values=-1)

        tiled_matmul = sliding_window_view(padded_matrix, window_shape=window_size)
        return tiled_matmul

    # 左右左移动计算块(A跳跃, B连续)
    def horizontal_tile(self, A_sparse_matrix, B_dense_matrix):
        
        return 
    
    # 下上下移动计算块(A连续, B跳跃)
    def vertical_tile(self, A_sparse_matrix, B_dense_matrix):
        
        return 
   
    
if __name__ == '__main__':
    A_sparse = SparseMatrix(2048, 2048, 1/16).matrix
    csr_A_sparse = SparseRepresentFormat(A_sparse, 'csr').sparse_matrix

    B_dense = np.random.randint(0, 10, size=(128, 2048))
    

    
    
        
