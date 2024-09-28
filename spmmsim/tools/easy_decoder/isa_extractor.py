REGISTER_NAMES = {
    0: "x0", 1: "ra", 2: "sp", 3: "gp", 4: "tp", 5: "t0", 6: "t1", 7: "t2",
    8: "s0", 9: "s1", 10: "a0", 11: "a1", 12: "a2", 13: "a3", 14: "a4", 15: "a5",
    16: "a6", 17: "a7", 18: "s2", 19: "s3", 20: "s4", 21: "s5", 22: "s6", 23: "s7",
    24: "s8", 25: "s9", 26: "s10", 27: "s11", 28: "t3", 29: "t4", 30: "t5", 31: "t6"
}


def extract_riscv_registers(instructions):
    for instruction in instructions:
        # # 将输入的十六进制字符串转换为二进制
        binary_instruction = format(int(instruction, 16), '032b')

        # 提取各个字段的二进制位
        rs2_bin = binary_instruction[7:12]    # rs2字段，位于[11:7]
        # print(rs2_bin)
        rs1_bin = binary_instruction[12:17]  # rs1字段，位于[16:12]
        # print(rs1_bin)
        rd_bin = binary_instruction[20:25]  # rd字段，位于[24:20]
        # print(rd_bin)

        # 将二进制字段转换为十进制（寄存器编号）
        rd = int(rd_bin, 2)
        # print(rd)
        rs1 = int(rs1_bin, 2)
        rs2 = int(rs2_bin, 2)

        # 获取寄存器的名字
        rd_name = REGISTER_NAMES.get(rd, f"x{rd}")
        rs1_name = REGISTER_NAMES.get(rs1, f"x{rs1}")
        rs2_name = REGISTER_NAMES.get(rs2, f"x{rs2}")

        print(f"Instruction: {instruction}")
        # print(f"rd: {rd_name}, rs1: {rs1_name}, rs2: {rs2_name}\n")
        print(f"rd, rs1, rs2 [{rd_name}, {rs1_name}, {rs2_name}]\n")
        


if __name__ == "__main__":
    instructions = [
        '00d7b07b',  
        '00f6b07b',  
        '00c6b07b'   
    ]
    
    extract_riscv_registers(instructions)