import numpy as np
from SystolicArray import SystolicArray
from SparseCompution import SparseCompution
from utils.SparseMatirx import SparseMatrix
from utils.IndexBuffer import IndexBuffer


def matmul_eval(matrix_A, matrix_B, systolic_row_opt=-1, systolic_col_opt=-1, 
                buffer_col_opt=-1, mode=0, Sparsity=False):
    if Sparsity:        
        sparse_compute = SparseCompution(systolic_row_opt, buffer_col_opt, systolic_col_opt)
        sparse_compute.systolic_array.reset()
        c = sparse_compute.sparse_compute(matrix_A, matrix_B, mode)
        cycle = sparse_compute.systolic_array.cycle
        print(f"脉动阵列为{systolic_row_opt}x{systolic_col_opt}, 稀疏矩阵填充方式为{mode}, cycle为{cycle}")
        return cycle
    else:
        dense_compute = SparseCompution(systolic_row_opt, buffer_col_opt, systolic_col_opt)
        dense_compute.systolic_array.reset()
        c = dense_compute.dense_compute(matrix_A.matrix, matrix_B)
        print(f"脉动阵列为{systolic_row_opt}x{systolic_col_opt}, 密集矩阵计算cycle:", dense_compute.systolic_array.cycle)
        return dense_compute.systolic_array.cycle

def memory_access_generate(matrix_A, matrix_B, systolic_row_opt=-1, systolic_col_opt=-1, 
                buffer_col_opt=-1, mode=0, Sparsity=False):
    if Sparsity:        
        sparse_compute = SparseCompution(systolic_row_opt, buffer_col_opt, systolic_col_opt)
        sparse_compute.systolic_array.reset()
        c = sparse_compute.sparse_compute(matrix_A, matrix_B, mode)
        cycle = sparse_compute.systolic_array.cycle
        print(f"脉动阵列为{systolic_row_opt}x{systolic_col_opt}, 稀疏矩阵填充方式为{mode}, cycle为{cycle}")
        return cycle
    else:
        dense_compute = SparseCompution(systolic_row_opt, buffer_col_opt, systolic_col_opt)
        dense_compute.systolic_array.reset()
        c = dense_compute.dense_compute(matrix_A.matrix, matrix_B)
        print(f"脉动阵列为{systolic_row_opt}x{systolic_col_opt}, 密集矩阵计算cycle:", dense_compute.systolic_array.cycle)
        return dense_compute.systolic_array.cycle

A = SparseMatrix(2048, 2048, 1/16)
B = np.random.randint(0, 10, size=(2048, 128))

# 测试跳了一个参数
matmul_eval(A, B, 32,  4, mode=0, Sparsity=True)
matmul_eval(A, B, 32,  4, mode=1, Sparsity=False)
matmul_eval(A, B, 32,  4, mode=1, Sparsity=True)
matmul_eval(A, B, 32,  8, mode=0, Sparsity=False)
matmul_eval(A, B, 32,  8, mode=0, Sparsity=True)
matmul_eval(A, B, 32,  8, mode=1, Sparsity=False)
matmul_eval(A, B, 32,  8, mode=1, Sparsity=True)
matmul_eval(A, B, 32, 16, mode=0, Sparsity=False)
matmul_eval(A, B, 32, 16, mode=0, Sparsity=True)
matmul_eval(A, B, 32, 16, mode=1, Sparsity=False)
matmul_eval(A, B, 32, 16, mode=1, Sparsity=True)
matmul_eval(A, B,  4, 32, mode=0, Sparsity=False)
matmul_eval(A, B,  4, 32, mode=0, Sparsity=True)
matmul_eval(A, B,  4, 32, mode=1, Sparsity=False)
matmul_eval(A, B,  4, 32, mode=1, Sparsity=True)
matmul_eval(A, B,  8, 32, mode=0, Sparsity=False)
matmul_eval(A, B,  8, 32, mode=0, Sparsity=True)
matmul_eval(A, B,  8, 32, mode=1, Sparsity=False)
matmul_eval(A, B,  8, 32, mode=1, Sparsity=True)
matmul_eval(A, B, 16, 32, mode=0, Sparsity=False)
matmul_eval(A, B, 16, 32, mode=0, Sparsity=True)
matmul_eval(A, B, 16, 32, mode=1, Sparsity=False)
matmul_eval(A, B, 16, 32, mode=1, Sparsity=True)