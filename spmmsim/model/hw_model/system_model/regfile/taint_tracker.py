class TaintTracker:
    """单独的 Taint Tracker 类，用于跟踪寄存器的 taint 状态"""
    def __init__(self, num_registers=32):
        # 用布尔列表来跟踪每个寄存器的 taint 状态
        self.tainted_registers = [False] * num_registers

    def mark_tainted(self, register_id):
        """标记指定寄存器为 tainted"""
        self.tainted_registers[register_id] = True

    def clear_tainted(self, register_id):
        """清除指定寄存器的 taint 状态"""
        self.tainted_registers[register_id] = False

    def is_tainted(self, register_id):
        """检查寄存器是否为 tainted"""
        return self.tainted_registers[register_id]