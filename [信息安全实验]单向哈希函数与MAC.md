##单向哈希函数与MAC实验报告

本次实验所有代码路径为：<https://github.com/wgsjack199213/simple_kernel/tree/master/security_exp>

####实验1：生成消息摘要和 MAC

用不同哈希算法生成信息摘要如下：

	MD4(test.txt)= 3c9e4020d3e3c7a09c68880a4b24fb91
	MD5(test.txt)= 59ca0efa9f5633cb0371bbc0355478d8
	RIPEMD160(test.txt)= 31bc8e633097159a704659964eadf48dd776e2c0
	SHA(test.txt)= dc1cfae9a755e56234677c258f1d9bdcf630f067
	SHA1(test.txt)= 47a013e660d408619d894b20806b1d5086aab03b
	SHA224(test.txt)= f771a839cff678857feee21492184ca7a456ac3cf57e78057b7beaf5
	SHA256(test.txt)= 0ba904eae8773b70c75333db4de2f3ac45a8ad4ddba1b242f0b3cfc199391dd8
	SHA384(test.txt)= f7f8f1b9d5a9a61742eeda26c20990282ac08dabda14e70376fcb4c8b46198a9959ea9d7d194b38520eed5397ffe6d8e
	SHA512(test.txt)= 32c07a0b3a3fd0dd8f28021b4eea1c19d871f4586316b394124f3c99fb68e59579e05039c3bd9aab9841214f1c132f7666eb8800f14be8b9b091a7dba32bfe6f
	MDC2(test.txt)= 1d4c963b31c2899ac3b3ff9782d73b4e

不同哈希算法生成的信息摘要长度有所不同，且内容混乱无规律，但实验可以观察到同一哈希算法生成的信息摘要长度是定值。

####实验2：Keyed Hash 和 HMAC

用三种哈希算法对我随机输入的字符串和key进行计算结果如下:

	HMAC-MD5(test.txt)= 11cc0a7f1a1db3888fe080f10a062501
	HMAC-SHA1(test.txt)= 11b36e045ef407dfc6ef622a8fffe2e9c879dbd4
	HMAC-SHA256(test.txt)= cd0dc2056fe8a913b6d0807a24996115015ca79ac95048613d409d3c54237b30
	
更换key的长度进行计算结果如下：

	HMAC-MD5(test.txt)= b1063f54d3f02e86ca27a9ca69700734
	HMAC-SHA1(test.txt)= b790e67183402a3fe4caacc195060313afc63a04
	HMAC-SHA256(test.txt)= e1c1d9ec3e1e2803dbbc671e9e410aa16cccef2c9be3f51f54329f0460718b08


key不需要固定长度。

根据协议规定：*K' is another secret key, derived from the original key K (by padding K to the right with extra zeroes to the input block size of the hash function, or by hashing K if it is longer than that block size)*。

所以K的长度可以是任意的，根据block size的大小可以对K进行补0或者hash处理，转换生成长度不大于block size的K’即可。

参考资料：<https://en.wikipedia.org/wiki/Hash-based_message_authentication_code>

####实验3：单向哈希函数的随机性
实验记录见下文。使用了SHA256和MD5两种哈希算法，并打印出任意翻转一位前后的信息摘要值。观察发现H1和H2不相似，混乱无规律。通过程序计数，发现在两种算法下，H1和H2相同位的数量均大致为位长的一半。

附实验记录如下：

	sha256
	WGSMacBook-Pro:security_exp wgs$ python hash.py
	= bbfa5b618a72859a5f56c2ed19397390e7718223fd0785b74b524c612cd9e6af
	= 208375dc649aa79daf4f74dc108ac5d5e8ee51966adafd65ea8fba444ea26af0
	hello, shiyanlou:
	1011101111111010010110110110000110001010011100101000010110011010010111110101011011000010111011010001100100111001011100111001000011100111011100011000001000100011111111010000011110000101101101110100101101010010010011000110000100101100110110011110011010101111
	hullo, shiyanlou:
	0010000010000011011101011101110001100100100110101010011110011101101011110100111101110100110111000001000010001010110001011101010111101000111011100101000110010110011010101101101011111101011001011110101010001111101110100100010001001110101000100110101011110000
	same count: 116
	diff count: 140
	
	md5
	WGSMacBook-Pro:security_exp wgs$ python hash.py
	d5c607f3b5f3b413b267f8f3081b3527
	ac194d133dd447f26d907427b43ba29b
	hello, shiyanlou:
	11010101110001100000011111110011101101011111001110110100000100111011001001100111111110001111001100001000000110110011010100100111
	hullo, shiyanlou:
	10101100000110010100110100010011001111011101010001000111111100100110110110010000011101000010011110110100001110111010001010011011
	same count: 57
	diff count: 71
	
