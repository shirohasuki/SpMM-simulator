import sys
sys.path.append("../")

from SystolicArray import SystolicArray
from SparseMatirx import SparseMatrix
from spmmsim.model.hw_model.compute_model.systolic_array.utils.IndexBuffer import IndexBuffer
from SparseCompution import SparseCompution
import numpy as np


matrix = SparseMatrix(2048,2048,1/16)
A = matrix.matrix
# print(matrix.matrix)
B = np.random.randint(0, 10, size=(2048, 128))

sparecomputeution = SparseCompution(32,2,32)
compution = SystolicArray(4,4)
mode = 1


# C = A@B
# print(A)
# compution.reset()
# result_0 = compution.compute(A,B,enable=False)
# print(compution.cycle)
# if C.all() == result_0.all():
#     print("result_0 correct")
# else:
#     print("result_0 wrong")


result_1 = sparecomputeution.compute(matrix,B,enable=False,mode=mode)
print(sparecomputeution.systolic_array.cycle)
# if C.all() == result_1.all():
#     print("result_1 correct")
# else:
#     print("result_1 wrong")

# rows = 4
# cols = 4
# compution = SystolicArray(rows,cols)
# print("脉动阵列大小为:",(rows,cols))

# A = np.random.randint(0, 10, size=(16, 16))
# matrix = SparseMatrix(16,16,1/4)
# A = matrix.matrix
# print("A矩阵大小为:",A.shape)
# # print(A)

# B = np.random.randint(0, 10, size=(16, 8))
# print("B矩阵大小为:",B.shape)
# # print(B)

# # A = np.loadtxt("A.csv", delimiter=",")
# # B = np.loadtxt("B.csv", delimiter=",")

# C = A@B

# compution.reset()
# result = compution.compute(A,B)
# # print(result)
# if C.all() == result.all():
#     print("计算结果正确！")
# else :
#     print("计算结果错误")
#     # np.savetxt("A.csv", A, delimiter=",", fmt='%d')
#     # np.savetxt("B.csv", B, delimiter=",", fmt='%d')
#     # np.savetxt("C.csv", C, delimiter=",", fmt='%d')
#     # np.savetxt("result.csv", result, delimiter=",", fmt='%d')
