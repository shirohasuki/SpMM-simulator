from spmmsim.model.hw_model.compute_model.systolic_array.ProcessingElement import ProcessingElement as PE
import numpy as np

class SystolicArray:
    def __init__(self,row=3,col=3):
        self.row = row
        self.col = col
        self.cycle = 0

        pe_array = []
        for i in range(row):
            pe_row = []
            for j in range(col):
                pe_row.append(PE())
            pe_array.append(pe_row)
        self.pe_array = pe_array

    # 复位
    def reset(self):
        self.cycle = 0
        for i in range(self.row):
            for j in range(self.col):
                self.pe_array[i][j].a = 0
                self.pe_array[i][j].b = 0
                self.pe_array[i][j].partial_sum = 0
                self.pe_array[i][j].mul_result = 0
                self.pe_array[i][j].sum_left = 0


    # 加载权重
    def preload(self, input_a_array):
        for i in range(self.row):
            for j in range(self.col):
                self.pe_array[i][j].a = input_a_array[i][j] 
    # 倒序传递
    def connect(self,input_b_vector):
        for i in range(self.row - 1, -1, -1):
            for j in range(self.col - 1, -1, -1):
                if i == 0:
                    self.pe_array[i][j].b = input_b_vector[j]
                    if j :
                        self.pe_array[i][j].sum_left = self.pe_array[i][j-1].partial_sum
                    else :
                        self.pe_array[i][j].sum_left = 0
                    self.pe_array[i][j].sum_up = 0
                else:
                    self.pe_array[i][j].b = self.pe_array[i-1][j].b
                    if j:
                        self.pe_array[i][j].sum_left = self.pe_array[i][j-1].partial_sum
                    else:
                        self.pe_array[i][j].sum_left = 0
                    self.pe_array[i][j].sum_up = self.pe_array[i-1][j].partial_sum
    
    # 计算单个PE
    def compute_single(self,input_b_vector, enable=False):
        self.cycle = self.cycle + 1
        if enable:
            self.connect(input_b_vector)
            for i in range(self.row):
                for j in range(self.col):
                    self.pe_array[i][j].compute(enable)

    # 生成平行四边形的输入
    def parallelogramize(self,B):
        # 1. 转置矩阵
        B_T = B.T
        rows, cols = B_T.shape
        result = np.zeros((rows+cols-1, cols), dtype=int)

        # 2. 按列逐步向下移动
        for j in range(cols):
            for i in range(rows):
                result[i + j, j] = B_T[i, j]

        return result
    
    # 将平行四边形结果还原为矩形输出
    def deparallelogramize(self, B):
        # 1. 去除初始全为0的几行
        B = np.array(B)
        # B = B[~np.all(B == 0, axis=1)]  # 去除全为0的行

        B = B[self.col-1:]

        # 2. 依次上移每列的元素（顶端移除，底部补0）
        rows, cols = B.shape
        for col in range(1, cols):
            B[:-col, col] = B[col:, col]  # 上移 col 格
            B[-col:, col] = 0             # 底部填充 0

        # 3. 移除尾部全为0的几行
        # B = B[~np.all(B == 0, axis=1)]
        B = B[0:-self.row-self.col]

        # 4. 转置矩阵
        return B.T


    def mvin(self,A,B):
        if A.shape[1] == B.shape[0]:
            self.A = A
            self.B = B
        else :
            print("矩阵形状有误，无法进行乘法")
    

    def compute(self, A, B, enable = False):
        self.mvin(A, B)
        row_cnt = int(self.A.shape[0]/self.row)
        col_cnt = int(self.A.shape[1]/self.col)

        C = np.zeros((self.A.shape[0], self.B.shape[1]))

        for i in range(row_cnt):
            temp_c = np.zeros((self.row, self.B.shape[1]))
            for j in range(col_cnt):
                # 取A的第row*i行到第row*i+row行, 第col*j列到第col*j+col列
                temp_a = self.A[self.row*i:self.row*i+self.row, self.col*j:self.col*j+self.col]
                self.preload(temp_a)
                # 取B的第col*j列到第col*j+col列
                temp_b = self.B[self.col*j:self.col*j+self.col,:]
                temp_b = self.parallelogramize(temp_b)
                zero_rows = np.zeros((self.row + self.col, temp_b.shape[1]))
                # 为下方的PE单元初始先填充0(B先得走PE行数才能到最后一行)
                temp_b = np.vstack((temp_b, zero_rows))
                temp_c_ = []
                
                # WS 循环计算
                for k in range(len(temp_b)):
                    self.compute_single(temp_b[k], enable=enable)
                    if enable:
                        result = np.zeros((self.row))
                        for i_ in range(self.row):
                            result[i_] = self.pe_array[i_][self.col-1].partial_sum
                        temp_c_.append(result)
                if enable:
                    temp_c_ = self.deparallelogramize(np.array(temp_c_))
                    temp_c = temp_c + temp_c_
            if enable:
                C[self.row*i:self.row*i+self.row,:] = temp_c
        
        return C
