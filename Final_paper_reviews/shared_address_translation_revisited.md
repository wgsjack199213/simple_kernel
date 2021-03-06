### Shared Address Translation Revisited

*Dong X, Dwarkadas S, Cox A L. Shared address translation revisited[C]//Proceedings of the Eleventh European Conference on Computer Systems. ACM, 2016: 18.*

<http://www.cs.rochester.edu/u/xdong/eurosys16.pdf>

内存共享的实例：PostgreSQL的缓冲池，动态链接库。

虽然内存得到共享，但页表还是每个进程分别维护，overhead还是随进程数线性增长，会引起可扩展性问题。多核机器的缓存利用也会低效（同一个物理地址，会向cache读进多个不同的页表项）。过去的改进方法着重在应用的优化和页表共享，而本文的思路是在进程间以一种更灵活的方式共享地址转换结构（页表的子集），从而提升应用的性能。

作者对安卓应用对共享库的访问模式进行了分析，发现共享库占了安卓指令足迹的大部分，且不同应用对共享库的访问有较多的重叠部分。

作者的关键思路是对于（安卓对不同应用）预加载的共享的共享库的【页表和TLB项】进行共享。通过设置32位ARM架构的全局位和domain protection model，在父进程fork出子进程时，页表页PTP以copy on write的模式被共享。这样一来就可以避免在内存和TLB、缓存中冗余地存储地址转换信息，提升性能的同时提升可扩展性。

共享PTP带来的性能提升（在测试实验中）：PTP分配数量下降35%，缺页异常减少38%。安卓进程间通信，client端和server端由于共享了TLB，TLB性能分别提升了36%和19%。

####动机
安卓应用的进程和Linux有所不同，所有安卓进程都从zygote这个进程fork出来（zygote是fork自init进程）。安卓进程不执行execve系统调用，而是动态地把应用的代码加载到继承自zygote的预先存在的地址空间中。应用进程从zygote继承动态库的地址转换时用的是copy-on-write的方式。这样的机制副作用是不同应用进程的对于预加载的共享库的虚拟地址到物理地址的转换是相同的。安卓中每个进程有独立的地址转换信息（私有的页表和TLB项）。因此不同进程的这些信息存在着冗余，冗余会直接给cache的性能带来负面影响。

安卓应用的指令足迹中，共享代码占据了很大份额，其中zygote预加载的代码比重很大。

实验分析发现大的页不够高效（虽然节约了地址转换信息的容量，但是浪费了物理内存）。

作者因而小结道：根据安卓进程创建模型和指令访问模式，在页表级别和TLB级别上共享地址转换信息可以获益。

####具体实现
具体实现方面，作者在二级页表页上实现共享。在fork时，子进程的一级页表项指向父进程的PTP（写时复制策略），并在一级页表项中用一个标志位来表示NEED_COPY。如果某个进程尝试修改NEED_COPY，则系统为该进程创建一个新的私有的PTP。

在共享PTP时，系统先检查NEED_COPY位是否为1，如果为0表示该PTP尚未共享过，系统遍历所有的PTE并写保护，然后标志该PTP为已被共享，并将共享计数器加1。如果PTP为1，则表示该PTP已被共享，PTE已被写保护，这时候只需要将子进程的一级页表项设置为指向该共享PTP的指针，增加PTP共享计数器即可。

需要解除共享PTP的几种情况：写访问导致的缺页异常，尝试修改共享的内存区域，进程在共享PTP的地址范围中新分配/释放内存，释放共享的PTP。

数据段和代码段如果被映射到同一个PTP中，则数据段一旦被修改，就不能再共享PTP了（会产生一系列拷贝等overhead）。所以研究者们尝试了重新编译共享库，把数据段和代码段映射到不同的PTP中。这样即使数据段有了修改，代码段还可以被继续共享。具体方法是在数据段和代码段中间插入2MB的地址空间，并在运行时将它们的地址区域以2MB进行对齐，保证数据段和代码段在不同的PTP中。

TLB的共享利用到了ARM架构的PTE具有全局位的特性，和domain protection model。全局位是二层页表项中的一位，会被加载到TLB中，并告知TLB忽略这个表项地址的标识符（address space identifier, ASID）。（该映射对于所有的虚拟地址空间是一样的。即不管哪个用户态进程在运行，内核态的地址空间是一样的，对于内核页的地址映射也是一样的。）这样一来，在TLB中的那些被标成了global的内存地址映射关系就可以被所有的进程共享了。

研究者们在TCB中增加了标志位，表征当前进程是否为zygote。如果mmap系统调用被发起映射共享库的代码段，且当前进程是zygote，则系统用全局标志位来吧对应的内存区域标识为全局的。因而所有安卓应用都会继承这些被标成global的内存区域。

domain protection model引入的原因是为了避免非zygote进程也能访问到全局的TLB项（又不想过分昂贵的在每次上下文切换时清除所有TLB项）。研究者们的解决方案是把所有zygote预加载的共享代码放进一个特定的域，只有zygote进程才有权限访问这些域。

####性能评测
研究者们在Nexus 7平板电脑上针对一系列非常普遍的安卓应用（如愤怒的小鸟，Adobe Reader，Chorme浏览器，谷歌日历，MX Player,WPS等等）上做实验评测性能。

Zygote方面，共享PTP使fork的性能提升了已被，同时减少了缺页异常的数量。安卓应用的启动性能（涉及IPC）方面，主要测了执行时间和L1指令缓存性能。L1缓存性能提升的主要原因是缺页减少后，内核执行指令的数量减小了。研究者们还评测了应用执行过程中总体性能（分配PTP数目减小，缺页中断减少），和IPC的性能（TLB的stall cycles略有减少）。

研究者们总结了共享PTP项和TLB项对各项性能带来的影响，同时表示由于他们对系统的修改主要在机器无关的代码中，所以也可以移植到别的多级页表架构中。研究者们还建议未来的处理器可以更多地探索类似domain protection model的保护机制，以支持TLB项在不同进程间的共享。

---

文章提出的方法的局限性除了需要硬件和系统进程管理机制的支持外，还有一点在于借助共享库的优化策略难以应用到大型数据中心中。因为随着容器技术的不断发展，数据中心更多地采用容器来部署业务，而普遍的现象是，不同任务的共享库都被静态链接到每个容器中（解耦合以避免对运行环境的依赖），打成了一个大包。这样即使大家都共享同样的一些库，但彼此还是使用着独立的私有的PTP，不能实现PTP和TLB项的共享。容器技术背景下数据中心共享库的使用方式会带来内存地址转换性能上的低效，但这可能并不是数据中心任务性能的瓶颈。具体系统的设计还是需要综合任务的需求、数据中心硬件、系统等多方面因素进行考量。
