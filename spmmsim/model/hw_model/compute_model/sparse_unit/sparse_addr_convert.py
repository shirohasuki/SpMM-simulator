# 得到相对于矩阵起始点的位置


class SparseAddrConvert:
    def __init__(self, matrix_row, matrix_col):
        self.matrix_row = matrix_row
        self.matrix_col = matrix_col

    def gate_to_skip(self, gate_access_matrix):
        skip_row_access_matrix = []

        # 遍历每一行
        for row_id, row_access in enumerate(gate_access_matrix):
            # 如果这一行没有访存地址，跳过
            # row_access = row_access.tolist()
            # print(type(row_access))
            if len(row_access) == 0:
                continue
            
            skip_row_access_matrix.append((row_id, row_access))

        return skip_row_access_matrix
    
    # 将相对于行的访存地址转换为相对于整个矩阵的访存地址，输入必须是skip_row_access_matrix
    def row_addr_to_matrix_addr(self, skip_row_access_matrix):
        converted_access_matrix = []

        # 遍历 skip_row_access_matrix 中的每一行
        for row_id, row_access in skip_row_access_matrix:
            # 针对每个访存地址，计算相对于整个矩阵的地址
            matrix_access = row_access
            for i in range(len(row_access)):
                matrix_access[i] = row_id * self.matrix_col + matrix_access[i]
            converted_access_matrix.append((row_id, matrix_access))

        return converted_access_matrix

    # 输入的必须是skip模式访存矩阵
    # 返回的消息格式:(id, [矩阵地址序列], if_vector)
    def skip_message(self, skip_access_matrix, vector_addr=False, vector_size=0):
        skip_access_message_matrix = []

        # 遍历 skip_access_matrix 中的每一行
        for i, (row_id, access) in enumerate(skip_access_matrix):
            if vector_addr: # 访存模式为向量
                skip_access_message_matrix.append((row_id, access, 1))
            else:
                skip_access_message_matrix.append((row_id, access, 0))

        return skip_access_message_matrix
    
    def gate_to_skip_message(self, gate_access_matrix, vector_addr=False, vector_size=0):
        skip_row_access_matrix = self.gate_to_skip(gate_access_matrix)
        # print(skip_row_access_matrix)
        skip_access_matrix = self.row_addr_to_matrix_addr(skip_row_access_matrix)
        # print(skip_access_matrix)
        skip_access_message_matrix = self.skip_message(skip_access_matrix, vector_addr, vector_size)
        # print(skip_access_message_matrix)
        
        return skip_access_message_matrix
        



if __name__ == '__main__':
    # 输入的访存地址矩阵
    gate_access_matrix = [
        [1, 2, 3],  # 第0行的访存地址
        [],         # 第1行无访存地址
        [0, 3],     # 第2行的访存地址
        [1]         # 第3行的访存地址
    ]

    addr_converter = SparseAddrConvert(4, 3)
    
    skip_access_message = addr_converter.gate_to_skip_message(gate_access_matrix)

    # 打印结果
    print("转换后的访存总线消息:", skip_access_message)