from collections import defaultdict
from os.path import exists
from sys import exit
from itertools import combinations
from csv import writer

from clusterTree import TreeBuilder
from flag import *

def CleanOutput(doomList, cap):
    cap = 0
    for x in doomList:
        if int(float(x[2])) > cap: cap = int(float(x[2]))
    i = 0
    for x in doomList:
        if int(float(x[2])) >= cap*0.8:
            doomList.remove(x)
            print(i)
            i = i+1
    return doomList

def GetInput(input):
    # with open(input, 'r') as f:
    #     spamreader = reader(csvfile, delimiter=' ', quotechar='|')
    #     list = []
    #     for row in spamreader:
    #         list.append(str(row))
    #     return list[0   ]
    # return "huh?"
    f = open(input, "r", encoding="utf8")
    # print(f.readline())
    list = []
    cap = 0
    i = 0
    for x in f:
        temp = str(x).replace('\n', '').split('\t')
        list.append(temp)
        # for x in doomList:
        if i !=0:
            if int(float(temp[2])) > cap: cap = int(float(temp[2]))
        else:
            i = 1
    list.pop(0)
    f.close()
    return list, cap

def wtf(input, max):
    f = open(input, "r", encoding="utf8")
    list = []
    i = 0
    for x in f:
        temp = str(x).replace('\n', '').split('\t')
        if i !=0:
            if int(float(temp[2])) < max*0.8:
                list.append(temp)
        else:
            list.append(temp)
            i = 1
    f.close()
    list.pop(0)
    return list

def massReduction(list):
    print("begin triangle reduction")
    
    return 0

input = "C:\\Users\\J\\Downloads\\test-output (2).csv"
inputList, max = GetInput(input)
print(len(inputList))
cleanedList = wtf(input, max)
print(len(cleanedList))
