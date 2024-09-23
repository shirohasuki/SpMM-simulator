## Compute Model - systolic_array

### Quick Start

You can quick start by running 
'''
python ./utils/test.py
'''

`demo.ipynb` in jupyter notebook will show you how to use this systolic_array simulator in detail.



### Interface

You can use this repository as a lib by `Interface.py`.

**Interface1 connect_to_memory:** This function connect our systolic array to the memory. It will send the access requests needed for the computation process.
<!-- - input parameter1: -->
<!-- - input parameter2: -->
- output parameter1: ren
- output parameter2: raddr

**Interface2 connect_to_matmul:** This function connect our systolic array to the input matmul. It will evaluate the cycles of matmul caculation.
`matmul_eval(systolic_row, systolic_col, matrix_A, matrix_B, mode=0, Sparsity=False)`
- systolic_row: rows of systolic array
- systolic_col: cols of systolic array
- matrix_A: A matrix
- matrix_B: B matrix
- Sparsity: if Density?(True) or Sparsity?(False)
- return: cycles
(will not output the C Matrix result)


### Supported Features and Configurations
You can use the cfg file to configure these parameters:
1. dataflow: WS


### ABC Matrix
**C = A * B**

**A** is the input Activation Matrix (IA) 

**B** is the weight Matrix (W) 

**C** is the output Activation Matrix (OA)
