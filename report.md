# Simple Kernel 模型分析

## Process Queue
该类用来描述进程队列。

### INIT
初始化函数保证队列初始是空的。

### IsEmpty
通过检查elts是否为空，判断队列是否为空。

### Enqueue
通过把指定元素放在elts末尾，将指定元素加入队列。

### RemoveFirst
取出队列头部第一个元素，并将其从队列中删除。

### QueueFront
返回队列头部第一个元素。

### RemoveElement
删除指定元素。
