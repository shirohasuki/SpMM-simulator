import numpy as np
import matplotlib.pyplot as plt
from numpy.lib.stride_tricks import sliding_window_view
from scipy.sparse import coo_matrix
from sparse_format import SparseRepresentFormat

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
        # 目前这种skip只是for interaction
        # 将 coo_matrix 转换为稠密矩阵
        dense_matrix = sparse_matrix.toarray()
        dense_matrix = self.replace_value_to_idx(dense_matrix)
        
        # 获取矩阵的原始大小
        rows, cols = dense_matrix.shape
        
        # 创建一个与原始矩阵大小相同的全为 -1 的矩阵
        OoO_skip_matrix = np.full((rows, cols), -1, dtype=object)
        
        # 用于记录非零行被填充到哪一行了
        row_idx = 0
        
        # 遍历原稀疏矩阵，按行紧凑填充非零元素，跳过全零行
        for i in range(rows):
            non_zero_elements = [x for x in dense_matrix[i] if x != 0]  # 获取当前行的非零元素
            if non_zero_elements:  # 如果当前行有非零元素
                # 将非零元素紧凑地填入 padded_matrix 的当前行
                OoO_skip_matrix[row_idx, :len(non_zero_elements)] = non_zero_elements
                row_idx += 1  # 更新填充行索引，跳到下一行
        
        return OoO_skip_matrix
    
    

    # 将非0数value换为(x,y)
    def replace_value_to_idx(self, dense_matrix):
        rows, cols = dense_matrix.nonzero()  
        idx_matrix = np.zeros(dense_matrix.shape, dtype=object)
        for r, c in zip(rows, cols):
            idx_matrix[r, c] = (r, c)
        return idx_matrix


        
    
if __name__ == '__main__':
    # sparse_matrix = np.array([[
    #     [1, 2, 3, 0, 1],  
    #     [0, 0, 2, 0, 1],         
    #     [0, 3, 9, 0, 0],     
    #     [1, 0, 5, 0, 1]         
    # ]])

    sparse_matrix = np.array([
        [5, 0, 10,  0, 0],
        [3, 10, 11, 0, 17],
        [0, 0, 0, 0, 0],
        [1, 0, 17, 0, 18],
        [7, 10, 0, 0, 19],
        [0, 0, 0, 0, 0],
    ]) 
    
    sparse_align = SparseSkip(coo_matrix(sparse_matrix), skip_strategy="col_dim").skip_func
    print(f"col_dim_skip\n{sparse_align}")
    sparse_align = SparseSkip(coo_matrix(sparse_matrix), skip_strategy="row_dim").skip_func
    print(f"row_dim_skip\n{sparse_align}")
    sparse_align = SparseSkip(coo_matrix(sparse_matrix), skip_strategy="two_dim").skip_func
    print(f"two_dim_skip\n{sparse_align}")
    sparse_align = SparseSkip(coo_matrix(sparse_matrix), skip_strategy="OoO").skip_func
    print(f"OoO_skip\n{sparse_align}")