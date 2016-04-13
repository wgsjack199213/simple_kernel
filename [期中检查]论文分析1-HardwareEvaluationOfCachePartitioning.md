####A Hardware Evaluation of Cache Partitioning to Improve Utilization and Energy-Efficiency while Preserving Responsiveness
 

主要考虑了四种benchmark：SPEC CPU 2006，DaCapo，PARSEC，4个增加的并行应用

文章为了减小研究对象的规模，用了single-linkage聚类的方法，将所有做过实验的benchmark做了聚类，特征是在不同的实验中的结果（nomalized execution time，也代表对某种实验的sensitivity）向量（19维）。single linkage聚类我理解是一种自底向上的层次聚类。为啥用层次聚类呢？我觉得是因为可以灵活地调整聚类的层级（粒度、结果簇的个数）。这种层次聚类出来的结果图叫dendogram。不知道Huffman Coding那种树结构能不能也叫dendogram。

race-to-halt，最佳的节能策略可能是先为了最高性能而优化，让任务早点跑完，然后让机器进入sleep-state节能。
高LLC miss意味着高能耗（任务运行时间、DRAM能耗）

diminish returns 报酬递减，收益递减

性能和能耗做联合比较时，同时调节两个变量（# threads，LLC分配大小）进行实验测试。结果显示race-to-halt对于大部分benchmark是最优策略。

多任务混布时，也是采用了一个矩阵，将所有benchmark任务两两组合，统计执行时间。（衡量任务混布对性能的影响程度）。
三种实验设置：shared（不做隔离），fair（均分LLC），biased（最佳的不均分LLC方案）
比较了运行时间、socket能耗，和相对于独占机器的加速比（顺序执行v.s.并发执行的总时间）。

文章最后提出了基于MPKI指标的动态LLC划分算法。应用场景主要是1在线+1离线。大致思路是检测在线任务的phase，在phase变化时，将LLC全分给在线任务，然后在在线任务phase不变时，逐渐地缓慢减少分配给它的LLC，直到它的MPKI再次上升超过阈值。

这种划分算法依赖于任务优先级的区分，而且通常只能有1个在线任务。多个高优先级任务混布时，算法会复杂很多。论文的实验也只用了1个离线任务。如果大于1+1的话，LLC显然是不够的，可能会降低离线任务的性能。这时又该如何权衡呢？