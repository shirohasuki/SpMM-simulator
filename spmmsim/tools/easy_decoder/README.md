### RISC-V Instruction Register Extractor
This Python script extracts the rd, rs1, and rs2 registers from a list of RISC-V 32-bit instructions (provided in hexadecimal format). It also translates the register numbers into their corresponding RISC-V register names (e.g., `x0` is `x0`, `x1` is `ra`, etc.).

just run the script:

```
python3 isa_extractor.py
```


### 目前只支持了R型的指令！！因为Gemmini自定义指令都是R型