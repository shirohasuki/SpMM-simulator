import numpy as np

class SparseMatrix:
    def __init__(self, rows, cols, sparsity=1/16, value_range=(0, 5)):
        """
        初始化稀疏矩阵。
        :param rows: 矩阵的行数
        :param cols: 矩阵的列数
        :param sparsity: 稀疏度(0 到 1)，表示非零元素的比例
        :param value_range: 非零元素的取值范围，默认 [0, 5]
        """
        self.rows = rows
        self.cols = cols
        self.sparsity = sparsity
        self.value_range = value_range
        self.matrix = self.generate_sparse_matrix()

    def generate_sparse_matrix(self):
        """
        根据指定的稀疏度生成稀疏矩阵
        """
        # 计算非零元素的数量
        total_elements = self.rows * self.cols
        nnz = int(total_elements * self.sparsity)
        
        # 创建一个全为零的矩阵
        matrix = np.zeros((self.rows, self.cols), dtype=int)
        
        # 随机选择 nnz 个位置并赋值为随机数(范围 0-5)
        indices = np.random.choice(total_elements, nnz, replace=False)
        matrix.flat[indices] = np.random.randint(self.value_range[0], self.value_range[1] + 1, nnz)

        return matrix