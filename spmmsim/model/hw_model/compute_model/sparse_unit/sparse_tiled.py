from format import SparseRepresentFormat
from spmmsim.model.hw_model.compute_model.sparse_unit.sparse_align import SparseAlign
from sparse_addr_convert import SparseAddrConvert
from spmmsim.model.hw_model.compute_model.sparse_unit.sparse_skip import SparseSkip


from utils.sparse_matrix import SparseMatrix

import numpy as np


class SparseTile: 
    # 原则，软件上永远密集矩阵操作，直到输出
    def __init__(self, ):
        self.a = 0
    

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
    

    
    
        