####实验4：单向特性（One-Way）与避免冲突特性（Collision-Free）的对比

实验楼网站上提供的代码在虚拟机环境中编译后运行时会报segement fault，调试无果，所以我自己重新编写了Python程序进行实验。

实验重复进行10轮，每轮随机生成一个preimage D，同时进行针对One-way攻击和Collision攻击，即通过暴力枚举，寻找m使得Hash(m) = D（实验中我用了MD5算法，为了缩短实验时间，仅取信息摘要的前24位），同时寻找m1，m2使得Hash(m1) = Hash(m2)，分别记录下两种寻找各自第一次成功时枚举字符串的个数，并进行对比。具体实验数据见下文。

在10轮实验中，每轮中均先击破Collision，再击破One-way。统计平均枚举次数，击破Collision为5234次，而击破One-way平均为15701578次，是前者的约30000倍。

所以One-way相比Collision更难击破。

这个结果很容易理解。我们可以假设哈希函数的输出是一个在[0, 2^24-1]中均匀分布的随机变量，且每次哈希函数的输出是独立的（独立同分布），则每次操作击破One-way的概率大约是1/(2^24-1)，所以击破One-way的期望计算次数为2^24 = 16777216。这和我们实验中观察到的15701578是非常接近的。

击破Collision的方式是Birthday attack。在哈希输出独立同分布的假设下，前k次不能击破Collision的概率是P_k = (1-1/S)(1-2/S)...(1-k/S)，其中S = 2^24 = 16777216。

由e^x ≥ x - 1可以放缩得到：P_k ≤ e^(-1/S)\*e^(-2/S)\*...\*e^(-k/S)
=e^(-k(k+1)/(2S))。

简单计算可以发现，5000次尝试不能击破Collision的概率不大于0.4746，10000次尝试不能击破Collision的概率不大于0.0508。

总而言之Collision的攻击难度远小于One-way的攻击难度。

附实验记录：

	WGSMacBook-Pro:security_exp wgs$ python attack.py
	preimage: 0xe13fa8 offset: 12876354
	Collision!
	One way!
	[[6161, 'c49253', 'c48491', '538497'], [870584, 'd1c2fa', 'e13fa8']]
	preimage: 0xcb72d1 offset: 3537167
	Collision!
	One way!
	[[7067, '3614aa', '360118', 'fb7499'], [27575246, '01dabcdd', 'cb72d1']]
	preimage: 0xea5ef1 offset: 10031690
	Collision!
	One way!
	[[7003, '992da5', '991493', '214f53'], [1091096, 'a9b862', 'ea5ef1']]
	preimage: 0xbc5ffc offset: 5514587
	Collision!
	One way!
	[[6319, '543e0a', '543b5a', '4670a0'], [21814098, '01a100ad', 'bc5ffc']]
	preimage: 0xf1b0c offset: 2932155
	Collision!
	One way!
	[[5742, '2cd429', '2cc16a', '6d75f6'], [22621284, '0185ea1f', '0f1b0c']]
	preimage: 0x8df04b offset: 6579870
	Collision!
	One way!
	[[4376, '6477b6', '647218', '780d2a'], [48495421, '034861db', '8df04b']]
	preimage: 0xcc99aa offset: 557946
	Collision!
	One way!
	[[1870, '088ac8', '08894f', 'd185a5'], [43844, '092ebe', 'cc99aa']]
	preimage: 0x9a35ca offset: 2008895
	Collision!
	One way!
	[[8987, '1eca5a', '1ec0fd', '919dad'], [12567040, 'de693f', '9a35ca']]
	preimage: 0xffe31c offset: 12113923
	Collision!
	One way!
	[[489, 'b8d9ec', 'b8d912', '086a34'], [9314742, '0146f9b9', 'ffe31c']]
	preimage: 0xbf507b offset: 7055849
	Collision!
	One way!
	[[4327, '6bbad0', '6bb591', '17943d'], [12622412, '012c4435', 'bf507b']]