class EWMALoopBoundDetector:
    def __init__(self, alpha=0.5, initial_bound=10):
        """
        初始化EWMA循环边界检测器。
        
        :param alpha: EWMA中的平滑系数，控制新值和历史值的重要性。取值范围为[0, 1]。
        :param initial_bound: 初始的循环边界估计值。
        """
        self.alpha = alpha
        self.estimated_bound = initial_bound  # 初始化的循环边界估计
        self.iteration_count = 0  # 当前循环的迭代次数

    def update(self, actual_iteration_count):
        """
        更新当前循环边界的估计值，使用实际的迭代次数。
        
        :param actual_iteration_count: 当前循环实际执行的迭代次数。
        :return: 更新后的边界估计值。
        """
        # 使用EWMA公式更新估计的边界
        self.estimated_bound = self.alpha * actual_iteration_count + (1 - self.alpha) * self.estimated_bound
        self.iteration_count = actual_iteration_count
        return self.estimated_bound

    def get_estimated_bound(self):
        """
        获取当前的循环边界估计值。
        
        :return: 当前估计的循环边界值。
        """
        return self.estimated_bound


class EWMALoopBoundDetectorGroup:
    """循环边界检测器组，包含多个EWMA循环边界检测器"""
    
    def __init__(self, num_detectors=16, alpha=0.5, initial_bound=10):
        """
        初始化LBD组，每个检测器有独立的EWMA参数。
        
        :param num_detectors: 检测器的数量
        :param alpha: EWMA中的平滑系数
        :param initial_bound: 每个LBD的初始循环边界值
        """
        self.detectors = [EWMALoopBoundDetector(alpha=alpha, initial_bound=initial_bound) for _ in range(num_detectors)]

    def update_group(self, actual_iterations_list):
        """
        更新整个检测器组的边界估计值，每个检测器根据实际的迭代次数更新。
        
        :param actual_iterations_list: 每个检测器对应的实际迭代次数列表
        :return: 包含每个检测器的更新后估计边界的结果列表
        """
        assert len(actual_iterations_list) == len(self.detectors), "实际迭代次数列表的长度应与检测器数量相等"
        
        results = []
        for i, actual_iterations in enumerate(actual_iterations_list):
            updated_bound = self.detectors[i].update(actual_iterations)
            results.append((i, actual_iterations, updated_bound))
        
        return results

    def get_estimated_bounds(self):
        """
        获取所有检测器的当前边界估计值。
        
        :return: 每个检测器的估计边界值列表
        """
        return [detector.get_estimated_bound() for detector in self.detectors]


if __name__ == "__main__":
    lbd_group = EWMALoopBoundDetectorGroup(num_detectors=4, alpha=0.3, initial_bound=10)

    # 模拟多个LBD对应的实际迭代次数
    actual_iterations_group = [
        [12, 15, 14, 16],  # 第一次四个检测器的实际迭代次数
        [20, 18, 22, 21],  # 第二次四个检测器的实际迭代次数
        [30, 28, 32, 29],  # 第三次四个检测器的实际迭代次数
        [40, 42, 44, 41],  # 第四次四个检测器的实际迭代次数
    ]

    # 打印初始边界估计值
    print("Initial Estimated Bounds:", lbd_group.get_estimated_bounds())

    # 更新每个LBD，并打印结果
    for i, actual_iterations in enumerate(actual_iterations_group):
        updated_bounds = lbd_group.update_group(actual_iterations)
        print(f"{i + 1} times Group Updated Bounds:")
        for detector_id, actual, bound in updated_bounds:
            print(f"  Detector {detector_id}: Actual Iterations = {actual}, Updated Estimated Bound = {bound:.2f}")
