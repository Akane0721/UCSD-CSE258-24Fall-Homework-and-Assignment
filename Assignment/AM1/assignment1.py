# -*- coding: utf-8 -*-
"""assignment1.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1bj36aFHCZOjldbDFuGZKD2vVG3NRNAB-
"""

import gzip
from collections import defaultdict
import math
import scipy.optimize
from sklearn import svm
import numpy as np
import string
import random
import string
from sklearn import linear_model

import warnings
warnings.filterwarnings("ignore")

def assertFloat(x):
    assert type(float(x)) == float

def assertFloatList(items, N):
    assert len(items) == N
    assert [type(float(x)) for x in items] == [float]*N

def readGz(path):
    for l in gzip.open(path, 'rt'):
        yield eval(l)

def readCSV(path):
    f = gzip.open(path, 'rt')
    f.readline()
    for l in f:
        u,b,r = l.strip().split(',')
        r = int(r)
        yield u,b,r

answers = {}

# Some data structures that will be useful
def acc(pred, y):
  return (np.array(pred)==np.array(y)).sum()/len(pred)

allRatings = []
for l in readCSV("train_Interactions.csv.gz"):
    allRatings.append(l)

len(allRatings)

random.seed(0)

ratingsTrain = allRatings[:190000]
ratingsValid = allRatings[190000:]
print(ratingsTrain[0])
ratingsPerUser = defaultdict(list)
ratingsPerItem = defaultdict(list)
usersPerItem = defaultdict(set)
itemsPerUser = defaultdict(set)
ratingDict = {}
for u,b,r in ratingsTrain:
    ratingsPerUser[u].append((b,r))
    ratingsPerItem[b].append((u,r))
    usersPerItem[b].add(u)
    itemsPerUser[u].add(b)
    ratingDict[(u,b)]=r

##################################################
# Read prediction                                #
##################################################
booksPerUser = {u: set(b for b, r in ratingsPerUser[u]) for u in ratingsPerUser}
Negative = []
avg_rating = np.mean([r for _,_,r in ratingsTrain])
all_books = set(ratingsPerItem.keys())

for u,b,r in ratingsValid:
  if u in booksPerUser:
    unread_books = list(all_books - booksPerUser[u])
    if unread_books:
      negative_book = random.choice(unread_books)
      Negative.append((u, negative_book, 0))

newRatingsValid = ratingsValid + Negative
print(len(newRatingsValid))

import csv
to1=[]
Neg=[]
for u,b,r in allRatings:
  to1.append((u,b,5))
  if u in booksPerUser:
    unread_books = list(all_books - booksPerUser[u])
    if unread_books:
      negative_book = random.choice(unread_books)
      Neg.append((u, negative_book, 0))

whole = to1 + Neg
output_file = '/content/dataTrain.csv'

# 将列表写入 CSV 文件
with open(output_file, mode='w', newline='') as file:
    writer = csv.writer(file)
    # 写入标题行
    writer.writerow(['userID', 'bookID', 'rating'])
    # 写入数据行
    writer.writerows(whole)

!pip install scikit-surprise
import pandas as pd
from surprise import SVD, Dataset, Reader, SVDpp
from surprise.model_selection import train_test_split

from surprise.model_selection import GridSearchCV

reader = Reader(line_format='user item rating', sep=',', skip_lines=1)
data = Dataset.load_from_file('/content/dataTrain.csv', reader=reader)
trainset, testset = train_test_split(data, test_size=0.05)

'''
df = pd.DataFrame(ratingsTrain, columns=['user_id', 'book_id', 'rating'])
reader = Reader(rating_scale=(0, 5))
train_data = Dataset.load_from_df(df[['user_id', 'book_id', 'rating']], reader)
trainset = train_data.build_full_trainset()'''

param_grid = {
    'n_factors': [50, 100, 150],
    'n_epochs': [10, 20, 30],
    'lr_all': [0.002, 0.005, 0.01],
    'reg_all': [0.05, 0.1, 0.2]
}

grid_search = GridSearchCV(SVD, param_grid, measures=['RMSE'], cv=3)
grid_search.fit(data)
best_params = grid_search.best_params['rmse']
print(f"Best parameters: {best_params}")

#svd=SVDpp(n_factors=50,n_epochs=10,lr_all=0.002,reg_all=0.2)
#trainset = data.build_full_trainset()
svd=SVD(n_factors=50,n_epochs=10,lr_all=0.005,reg_all=0.05)
svd.fit(trainset)
from surprise import accuracy
predictions = svd.test(testset)
accuracy.rmse(predictions)

sse = 0
for p in predictions:
  sse += (p.r_ui - p.est) ** 2

mses = sse/len(predictions)
print(mses)

pred=[]
y=[]
realp=[]
realy=[]

def mseSVD(pred, y):
  return np.mean((np.array(pred) - np.array(y)) ** 2)

for u,b,r in newRatingsValid:
  predRating=svd.predict(u,b).est
  realp.append(predRating)
  realy.append(r)
  if predRating>2.35:
    pred.append(1)
  else:
    pred.append(0)
  if r>0: y.append(1)
  else: y.append(0)

accs=acc(pred,y)
mses=mseSVD(realp,realy)
print(accs,mses)
print(np.mean(realp))

predictions = open("predictions_Read.csv", 'w')
for l in open("pairs_Read.csv"):
    if l.startswith("userID"):
        predictions.write(l)
        continue
    u,b = l.strip().split(',')
    pred=svd.predict(u,b).est
    if pred>2.35: pred=1
    else: pred=0
    predictions.write(f"{u},{b},{pred}\n")
    # (etc.)

predictions.close()

reader = Reader(line_format='user item rating', sep=',', skip_lines=1)
data = Dataset.load_from_file('/content/train_Interactions.csv', reader=reader)
trainset, testset = train_test_split(data, test_size=0.05)

param_grid = {
    'n_factors': [50, 100, 200],
    'n_epochs': [10, 20, 30],
    'lr_all': [0.005, 0.01, 0.015],
    'reg_all': [0.05, 0.1, 0.2]
}

grid_search = GridSearchCV(SVD, param_grid, measures=['RMSE'], cv=3)
grid_search.fit(data)
best_params = grid_search.best_params['rmse']
print(f"Best parameters: {best_params}")

svd2=SVD(n_factors=25,n_epochs=20,lr_all=0.01,reg_all=0.3)
trainset = data.build_full_trainset()
svd2.fit(trainset)

sse=0
for u,b,r in ratingsValid:
  p=svd2.predict(u,b).est
  sse+=(p-r)**2
print(sse/len(ratingsValid))

#a, bu, bi = best_para_l

predictions = open("predictions_Rating.csv", 'w')
for l in open("pairs_Rating.csv"):
    if l.startswith("userID"): # header
        predictions.write(l)
        continue
    u,b = l.strip().split(',') # Read the user and item from the "pairs" file and write out your prediction
    pred = svd2.predict(u,b).est
    predictions.write(f"{u},{b},{pred}\n")
    # (etc.)

predictions.close()