from collections import defaultdict
from os.path import exists
from sys import exit
from itertools import combinations
from csv import writer
from itertools import combinations
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
    print(max)
    for x in f:
        temp = str(x).replace('\n', '').split('\t')
        if i !=0:
            if int(float(temp[2])) < max*0.1:
                list.append(temp)
        else:
            list.append(temp)
            i = 1
    f.close()
    list.pop(0)
    return list

def massReduction(list):
    print("begin triangle reduction")
    for a, b, c in combinations(list, 3):
        w1 = 0
        w2 = 0
        w3 = 0
        if w1 < 10 and w2 < 10 and w3 < 10:
            area = get_area(w1, w2, w3)
            if area < 10:
                label = str([a,b,c])
                print("aaaaaa")



    return 0

def get_area(a, b, c):
    s = (a+b+c)/2
    return (s*(s-a)*(s-b)*(s-c)) ** 0.5

input = "C:\\Users\\J\\Downloads\\test-output (2).csv"
inputList, max = GetInput(input)
print(len(inputList))
cleanedList = wtf(input, max)
print(len(cleanedList))

with open('C:\\Users\\J\\Downloads\\test-output (17).csv', 'w+') as f:
    csv_writer = writer(f, delimiter='\t')
    csv_writer.writerow('source target weight'.split())
    # csv_writer.writerow(['source', 'target', 'weight'])
    for result in cleanedList:
        # this should get rid of some of the incredibly distant locations
        # if result[2] < 400:
        csv_writer.writerow(result)
