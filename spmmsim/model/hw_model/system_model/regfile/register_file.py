class Register:
    """单个寄存器的类"""
    def __init__(self, value=0):
        self.value = value  # 初始化寄存器的值
        # self.tainted = False  # 表示寄存器是否被污染

class RegisterFile:
    """寄存器堆类，模拟多个寄存器"""
    def __init__(self, num_registers=32):
        # 初始化一个寄存器堆，假设有 num_registers 个寄存器
        self.registers = {i: Register() for i in range(num_registers)}
    
    def write(self, register_id, value):
        """写入值到寄存器"""
        if register_id in self.registers:
            self.registers[register_id].value = value
        else:
            raise ValueError(f"寄存器 {register_id} 不存在")

    def read(self, register_id):
        """从寄存器读取值"""
        if register_id in self.registers:
            return self.registers[register_id].value
        else:
            raise ValueError(f"寄存器 {register_id} 不存在")

    # def mark_tainted(self, register_id):
    #     """标记寄存器为污染状态"""
    #     if register_id in self.registers:
    #         self.registers[register_id].tainted = True
    #     else:
    #         raise ValueError(f"寄存器 {register_id} 不存在")

    # def is_tainted(self, register_id):
    #     """检查寄存器是否被污染"""
    #     if register_id in self.registers:
    #         return self.registers[register_id].tainted
    #     else:
    #         raise ValueError(f"寄存器 {register_id} 不存在")

if __name__ == "__main__":
    register_file = RegisterFile(num_registers=32)  # 初始化一个包含32个寄存器的寄存器堆

    # 写入和读取寄存器
    value = register_file.read(5)  # 读取寄存器5的值
    print(f"寄存器5的值: {value}")

    register_file.write(5, 100)  # 将值100写入寄存器5
    value = register_file.read(5)  # 读取寄存器5的值
    print(f"寄存器5的值: {value}")

    # # 标记寄存器为污染状态并检查
    # register_file.mark_tainted(5)
    # is_tainted = register_file.is_tainted(5)
    # print(f"寄存器5是否被污染: {is_tainted}")
