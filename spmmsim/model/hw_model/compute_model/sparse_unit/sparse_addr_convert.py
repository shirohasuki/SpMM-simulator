# 得到相对于矩阵起始点的位置
    
from collections import deque
import numpy as np

class SparseAddrConvert:
    def __init__(self, storage_strategy, PE_tile_array, vector_addr, vector_len, log_file):
        #
        # 输入 PE_tile_array
        # 输出最终访存序列
        #         
        # self.storage_strategy_map = {
        #     "dense": self.dense_storage_addr(PE_tile_array, vector_addr, vector_len), 
        #     "sparse": self.sparse_storage_addr(PE_tile_array, vector_addr, vector_len), 
        # } # map字典

        # if storage_strategy not in self.storage_strategy_map:
        #     raise ValueError(f"Unknown strategy: {storage_strategy}")
        if (storage_strategy == "sparse"):
            self.vaddr_msg = self.sparse_storage_addr(PE_tile_array, vector_addr, vector_len)
        elif (storage_strategy == "dense"):
            self.vaddr_msg = self.dense_storage_addr(PE_tile_array, vector_addr, vector_len)
        else:
            self.vaddr_msg=0
                    
        if log_file:
            np.set_printoptions(threshold=np.inf)
            with open(log_file, "w") as f:
                # print(self.vaddr_msg)
                for block_row_id, pe_id, addrs in self.vaddr_msg:
                    line = f"[block_row_id: {block_row_id}, PE_id: {pe_id}], [vector_addr: {vector_addr}, vector_len: {vector_len}][ "
                    line += ", ".join(map(str, addrs)) + " ]\n"
                    f.write(line)     
            np.set_printoptions(threshold=1000)
    

    def dense_storage_addr(self, PE_tile_array, vector_addr=False, vector_len=0):
        # print("in dense")
        access_msg = []
        PE_ID = 0
        for block_row_id, pe_id, tile_coo in PE_tile_array:
            cols = []
            for row, col, value in zip(tile_coo.row, tile_coo.col, tile_coo.data):
                if value == -1:
                    continue
                (row_i, col_i) = value
                cols.append(col_i)  # 只保存col_i

            access_msg.append((block_row_id, PE_ID, cols))  # 返回元组
            PE_ID += 1
        return access_msg

    def sparse_storage_addr(self, PE_tile_array, vector_addr=False, vector_len=0):
        # print("in sparse")
        global_counter = 1  # 全局编码从 1 开始
        encoded_values = []  # 保存编码后的值和对应位置

        for block_row_id in range(max(block_row_id for block_row_id, _, _ in PE_tile_array) + 1):
            block_row_pes = [tile for row_id, pe_id, tile in PE_tile_array if row_id == block_row_id]
            if not block_row_pes:
                continue

            num_rows, num_cols = block_row_pes[0].shape

            # 遍历每个 tile
            for i in range(num_rows):
                for pe_id, tile in enumerate(block_row_pes):
                    for j in range(num_cols):
                        if tile[i][j] not in (0, -1):  # 检查非零且非-1
                            # print("here")
                            encoded_values.append((block_row_id, pe_id, i, j, global_counter))
                            global_counter += 1  

        block_row_pe_dict = {}
        for block_row_id, pe_id, row, col, access in encoded_values:
            if (block_row_id, pe_id) not in block_row_pe_dict:
                block_row_pe_dict[(block_row_id, pe_id)] = []
            block_row_pe_dict[(block_row_id, pe_id)].append(str(access))  # 只保存 code

        access_msg = []
        PE_ID = 0
        # with open("./A_mem_access1.txt", "w") as f:
        for (block_row_id, pe_id), access in block_row_pe_dict.items():
            # f.write(f"[block_row_id: {block_row_id}, PE_id: {PE_ID}], " +  ", ".join(access) + "\n")
            access_msg.append((block_row_id, PE_ID, access))
            PE_ID += 1
            
        return access_msg
    
    

    # =============== 下面是 version1 的屎山代码, 弃用 (包括下面的测试用例，都是屎) ========================
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
        # print("======================")
        # with open ("./tmp.txt", "w") as f:
        #     f.write(str(skip_row_access_matrix) + "\n")
        skip_access_matrix = self.row_addr_to_matrix_addr(skip_row_access_matrix)
        # print(skip_access_matrix)
        skip_access_message_matrix = self.skip_message(skip_access_matrix, vector_addr, vector_size)
        # print(skip_access_message_matrix)
        
        return skip_access_message_matrix

    def addr_convert_deque(self, matrix1, matrix2):
        # 将矩阵1的每一行转换为deque，方便进行弹出和插入操作
        matrix1_deque = [deque(row) for row in matrix1]

        # 存储弹出的元素
        popped_elements = []

        # 遍历矩阵2的每一行
        for i, row in enumerate(matrix2):
            # 计算当前行中非零元素的数量
            non_zero_count = sum(1 for x in row if x != 0)  # 统计非零元素的数量

            # 根据非零元素的数量，弹出矩阵1对应行的头部元素
            for _ in range(non_zero_count):
                if len(matrix1_deque[i]) > 0:  # 检查矩阵1对应行是否还有元素
                    popped_element = matrix1_deque[i].popleft()
                    popped_elements.append(popped_element)  # 记录弹出的元素

        # 将deque转换回列表
        updated_matrix1 = [list(row) for row in matrix1_deque]

        return updated_matrix1, popped_elements
    



        



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


    matrix1 = [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]]  # Python列表（二维序列）
    matrix2 = [[0, 0, 0, 1], [0, 2, 0, 0], [3, 0, 4, 0]]    # Python列表（二维序列）

    updated_matrix1, popped_elements = addr_converter.addr_convert_deque(matrix1, matrix2)

    print("Updated Matrix 1:")
    print(updated_matrix1)

    print("Popped Elements:")
    print(popped_elements)