import re
import math
maxlen = 32 # 原词库数据集文件为all_train_test.txt .文件dcitonary 是处理好的词库
dictionary = []#存放在内存中的词库
result_shortestpath = []
edges = []#最短路径算法要用到
hmm_dic = [] #基于统计的隐马尔可夫算法要用到
hmm_stat = []
hmm_DicWithStat = [] #带有hmm状态的词典
#author YanYe/Yious

print("dictionary initialing...")
with open('dictionary.txt','r',encoding='utf-8') as f: #dictionary 列表存的是所有词
    lines = f.readlines()
    for i in lines:
        words = i.split(' ')
        for j in words:
            dictionary.append(j)
print("Success!")
print("HMM dictionary initialing...")
with open('hmm_dic.txt','r',encoding='utf-8') as f: #hmm_dic 列表存的是所有句子
    lines = f.readlines()
    for i in lines:
        stats = []
        sentence = i.rstrip('\n')
        hmm_dic.append(sentence)
        words = sentence.split(' ')
        for j in words:
            if len(j) == 1:
                stats.append('S')
            elif len(j) ==2:
                stats.append('BE')  
            else:
                stats.append('B'+'M'*(len(j)-2)+'E')  #stats包含所有字的状态，为语料库已知
        hmm_stat.append(stats)
        hmm_DicWithStat.append((sentence.replace(' ',''),''.join(stats)))
print("Success!")

def initil_matrix(hmm_stat): # 建立初始矩阵
    print('initiling start matrix...')
    ini_matrix = [0,0,0,0]
    for i in hmm_stat:
        if i[0][0] == 'B':
            ini_matrix[0] += 1
        if i[0][0] == 'M':
            ini_matrix[1] += 1
        if i[0][0] == 'E':
            ini_matrix[2] += 1
        if i[0][0] == 'S':
            ini_matrix[3] += 1
    sum = ini_matrix[0] + ini_matrix[1] + ini_matrix[2] + ini_matrix[3]
    ini_matrix[0] = ini_matrix[0] / sum
    ini_matrix[1] = ini_matrix[1] / sum
    ini_matrix[2] = ini_matrix[2] / sum
    ini_matrix[3] = ini_matrix[3] / sum
    print('ini_matrix : ')
    print(ini_matrix)
    return ini_matrix

def transfer_matrix(hmm_stat): #建立转移矩阵
    print('initiling transfer matrix...')
    trans_matrix = [[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]]
    pure_stats = []
    for i in hmm_stat:
        for j in i:
            for k in j:
                pure_stats.append(k)
    for i in range(len(pure_stats)-1):
        if pure_stats[i] == 'B':
            add_row = 0
        if pure_stats[i] == 'M':
            add_row = 1
        if pure_stats[i] == 'E':
            add_row = 2
        if pure_stats[i] == 'S':
            add_row = 3
        if pure_stats[i+1] == 'B':
            add_col = 0
        if pure_stats[i+1] == 'M':
            add_col = 1
        if pure_stats[i+1] == 'E':
            add_col = 2
        if pure_stats[i+1] == 'S':
            add_col = 3
        # if not add_col:
        #     break
        trans_matrix[add_row][add_col] = trans_matrix[add_row][add_col] + 1
    print('transfer matrix:')
    for i in range(len(trans_matrix)):
        row_sum = sum(trans_matrix[i])
        for j in range(len(trans_matrix[i])):
            trans_matrix[i][j] = trans_matrix[i][j]/row_sum
        print(trans_matrix[i])
    return trans_matrix

def launch_matrix(hmm_DicWithStat): #建立发射矩阵
    print('initiling launch matrix...')
    B = {}
    M = {}
    E = {}
    S = {}
    for i in hmm_DicWithStat:
        words = i[0]
        stats = i[1]
        for j in range(len(words)):
            if stats[j] == 'B':
                if words[j] in B.keys():
                    B[words[j]] = B[words[j]] + 1
                else:
                    B[words[j]] =  1
            if stats[j] == 'M':
                if words[j] in M.keys():
                    M[words[j]] = M[words[j]] + 1
                else:
                    M[words[j]] =  1
            if stats[j] == 'E':
                if words[j] in E.keys():
                    E[words[j]] = E[words[j]] + 1
                else:
                    E[words[j]] =  1
            if stats[j] == 'S':
                if words[j] in S.keys():
                    S[words[j]] = S[words[j]] + 1
                else:
                    S[words[j]] =  1
    for k,v in B.items():
        v = v / sum(B.values())
        B[k] = v
    for k,v in M.items():
        v = v / sum(M.values())
        M[k] = v
    for k,v in E.items():
        v = v / sum(E.values())
        E[k] = v
    for k,v in S.items():
        v = v / sum(S.values())
        S[k] = v
    print('launch matrix:')
    print(B)
    print(M)
    print(E)
    print(S)
    return (B,M,E,S)

