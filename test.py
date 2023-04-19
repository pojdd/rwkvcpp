# s = '你' # python3中，汉字默认以unicode编码方式存储，所以在print打印时会将unicode对应的字符输出
# print(s)
# uni1=s.encode('utf-8') # 为字符串s编码，即将汉字的unicode转换为utf-8编码（ASCII）
# print(uni1)
# uni11=s.encode('utf-8').decode() # utf-8编码后又解码，得到了汉字的unicode编码，所以print后仍为汉字
# uni2=s.encode('unicode-escape') # 将汉字的unicodee进行utf-8编码，得到byte类型
# print(uni2)

# print(b'\xe4\xbd\x142'.decode())
# print("\u010a")

import tokenizers
tokenizer = tokenizers.Tokenizer.from_file('20B_tokenizer.json')
decoded = tokenizer.decode([14377,5690,211,43244])
print(decoded)
