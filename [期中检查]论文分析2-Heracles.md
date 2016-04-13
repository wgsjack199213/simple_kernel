#### Heracles

目标：将在线业务和离线业务做混布，提升平均的资源利用率。

难点：性能干扰，影响在线任务SLO。

解决方案：动态反馈控制，细粒度隔离各项资源，保障LC任务SLO的同时，尽量提升BE任务的吞吐量。

结果：设计实现资源隔离控制系统，使（实验）计算集群的服务器平均利用率达到90%。

server TCO占较大比例，为了省钱，一个思路是降低开销，另一个思路是提升资源利用率。现状是平均资源利用率低。因此混布是一种思路。混布的问题是共享资源之间会有干涉干扰，包括cache，memory，IO通道，网络带宽。14年9月Intel的CPU出了新技术CAT（cache allocation technology），可以对LLC（last level cache）进行进程级别的资源隔离。（大概就是把缓存划分不同的区域，供不同的进程使用。这样就不会互相刷新缓存了，可以降低miss rate。）难点是什么呢？

如果做好资源划分共享？
任务的性能受到多种资源的共同作用，不是受单一变量影响。
隔离资源和非隔离资源间会有复杂和不显然的交互关联。
Heracles实现的就是一个动态的控制器，对各项任务进行实时地动态划分隔离，保证LC任务的SLO，最大化BE任务的吞吐量。

#####共享资源的干扰干涉

不能静态绑核。重负载时LC需要全部核。

不能依赖操作系统基于进程优先级的调度。会造成大量SLO violation。

LLC的共享会对混布任务带来诸多负面影响。需要对LLC缓存进行动态的划分。需要用CAT技术。

一些LC任务户对DRAM带宽造成压力，对DRAM带宽的干扰很敏感。但是商业化的CPU芯片没有硬件隔离DRAM带宽的机制。

网络的共享可能造成带宽拥塞。需要动态调整网络带宽限制的机制。

功耗方面需要对每个核分别做DVFS控制，避免LC任务突然降频。

任务混布的一项挑战是不同资源间会互相影响、干扰，使得问题复杂化。

#####对干扰进行刻划，分析

依赖具体任务。选了三种谷歌的LC任务：websearch，ml_cluster,memkeyval。介绍了各任务的特点。用了一系列的影响手段，包括cpu power virous，通过数组循环频繁访问某片缓存，iperf产生网络流量等。

绘制了一个巨大的表格，针对机器不同的负载水平，统计了LC任务的SLO的满足比例。

#####Heracles设计

核的隔离：用cgroups的cpuset，动态绑定。
LLC的隔离：CAT
内存：通过调节核数动态调整来间接调整。无法直接隔离
功耗：per-core DVFS
网络流量：qdisc scheduler做HTB（hierarchical token bucket）
设计理念：是个联合优化问题。Reduce the optimization complexity by decoupling interference sources. 理由是：Interference is problematic only when a shared resource becomes saturated.

Heracles持续监测各任务的延迟和延迟松弛量。需要一个离线模型来描述内存带宽（受负载，核，LLC比例的影响）。因为Inter芯片不能在单核级别上准确测量或者限制DRAM带宽。

架构：

Heracles控制器：检测SLO的松弛级别，确定BE是否可以继续增长，是否需要减核。
核、内存子控制器：用DRAM的计数器判断内存带宽占用情况，用一个离线模型估计每个任务占用内存带宽的情况，把BE限制在单个核上，用numactl调节内存的分配。LLC的分配以10%为粒度增加或减少。LC的性能是核数和LLC份额的凸函数，凸优化，梯度下降法得到全局最优解。
功耗控制器：运行功率接近峰值TDP，并且LC频率低，压制BE任务的核的频率
网络控制器：HTB qdics

#####实验评估

将三种LC任务和多种BE任务两两组合，在单机上，和集群上测试。BE的负载来自真实环境或者合成，包括stream-LLC，cpu_pwr，iperf，brain（真实），streetview（真实）。

关注指标：在线SLO，机器利用率，共享资源利用率。

集群实验用一个小集群跑web-search，树状任务分发结构。同样关注上述两个指标和估算了TCO的收益。

average EMU(Effective Machine Utilization) 90%