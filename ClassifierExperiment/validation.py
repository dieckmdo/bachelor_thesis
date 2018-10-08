#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pickle
import os
import numpy as np
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
from sklearn.metrics import f1_score
from sklearn.metrics import accuracy_score
from sklearn.metrics import confusion_matrix
import matplotlib.pyplot as plt
from scikitplot.metrics import plot_confusion_matrix

dbFileName = '/home/dominik/python_ws/Classifier/SVMUnrealClassifier.txt'

predictionList = []
predIdx = 0
groundTruthList = []
gtIdx = 0

delimiter = '---'
fs = open(dbFileName, 'r')
dbs = fs.read().split(delimiter)

for db in dbs:
    lines = db.split('\n')
    for l in lines:
        if l.find('object') > -1:
            groundTruthList.append(l)
        elif l.find('instance') > -1:
            predictionList.append(l)

#############################################################
## change list to only contain the objectnames
#############################################################
## create results Directory
dirName = 'results2'
os.mkdir(dirName)

for x, entry in enumerate(groundTruthList):
  groundTruthList[x] = entry.split(',')[1].split(')')[0]

for x, entry in enumerate(predictionList):
  predictionList[x] = entry.split(',')[1].split(')')[0]

##########################################################
## metrics
##########################################################
fileName = dirName + '/metrics.txt'

fs = open(fileName, 'w')

print 'accuracy: ' + str(accuracy_score(groundTruthList, predictionList))
fs.write('accuracy: ' + str(accuracy_score(groundTruthList, predictionList)) + '\n')

print 'precision(macro): ' + str(precision_score(groundTruthList, predictionList, average='macro'))
print 'precision(micro): ' + str(precision_score(groundTruthList, predictionList, average='micro'))
fs.write('precision(macro): ' + str(precision_score(groundTruthList, predictionList, average='macro')) + '\n')
fs.write('precision(micro): ' + str(precision_score(groundTruthList, predictionList, average='micro')) + '\n')

print 'recall(macro): ' + str(recall_score(groundTruthList, predictionList, average='macro'))
print 'recall(micro): ' + str(recall_score(groundTruthList, predictionList, average='micro'))
fs.write('recall(macro): ' + str(recall_score(groundTruthList, predictionList, average='macro')) + '\n')
fs.write('recall(micro): ' + str(recall_score(groundTruthList, predictionList, average='micro')) + '\n')

print 'f1(macro): ' + str(f1_score(groundTruthList, predictionList, average='macro'))
print 'f1(micro): ' + str(f1_score(groundTruthList, predictionList, average='micro'))
fs.write('f1(macro): ' + str(f1_score(groundTruthList, predictionList, average='macro')) + '\n')
fs.write('f1(micro): ' + str(f1_score(groundTruthList, predictionList, average='micro')) + '\n')


print confusion_matrix(groundTruthList, predictionList)

plot_confusion_matrix(groundTruthList, predictionList, x_tick_rotation=90, figsize=(14,13), title=' ', text_fontsize='large', cmap='Reds')
matrixFileName = dirName + '/confusionMatrix.png'
plt.savefig(matrixFileName)
#plt.show()
fs.close()
