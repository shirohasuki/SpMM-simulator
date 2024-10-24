# SpMM-simulator

### Features
- Models we have
  - A cache/scratchpad mem system simulator
  - A systolic_array model
  - A sparse computing model
  - supported prefetchers models: DVR, IMP, Stream
- Tools we have
  - task profiler
  - custom inst decoder

### Run the source code
1. Set the PYTHONPATH environment variable. 

Make sure you are in the root directory.
```
$ export PYTHONPATH=$PWD:${PYTHONPATH}
```

### TODO
1. - [x] Tools: 
   1. - [x] 解析gemmini, 添加要供给Profile的latency
   2. - [x] 解析gemmini, 确定task_profile需要的并行串行关系
2. - [ ] Modeling:
   1. - [x] NVR: 添加NVR实现 
   2. - [x] 添加scratchpad的模型，并能调节和cache(NPU内)比例
   3. - [x] 添加新的计算模式
   4. - [x] 添加对照DVR, IMP, stride prefetch
   5. - [x] 添加mem_access文件的ss_start和ss_end信息提取
   6. - [ ] check双边稀疏的正确访存序列生成
   7. - [ ] 完善双边稀疏的预取
3. - [ ] Workload: 添加八个workload
