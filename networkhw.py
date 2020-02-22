# -*- coding: utf-8 -*-
"""
Created on Sat Dec  7 07:34:50 2019

@author: 李梓童
"""

import jieba.posseg
import operator
import networkx as nx
import csv

filename = 'ruc_news.txt'
rowcount = 0
outfile = 'res.csv'

def stopwordslist(filepath):
    stopwords = [line.strip() for line in open(filepath, 'r',encoding='utf-8').readlines()]
    return stopwords

def Proc_File(input_file_name):
    data = []
    row_sec = []
    tmpnamelist = []
    Namedict = {}
    Graphdict = {}
    Graphdict2 = {}
    Groupdict = {}
    
    jieba.load_userdict('userdict.txt')
    stopwords = stopwordslist('stopwords.txt')
    
    with (open(input_file_name,'r',encoding='utf-8')) as inputfile:
        strread = inputfile.read()
    
    #处理最后可能的换行符
    if(strread[len(strread)-1] == '\n' ):
        strread2 = strread[:-1]
    else:
        strread2 = strread

    data = strread2.split('\n')
    
    print(str(len(data))+' lines in total.')
    
    for i, row in enumerate(data):
        row_sec = row.split('\t')
        if(i%1000==0):
            print(str(i)+' lines have been processed.')
        if(i==0):
            continue
        
        for j,row_part in enumerate(row_sec):
            if(j<5):
                continue #跳过pageid,date等
            
            tmpnamelist=[]
            newsorglist = []
            words = jieba.posseg.cut(row_part)
            
            for item in words:
                if(item.word in stopwords):
                    continue
                
                if(item.flag=='nr' or item.flag=='nrfg' or item.flag=='nrt'):
                    if(item.word not in tmpnamelist):
                        tmpnamelist.append(item.word)
                    else:
                        continue
                    
                    if(item.word in Namedict.keys()):
                        Namedict[item.word]=Namedict[item.word]+1
                    else:
                        Namedict[item.word]=1
                    
                elif(item.flag=='nt'):
                    if(item.word in newsorglist):
                        continue
                    else:
                        newsorglist.append(item.word)
                        
                    if(item.word in Groupdict.keys()):
                        if(item.word=='人民大学'):
                            tmpword='中国人民大学'
                            Groupdict[tmpword]=Groupdict[tmpword]+1
                        else:
                            Groupdict[item.word]=Groupdict[item.word]+1
                    else:
                        Groupdict[item.word]=1
            
            for x,name1 in enumerate(tmpnamelist):
                for y,name2 in enumerate(tmpnamelist):
                    if(y<=x):
                        continue
                    if((name1,name2) in Graphdict.keys()):
                        Graphdict[(name1,name2)]=Graphdict[(name1,name2)]+1
                    elif((name2,name1) in Graphdict.keys()):
                        Graphdict[(name2,name1)]=Graphdict[(name2,name1)]+1
                    else:
                        Graphdict[(name1,name2)]=1

            for x,name1 in enumerate(newsorglist):
                for y,name2 in enumerate(newsorglist):
                    if(y<=x):
                        continue
                    if((name1,name2) in Graphdict2.keys()):
                        Graphdict2[(name1,name2)]=Graphdict2[(name1,name2)]+1
                    elif((name2,name1) in Graphdict.keys()):
                        Graphdict2[(name2,name1)]=Graphdict2[(name2,name1)]+1
                    else:
                        Graphdict2[(name1,name2)]=1            
    
    print('Load raw txt file done.')
    return Namedict,Graphdict,Groupdict,Graphdict2

def createGraph(graphdict,flag,output):
    if(flag==1 and output!=0):
        print("开始建立人物图：")
    elif(flag==2 and output!=0 ):
        print("开始建立机构图：")
    G=nx.Graph()
    
    for i in graphdict:
        node=[]
        for j in i:
            node.append(j) #初始点
        G.add_edge(node[0], node[1],weight=graphdict[i])
    
    if(output==0):
        return G
    
    print('节点数：')
    print(G.number_of_nodes())
    print('边数')
    print(G.number_of_edges())
    
    print('联通子图数：')
    print(nx.number_connected_components(G))
    print('最大联通子图大小：')
    largest_components=max(nx.connected_components(G),key=len)  # 高效找出最大的联通成分，其实就是sorted里面的No.1
    #print(largest_components)  #找出最大联通成分
    print(len(largest_components))
    if(flag==1):
        print("人物图建立完毕")
    elif(flag==2):
        print("机构图建立完毕")
        
    return G

def writeEntity(output_file_name,mydict):
    path = output_file_name

    with open(path,'w',newline='') as f:
        csv_write = csv.writer(f)
        for i in mydict:
            data_row = [i,mydict[i]]
            csv_write.writerow(data_row)
    return 0

