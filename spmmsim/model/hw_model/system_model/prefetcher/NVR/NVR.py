import sys
sys.path.append("../")
# import math 


from ..SP.stride_prefetch import StridePrefetcher


class NVR:
    def __init__(self):
        self.coeff = 4 # 假设每个元素 4 字节
        self.stride_prefetcher = StridePrefetcher()  # 使用步长预取器
    
    # def stride_detector(self, curr_i):
    #     """步长检测器：使用传入的 StridePrefetcher 来预测下一个i值"""
    #     predicted_i, stride = self.stride_prefetcher.execute_mvin(curr_i)
    #     print(f"当前 i={curr_i}, 预测的下一个为 i={predicted_i}, 步长: {stride}")
    #     return predicted_i

    # def loop_bound_detector(self, bound):
    #     """边界检测器"""
    #     # updated_bound = self.loop_bound_prefetcher.update(bound)
    #     updated_bounds = self.loop_bound_group.update_group(bound)
    #     return updated_bounds
    
    # def addr_generator(self, base_ptr, col_add):
    #     """ 地址生成器 """
    #     return base_ptr + col_add

    def prefetch(self, ss_end, ss_start):
        """bound和ptr_vector都是PE行数相同的数组, bound[i]表示PE第i行的循环边界
        整合 stride_detector, loop_bound_detector, addr_generator
        """
        
        # predicted_bounds = self.loop_bound_detector(bound)

        results = []
        # 对每个PE内处理
        for i in range(len(ss_start)):
            if (ss_end[i] != 0) and  (ss_start[i] != 0):
                for col in range(ss_end[i], ss_start[i]+1):
                    # for predicted_addr in col:
                        # predicted_addr = self.addr_generator(ptr_vector[detector_id], col)
                        results.append((i, col))
                    # PE第几行的CSR第几个数
                
        return results


if __name__ == "__main__":
    ss_start = [
        [0, 0, 0, 0],
        [2, 1, 3, 0],
        [2, 3, 4, 2]
    ] 

    ss_end = [
        [2, 1, 3, 0],
        [2, 3, 4, 2],
        [4, 4, 4, 4],
    ]  

    nvr = NVR()

    for i in range(len(ss_start)):
        predict_addr = nvr.prefetch(ss_start[i], ss_end[i])
        print(f"第{i}轮生成的mem access{predict_addr}")
    