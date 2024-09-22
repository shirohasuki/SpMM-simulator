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

**Interface2 connect_to_matmul:** This function connect our systolic array to the input matmul. It will send the access requests needed for the computation process.
- input parameter1: A matrix
- input parameter2: B matrix
- input parameter3: if Density?(True) or Sparsity?(False)
- output parameter: cycles
(will not output the C Matrix result)


### Supported Features and Configurations
You can use the cfg file to configure these parameters:
1. dataflow: WS


### ABC Matrix
**C = A * B**

**A** is the input Activation Matrix (IA) 

**B** is the weight Matrix (W) 

**C** is the output Activation Matrix (OA)