def writerowtocsv(output_file_name,mydict,rowc):
    path = output_file_name
    myc=0
    with open(path,'a+',newline='') as f:
        csv_write = csv.writer(f)
        for i in mydict:
            data_row = i
            csv_write.writerow(data_row)
            myc=myc+1
            if(myc==rowc):
                break
    return 0

def writeRelation(output_file_name,mydict):
    path = output_file_name

    with open(path,'w',newline='') as f:
        csv_write = csv.writer(f)
        for i in mydict:
            data_row = []
            for j in i:
                data_row.append(j)
            data_row.append(mydict[i])
            csv_write.writerow(data_row)
    return 0

def HotEntity(mydict):
    mydict=sorted(mydict.items(),key=operator.itemgetter(1),reverse=True)
    #writerowtocsv(outfile,mydict,10)
    print(mydict[:10])
    return mydict[:10]

def csvtoEntitydict(input_file_name):
    mydict = {}
    
    with (open(input_file_name,'r',encoding='utf-8')) as inputfile:
        strread = inputfile.read()
    
    #处理最后可能的换行符
    if(strread[len(strread)-1] == '\n' ):
        strread2 = strread[:-1]
    else:
        strread2 = strread

    data = strread2.split('\n')
    
    for i, row in enumerate(data):
        row_sec = row.split(',')
        
        for j,row_part in enumerate(row_sec):
            if(j==0):
                tmpname=row_part
            elif(j==1):
                tmpcount=int(row_part)
        
        mydict[tmpname]=tmpcount
    
    return mydict

def csvtoRelationdict(input_file_name):
    mydict = {}
    
    with (open(input_file_name,'r',encoding='utf-8')) as inputfile:
        strread = inputfile.read()
    
    #处理最后可能的换行符
    if(strread[len(strread)-1] == '\n' ):
        strread2 = strread[:-1]
    else:
        strread2 = strread

    data = strread2.split('\n')
    
    for i, row in enumerate(data):
        row_sec = row.split(',')
        
        for j,row_part in enumerate(row_sec):
            #print(j,row_part)
            if(j==0):
                tmpname1=row_part
            elif(j==1):
                tmpname2=row_part
            else:
                tmpweight=int(row_part)
        
        mydict[(tmpname1,tmpname2)]=tmpweight
    
    return mydict

def PageRank(G, damping_factor):
    d = 1
    V = len(G)
    ranks = dict()
    ranks_store = dict()
    
    # 初始化
    for key, node in G.nodes(data=True):
        ranks[key] = 1/V
    
    ranks_store = ranks.copy()
    
    print('开始计算pagerank...')
    for _ in range(20):
        ranks_store = ranks.copy()
        for key, node in G.nodes(data=True):
            rank_sum = 0.0
            links = G.degree(key)
            neighbors = G.neighbors(key)
            for n in neighbors:
                if (links > 0):
                    rank_sum  += (1 / float(links)) * ranks_store[n]*G[key][n]['weight'] #计算RAW
          
            ranks[key] = ((1 - float(d)) * (1/float(V))) + d*rank_sum #加工后
    
    sumf=0.0
    for i in ranks:
        sumf+=ranks[i]
    
    for i in ranks:
        ranks[i]=ranks[i]/sumf
    #排序
    sorted_r = sorted(ranks.items(), key=operator.itemgetter(1,0), reverse=True)
   
    countnode = 0
    node_list_in_descending_order=[]
    
    for i in sorted_r:
        node_list_in_descending_order.append(i)
        countnode = countnode+1
        
        if(countnode>20):
            break
        
    print("Pagerank 排名前20位：")
    print(node_list_in_descending_order)
    
    writerowtocsv(outfile,sorted_r,20)
    return node_list_in_descending_order

def PageRank2(G, damping_factor):
    if(G.is_directed()==False):
        G.to_directed()
    
    print('开始计算pagerank...')
    ranks = nx.pagerank(G, alpha=0.85,weight='weight')

    sorted_r = sorted(ranks.items(), key=operator.itemgetter(1,0), reverse=True)
   
    countnode = 0
    node_list_in_descending_order=[]
    
    for i in sorted_r:
        node_list_in_descending_order.append(i)
        countnode = countnode+1
        
        if(countnode>=20):
            break
        
    print("Pagerank 排名前20位：")
    print(node_list_in_descending_order)
    
    #writerowtocsv(outfile,sorted_r,20)
    
    return node_list_in_descending_order

