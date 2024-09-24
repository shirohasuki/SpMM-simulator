import numpy as np

# 返回memory_access hit或者miss
def memory_access_eval(matrix_A, matrix_B, systolic_row_opt=-1, systolic_col_opt=-1, 
                buffer_col_opt=-1, mode=0, Sparsity=False):
    if_hit = False
    return if_hit