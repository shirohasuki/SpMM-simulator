### Scalar Vector Runahead (SVR) 
对 Scalar Vector Runahead (SVR) 的简化模拟，展示了其如何通过步幅检测和标量向量指令来提高内存级并行性（MLP），适用于处理复杂内存访问模式的程序。

重点展示了以下功能模块：

- 步幅检测器（Stride Detector）：检测内存访问是否具有固定步幅模式。
- 污染跟踪器（Taint Tracker）：跟踪受步幅加载影响的寄存器及其依赖链。
- 预测寄存器文件（Speculative Register File, SRF）：存储预取期间的临时数据。
- 标量向量单元（Scalar Vector Unit, SVU）：根据步幅生成标量向量指令，进行内存预取。
- 循环边界检测器（Loop Bound Detector, LBD）：检测循环边界，避免过度预取。

Scalar Vector Runahead (SVR) System
Introduction
The Scalar Vector Runahead (SVR) system is a microarchitectural design aimed at improving Memory-Level Parallelism (MLP) through stride detection, speculative execution, and efficient memory prefetching. The SVR system leverages various components such as the Stride Detector, Taint Tracker, Head Striding Load Register (HSLR), Scalar Vector Unit (SVU), and Scoreboard to coordinate the processing of stride-based load instructions.

Features
- Stride Detection: Detects stride patterns in load instructions to identify memory access patterns and initiate scalar-vector execution.
- Taint Tracking: Tracks registers tainted by stride-based load instructions and maintains dependency chains.
- Speculative Execution: Supports the generation of scalar vector instructions (SVI) to prefetch data and execute independent scalar operations.
- Scoreboard Management: Manages the status of instructions, detects data hazards, and ensures correct execution ordering.
- Modular Design: Each component is implemented as an independent module, facilitating testing, debugging, and extension.
- Components Overview

The system consists of the following primary components:

- Taint Tracker (TT): Manages the taint state of registers, tracking whether a register has been influenced by a stride-based load instruction.
- Stride Detector (SD): Detects stride patterns in load instructions, updating confidence levels, and initiating vectorized execution.
- Head Striding Load Register (HSLR): Stores the PC and control mask of a detected stride-based load instruction, assisting the SVU in generating scalar vector instructions.
- Scalar Vector Unit (SVU): Generates and executes scalar vector instructions (SVIs), maintains a speculative register file (SRF), and coordinates with the Scoreboard.
- Scoreboard: Manages instruction statuses, tracks return counters, and ensures that instructions are correctly ordered and data dependencies are respected.


#### Configuration
1. 修改模拟参数
您可以通过修改 ScalarVectorRunahead 类的初始化参数来调整步幅长度和标量向量的长度。
```
```

2. 自定义内存访问
```
```