def ConnectInfluence(Srclist,Tarlist,input_file_name):

    jieba.load_userdict('userdict.txt')
    stopwords = stopwordslist('stopwords.txt')
    
    with (open(input_file_name,'r',encoding='utf-8')) as inputfile:
        strread = inputfile.read()
    
    #处理最后可能的换行符
    if(strread[len(strread)-1] == '\n' ):
        strread2 = strread[:-1]
    else:
        strread2 = strread

    data = strread2.split('\n')
    
    print(str(len(data))+' lines in total.')
    
    counta=0
    flaga=0
    countb=0
    flagb=0
    
    print('统计中...')
    for i, row in enumerate(data):
        row_sec = row.split('\t')
        if(i%1000==0):
            print(str(i)+' lines have been processed.')
        if(i==0):
            continue
        #if(i>500):
        #    break
        
        for j,row_part in enumerate(row_sec):
            if(j<5):
                continue #跳过pageid,date等
            
            flaga=0
            flagb=0
            words = jieba.posseg.cut(row_part)
            
            for item in words:
                if(item.flag!='nt' and item.flag!='nr' and item.flag!='nrfg' and item.flag!='nrt'):
                    continue
                
                if(item.word in Srclist and flaga==0):
                    flaga=1
                    continue
                
                if(item.word in Tarlist and flagb==0):
                    flagb=1
                    continue
    
        if(flaga==1):
            counta+=1
            if(flagb==1):
                countb+=1
    
    print('出现了强影响力机构的新闻'+str(counta)+'篇，其中出现了强影响力人物的新闻'+str(countb)+'篇')    
    print('重合比例为：'+str(countb*1.0/counta))
    return countb*1.0/counta

def ConfidenceTest(Persondict,Orgdict):
    print("-----正确性检验-----")
    print("前10位热门人物：")
    HotEntity(Persondict)
    print("前10个热门机构：")
    HotEntity(Orgdict)

def Findtop10neighbors(G,Persondict):
    query = input("请输入想查询的人物：")
    
    if(query not in Persondict.keys()):
        print('人物不存在')
        return 1
    
    top10dict = {}
    
    neighbors = G.neighbors(query)
    for n in neighbors:
        top10dict[n]=int(G[query][n]['weight'])
    
    sorted_top10dict = sorted(top10dict.items(), key=operator.itemgetter(1), reverse=True)
    
    print("查询结果为：")
    if(len(sorted_top10dict)>=10):
        print(sorted_top10dict[:10])
        #writerowtocsv(outfile,sorted_top10dict,10)
    else:
        print(sorted_top10dict)
       # writerowtocsv(outfile,sorted_top10dict,len(sorted_top10dict))
    return 0

def Betweenness_nx(G):
    print('计算中介中心性...')
    bc=nx.betweenness_centrality(G,k=20,weight='weight')
    
    sorted_bc = sorted(bc.items(), key=operator.itemgetter(1), reverse=True)
    sorted_bc_list=[]
    countnode = 0
    
    for i in sorted_bc:
        sorted_bc_list.append(i)
        countnode = countnode+1
        
        if(countnode>=10):
            break
    writerowtocsv(outfile,sorted_bc,10)    
    print('中介中心性最大的前10个人为：')
    print(sorted_bc_list)
    
def Clusteringcoefficient(G):
    clucoe = {}
    
    print('计算聚集系数...')
    for key, node in G.nodes(data=True):
        neighbors = G.neighbors(key)
        alledges= G.degree(key)
        conn = 0
        for i,n in enumerate(neighbors):
            for j,m in enumerate(neighbors):
                if( i>=j ):
                    continue
                elif( G.has_edge(n,m) ):
                    conn = conn+1
        if(alledges>1):
            clucoe[key]=2*conn/(alledges*(alledges-1))
        else:
            clucoe[key]=0
    
    sorted_clucoe = sorted(clucoe.items(), key=operator.itemgetter(1), reverse=True)
    sorted_clucoe_list=[]
    countnode = 0
    
    for i in sorted_clucoe:
        sorted_clucoe_list.append(i)
        countnode = countnode+1
        
        if(countnode>=10):
            break
    
   # writerowtocsv(outfile,sorted_clucoe,10)
    print('聚集系数最大的前10个人为：')
    print(sorted_clucoe_list)

