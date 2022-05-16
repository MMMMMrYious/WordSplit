import re

lines = []
maxlen = 0
maxword = ''
#CharsToRemove = '[·’!"\#$%&\'()＃！（）*+,-./:;<=>?\@，：\\n?￥—『』★、…．。＞【】［］《》？“”‘’\[\\]^_`{|}~]+'
with open('all_train_text.txt','r',newline='',encoding='utf-8') as f:
    att = 0
    print('wait for reading')
    for i in f.readlines():
        line = " ".join(re.findall(r'\b\w+\b',i))
        words = line.split(' ')
        for j in words:
            if len(j)> maxlen:
                maxlen = len(j)
                maxword = j
        lines.append(line)
        att += 1
        print(att)

    print(maxlen)
    print(maxword)
with open('dictionary.txt','w',newline='\n',encoding='utf-8') as f:
    att = 0
    print('wait for writing')
    for i in lines:
        f.write(i)
        f.write(' ')
        att += 1
    print('done')
with open('hmm_dic.txt','w',newline='\n',encoding='utf-8') as f:
    att = 0
    print('wait for writing')
    for i in lines:
        f.write(i)
        f.write('\n')
        att += 1
    print('done')







