import numpy as np
class SparseMatrix:
    def __init__(self, rows, cols, sparsity=1/16, value_range=(0, 5)):
        """
        初始化稀疏矩阵。
        :param rows: 矩阵的行数
        :param cols: 矩阵的列数
        :param sparsity: 稀疏度（0 到 1），表示非零元素的比例
        :param value_range: 非零元素的取值范围，默认 [0, 5]
        """
        self.rows = rows
        self.cols = cols
        self.sparsity = sparsity
        self.value_range = value_range
        self.matrix = self._generate_sparse_matrix()
        self.to_csr()

    def _generate_sparse_matrix(self):
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

    def to_csr(self):
        """
        将稀疏矩阵转换为 CSR 格式
        :return: CSR 格式的三个数组：data, indices, indptr
        """
        data = []  # 非零元素值
        indices = []  # 非零元素的列索引
        indptr = [0]  # 每一行的第一个非零元素在 data 中的位置

        for i in range(self.rows):
            row_non_zero_count = 0
            for j in range(self.cols):
                if self.matrix[i, j] != 0:
                    data.append(self.matrix[i, j])
                    indices.append(j)
                    row_non_zero_count += 1
            indptr.append(indptr[-1] + row_non_zero_count)
        self.data = np.array(data)
        self.indices = np.array(indices)
        self.indptr = np.array(indptr)
        
        # return np.array(data), np.array(indices), np.array(indptr)