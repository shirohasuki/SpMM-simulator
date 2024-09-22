from SystolicArray import SystolicArray
from SparseMatirx import SparseMatrix
from IndexBuffer import IndexBuffer
from SparseCompution import SparseCompution
import numpy as np


def eval(systolic_row, systolic_col, matrix_A, matrix_B, mode=0, Sparsity=False):
    if Sparsity:
        buffer_width = [2, 4, 8, 16, 32]
        cycles = []
        for i in buffer_width:
            sparse_compute = SparseCompution(systolic_row, i, systolic_col)
            sparse_compute.systolic_array.reset()
            c = sparse_compute.compute(matrix_A,matrix_B,mode)
            cycle = sparse_compute.systolic_array.cycle
            cycles.append(cycle)
            print(f"脉动阵列为{systolic_row}x{systolic_col}, buf宽度为{i}, 填充方式为{mode}, cycle为{cycle}")
    else:
        dense_compute = SystolicArray(systolic_row,systolic_col)
        dense_compute.reset()
        c = dense_compute.compute(matrix_A.matrix,matrix_B)
        print("密集矩阵计算cycle:", dense_compute.cycle)

A = SparseMatrix(2048, 2048, 1/16)
B = np.random.randint(0, 10, size=(2048, 128))

eval(32,  4, A, B, 0, True)
eval(32,  4, A, B, 1, False)
eval(32,  4, A, B, 1, True)
eval(32,  8, A, B, 0, False)
eval(32,  8, A, B, 0, True)
eval(32,  8, A, B, 1, False)
eval(32,  8, A, B, 1, True)
eval(32, 16, A, B, 0, False)
eval(32, 16, A, B, 0, True)
eval(32, 16, A, B, 1, False)
eval(32, 16, A, B, 1, True)
eval(4,  32, A, B, 0, False)
eval(4,  32, A, B, 0, True)
eval(4,  32, A, B, 1, False)
eval(4,  32, A, B, 1, True)
eval(8,  32, A, B, 0, False)
eval(8,  32, A, B, 0, True)
eval(8,  32, A, B, 1, False)
eval(8,  32, A, B, 1, True)
eval(16, 32, A, B, 0, False)
eval(16, 32, A, B, 0, True)
eval(16, 32, A, B, 1, False)
eval(16, 32, A, B, 1, True)