def waitb(strs):  #维特比算法求解HMM问题
    print('start waitb method...')
    strs = "".join(re.findall(r'\b\w+\b', strs))
    print(strs)
    hidden_stats = ['S']*len(strs)
    hidden_path = []
    pros = []
    for i in range(len(strs)):
        hidden_path.append([0,1,2,3])
    for i in range(len(hidden_path)-1):
        if i == 0:
            for j in hidden_path[i]:
                pros.append((0,-1,0,ini_matrix[j]*lau_matrix[j][strs[i]]))
        else:
            for j in hidden_path[i]:
                for k in hidden_path[i+1]:
                    pros.append((i,j,k,trans_matrix[j][k]*lau_matrix[k][strs[i+1]]))
    temp = []
    mats = []
    index = 0
    for i in pros:
        if i[0] != 0:
            temp.append(i)
            index += 1
            if index ==16:
                index = 0
                mats.append(temp)
                temp = []
    result_waitb = []
    for i in mats:
        maxprob0 = 0
        maxindex0 = 0
        maxprob1 = 0
        maxindex1 = 0
        maxprob2 = 0
        maxindex2 = 0
        maxprob3 = 0
        maxindex3 = 0
        for j in i:
            if j[2] ==0 and (j[3] > maxprob0):
                maxprob0 = j[3]
                maxindex0 = (j[1],j[2],-math.log(maxprob0))
            if j[2] == 1 and (j[3] > maxprob1):
                maxprob1 = j[3]
                maxindex1 = (j[1],j[2],-math.log(maxprob1))
            if j[2] == 2 and (j[3] > maxprob2):
                maxprob2 = j[3]
                maxindex2 = (j[1],j[2],-math.log(maxprob2))
            if j[2] == 3 and (j[3] > maxprob3):
                maxprob3 = j[3]
                maxindex3 = (j[1],j[2],-math.log(maxprob3))
        result_waitb.append([maxindex0,maxindex1,maxindex2,maxindex3])
    result_waitb.reverse()
    edistance = 0
    sdistance = 0
    goal = 2
    path1 = []
    path2 = []
    look = {0:'B',1:'M',2:'E',3:'S'}
    for i in result_waitb:
        for j in i:
            if j[1] == goal:
                path1.append(look[goal])
                goal = j[0]
                edistance = edistance + j[2]
                break
    goal = 3
    for i in result_waitb:
        for j in i:
            if j[1] == goal:
                path2.append(look[goal])
                goal = j[0]
                sdistance = sdistance + j[2]
                break
    if edistance < sdistance:
        path1.append('E')
        path1.insert(0,0)
        print(path1)
    else:
        path2.insert(0, 0)
        path2.append('S')
        print(path2)


def ForwardMaxMaching(strs): #前向最大匹配算法
    strs = "".join(re.findall(r'\b\w+\b', strs))
    strs = strs+'||'
    split_result = []
    print(strs)
    i = 0
    while(i<len(strs)):
        strs = strs[i:-1]
        j = maxlen
        while(j>=1):
            if j ==1 and strs[i:i+j] == '||':
                break
            #print(j)
            if strs[i:i+j] in dictionary:
                split_result.append(strs[i:i+j])
                #print(strs[i:i+j])
                i = i + j
                j = maxlen

            else:
                j = j -1
        i = i + 1
    print(len(split_result))
    print("The result of ForwardMaxMarching : ")
    print(split_result)
    return (split_result)

def BackwardMaxMaching(strs):#后向最大匹配算法
    strs = "".join(re.findall(r'\b\w+\b', strs))
    strs = '||'+strs  # 两束都表示识别结束的标识
    split_result = []
    print(strs)
    i = len(strs)
    while(i>=0):
        strs = strs[0:i]
        j = maxlen
        while(j>=1):
            if j ==1 and strs[i-j:i] == '||':
                break
            #print(j)
            if strs[i-j:i] in dictionary:
                split_result.append(strs[i-j:i])
                #print(strs[i-j:i])
                i = i - j
                j = maxlen

            else:
                j = j -1
        i = i - 1
    print(len(split_result))
    split_result.reverse()
    print("The result of BackwardMaxMarching : ")
    print(split_result)
    return split_result

def ForBackWardMaxMaching(strs): #双向最大匹配
    For_result = ForwardMaxMaching(strs)
    Back_result = BackwardMaxMaching(strs)
    sigles_for = 0
    sigles_back = 0

    if len(For_result) < len(Back_result):
        print(For_result)
        return For_result

    if len(For_result) > len(Back_result):
        print(Back_result)
        return Back_result

    if len(For_result) == len(Back_result):
        for i in For_result:
            if len(i) == 1:
                sigles_for += 1
        for i in Back_result:
            if len(i) == 1:
                sigles_back += 1
        if sigles_for < sigles_back:
            print("The result of TwoDirecitonMaxMarching : ")
            print(For_result)
            return For_result
        else:
            print("The result of TwoDirecitonMaxMarching : ")
            print(Back_result)
            return Back_result

def ShortestPathMarching(strs): # 最短路径法优化贪婪列举算法
    strs = "".join(re.findall(r'\b\w+\b', strs))
    strs = strs+ '||'
    print(strs)
    print('please wait')
    #edges = []
    strs_len = len(strs)
    for i in range(strs_len):
        j = i + 1
        while(j<strs_len):
            if strs[i:j] in dictionary:
                #print(strs[i:j])
                edges.append((i,j,i-j,strs[i:j]))#这里i-j是负数，表示距离
            j += 1
    #print(edges)

    GetShortestPath(edges[len(edges)-1][1])
    result_shortestpath.reverse()
    print(result_shortestpath)

def GetShortestPath(end): #递归获取最大路径
    if end == 0:
        return 0
    options = []
    for i in edges:
        if i[1] == end:
            options.append(i)
    options.sort(key=lambda x :  x[2])#按最短路径排序
    #print(options)
    Jackpot = options[0]
    result_shortestpath.append(Jackpot[3])
    GetShortestPath(Jackpot[0])


#author YanYe/Yious
strs = '每次北京大学生前来应聘，总经理和副总经理经常有意见分歧'

ForwardMaxMaching(strs) #前向最大匹配
BackwardMaxMaching(strs) #后向最大匹配
ForBackWardMaxMaching(strs) #双向最大匹配
ShortestPathMarching(strs) #用最短路径优化的贪婪列举法
# HMM隐马尔科夫+维特比算法
ini_matrix = initil_matrix(hmm_stat)
trans_matrix = transfer_matrix(hmm_stat)
lau_matrix = launch_matrix(hmm_DicWithStat)
waitb(strs)

