import sys
sys.path.append("../")

from SP.stride_prefetch import StridePrefetcher


class IMP:

    def __init__(self):
        self.coeff = 4 # 假设每个元素 4 字节
        self.stride_prefetcher = StridePrefetcher()  # 使用步长预取器
    
    def stride_detector(self, b_curr):
        """
        步长检测器：使用传入的 StridePrefetcher 来预测下一个 B 的值
        """
        predicted_b_addr, stride = self.stride_prefetcher.execute_mvin(b_curr)
        print(f"当前 B[{b_curr}], 预测的下一个为 B[{predicted_b_addr}], 步长: {stride}")
        return predicted_b_addr

    def indirect_mem_detector(self, coeff, b_value, a_value):
        """
        间接访存检测器：学习 coeff 和 base_addr
        """
        coeff = coeff  
        base_addr = a_value - (coeff * b_value)
        print(f"学习到的 Coeff: {coeff}, BaseAddr: {base_addr}")
        return coeff, base_addr
    
    def addr_generator(self, b_predicted, coeff, base_addr):
        """
        地址生成器：根据预测的 B[i+1] 生成 A[B[i+1]] 的地址
        """
        if b_predicted is None:
            return -1
        return base_addr + coeff * b_predicted

    def prefetch(self, b_i, b_list, a_value):
        """
        执行一步，整合 stride_detector, indirect_mem_detector, addr_generator
        """
        # 1. 间接访存检测器学习关系
        # print(f"当前 {b_list[b_i]}, a_value={a_value}")
        coeff, base_addr = self.indirect_mem_detector(self.coeff, b_list[b_i], a_value)

        # 2. 步长检测器预测下一个 B 的值
        predicted_b_addr = self.stride_detector(b_i)

        # 检查 predicted_b_addr 是否越界
        if predicted_b_addr >= len(b_list) or predicted_b_addr < 0:
            print(f"预测的 B[{predicted_b_addr}] 越界，返回 -1")
            return predicted_b_addr, -1, -1

        # 3. 地址生成器生成 A[B[i+1]] 的地址
        # print(b_array, predicted_b_addr)
        predicted_a_addr = self.addr_generator(b_list[predicted_b_addr], coeff, base_addr)

        return predicted_b_addr, b_list[predicted_b_addr], predicted_a_addr


if __name__ == "__main__":
    # A = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]  # 数据数组 A
    A_addr = [0, 4, 8, 12, 16, 20, 24, 28, 32, 36]  # 数据数组 A 的地址数组
    B = [2, 5, 7, 3, 1, 8]  # 索引数组 B

    # 创建 IMP 实例并进行逐步模拟
    imp = IMP()

    for i in range(len(B)):
        predicted_b_addr, predicted_b_value, predicted_a_addr = imp.prefetch(i, B, A_addr[B[i]])
        if predicted_b_value == -1:
            print(f"预测的 B[{predicted_b_addr}] 越界\n")
        else:
            print(f"预测下一个为 A[B[{predicted_b_addr}]], B[{predicted_b_addr}]={predicted_b_value}, A[B[{predicted_b_addr}]]的地址={predicted_a_addr}\n")

class IMPGroup:
    """IMP组，包含多个IMP实例并行运行"""
    def __init__(self, num_units=16):
        # 创建指定数量的 IMP 实例
        self.imp_units = [IMP() for _ in range(num_units)]

    def execute_group(self, B, B_addr, A_addr):
        """
        执行多个 IMP 子单元的预取操作，处理单个 B 和 A 列表。
        每个 IMP 单元处理 B 和 A 中不同的元素。
        """
        num_units = len(self.imp_units)
        results = []

        for i in range(0, len(B), num_units):
            unit_results = []
            for unit_id, imp in enumerate(self.imp_units):
                # 确保不会越界
                if i + unit_id < len(B):
                    b_index = i + unit_id
                    # if B[b_index] >= len(A):
                    #     # B[b_index] 超出 A 的范围，返回 -1 以避免越界
                    #     unit_results.append((unit_id, -1, -1, -1))
                    # else:
                        # 执行每个 IMP 单元的预取操作
                    # print(len(B))
                    predicted_b_addr, predicted_b_value, predicted_a_addr = imp.prefetch(B[b_index], B, B_addr, A_addr[B[b_index]])
                    unit_results.append((unit_id, predicted_b_addr, predicted_b_value, predicted_a_addr))
                else:
                    unit_results.append((unit_id, -1, -1, -1))  # 越界返回 -1
            results.append((i, unit_results))

        return results


if __name__ == "__main__":
    A_addr = [
        100, 104, 108, 112, 116, 120, 124, 128, 132, 136, 140, 144, 148, 152, 156, 160,
        # [164, 168, 172, 176, 180, 184, 188, 192, 196, 200, 204, 208, 212, 216, 220, 224],
        228, 232, 236, 240, 244, 248, 252, 256, 260, 264, 268, 272, 276, 280, 284, 288,
        # [292, 296, 300, 304, 308, 312, 316, 320, 324, 328, 332, 336, 340, 344, 348, 352]
        356, 360, 364, 368, 372, 376, 380, 384, 388, 392, 396, 400, 404, 408, 412, 416,
        # [420, 424, 428, 432, 436, 440, 444, 448, 452, 456, 460, 464, 468, 472, 476, 480],
        484, 488, 492, 496, 500, 504, 508, 512, 516, 520, 524, 528, 532, 536, 540, 544,
        548, 552, 556, 560, 564, 568, 572, 576, 580, 584, 588, 592, 596, 600, 604, 608
    ]

    B_addr = [
        0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,
        16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,
        32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,
        48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,
        64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79
    ]


    B = [
        [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15],
        [16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31],
        [32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47],
        [48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63],
        [64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79]
    ]

    imp_group = IMPGroup(num_units=16)

    # 循环测试每一组 A 和 B 数据
    for idx in range(len(B)):
        group_results = imp_group.execute_group(B[idx], B_addr, A_addr)
        print(f"测试第 {idx + 1} 组 A 和 B 数据:")
        for unit_id, results in group_results:
            print(f"IMP 批处理 {unit_id} 预测结果:")
            for unit_id, b_addr, b_value, a_addr in results:
                print(f"IMP[{unit_id}] 预测的下一个为A[B[{b_value}]] 的地址={a_addr}")
            print("\n")