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

def toLatexTab(accList, precList, recList, f1List, r):
    resultString = ''
    objectList = ['Bowl', 'BreakfastCereal', 'Buttermilk', 'Coffee', 'Cup', 'DinnerPlate', 'DrinkingBottle', 'DrinkingMug', 'Fork', 'Juice', 'Knife', 'Milk', 'PancakeMaker', 'PancakeMix', 'Rice', 'Spatula', 'Spoon', 'TableSalt', 'Tea-Iced', 'TomatoSauce']
    for i in range(0, 20):
        resultString += objectList[i] + ' & ' 
        resultString += str(round(accList[i], r)) + ' & ' 
        resultString += str(round(precList[i], r)) + ' & '   
        resultString += str(round(recList[i], r)) + ' & ' 
        resultString += str(round(f1List[i], r)) 
        resultString += ' \\\  \n'
    return resultString


dbFileName = 'RFUnrealClassifier.txt'

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
dirName = 'RFresults'
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

#print 'accuracy: ' + str(accuracy_score(groundTruthList, predictionList))
fs.write('accuracy: ' + str(accuracy_score(groundTruthList, predictionList)) + '\n')

# #print 'precision(macro): ' + str(precision_score(groundTruthList, predictionList, average='macro'))
# #print 'precision(micro): ' + str(precision_score(groundTruthList, predictionList, average='micro'))
# #print 'precision(None): ' + str(precision_score(groundTruthList, predictionList, average=None))
fs.write('precision(macro): ' + str(round(precision_score(groundTruthList, predictionList, average='macro'), 4)) + '\n')
fs.write('precision(micro): ' + str(round(precision_score(groundTruthList, predictionList, average='micro'), 4)) + '\n')
fs.write('precision(None): ' + str(precision_score(groundTruthList, predictionList, average=None)) + '\n')

# #print 'recall(macro): ' + str(recall_score(groundTruthList, predictionList, average='macro'))
# #print 'recall(micro): ' + str(recall_score(groundTruthList, predictionList, average='micro'))
# #print 'recall(None): ' + str(recall_score(groundTruthList, predictionList, average=None))
fs.write('recall(macro): ' + str(round(recall_score(groundTruthList, predictionList, average='macro'), 4)) + '\n')
fs.write('recall(micro): ' + str(round(recall_score(groundTruthList, predictionList, average='micro'), 4)) + '\n')
fs.write('recall(None): ' + str(recall_score(groundTruthList, predictionList, average=None)) + '\n')

# #print 'f1(macro): ' + str(f1_score(groundTruthList, predictionList, average='macro'))
# #print 'f1(micro): ' + str(f1_score(groundTruthList, predictionList, average='micro'))
# #print 'f1(None): ' + str(f1_score(groundTruthList, predictionList, average=None))
fs.write('f1(macro): ' + str(round(f1_score(groundTruthList, predictionList, average='macro'), 4)) + '\n')
fs.write('f1(micro): ' + str(round(f1_score(groundTruthList, predictionList, average='micro'), 4)) + '\n')
fs.write('f1(None): ' + str(f1_score(groundTruthList, predictionList, average=None)) + '\n')

# #print confusion_matrix(groundTruthList, predictionList)
cm = confusion_matrix(groundTruthList, predictionList)

allCases = len(groundTruthList)
accuracys = []
for i in range(0, len(cm)):
    li = cm[i]
    tp = li[i]
    rowAll = 0
    for k in range(0, len(li)):
        rowAll += li[k]
    
    rowAll -= tp
    tn = allCases - tp - rowAll
    result = round((tp + tn) / float(allCases), 4)
    accuracys.append(result)

#print accuracys

fs.write('class accuracys: ' + str(accuracys).strip('[]'))
fs.write('\n')
fs.write('\n')
fs.write(toLatexTab(accuracys, precision_score(groundTruthList, predictionList, average=None), recall_score(groundTruthList, predictionList, average=None), f1_score(groundTruthList, predictionList, average=None), 4 ))
fs.write('\n')
fs.write(toLatexTab(accuracys, precision_score(groundTruthList, predictionList, average=None), recall_score(groundTruthList, predictionList, average=None), f1_score(groundTruthList, predictionList, average=None), 2 ))
plot_confusion_matrix(groundTruthList, predictionList, x_tick_rotation=90, figsize=(14,13), title=' ', text_fontsize='large', cmap='Reds')
matrixFileName = dirName + '/confusionMatrix.png'
plt.savefig(matrixFileName)
#plt.show()
fs.close()
