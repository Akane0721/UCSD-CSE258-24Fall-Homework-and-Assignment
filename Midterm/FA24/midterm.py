# -*- coding: utf-8 -*-
"""Midterm_stub.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1rMmnFZq7LCLIKLEp_GLjZGLPXtr6xq9L
"""

import json
import gzip
import math
import numpy as np
from collections import defaultdict
from sklearn import linear_model
import random
import statistics

def assertFloat(x):
    assert type(float(x)) == float

def assertFloatList(items, N):
    assert len(items) == N
    assert [type(float(x)) for x in items] == [float]*N

answers = {}

# From https://cseweb.ucsd.edu/classes/fa24/cse258-b/files/steam.json.gz
z = gzip.open("/content/steam.json.gz")

dataset = []
for l in z:
    d = eval(l)
    dataset.append(d)

z.close()

dataset[0]

### Question 1

def MSE(y, ypred):
    diffs = [(a-b)**2 for (a,b) in zip(y,ypred)]
    return sum(diffs) / len(diffs)

def feat1(d):
    return [1, len(d['text'])]

X = [feat1(d) for d in dataset]
y = [d['hours'] for d in dataset]

mod=linear_model.LinearRegression(fit_intercept=False)
mod.fit(X, y)
pred = mod.predict(X)

mse1 = MSE(pred, y)
print(mod.coef_)
print(mse1)

answers['Q1'] = [float(mod.coef_[1]), float(mse1)] # Remember to cast things to float rather than (e.g.) np.float64

assertFloatList(answers['Q1'], 2)

### Question 2

dataTrain = dataset[:int(len(dataset)*0.8)]
dataTest = dataset[int(len(dataset)*0.8):]

Xtrain = [feat1(d) for d in dataTrain]
ytrain = [d['hours'] for d in dataTrain]
Xtest = [feat1(d) for d in dataTest]
ytest = [d['hours'] for d in dataTest]

mod = linear_model.LinearRegression(fit_intercept=False)
mod.fit(Xtrain,ytrain)
pred=mod.predict(Xtest)

def uom(pred,ytest):
  under = 0
  over = 0

  for pre, real in zip(pred, ytest):
    if pre<real:  under+=1
    elif pre>real:  over+=1
  mse=MSE(pred,ytest)
  return under,over,mse

under,over,mse2=uom(pred,ytest)
print(under,over,mse2)

answers['Q2'] = [mse2, under, over]

assertFloatList(answers['Q2'], 3)

### Question 3



y2 = ytrain[:]
y2.sort()
perc90 = y2[int(len(y2)*0.9)] # 90th percentile
dataset90=[d for d in dataTrain if d['hours']<perc90]

X3a = [feat1(d) for d in dataset90]
y3a = [d['hours'] for d in dataset90]

mod3a = linear_model.LinearRegression(fit_intercept=False)
mod3a.fit(X3a,y3a)
pred3a = mod3a.predict(Xtest)

under3a, over3a, mse3a = uom(pred3a, ytest)
print(under3a, over3a, mse3a)

# etc. for 3b and 3c

X3b = [feat1(d) for d in dataTrain]
y3b = [d['hours_transformed'] for d in dataTrain]
X3btest = [feat1(d) for d in dataTest]
y3btest = [d['hours_transformed'] for d in dataTest]

mod3b = linear_model.LinearRegression(fit_intercept=False)
mod3b.fit(X3b,y3b)
pred3b = mod3b.predict(X3btest)
under3b, over3b, mse3b = uom(pred3b, y3btest)
print(under3b, over3b, mse3b)

