###Large-scale cluster management at Google with Borg

*Verma A, Pedrosa L, Korupolu M, et al. Large-scale cluster management at Google with Borg[C]//Proceedings of the Tenth European Conference on Computer Systems. ACM, 2015: 18.*

<http://www.iiis.systems/wp/wp-content/uploads/2015/11/Large-scale-cluster-management-at-Google-with-Borg.pdf>

Borg是谷歌的集群管理系统，控制有万级别机器的数据中心，用了十多年，积累了大量的经验和教训，含金量非常高。谷歌将Borg中的精华继承到了开源项目Kubernetes（新一代基于容器的集群管理系统）中。这篇论文主要是谷歌对Borg这个庞大繁复的集群管理系统中的诸多技术细节和设计考量进行了总结概括。

**用户层面**

分析业务：Borg上跑了哪些业务。大致分为离线在线两类。在线多常驻，离线流动性更大。

按照cluster分成cell单位，每个cell包含万级别机器。

job和task，没在虚拟机里为了减少虚拟化开销，静态编译，有一批属性，如配额需求。通过RPC控制任务。任务的生命周期。

Alloc，保留的资源集，用于未来的任务，或者收集来自不同job的task。

Priority，细粒度。优先级带间不重叠。在线任务最高。同优先级带内禁止抢占。Quota，资源需求，用于admission control，以CPU,RAM,disk等多维度的资源份额表示。高优先级的quota比低优先级的更贵。有了quota就不用DRF啦（dominant resource fairness）。

Naming，BNS服务，通过Chubby分布式文件锁实现。定位资源。全方位的实时监控系统，采集及其丰富的数据，包括SLO方面，健康状态方面等等。提供了web端的UI供用户查询监控数据，和调试系统。让用户理解、调试Borg和Borg上的任务。极大地简化的运维的复杂度。

**系统架构**

Borgmaster，独立进程来做调度器。5个副本通过Paxos保持一致性，一是容灾，二是对于boglet可以分区管理，缓解单点压力。为了调试Borgmaster，他们任性地搭了个Borgmaster simulator，包含完整的borgmaster代码和与borglet的交互接口，用于读取check point文件，debug，和做模拟实验。

调度，异步扫描pending queue，按优先级次序进行调度（同优先级内round robin），可用资源要满足任务的需求。对于满足资源约束的目标机器进行打分，可以根据用户喜好定，也有内置策略（抢占尽量少的任务，数据局域性，高低优先级搭配干活不累）。打分用的E-PVM是一套调度时的评分机制（决定调度策略）。

调度时用worst-fit（给spike留出余地）还是best-fit（减少碎片）呢？谷歌工程师们用了个混合策略，效果好点。这里一个问题是怎么怎么评估效果好？引文[78]介绍evaluating的模型。

资源足够就部署，资源不够，就挨个杀任务，按照优先级从低到高，按次序挨个杀掉任务，直到资源够了。被剁了的进入pending queue（部分环境是做迁移）。有人告诉我：“Google所有任务都是设计成可以随时杀掉重启的，这个跟一般的系统不一样。所以它是强制做出来的preemptive 的scheduling。一般的系统还真不能这么做，比如你把一个网站的数据库后台杀了，那几个前端也不能用了。”

Borglet，本地代理，具有本地任务的生杀大权，维护状态，写日志，和Borgmaster交互。link shard是master的副本和borglet进行分区交互的无状态的组件，向master汇报基层状态时取增量（减轻负担）。

**可扩展性**

Borgmaster使用单独进程做调度。乐观并发机制。使用并行的多线程响应所有只读的RPC。缓存打分，忽略较小的改变。同一job的task视为等价类，只做一次评分。随机排序目标机器进行调度尝试（采样）。

**可用性**

自动reschedule，减少相关性的故障（均匀散开任务分布），使用幂等的变更操作，一段时间内持久固化中间数据日志，等等等等。

即使Borgmaster挂了，或者Borglet挂了，任务继续运行。

谷歌的Borg实现了99.99%可用性。

**利用率**

cell compaction: 给定负载，可以用多小的cell来跑。（consolidation程度）

cell共享：在线任务离线任务混布。互相的干扰怎么评估？用CPI指标。

CPI与总体CPU利用率和单机任务数正相关。但更多的是业务特性相关的内在特征模式。

没有深入分析干扰的问题。即使CPU慢了，但总体机器数少了，以及其他资源（disk，memory）的复用带来的收益更大。

大cell比小cell省机器。细粒度的资源请求。

资源回收：reserveration，limit。保证reservation，可以超用，最多limit。需要时回收reservation~limit之间的资源。

reservation是算出来的，根据历史估计出来，实时更新。分配资源缓慢收缩，如利用率超出分配资源，则迅速调高reservation。

只有离线任务可以用回收的资源。在线任务要确保其有稳定的资源用。

评估了这种资源复用可以节省多少机器。调节了一个safety margin，选用了一个净利益最大的配置。

**资源隔离**

安全性隔离：Linux chroot jail

性能隔离：早期Borglet事后分析，如多用则杀掉。现在Borg用Linux cgroup容器做资源隔离。可以绑定核。底层干扰仍然存在！memory bandwidth，LLC pollution。

两种手段：kill，压制。如果资源不可压缩（磁盘，内存），则kill。否则压制。

在线任务内存分配基于predicted future usage。这里我也不是非常清楚。我理解为谷歌采用了一些预测的机制来评估应当给不同人物预留多少内存。

动态CFS bandwidth control防止LS造成BE饥饿。

这篇文章内容非常丰富，包含了Borg系统的资源管理、隔离，资源利用率，用户层面视角，系统架构，可用性，可扩展性等方方面面。因为系统实在很复杂，所以每一块的具体内容也无法很深入地介绍，主要是介绍了基本的设计考量和重要的技术要点、特点等等。通过学习这篇论文我觉得我对于集群管理系统的理解更加深入了。我觉得最有收获的地方是，了解了涉及到集群处理资源、调度等方面的一些问题中的一些策略和设计考量。
