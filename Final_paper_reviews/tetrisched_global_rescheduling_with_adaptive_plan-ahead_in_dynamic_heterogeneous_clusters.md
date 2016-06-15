###TetriSched: global rescheduling with adaptive plan-ahead in dynamic heterogeneous clusters

*Tumanov A, Zhu T, Park J W, et al. TetriSched: global rescheduling with adaptive plan-ahead in dynamic heterogeneous clusters[C]// Eleventh European Conference on Computer Systems. ACM, 2016.*

TetriSched是一个在在线任务（deadline严格的重要商业任务）和离线任务混布的环境中工作的调度器。它利用了商业任务的可预测性，来优化资源分配的方案，总体目标是为了提升商业任务的SLO和集群的整理利用率。

研究者们说商业任务（SLO严格的任务）可预测（完成时间）主要原因是它们经常是被周期性地，批量地提交，而且运行时间长，数据量大。然而当前的Hadoop/Yarn集群调度器的框架却没有充分利用任务相关的一些信息、知识，对于自愿的分配是静态的。研究者们希望设计一种调度器去理解任务的要求，折衷，运行时间估计，并利用这些信息做短期的调度决策和长期的调度计划（对未来任务的预测）。

Space-time request language (STRL), an expressive language for declarative specification of preferences in resource space-time.

调度器的三个元素：capacity reservation, place ment, and ordering。容量预留是系统保留一部分资源供未来使用的能力（多针对长期的资源的规划）；放置是把具体资源分配给某一任务的动作；排序是决定下一步放置等待调度的任务中的哪一个。放置和排序主要针对的短期的任务调度。

Reservation system（例如Yarn的Rayon）和scheduling system解决的是互补的问题。预留系统关注长期的资源分配方案，可以看做一种准入控制，而调度系统主要关注短期的任务调度，做出排序和放置的决策。TetriSched和Rayon合作一起工作。

集群资源的异构性包括静态，动态和组合的异构。静态异构指硬件型号的异构，动态异构指不同任务对不同机器的不同偏好（数据局部性等等），组合异构指分布式任务运行机器符合某些组合（同机架机器等）的情况下性能会更高。

TetriSched是一个动态更新的全局调度器，每个调度周期都会重新计算调度决策，同时考虑多个任务的放置和对机器的偏好，因为一方面会不断有新任务来，另一方面对已运行任务的完成时间的预测可能会有误差。这个问题想想就觉得是一个混合整数规划的优化问题。

STRL生成器将任务的时空资源需求进行编码，然后TetriSched对编码编译转换为整数规划问题并求解，最后得到的任务调度放置策略异步地发送给YARN的资源管理器。MILP问题是用IBM的Cplex求解的。

STRL定义了若干种元语，nCk，MAX，MIN，BARRIER，SCALE，SUM，对应着不同类型的约束条件。我理解为这些元语的作用主要是为了便于将调度问题形式化成整数规划问题。最主要的元语nCk是nCk(equivalence_set, k, start, dur, v)，代表着从等价类中任取k个，以及任务开始、结束的时间，和对应一种分配的值（类似总收益）。

评测方面，研究者们关注的指标包括接受的SLO任务完成情况（在deadline前结束的接受SLO的比例），整体SLO任务完成情况，无预留SLO任务情况，平均延迟（离线任务的完成时间平均值）。研究者们使用合成的生成器（基于Gridmix 3）生成MapReduce任务。生成器可以调节任务完成时间，数目，大小，deadline等等参数。

实验发现在不同情况下，使用TetriSched的任务完成情况都不Rayon/CS差，离线任务的平均延迟也比Rayon/CS更低。考虑到任务软约束时，TetriSched的性能更好。TetriSched的全局调度比贪心调度（每次调度一个任务）的性能更好。随着Plan-ahead的增加，TetriSched的性能呈提高趋势。研究者们小结到TetriSched的三个主要特性兼备时，SLO任务的完成情况和离线任务的延迟最好，移除三个特性中的任意一个TetriSched的性能都大打折扣。

整数线性规划是NP-hard问题，所以用MILP求解器的时间延迟是一个需要考虑的问题，因为如果集群规模变得很大，MILP求解可能需要很久。CPLEX可以通过参数设置近似求解，比如我可以设置当算法确定当前解最差不比最优解差10%时，提前结束求解。另外CPLEX还可以设置初始解（局部解），可以对分支限界进行优化。此外还有一些细节可以缩减MILP的问题规模从而优化MILP的求解时间。

本文提出的任务调度器对于异构集群中混合部署的任务进行动态的全局最优的调度有着很好的效果。本质上还是把任务在时间和空间上的放置问题形式化成为了整数线性规划问题，并进行求解，同时通过周期地动态重新评估调度来弥补任务运行时间预测的误差。
TetriSched的有效性依赖于对任务完成时间的预测，然而我觉得有可能在实际异构集群中不同mapreduce任务的运行时间不一定预测的准。这个主要还是看TetriSched的调度对于时间预测的敏感性。如果任务运行时间普遍较长较稳定，TetriSched的效果不会太差。

我觉得本文最有趣的地方在于研究者们对STRL元语的设计以及对MILP问题的建模。
