class StridePrefetcher:
    """简单的步长预取器，基于 mvin 指令"""
    def __init__(self, stride=4):
        self.stride = stride  # 默认步长
        self.last_rs1_address = 0  # 记录上一次 mvin 指令的 rs1 地址

    def execute_mvin(self, rs1):
        """
        模拟 mvin 指令的执行，并根据步长进行预取。
        rs1: 虚拟 DRAM 地址
        rs2: scratchpad 或 accumulator 地址
        """
        # if self.last_rs1_address is not None:
        # 更新stride
        stride = rs1 - self.last_rs1_address
        self.set_stride(stride) 


        # 根据上一次的 rs1 地址预测下一次访问的 DRAM 地址
        predicted_address = rs1 + self.stride
        # print(f"{predicted_address} {self.last_rs1_address} {self.stride}")

        # 更新上一次访问的 rs1 地址
        self.last_rs1_address = rs1

        if predicted_address < 0:
            predicted_address = -1
        
        return predicted_address, stride

    def set_stride(self, new_stride):
        """动态调整步长"""
        self.stride = new_stride


class StridePrefetcherGroup:
    """预取器组，包含多个步长预取器"""
    def __init__(self, num_prefetchers=16, default_stride=4):
        # 创建指定数量的步长预取器，每个预取器初始步长为默认值
        self.prefetchers = [StridePrefetcher(stride=default_stride) for _ in range(num_prefetchers)]

    def prefetch(self, mvin_instructions):
        """
        执行一组 mvin 指令，每个预取器处理一个。
        mvin_instructions: 每个元素是 rs1 ，表示 mvin 指令
        """
        # 确保 mvin 指令的数量和预取器数量一致
        assert len(mvin_instructions) == len(self.prefetchers), "mvin 指令数量应与预取器数量相等"

        # 执行每个预取器的 mvin 指令
        results = []
        for i, rs1 in enumerate(mvin_instructions):
            predicted_address, stride = self.prefetchers[i].execute_mvin(rs1)
            results.append((i, rs1, predicted_address, stride))
        
        return results