def ProveClosure(G,Persondict,threshold):
    closure = {}
    visited = []
    nodec = 0
    
    print('计算共同好友数...')
    for key, node in G.nodes(data=True):
        nodec = nodec+1
        if(Persondict[key]<threshold):
            continue
        if(nodec%100==0):
            print('已完成'+str(nodec))
            
        neighbors1 = G.neighbors(key)
        for i,n in enumerate(neighbors1):
            if(Persondict[n]<threshold):
                continue

            neighbors2 = G.neighbors(n)
            tmpset = set([key,n])
            conn=0
            if(tmpset in visited):
                continue
            else:
                visited.append(tmpset)
            
            for j,m in enumerate(neighbors2):
                #if(Persondict[m]<threshold):
                #    continue
                
                if(conn > 10):
                    break
                if( G.has_edge(key,m) ):
                    conn = conn+1
        
        if(conn>=10):
            if(10 not in closure.keys()):
                closure[10]=1
            else:
                closure[10]=closure[10]+1
        else:
            if(conn not in closure.keys()):
                closure[conn]=1
            else:
                closure[conn]=closure[conn]+1
    
    print('共同好友数统计如下：')
    print(closure)
    
    sorted_closure = sorted(closure.items(), key=operator.itemgetter(1), reverse=True)
    #writerowtocsv(outfile,sorted_closure,len(sorted_closure))
    return sorted_closure

    
def menu():
    print('0: 退出')
    print('1：查询与人物A联系最紧密的前10个人')
    print('2: Pagerank，输出影响力排名前20位人物（damping_factor=0.85）')
    print('3: 查询中介中心性最大的10个人')
    print('4: 查询聚集系数最大的前10个人')
    print('5: 验证三元闭包')
    print('6: Pagerank，输出影响力排名前20个机构（damping_factor=0.85）')
    print('7: 强影响力机构与强影响力人物之间关联计算')

def datapreproc(Personfile,Orgfile,Relationfile,Relationfile2):
    Persondict,Relationdict,Orgdict,Relationdict2=Proc_File(filename)
    
    Personfile='person.csv'
    Orgfile='organization.csv'
    Relationfile='relation.csv'
    Relationfile2='relation2.csv'
    
    writeEntity(Personfile,Persondict)
    writeEntity(Orgfile,Orgdict)
    writeRelation(Relationfile,Relationdict)
    writeRelation(Relationfile2,Relationdict2)

    print('数据载入完毕，写入'+Personfile+', '+Orgfile+', '+Relationfile+','+Relationfile2)
    
def main():
    
    q = input('若需从源数据重新处理数据，请输入1；若需直接读取已处理好的数据，请输入2：')
    if(q=='1'):
        Persondict,Relationdict,Orgdict,Relationdict2=Proc_File(filename)
    elif(q=='2'):
        Personfile = '_person.txt'
        Orgfile = '_organization.txt'
        Relationfile = '_relation.txt'
        Relationfile2 = '_relation2.txt'
        
        Persondict = csvtoEntitydict(Personfile)
        print("Persondict 加载完毕")
        Orgdict = csvtoEntitydict(Orgfile)
        print("Orgdict 加载完毕")
        Relationdict = csvtoRelationdict(Relationfile)
        print("Relationdict 加载完毕")
        Relationdict2 = csvtoRelationdict(Relationfile2)
        print("Relationdict-organization 加载完毕")
    
    
    ConfidenceTest(Persondict,Orgdict)
    
    q=input('准确性验证通过？y/n')
    if(q=='n' or q=='N'):
        return 0
    
    G = createGraph(Relationdict,1,1)
    G2 = createGraph(Relationdict2,2,1)
    pr = []
    pr2 = []
    Srclist = []
    Tarlist = []
    
    menu()
    op = input("请输入指令序号：")
    while(1):
        if(op=='1'):
            Findtop10neighbors(G,Persondict)
        elif(op=='2'):
            pr = PageRank2(G,0.85)
            G = createGraph(Relationdict,1,0)
        elif(op=='3'):
            Betweenness_nx(G)
        elif(op=='4'):
            Clusteringcoefficient(G)
        elif(op=='5'):
            threshold = int(input("请输入选择节点的出现频数最小值："))
            ProveClosure(G,Persondict,threshold)
        elif(op=='6'):
            pr2 = PageRank2(G2,0.85)
            G2 = createGraph(Relationdict2,2,0)
        elif(op=='7'):
            if(len(pr)==0):
                pr = PageRank2(G,0.85)
                G = createGraph(Relationdict,1,0)
            if(len(pr2)==0):
                pr2 = PageRank2(G2,0.85)
                G2 = createGraph(Relationdict2,2,0)
            for i in pr:
                Srclist.append(i[0])
            for i in pr2:
                Tarlist.append(i[0])
            op2=input('计算强影响力人物/强影响力机构，键入1；强影响力机构/强影响力人物，键入2：')
            if(op2=='1'):
                ConnectInfluence(Srclist,Tarlist,filename)
            elif(op2=='2'):
                ConnectInfluence(Tarlist,Srclist,filename)
            else:
                print('输入无效')
        elif(op=='0'):
            return 0
        else:
            print(op+" 输入无效")
        op = input("请输入指令序号：")
    

main()