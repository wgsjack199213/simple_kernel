#### The Scalable Commutativity Rule: Designing Scalable Software for Multicore Processors

我在本科时上过陈渝老师的操作系统课程（0字班姚班修的操作系统课）。当年根据老师的布置我门已经阅读过了这篇论文，而且在课堂上也参与了commuter的小实验，大致是用Python语言给接口函数建模，然后用ucore-os-analyser对这些接口模型进行成对的commutativity分析，自动生成一系列测试。所以这次我没有仔细通读论文全文，只读了Abstract，Introduction和Conclusion，大致浏览了中间内容。

这篇文章针对多核系统中软件的可扩展性，提出了一些重要的思想理念。首先作者们认为

> Whenever interface operations commute, they can be implemented in a way that scales。

也就是说操作具有交换性的接口，是可以实现为可扩展的。由此作者们提出了新的观点：可扩展性不应当被理解成一种软件实现的特性，而应当理解成一种软件接口设计的特性。也就是说，软件的可扩展性应当从接口的设计时就开始考量，而不应当等到实现时再去优化。而具体设计接口遵循的规则，就是前文提到的commutativity rule。

作者还实现了一个分析工具commuter，可以对接口的模型进行形式化的分析。这样一种新的软件设计方法是，先设计接口的模型，通过工具分析证明其commutativity，然后再根据模型去实现具体的接口代码。

文章基于他们实现的分析工具分析了Linux的内核设计，结果发现系统调用接口间的commutativity并不好，影响了其可扩展性。研究者们自己设计、开发了SV6，系统调用间的commutativity大大增强。（因此此项研究工作非常坚实，有创新的思想理念，有系统实现，达到了顶级学术会议的水准。）

对于这种系统可扩展性的研究，实验评测的一项重要指标是使用不同数目的核，运行一些benchmark，计算throughput per core。可扩展性好的系统，在不同核数的多核系统上，该项指标应接近同一数值，而可扩展性差的系统，随着核数增加，该项指标的值会迅速下降。

- 为什么commutativity性质差的系统可扩展性差？因为不同线程间的同步会引入额外开销。