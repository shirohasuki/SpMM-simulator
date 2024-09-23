import numpy as np
from SystolicArray import SystolicArray
from SparseCompution import SparseCompution
from utils.SparseMatirx import SparseMatrix
from utils.IndexBuffer import IndexBuffer

def matmul_eval(systolic_row, systolic_col, matrix_A, matrix_B, mode=0, Sparsity=False):
    if Sparsity:
        buffer_width = [2, 4, 8, 16, 32]
        cycles = []
        for i in buffer_width:
            sparse_compute = SparseCompution(systolic_row, i, systolic_col)
            sparse_compute.systolic_array.reset()
            c = sparse_compute.sparse_compute(matrix_A, matrix_B, mode)
            cycle = sparse_compute.systolic_array.cycle
            cycles.append(cycle)
            print(f"脉动阵列为{systolic_row}x{systolic_col}, buf宽度为{i}, 填充方式为{mode}, cycle为{cycle}")
        return cycle
    else:
        dense_compute = SparseCompution(systolic_row, 0, systolic_col)
        # dense_compute = SystolicArray(systolic_row, systolic_col)
        dense_compute.systolic_array.reset()
        c = dense_compute.dense_compute(matrix_A.matrix, matrix_B)
        print("密集矩阵计算cycle:", dense_compute.cycle)
        return dense_compute.cycle

A = SparseMatrix(2048, 2048, 1/16)
B = np.random.randint(0, 10, size=(2048, 128))