mod3c = linear_model.LinearRegression(fit_intercept=False)
mod3c.fit(Xtrain,ytrain)
theta0 = mod3c.coef_[0]
ycopy=ytrain[:]
ycopy.sort()
ymedian=ycopy[len(ycopy)//2]
#print(np.median(ycopy))
Xcopy=Xtrain[:]
Xcopy=sorted(Xtrain, key=lambda x:x[1])
#print(Xcopy)
Xmedian=Xcopy[len(Xcopy)//2]
#print(np.median(Xcopy))
print(Xmedian, ymedian)
theta1=(ymedian-theta0)/ Xmedian[1]
mod3c.coef_[1]=theta1
pred3c = mod3c.predict(Xtest)

under3c, over3c, mse3c = uom(pred3c, ytest)
print(under3c, over3c, mse3c)

answers['Q3'] = [under3a, over3a, under3b, over3b, under3c, over3c]
#answers['Q3'] = [under3a, over3a, -1, -1, -1, -1]
#answers['Q3'] = [-1, -1, -1, -1, under3c, over3c]
#answers['Q3'] = [-1, -1, under3b, over3b, -1, -1]
#answers['Q3'] = [over3a,under3a, over3b, under3b, over3c, under3c ]

assertFloatList(answers['Q3'], 6)

### Question 4

def ber(predictions, y):
    TP = [a and b for (a,b) in zip(predictions,y)]
    TN = [not a and not b for (a,b) in zip(predictions,y)]
    FP = [a and not b for (a,b) in zip(predictions,y)]
    FN = [not a and b for (a,b) in zip(predictions,y)]

    TP = sum(TP)
    TN = sum(TN)
    FP = sum(FP)
    FN = sum(FN)

    BER = (FP / (TN + FP) + FN / (TP + FN)) / 2

    return TP, TN, FP, FN, BER

ytrainC = [1 if y > ymedian else 0 for y in ytrain]
ytestC = [1 if y > ymedian else 0 for y in ytest]
mod=linear_model.LogisticRegression(C=1)
mod.fit(Xtrain, ytrainC)
predictions=mod.predict(Xtest)
TP,TN,FP,FN,BER=ber(predictions,ytestC)
print(TP,TN,FP,FN,BER)

answers['Q4'] = [TP, TN, FP, FN, BER]

assertFloatList(answers['Q4'], 5)

### Question 5

underC, overC, _ = uom(predictions,ytestC)
print(underC, overC)

answers['Q5'] = [overC, underC]

assertFloatList(answers['Q5'], 2)

### Question 6

years_train = [int(d['date'][:4]) for d in dataTrain]
years_test = [int(d['date'][:4]) for d in dataTest]
mask_pre_train = np.array(years_train)<=2014
mask_after_train = np.array(years_train)>=2015
mask_pre_test = np.array(years_test)<=2014
mask_after_test = np.array(years_test)>=2015

X2014train = np.array(Xtrain)[mask_pre_train]
y2014train = np.array(ytrainC)[mask_pre_train]
X2015train = np.array(Xtrain)[mask_after_train]
y2015train = np.array(ytrainC)[mask_after_train]
X2014test = np.array(Xtest)[mask_pre_test]
y2014test = np.array(ytestC)[mask_pre_test]
X2015test = np.array(Xtest)[mask_after_test]
y2015test = np.array(ytestC)[mask_after_test]

print(len(X2014train),len(y2014train),len(X2015train),len(X2014test),len(y2015test))
print(y2014train)

'''
pA = mod.predict(X2014test)
_,_,_,_,BER_A=ber(pA,y2014test)
print(BER_A)

pB = mod.predict(X2015test)
_,_,_,_,BER_B=ber(pB,y2015test)
print(BER_B)'''

modA=linear_model.LogisticRegression(C=1)
modA.fit(X2014train, y2014train)
pA = modA.predict(X2014test)
_,_,_,_,BER_A=ber(pA,y2014test)
print(BER_A)

modB=linear_model.LogisticRegression(C=1)
modB.fit(X2015train, y2015train)
pB = modB.predict(X2015test)
_,_,_,_,BER_B=ber(pB,y2015test)
print(BER_B)

modC=linear_model.LogisticRegression(C=1)
modC.fit(X2014train, y2014train)
pC = modC.predict(X2015test)
_,_,_,_,BER_C=ber(pC,y2015test)
print(BER_C)

modD=linear_model.LogisticRegression(C=1)
modD.fit(X2015train, y2015train)
pD = modD.predict(X2014test)
_,_,_,_,BER_D=ber(pD,y2014test)
print(BER_D)

answers['Q6'] = [BER_A, BER_B, BER_C, BER_D]

assertFloatList(answers['Q6'], 4)

### Question 7

dataTrain[0]

usersPerItem = defaultdict(set) # Maps an item to the users who rated it
itemsPerUser = defaultdict(set) # Maps a user to the items that they rated
hoursDict = defaultdict(float)
yearsDict = defaultdict(int)
reviewsPerUser = defaultdict(list)
reviewsPerItem = defaultdict(list)


for d in dataTrain:
    u,i,h,y = d['userID'],d['gameID'],d['hours_transformed'],int(d['date'][:4])
    usersPerItem[i].add(u)
    itemsPerUser[u].add(i)
    hoursDict[(u,i)]=h
    yearsDict[(u,i)]=y

for d in dataTest:
    u,i,y = d['userID'],d['gameID'],int(d['date'][:4])
    yearsDict[(u,i)]=y

def Jaccard(s1, s2):
  intersection= s1.intersection(s2)
  union = s1.union(s2)
  return len(intersection)/len(union) if union !=0 else 0

first_u = dataTrain[0]['userID']

similarities = []
for u in itemsPerUser:
  if u == first_u:  continue
  similarities.append(Jaccard(itemsPerUser[u], itemsPerUser[first_u]))
similarities.sort(reverse=True)
first=similarities[0]
tenth=similarities[9]
print(first,tenth)

answers['Q7'] = [first, tenth]

assertFloatList(answers['Q7'], 2)

### Question 8

def u2u(u,i):
  js=usersPerItem[i]-{u}
  numer=0
  denom=0
  for j in js:
    sim = Jaccard(itemsPerUser[j],itemsPerUser[u])
    numer += hoursDict[(j,i)] * sim
    denom += sim
  return numer / denom if denom!=0 else 0

def i2i(u,i):
  js=itemsPerUser[u]-{i}
  numer=0
  denom=0
  for j in js:
    sim = Jaccard(usersPerItem[j],usersPerItem[i])
    numer += hoursDict[(u,j)] * sim
    denom += sim
  return numer / denom if denom!=0 else 0

def predict(func):
  pred=[]
  y=[]
  for d in dataTest:
    pred.append(func(d['userID'], d['gameID']))
    y.append(d['hours_transformed'])
  return MSE(pred, y)

MSEU = predict(u2u)
MSEI = predict(i2i)
print(MSEU, MSEI)

answers['Q8'] = [MSEU, MSEI]

assertFloatList(answers['Q8'], 2)

### Question 9

def u2uy(u,i):
  js=usersPerItem[i]-{u}
  numer=0
  denom=0
  for j in js:
    sim = Jaccard(itemsPerUser[j],itemsPerUser[u])
    recency = np.exp(-1 * abs(yearsDict[(u,i)]-yearsDict[(j,i)]))
    numer += hoursDict[(j,i)] * sim * recency
    denom += sim * recency
  return numer / denom if denom!=0 else 0

MSE9 = predict(u2uy)
print(MSE9)

answers['Q9'] = MSE9

assertFloat(answers['Q9'])

if "float" in str(answers) or "int" in str(answers):
    print("it seems that some of your answers are not native python ints/floats;")
    print("the autograder will not be able to read your solution unless you convert them to ints/floats")

f = open("answers_midterm.txt", 'w')
f.write(str(answers) + '\n')
f.close()

